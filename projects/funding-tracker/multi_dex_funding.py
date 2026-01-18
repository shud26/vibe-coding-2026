#!/usr/bin/env python3
"""
멀티 DEX 펀딩비 트래커
- Hyperliquid, Pacifica, Variational 지원
- 펀딩비 차익거래 기회 감지
- 텔레그램 알림
"""

import urllib.request
import json
import ssl
import time
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional

# ============================================================
# 설정
# ============================================================

TELEGRAM_TOKEN = "7881191796:AAEB4mN7dMIj3jEN0PoWAo46z6TPX-hawfI"
TELEGRAM_CHAT_ID = "6329588659"

# 추적할 코인 (공통)
COINS = ["BTC", "ETH", "SOL"]

# 알림 기준
SINGLE_THRESHOLD = 0.01      # 단일 DEX 펀딩비 ±0.01% 이상
ARBITRAGE_THRESHOLD = 0.02   # DEX 간 차이 0.02% 이상이면 차익 기회

# ============================================================
# 데이터 클래스
# ============================================================

@dataclass
class FundingData:
    dex: str
    coin: str
    funding_rate: float      # 원본 값
    funding_pct: float       # 퍼센트 (%)
    price: float
    timestamp: datetime

# ============================================================
# 유틸리티
# ============================================================

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def api_request(url: str, method: str = "GET", data: dict = None) -> dict:
    """API 요청 헬퍼"""
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    if data:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method=method
        )
    else:
        req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, context=get_ssl_context(), timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))

def send_telegram(message: str) -> bool:
    """텔레그램 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        api_request(url, "POST", data)
        return True
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")
        return False

# ============================================================
# DEX별 펀딩비 조회
# ============================================================

def get_hyperliquid_funding() -> List[FundingData]:
    """Hyperliquid 펀딩비 조회"""
    result = []
    try:
        data = api_request(
            "https://api.hyperliquid.xyz/info",
            "POST",
            {"type": "metaAndAssetCtxs"}
        )

        meta = data[0]
        asset_ctxs = data[1]
        coin_names = [asset["name"] for asset in meta["universe"]]

        for i, ctx in enumerate(asset_ctxs):
            coin = coin_names[i]
            if coin in COINS:
                funding = float(ctx["funding"])
                result.append(FundingData(
                    dex="Hyperliquid",
                    coin=coin,
                    funding_rate=funding,
                    funding_pct=funding * 100,
                    price=float(ctx["markPx"]),
                    timestamp=datetime.now(timezone.utc)
                ))
    except Exception as e:
        print(f"Hyperliquid 오류: {e}")

    return result

def get_pacifica_funding() -> List[FundingData]:
    """Pacifica 펀딩비 조회"""
    result = []

    for coin in COINS:
        try:
            data = api_request(
                f"https://api.pacifica.fi/api/v1/funding_rate/history?symbol={coin}&limit=1"
            )

            if data.get("success") and data.get("data"):
                item = data["data"][0]
                funding = float(item["funding_rate"])
                result.append(FundingData(
                    dex="Pacifica",
                    coin=coin,
                    funding_rate=funding,
                    funding_pct=funding * 100,
                    price=float(item["oracle_price"]),
                    timestamp=datetime.now(timezone.utc)
                ))
        except Exception as e:
            print(f"Pacifica {coin} 오류: {e}")

    return result

def get_variational_funding() -> List[FundingData]:
    """Variational 펀딩비 조회"""
    result = []

    # Variational 심볼 매핑
    symbol_map = {"BTC": "BTC", "ETH": "ETH", "SOL": "SOL"}

    try:
        data = api_request(
            "https://omni-client-api.prod.ap-northeast-1.variational.io/metadata/stats"
        )

        if "listings" in data:
            for listing in data["listings"]:
                ticker = listing.get("ticker", "")
                if ticker in symbol_map.values():
                    coin = ticker
                    # Variational은 펀딩비가 이미 퍼센트 (8시간 기준)
                    # 1시간 기준으로 변환: /8
                    funding_pct = float(listing["funding_rate"])
                    funding_hourly = funding_pct / 8

                    result.append(FundingData(
                        dex="Variational",
                        coin=coin,
                        funding_rate=funding_hourly / 100,
                        funding_pct=funding_hourly,
                        price=float(listing["mark_price"]),
                        timestamp=datetime.now(timezone.utc)
                    ))
    except Exception as e:
        print(f"Variational 오류: {e}")

    return result

# ============================================================
# 분석 & 알림
# ============================================================

def analyze_arbitrage(all_data: List[FundingData]) -> List[dict]:
    """차익거래 기회 분석"""
    opportunities = []

    # 코인별로 그룹화
    by_coin: Dict[str, List[FundingData]] = {}
    for d in all_data:
        if d.coin not in by_coin:
            by_coin[d.coin] = []
        by_coin[d.coin].append(d)

    # 각 코인에 대해 DEX 간 차이 분석
    for coin, data_list in by_coin.items():
        if len(data_list) < 2:
            continue

        # 펀딩비 정렬 (높은 순)
        sorted_data = sorted(data_list, key=lambda x: x.funding_pct, reverse=True)

        highest = sorted_data[0]
        lowest = sorted_data[-1]
        diff = highest.funding_pct - lowest.funding_pct

        if diff >= ARBITRAGE_THRESHOLD:
            opportunities.append({
                "coin": coin,
                "high_dex": highest.dex,
                "high_rate": highest.funding_pct,
                "low_dex": lowest.dex,
                "low_rate": lowest.funding_pct,
                "diff": diff
            })

    return opportunities

def format_funding_table(all_data: List[FundingData]) -> str:
    """펀딩비 테이블 포맷"""
    # 코인별로 그룹화
    by_coin: Dict[str, Dict[str, FundingData]] = {}
    for d in all_data:
        if d.coin not in by_coin:
            by_coin[d.coin] = {}
        by_coin[d.coin][d.dex] = d

    lines = []
    lines.append("=" * 55)
    lines.append(f"{'코인':<6} {'Hyperliquid':>12} {'Pacifica':>12} {'Variational':>12}")
    lines.append("-" * 55)

    for coin in COINS:
        if coin in by_coin:
            hl = by_coin[coin].get("Hyperliquid")
            pc = by_coin[coin].get("Pacifica")
            vr = by_coin[coin].get("Variational")

            hl_str = f"{hl.funding_pct:+.4f}%" if hl else "N/A"
            pc_str = f"{pc.funding_pct:+.4f}%" if pc else "N/A"
            vr_str = f"{vr.funding_pct:+.4f}%" if vr else "N/A"

            lines.append(f"{coin:<6} {hl_str:>12} {pc_str:>12} {vr_str:>12}")

    lines.append("=" * 55)
    return "\n".join(lines)

def format_arbitrage_alert(opp: dict) -> str:
    """차익거래 알림 메시지"""
    return f"""
🔔 <b>{opp['coin']} 펀딩비 차익 기회!</b>

📈 {opp['high_dex']}: <b>{opp['high_rate']:+.4f}%</b> (숏)
📉 {opp['low_dex']}: <b>{opp['low_rate']:+.4f}%</b> (롱)

💰 차이: <b>{opp['diff']:.4f}%</b>

전략: {opp['high_dex']} 숏 + {opp['low_dex']} 롱

⏰ {datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M KST")}
"""

def format_single_alert(data: FundingData) -> str:
    """단일 DEX 펀딩비 알림"""
    direction = "🔴 숏 유리" if data.funding_pct > 0 else "🟢 롱 유리"
    return f"""
⚠️ <b>{data.coin} 펀딩비 알림</b> [{data.dex}]

💰 펀딩비: <b>{data.funding_pct:+.4f}%</b>
{direction}

📊 가격: ${data.price:,.2f}
⏰ {datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M KST")}
"""

# ============================================================
# 메인 로직
# ============================================================

def check_all_funding():
    """모든 DEX 펀딩비 체크"""
    print(f"\n🔍 펀딩비 조회 중... {datetime.now().strftime('%H:%M:%S')}")

    # 모든 DEX에서 데이터 수집
    all_data = []
    all_data.extend(get_hyperliquid_funding())
    all_data.extend(get_pacifica_funding())
    all_data.extend(get_variational_funding())

    # 테이블 출력
    print(format_funding_table(all_data))

    # 차익거래 기회 분석
    arbitrage_opps = analyze_arbitrage(all_data)

    alerts_sent = 0

    # 차익거래 알림
    for opp in arbitrage_opps:
        print(f"🔔 차익 기회: {opp['coin']} ({opp['diff']:.4f}%)")
        send_telegram(format_arbitrage_alert(opp))
        alerts_sent += 1

    # 단일 DEX 고펀딩 알림
    for data in all_data:
        if abs(data.funding_pct) >= SINGLE_THRESHOLD:
            print(f"⚠️ 고펀딩: {data.dex} {data.coin} {data.funding_pct:+.4f}%")
            send_telegram(format_single_alert(data))
            alerts_sent += 1

    if alerts_sent == 0:
        print("✅ 특이사항 없음")

    return all_data, arbitrage_opps

def run_monitor(interval: int = 300):
    """모니터링 실행"""
    print("🚀 멀티 DEX 펀딩비 트래커 시작!")
    print(f"📌 DEX: Hyperliquid, Pacifica, Variational")
    print(f"📌 코인: {', '.join(COINS)}")
    print(f"⚠️ 단일 알림: ±{SINGLE_THRESHOLD}%")
    print(f"💰 차익 알림: {ARBITRAGE_THRESHOLD}% 이상 차이")
    print(f"⏱️ 체크 간격: {interval}초")

    send_telegram(f"""🚀 <b>멀티 DEX 펀딩비 트래커 시작</b>

DEX: Hyperliquid, Pacifica, Variational
코인: {', '.join(COINS)}
단일 알림: ±{SINGLE_THRESHOLD}%
차익 알림: {ARBITRAGE_THRESHOLD}% 차이""")

    while True:
        try:
            check_all_funding()
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 종료")
            break
        except Exception as e:
            print(f"❌ 에러: {e}")
            time.sleep(60)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        check_all_funding()
    else:
        run_monitor()
