#!/usr/bin/env python3
"""
Cross-DEX 펀딩비 차익거래 모니터링 봇
Hyperliquid vs Binance 펀딩비 스프레드 감지

사용법:
  python3 funding_arb.py --once     # 한 번 실행
  python3 funding_arb.py            # 30분마다 반복 실행
"""

import requests
import time
import argparse
from datetime import datetime
from typing import Dict, List, Tuple

# === 설정 ===
TELEGRAM_TOKEN = "7881191796:AAEB4mN7dMIj3jEN0PoWAo46z6TPX-hawfI"
TELEGRAM_CHAT_ID = "6329588659"

# 모니터링할 코인 (양쪽 거래소에 다 있는 것들)
COINS = ["BTC", "ETH", "SOL", "DOGE", "AVAX", "ARB", "LINK", "XRP", "SUI", "APT", "OP", "INJ", "TIA", "SEI", "PEPE"]

# 알림 기준 (스프레드가 이 이상이면 알림)
MIN_SPREAD_ALERT = 0.01  # 0.01% = 연 10.8% 수익률

# === API 함수들 ===

def get_hyperliquid_funding() -> Dict[str, float]:
    """Hyperliquid 펀딩비 조회"""
    url = "https://api.hyperliquid.xyz/info"
    payload = {"type": "metaAndAssetCtxs"}

    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()

        funding_rates = {}

        # meta에서 코인 이름 가져오기
        universe = data[0]["universe"]
        asset_contexts = data[1]

        for i, asset in enumerate(universe):
            coin = asset["name"]
            if coin in COINS:
                # funding은 8시간 기준, 퍼센트로 변환
                funding = float(asset_contexts[i]["funding"]) * 100
                funding_rates[coin] = funding

        return funding_rates
    except Exception as e:
        print(f"[Hyperliquid 에러] {e}")
        return {}


def get_binance_funding() -> Dict[str, float]:
    """Binance 펀딩비 조회"""
    url = "https://fapi.binance.com/fapi/v1/premiumIndex"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        funding_rates = {}

        for item in data:
            symbol = item["symbol"]
            # BTCUSDT -> BTC
            if symbol.endswith("USDT"):
                coin = symbol.replace("USDT", "")
                if coin in COINS:
                    # 이미 퍼센트가 아님, 변환 필요 (0.0001 = 0.01%)
                    funding = float(item["lastFundingRate"]) * 100
                    funding_rates[coin] = funding

        return funding_rates
    except Exception as e:
        print(f"[Binance 에러] {e}")
        return {}


def calculate_spreads(hl_rates: Dict[str, float], bn_rates: Dict[str, float]) -> List[Dict]:
    """스프레드 계산 및 기회 분석"""
    opportunities = []

    for coin in COINS:
        if coin not in hl_rates or coin not in bn_rates:
            continue

        hl_rate = hl_rates[coin]
        bn_rate = bn_rates[coin]

        # 스프레드 = |Hyperliquid - Binance|
        spread = abs(hl_rate - bn_rate)

        # 어디서 숏하고 어디서 롱할지 결정
        if hl_rate > bn_rate:
            # Hyperliquid에서 숏 (펀딩 받음), Binance에서 롱
            strategy = "HL 숏 / BN 롱"
            hl_action = "SHORT"
            bn_action = "LONG"
            # 수익 = HL 펀딩(받음) - BN 펀딩(지불) = hl_rate - bn_rate
            net_funding = hl_rate - bn_rate
        else:
            # Binance에서 숏 (펀딩 받음), Hyperliquid에서 롱
            strategy = "BN 숏 / HL 롱"
            hl_action = "LONG"
            bn_action = "SHORT"
            # 수익 = BN 펀딩(받음) - HL 펀딩(지불) = bn_rate - hl_rate
            net_funding = bn_rate - hl_rate

        # 연간 수익률 계산 (8시간마다 × 3 × 365)
        annual_yield = net_funding * 3 * 365

        opportunities.append({
            "coin": coin,
            "hl_rate": hl_rate,
            "bn_rate": bn_rate,
            "spread": spread,
            "net_funding": net_funding,
            "annual_yield": annual_yield,
            "strategy": strategy,
            "hl_action": hl_action,
            "bn_action": bn_action
        })

    # 스프레드 순으로 정렬
    opportunities.sort(key=lambda x: x["spread"], reverse=True)

    return opportunities


def format_rate(rate: float) -> str:
    """펀딩비 포맷팅 (색상 표시용)"""
    if rate > 0:
        return f"+{rate:.4f}%"
    else:
        return f"{rate:.4f}%"


def send_telegram(message: str):
    """텔레그램 알림 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[텔레그램 에러] {e}")


def print_results(opportunities: List[Dict]):
    """결과 출력"""
    print("\n" + "="*70)
    print(f"  Cross-DEX 펀딩비 차익거래 기회 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print(f"{'코인':<6} {'Hyperliquid':>12} {'Binance':>12} {'스프레드':>10} {'연수익률':>10} {'전략'}")
    print("-"*70)

    for opp in opportunities:
        coin = opp["coin"]
        hl = format_rate(opp["hl_rate"])
        bn = format_rate(opp["bn_rate"])
        spread = f"{opp['spread']:.4f}%"
        annual = f"{opp['annual_yield']:.1f}%"
        strategy = opp["strategy"]

        # 좋은 기회는 하이라이트
        if opp["spread"] >= MIN_SPREAD_ALERT:
            print(f"{coin:<6} {hl:>12} {bn:>12} {spread:>10} {annual:>10} {strategy} ⭐")
        else:
            print(f"{coin:<6} {hl:>12} {bn:>12} {spread:>10} {annual:>10} {strategy}")

    print("="*70)


def check_and_alert(opportunities: List[Dict]):
    """좋은 기회 발견시 알림"""
    good_opps = [o for o in opportunities if o["spread"] >= MIN_SPREAD_ALERT]

    if good_opps:
        msg = f"🔥 펀딩비 차익거래 기회!\n\n"

        for opp in good_opps[:5]:  # 상위 5개만
            msg += f"▸ {opp['coin']}\n"
            msg += f"  HL: {format_rate(opp['hl_rate'])} | BN: {format_rate(opp['bn_rate'])}\n"
            msg += f"  스프레드: {opp['spread']:.4f}% (연 {opp['annual_yield']:.1f}%)\n"
            msg += f"  전략: {opp['strategy']}\n\n"

        msg += f"⏰ {datetime.now().strftime('%H:%M')}"

        send_telegram(msg)
        print(f"\n✅ 텔레그램 알림 전송 완료! ({len(good_opps)}개 기회)")


def main():
    parser = argparse.ArgumentParser(description="Cross-DEX 펀딩비 차익거래 모니터링")
    parser.add_argument("--once", action="store_true", help="한 번만 실행")
    parser.add_argument("--interval", type=int, default=30, help="반복 주기 (분)")
    parser.add_argument("--alert-only", action="store_true", help="기회 발견시에만 알림")
    args = parser.parse_args()

    print("🚀 Cross-DEX 펀딩비 차익거래 봇 시작!")
    print(f"   모니터링 코인: {', '.join(COINS)}")
    print(f"   알림 기준: 스프레드 >= {MIN_SPREAD_ALERT}%")

    while True:
        try:
            # 1. 펀딩비 조회
            print("\n📊 펀딩비 조회 중...")
            hl_rates = get_hyperliquid_funding()
            bn_rates = get_binance_funding()

            if not hl_rates or not bn_rates:
                print("⚠️ API 조회 실패, 재시도...")
                time.sleep(60)
                continue

            # 2. 스프레드 계산
            opportunities = calculate_spreads(hl_rates, bn_rates)

            # 3. 결과 출력
            print_results(opportunities)

            # 4. 알림 전송
            if not args.alert_only:
                check_and_alert(opportunities)
            else:
                good_opps = [o for o in opportunities if o["spread"] >= MIN_SPREAD_ALERT]
                if good_opps:
                    check_and_alert(opportunities)

            if args.once:
                break

            print(f"\n⏳ {args.interval}분 후 다시 체크...")
            time.sleep(args.interval * 60)

        except KeyboardInterrupt:
            print("\n\n👋 봇 종료!")
            break
        except Exception as e:
            print(f"[에러] {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
