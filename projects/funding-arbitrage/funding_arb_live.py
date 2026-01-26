#!/usr/bin/env python3
"""
펀딩비 차익거래 실전 봇 - Hyperliquid + Extended

델타뉴트럴 전략: 한쪽 롱 + 한쪽 숏 → 가격 위험 없이 펀딩비 차이만큼 수익

사용법:
  python3 funding_arb_live.py --monitor --once         # 모니터링 1회
  python3 funding_arb_live.py --live --dry-run --once   # 드라이런 1회
  python3 funding_arb_live.py --live --once              # 실전 1회
  python3 funding_arb_live.py --live                     # 자동 반복 (30분)
"""

import os
import json
import time
import argparse
import requests
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# .env 로드
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# === 설정 ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7881191796:AAEB4mN7dMIj3jEN0PoWAo46z6TPX-hawfI")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6329588659")

MAX_POSITION_USD = float(os.getenv("MAX_POSITION_USD", "100"))
MIN_SPREAD = float(os.getenv("MIN_SPREAD", "0.02"))  # 0.02% = 최소 진입 스프레드
CLOSE_SPREAD = float(os.getenv("CLOSE_SPREAD", "0.005"))  # 0.005% 이하면 청산

# 모니터링할 코인 (양쪽 거래소에 있는 것들)
COINS = ["BTC", "ETH", "SOL", "DOGE", "AVAX", "ARB", "LINK", "XRP", "SUI", "APT",
         "OP", "INJ", "TIA", "SEI", "PEPE"]

# 포지션 상태 파일
POSITIONS_FILE = os.path.join(os.path.dirname(__file__), "positions.json")


# === 유틸리티 ===

def send_telegram(message: str):
    """텔레그램 알림 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"[텔레그램 에러] {e}")


def format_rate(rate: float) -> str:
    if rate > 0:
        return f"+{rate:.4f}%"
    return f"{rate:.4f}%"


def load_positions() -> dict:
    """저장된 포지션 로드"""
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_positions(positions: dict):
    """포지션 상태 저장"""
    with open(POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=2, default=str)


# === 펀딩비 조회 (모니터링 모드용 - SDK 없이도 작동) ===

# 코인 이름 매핑 (표준 → 거래소별)
HL_COIN_MAP = {"PEPE": "kPEPE", "BONK": "kBONK", "SHIB": "kSHIB"}
HL_COIN_MAP_REVERSE = {v: k for k, v in HL_COIN_MAP.items()}
EXT_COIN_MAP = {"PEPE": "1000PEPE", "BONK": "1000BONK", "SHIB": "1000SHIB"}


def get_hl_funding_api() -> dict[str, float]:
    """Hyperliquid 펀딩비 - REST API 직접 호출"""
    try:
        url = "https://api.hyperliquid.xyz/info"
        resp = requests.post(url, json={"type": "metaAndAssetCtxs"}, timeout=10)
        data = resp.json()
        universe = data[0]["universe"]
        asset_contexts = data[1]

        rates = {}
        for i, asset in enumerate(universe):
            hl_name = asset["name"]
            # 역매핑: HL 이름 → 표준 이름
            coin = HL_COIN_MAP_REVERSE.get(hl_name, hl_name)
            if coin in COINS:
                rates[coin] = float(asset_contexts[i]["funding"]) * 100
        return rates
    except Exception as e:
        print(f"[Hyperliquid 에러] {e}")
        return {}


def get_ext_funding_api(coins: list[str] | None = None) -> dict[str, float]:
    """Extended 펀딩비 - REST API 직접 호출"""
    target_coins = coins or COINS
    rates = {}
    headers = {"User-Agent": "funding-arb-bot/1.0", "Accept": "application/json"}
    base_url = "https://api.starknet.extended.exchange"

    for coin in target_coins:
        try:
            ext_coin = EXT_COIN_MAP.get(coin, coin)
            market = f"{ext_coin}-USD"
            url = f"{base_url}/api/v1/info/markets/{market}/stats"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                stats = result.get("data", result)  # {"status": "OK", "data": {...}}
                funding_rate = stats.get("fundingRate")
                if funding_rate is not None:
                    # Extended: hourly → ×8 for 8h, ×100 for %
                    rates[coin] = float(funding_rate) * 8 * 100
        except Exception as e:
            print(f"[Extended 에러] {coin}: {e}")
    return rates


# === 스프레드 계산 ===

def calculate_opportunities(hl_rates: dict, ext_rates: dict) -> list[dict]:
    """양쪽 펀딩비 비교 및 기회 계산"""
    opportunities = []

    for coin in COINS:
        if coin not in hl_rates or coin not in ext_rates:
            continue

        hl_rate = hl_rates[coin]
        ext_rate = ext_rates[coin]
        spread = abs(hl_rate - ext_rate)

        if hl_rate > ext_rate:
            # HL 펀딩비가 높음 → HL 숏 (펀딩 받음) + EXT 롱
            strategy = "HL 숏 / EXT 롱"
            hl_side = "SHORT"
            ext_side = "LONG"
            net_funding = hl_rate - ext_rate
        else:
            # EXT 펀딩비가 높음 → EXT 숏 (펀딩 받음) + HL 롱
            strategy = "EXT 숏 / HL 롱"
            hl_side = "LONG"
            ext_side = "SHORT"
            net_funding = ext_rate - hl_rate

        annual_yield = net_funding * 3 * 365  # 8시간 × 3 × 365

        opportunities.append({
            "coin": coin,
            "hl_rate": hl_rate,
            "ext_rate": ext_rate,
            "spread": spread,
            "net_funding": net_funding,
            "annual_yield": annual_yield,
            "strategy": strategy,
            "hl_side": hl_side,
            "ext_side": ext_side,
        })

    opportunities.sort(key=lambda x: x["spread"], reverse=True)
    return opportunities


# === 포지션 관리 ===

def open_position(coin: str, hl_side: str, ext_side: str, size_usd: float,
                  hl_client, ext_client, dry_run: bool = False) -> bool:
    """양쪽 동시 진입

    Returns:
        True if both sides opened successfully
    """
    # 코인 이름 변환
    hl_coin = HL_COIN_MAP.get(coin, coin)

    # 가격 조회 (HL에서)
    prices = hl_client.get_mark_prices()
    price = prices.get(hl_coin)
    if not price:
        print(f"[에러] {coin} 가격 조회 실패")
        return False

    # 수량 계산
    sz_decimals = hl_client.get_sz_decimals()
    decimals = sz_decimals.get(hl_coin, 2)
    size_coin = round(size_usd / price, decimals)

    if size_coin <= 0:
        print(f"[에러] {coin} 수량이 0 이하: ${size_usd} / ${price:.2f} = {size_coin}")
        return False

    hl_is_buy = hl_side == "LONG"
    ext_is_buy = ext_side == "LONG"

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}포지션 진입:")
    print(f"  코인: {coin}")
    print(f"  크기: {size_coin} {coin} (${size_usd})")
    print(f"  HL: {'롱' if hl_is_buy else '숏'} | EXT: {'롱' if ext_is_buy else '숏'}")
    print(f"  가격: ${price:.2f}")

    if dry_run:
        send_telegram(
            f"📊 [DRY-RUN] 포지션 진입 시뮬레이션\n\n"
            f"코인: {coin}\n"
            f"HL {'롱' if hl_is_buy else '숏'} + EXT {'롱' if ext_is_buy else '숏'}\n"
            f"크기: {size_coin} {coin} (${size_usd})\n"
            f"가격: ${price:.2f}"
        )
        return True

    # 1. HL 주문 (HL 이름 사용)
    print(f"  HL 주문 중...")
    hl_result = hl_client.place_market_order(hl_coin, hl_is_buy, size_coin)
    print(f"  HL 결과: {hl_result}")

    if not hl_result.get("success"):
        print(f"  [실패] HL 주문 실패: {hl_result.get('error')}")
        send_telegram(
            f"⚠️ HL {coin} {'롱' if hl_is_buy else '숏'} 주문 실패!\n"
            f"에러: {hl_result.get('error')}"
        )
        return False

    # 2. EXT 주문
    print(f"  EXT 주문 중...")
    ext_result = ext_client.place_market_order(coin, ext_is_buy, size_coin)
    print(f"  EXT 결과: {ext_result}")

    if not ext_result.get("success"):
        # EXT 실패 → HL 즉시 청산
        print(f"  [실패] EXT 주문 실패! HL 포지션 긴급 청산...")
        send_telegram(
            f"⚠️ EXT {coin} {'롱' if ext_is_buy else '숏'} 주문 실패!\n"
            f"에러: {ext_result.get('error')}\n"
            f"→ HL 포지션 긴급 청산 중..."
        )
        close_result = hl_client.close_position(hl_coin)
        print(f"  HL 청산 결과: {close_result}")
        send_telegram(
            f"{'✅ HL 청산 완료' if close_result.get('success') else '❌ HL 청산도 실패!'}\n"
            f"결과: {close_result}"
        )
        return False

    # 양쪽 성공 → 포지션 저장
    positions = load_positions()
    positions[coin] = {
        "hl_side": hl_side,
        "ext_side": ext_side,
        "size_coin": size_coin,
        "size_usd": size_usd,
        "entry_price": price,
        "opened_at": datetime.now().isoformat(),
        "hl_order": hl_result,
        "ext_order": ext_result,
    }
    save_positions(positions)

    send_telegram(
        f"🟢 포지션 진입 완료\n\n"
        f"코인: {coin}\n"
        f"HL {'롱' if hl_is_buy else '숏'} + EXT {'롱' if ext_is_buy else '숏'}\n"
        f"크기: {size_coin} {coin} (${size_usd})\n"
        f"가격: ${price:.2f}"
    )
    return True


def close_position(coin: str, hl_client, ext_client, dry_run: bool = False) -> bool:
    """양쪽 동시 청산"""
    positions = load_positions()
    pos = positions.get(coin)
    if not pos:
        print(f"[에러] {coin} 포지션 없음")
        return False

    opened_at = pos.get("opened_at", "?")
    size_coin = pos.get("size_coin", 0)

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}포지션 청산:")
    print(f"  코인: {coin}")
    print(f"  크기: {size_coin} {coin}")
    print(f"  진입: {opened_at}")

    # 코인 이름 변환
    hl_coin = HL_COIN_MAP.get(coin, coin)

    if dry_run:
        send_telegram(
            f"📊 [DRY-RUN] 포지션 청산 시뮬레이션\n\n"
            f"코인: {coin} | 크기: {size_coin}\n"
            f"진입: {opened_at}"
        )
        del positions[coin]
        save_positions(positions)
        return True

    # 1. HL 청산 (HL 이름 사용)
    print(f"  HL 청산 중...")
    hl_result = hl_client.close_position(hl_coin)
    print(f"  HL 결과: {hl_result}")

    # 2. EXT 청산 (표준 이름 사용 - ExtendedClient가 자체 매핑)
    print(f"  EXT 청산 중...")
    ext_result = ext_client.close_position(coin)
    print(f"  EXT 결과: {ext_result}")

    hl_ok = hl_result.get("success", False)
    ext_ok = ext_result.get("success", False)

    if hl_ok and ext_ok:
        del positions[coin]
        save_positions(positions)
        send_telegram(
            f"🔴 포지션 청산 완료\n\n"
            f"코인: {coin}\n"
            f"크기: {size_coin}\n"
            f"진입: {opened_at}\n"
            f"청산: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        return True
    else:
        msg = f"⚠️ {coin} 청산 일부 실패!\n"
        if not hl_ok:
            msg += f"HL 에러: {hl_result.get('error')}\n"
        if not ext_ok:
            msg += f"EXT 에러: {ext_result.get('error')}\n"
        msg += "수동 확인 필요!"
        send_telegram(msg)
        print(f"  [경고] 청산 일부 실패 - 수동 확인 필요")
        return False


def check_positions(hl_client, ext_client) -> list[dict]:
    """현재 포지션 상태 확인 및 크기 불일치 경고"""
    positions = load_positions()
    if not positions:
        print("열린 포지션 없음")
        return []

    hl_positions = hl_client.get_positions()
    ext_positions = ext_client.get_positions()

    # HL은 자체 이름 사용 (kPEPE 등) → 표준 이름으로 변환
    hl_map = {}
    for p in hl_positions:
        std_name = HL_COIN_MAP_REVERSE.get(p["coin"], p["coin"])
        hl_map[std_name] = p
    ext_map = {p["coin"]: p for p in ext_positions}

    results = []
    for coin, pos_info in positions.items():
        hl_pos = hl_map.get(coin)
        ext_pos = ext_map.get(coin)

        result = {
            "coin": coin,
            "saved": pos_info,
            "hl_actual": hl_pos,
            "ext_actual": ext_pos,
            "ok": True,
        }

        # 크기 불일치 체크
        if hl_pos and ext_pos:
            hl_size = hl_pos["size"]
            ext_size = ext_pos["size"]
            if abs(hl_size - ext_size) / max(hl_size, ext_size) > 0.1:  # 10% 이상 차이
                result["ok"] = False
                result["warning"] = f"크기 불일치: HL={hl_size}, EXT={ext_size}"
                send_telegram(
                    f"⚠️ {coin} 포지션 크기 불일치!\n"
                    f"HL: {hl_size} {coin}\n"
                    f"EXT: {ext_size} {coin}\n"
                    f"수동 확인 필요!"
                )
        elif not hl_pos or not ext_pos:
            result["ok"] = False
            missing = "HL" if not hl_pos else "EXT"
            result["warning"] = f"{missing} 포지션 없음"
            send_telegram(
                f"⚠️ {coin} {missing} 포지션이 없습니다!\n"
                f"한쪽만 열려 있음 - 수동 확인 필요!"
            )

        results.append(result)

    return results


def risk_check(hl_client, ext_client) -> bool:
    """리스크 체크 - 포지션 크기/PnL 한도"""
    hl_balance = hl_client.get_balance()
    ext_balance = ext_client.get_balance()

    total_value = hl_balance.get("account_value", 0) + ext_balance.get("equity", 0)
    positions = load_positions()
    total_position = sum(p.get("size_usd", 0) for p in positions.values())

    print(f"\n리스크 현황:")
    print(f"  HL 잔액: ${hl_balance.get('account_value', 0):.2f}")
    print(f"  EXT 잔액: ${ext_balance.get('equity', 0):.2f}")
    print(f"  총 포지션: ${total_position:.2f}")
    print(f"  MAX 허용: ${MAX_POSITION_USD:.2f}")

    if total_position >= MAX_POSITION_USD:
        print(f"  ⚠️ 최대 포지션 한도 도달!")
        return False
    return True


# === 메인 로직 ===

def run_monitor(once: bool = False):
    """모니터링 모드: 스프레드만 감시"""
    print("\n📊 [모니터링 모드] HL vs Extended 펀딩비 비교")
    print(f"   모니터링 코인: {', '.join(COINS)}")
    print(f"   알림 기준: 스프레드 >= {MIN_SPREAD}%\n")

    while True:
        try:
            print(f"\n{'='*70}")
            print(f"  펀딩비 조회 중... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}")

            hl_rates = get_hl_funding_api()
            ext_rates = get_ext_funding_api()

            if not hl_rates or not ext_rates:
                print("⚠️ API 조회 실패")
                if not once:
                    time.sleep(60)
                    continue
                return

            opportunities = calculate_opportunities(hl_rates, ext_rates)

            # 결과 표
            print(f"\n{'코인':<6} {'Hyperliquid':>12} {'Extended':>12} {'스프레드':>10} {'연수익률':>10} {'전략'}")
            print("-" * 75)

            for opp in opportunities:
                mark = " ⭐" if opp["spread"] >= MIN_SPREAD else ""
                print(
                    f"{opp['coin']:<6} "
                    f"{format_rate(opp['hl_rate']):>12} "
                    f"{format_rate(opp['ext_rate']):>12} "
                    f"{opp['spread']:.4f}%{'':<4} "
                    f"{opp['annual_yield']:.1f}%{'':<4} "
                    f"{opp['strategy']}{mark}"
                )

            # 좋은 기회 알림
            good = [o for o in opportunities if o["spread"] >= MIN_SPREAD]
            if good:
                msg = f"🔥 HL vs EXT 차익거래 기회!\n\n"
                for opp in good[:5]:
                    msg += (
                        f"▸ {opp['coin']}\n"
                        f"  HL: {format_rate(opp['hl_rate'])} | EXT: {format_rate(opp['ext_rate'])}\n"
                        f"  스프레드: {opp['spread']:.4f}% (연 {opp['annual_yield']:.1f}%)\n"
                        f"  전략: {opp['strategy']}\n\n"
                    )
                msg += f"⏰ {datetime.now().strftime('%H:%M')}"
                send_telegram(msg)
                print(f"\n✅ 텔레그램 알림 전송 ({len(good)}개 기회)")

            if once:
                return

            print(f"\n⏳ 30분 후 재체크...")
            time.sleep(30 * 60)

        except KeyboardInterrupt:
            print("\n\n👋 모니터링 종료")
            return
        except Exception as e:
            print(f"[에러] {e}")
            if once:
                return
            time.sleep(60)


def run_live(once: bool = False, dry_run: bool = False):
    """실전 모드: 실제 주문 실행"""
    from exchanges.hyperliquid_client import HyperliquidClient
    from exchanges.extended_client import ExtendedClient

    # 환경변수 검증
    hl_key = os.getenv("HL_PRIVATE_KEY")
    hl_wallet = os.getenv("HL_WALLET_ADDRESS")
    ext_api_key = os.getenv("EXT_API_KEY")
    ext_stark_priv = os.getenv("EXT_STARK_PRIVATE_KEY")
    ext_stark_pub = os.getenv("EXT_STARK_PUBLIC_KEY")
    ext_vault = os.getenv("EXT_VAULT")

    missing = []
    if not hl_key:
        missing.append("HL_PRIVATE_KEY")
    if not hl_wallet:
        missing.append("HL_WALLET_ADDRESS")
    if not ext_api_key:
        missing.append("EXT_API_KEY")
    if not ext_stark_priv:
        missing.append("EXT_STARK_PRIVATE_KEY")
    if not ext_stark_pub:
        missing.append("EXT_STARK_PUBLIC_KEY")
    if not ext_vault:
        missing.append("EXT_VAULT")

    if missing:
        print(f"❌ 환경변수 누락: {', '.join(missing)}")
        print(f"   .env 파일을 확인하세요!")
        return

    # 클라이언트 초기화
    print(f"\n🚀 [{'DRY-RUN' if dry_run else '실전'} 모드] 차익거래 봇 시작")
    print(f"   최대 포지션: ${MAX_POSITION_USD}")
    print(f"   진입 기준: 스프레드 >= {MIN_SPREAD}%")
    print(f"   청산 기준: 스프레드 <= {CLOSE_SPREAD}%\n")

    hl_client = HyperliquidClient(hl_key, hl_wallet)
    ext_client = ExtendedClient(ext_api_key, ext_stark_priv, ext_stark_pub, int(ext_vault))

    send_telegram(
        f"🚀 차익거래 봇 시작\n"
        f"모드: {'DRY-RUN' if dry_run else '실전'}\n"
        f"최대 포지션: ${MAX_POSITION_USD}\n"
        f"진입 스프레드: >= {MIN_SPREAD}%\n"
        f"청산 스프레드: <= {CLOSE_SPREAD}%"
    )

    while True:
        try:
            print(f"\n{'='*70}")
            print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 차익거래 체크")
            print(f"{'='*70}")

            # 1. 펀딩비 조회
            hl_rates = get_hl_funding_api()
            ext_rates = get_ext_funding_api()

            if not hl_rates or not ext_rates:
                print("⚠️ API 조회 실패")
                if not once:
                    time.sleep(60)
                    continue
                return

            # 2. 기회 계산
            opportunities = calculate_opportunities(hl_rates, ext_rates)

            # 결과 표시
            for opp in opportunities[:5]:
                mark = " ⭐" if opp["spread"] >= MIN_SPREAD else ""
                print(
                    f"  {opp['coin']:<6} 스프레드: {opp['spread']:.4f}% "
                    f"(연 {opp['annual_yield']:.1f}%) {opp['strategy']}{mark}"
                )

            # 3. 기존 포지션 체크 - 청산 조건
            positions = load_positions()
            for coin, pos_info in list(positions.items()):
                opp = next((o for o in opportunities if o["coin"] == coin), None)
                if not opp:
                    continue

                # 스프레드가 반전되었거나 CLOSE_SPREAD 이하면 청산
                current_hl_side = opp["hl_side"]
                saved_hl_side = pos_info["hl_side"]

                spread_reversed = current_hl_side != saved_hl_side
                spread_too_low = opp["spread"] <= CLOSE_SPREAD

                if spread_reversed or spread_too_low:
                    reason = "스프레드 반전" if spread_reversed else f"스프레드 {opp['spread']:.4f}% <= {CLOSE_SPREAD}%"
                    print(f"\n  📉 {coin} 청산 신호: {reason}")
                    close_position(coin, hl_client, ext_client, dry_run)

            # 4. 신규 진입 검토
            if not risk_check(hl_client, ext_client) and not dry_run:
                print("  포지션 한도 도달 - 신규 진입 불가")
            else:
                positions = load_positions()  # 리로드 (청산 후 변경됐을 수 있음)
                for opp in opportunities:
                    coin = opp["coin"]
                    if coin in positions:
                        continue  # 이미 포지션 있음
                    if opp["spread"] < MIN_SPREAD:
                        break  # 정렬되어 있으므로 더 볼 필요 없음

                    # 포지션 크기 계산 (MAX에서 현재 사용량 차감)
                    current_used = sum(p.get("size_usd", 0) for p in positions.values())
                    available = MAX_POSITION_USD - current_used
                    if available <= 0 and not dry_run:
                        break

                    # 코인당 최대 포지션 = 전체의 50%
                    size_usd = min(available, MAX_POSITION_USD * 0.5)
                    if size_usd < 10:
                        size_usd = min(10, available)  # 최소 $10

                    print(f"\n  🟢 {coin} 진입 기회: 스프레드 {opp['spread']:.4f}%")
                    success = open_position(
                        coin, opp["hl_side"], opp["ext_side"], size_usd,
                        hl_client, ext_client, dry_run
                    )
                    if success and not dry_run:
                        positions = load_positions()  # 리로드

            # 5. 포지션 상태 확인
            if positions:
                print("\n  현재 포지션:")
                check_positions(hl_client, ext_client)

            if once:
                return

            print(f"\n⏳ 30분 후 재체크...")
            time.sleep(30 * 60)

        except KeyboardInterrupt:
            print("\n\n👋 봇 종료")
            send_telegram("🛑 차익거래 봇 종료")
            return
        except Exception as e:
            print(f"[에러] {e}")
            import traceback
            traceback.print_exc()
            if once:
                return
            time.sleep(60)


# === 엔트리포인트 ===

def main():
    parser = argparse.ArgumentParser(description="펀딩비 차익거래 봇 - HL vs Extended")
    parser.add_argument("--monitor", action="store_true", help="모니터링 모드 (스프레드 감시만)")
    parser.add_argument("--live", action="store_true", help="실전 모드 (주문 실행)")
    parser.add_argument("--dry-run", action="store_true", help="드라이런 (주문 안 보냄)")
    parser.add_argument("--once", action="store_true", help="한 번만 실행")
    parser.add_argument("--status", action="store_true", help="현재 포지션 상태")
    parser.add_argument("--close", type=str, help="특정 코인 포지션 청산")
    parser.add_argument("--close-all", action="store_true", help="모든 포지션 청산")
    args = parser.parse_args()

    if args.status:
        positions = load_positions()
        if not positions:
            print("열린 포지션 없음")
        else:
            print(f"\n현재 포지션 ({len(positions)}개):")
            for coin, info in positions.items():
                print(f"  {coin}: {info['hl_side']} (HL) + {info['ext_side']} (EXT)")
                print(f"    크기: {info['size_coin']} {coin} (${info['size_usd']})")
                print(f"    진입: {info['opened_at']}")
        return

    if args.close or args.close_all:
        from exchanges.hyperliquid_client import HyperliquidClient
        from exchanges.extended_client import ExtendedClient

        hl_client = HyperliquidClient(
            os.getenv("HL_PRIVATE_KEY", ""),
            os.getenv("HL_WALLET_ADDRESS", ""),
        )
        ext_client = ExtendedClient(
            os.getenv("EXT_API_KEY", ""),
            os.getenv("EXT_STARK_PRIVATE_KEY", ""),
            os.getenv("EXT_STARK_PUBLIC_KEY", ""),
            int(os.getenv("EXT_VAULT", "0")),
        )

        if args.close_all:
            positions = load_positions()
            for coin in list(positions.keys()):
                close_position(coin, hl_client, ext_client)
        elif args.close:
            close_position(args.close, hl_client, ext_client)
        return

    if args.live:
        run_live(once=args.once, dry_run=args.dry_run)
    elif args.monitor:
        run_monitor(once=args.once)
    else:
        print("모드를 선택하세요:")
        print("  --monitor    모니터링 (스프레드 감시)")
        print("  --live       실전 (주문 실행)")
        print("  --status     포지션 상태 확인")
        print("  --close BTC  특정 코인 청산")
        print("  --close-all  전체 청산")
        print("")
        print("옵션:")
        print("  --dry-run    드라이런 (주문 안 보냄)")
        print("  --once       한 번만 실행")


if __name__ == "__main__":
    main()
