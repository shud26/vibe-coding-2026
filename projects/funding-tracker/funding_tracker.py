#!/usr/bin/env python3
"""
펀딩비 트래커 - Hyperliquid 펀딩비 모니터링 및 텔레그램 알림

펀딩비가 높으면 → 숏 포지션이 롱에게 지불 (숏 기회)
펀딩비가 낮으면 → 롱 포지션이 숏에게 지불 (롱 기회)
"""

import urllib.request
import json
import ssl
import time
from datetime import datetime, timezone, timedelta

# 설정
TELEGRAM_TOKEN = "7881191796:AAEB4mN7dMIj3jEN0PoWAo46z6TPX-hawfI"
TELEGRAM_CHAT_ID = "6329588659"

# 추적할 코인
COINS = ["BTC", "ETH", "SOL", "DOGE", "XRP", "AVAX", "LINK", "ARB", "OP", "SUI"]

# 알림 기준 (0.01% = 0.0001)
FUNDING_THRESHOLD = 0.0001  # ±0.01% 이상이면 알림

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def get_funding_rates():
    """Hyperliquid에서 펀딩비 데이터 가져오기"""
    url = "https://api.hyperliquid.xyz/info"
    data = json.dumps({"type": "metaAndAssetCtxs"}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

    with urllib.request.urlopen(req, context=get_ssl_context()) as response:
        result = json.loads(response.read().decode("utf-8"))

    # meta와 assetCtxs 분리
    meta = result[0]
    asset_ctxs = result[1]

    # 코인 이름 매핑
    coin_names = [asset["name"] for asset in meta["universe"]]

    funding_data = {}
    for i, ctx in enumerate(asset_ctxs):
        coin = coin_names[i]
        if coin in COINS:
            funding_rate = float(ctx["funding"])
            funding_data[coin] = {
                "funding": funding_rate,
                "funding_pct": funding_rate * 100,  # 퍼센트로 변환
                "mark_price": float(ctx["markPx"]),
                "open_interest": float(ctx["openInterest"])
            }

    return funding_data

def send_telegram(message):
    """텔레그램 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with urllib.request.urlopen(req, context=get_ssl_context()) as response:
            return True
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")
        return False

def format_funding_message(coin, data):
    """펀딩비 알림 메시지 포맷"""
    funding_pct = data["funding_pct"]
    mark_price = data["mark_price"]

    if funding_pct > 0:
        direction = "🔴 양수 (숏이 유리)"
        emoji = "📈"
    else:
        direction = "🟢 음수 (롱이 유리)"
        emoji = "📉"

    return f"""
{emoji} <b>{coin} 펀딩비 알림</b>

💰 펀딩비: <b>{funding_pct:+.4f}%</b>
{direction}

📊 현재가: ${mark_price:,.2f}

⏰ {datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST")}
"""

def check_funding_rates():
    """펀딩비 체크 및 알림"""
    funding_data = get_funding_rates()
    alerts = []

    print(f"\n{'='*50}")
    print(f"펀딩비 체크: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    for coin in COINS:
        if coin in funding_data:
            data = funding_data[coin]
            funding = data["funding"]
            funding_pct = data["funding_pct"]

            # 펀딩비 출력
            indicator = "🔴" if funding > 0 else "🟢" if funding < 0 else "⚪"
            print(f"{indicator} {coin:>5}: {funding_pct:+.4f}% | ${data['mark_price']:,.2f}")

            # 임계값 초과시 알림 추가
            if abs(funding) >= FUNDING_THRESHOLD:
                alerts.append((coin, data))

    # 알림 전송
    if alerts:
        print(f"\n⚠️ {len(alerts)}개 알림 전송 중...")
        for coin, data in alerts:
            message = format_funding_message(coin, data)
            send_telegram(message)
            print(f"  ✅ {coin} 알림 전송됨")
    else:
        print(f"\n✅ 임계값({FUNDING_THRESHOLD*100:.2f}%) 초과 코인 없음")

    return funding_data, alerts

def run_monitor(interval=300):
    """
    펀딩비 모니터링 실행
    interval: 체크 간격 (초, 기본 5분)
    """
    print("🚀 펀딩비 트래커 시작!")
    print(f"📌 추적 코인: {', '.join(COINS)}")
    print(f"⚠️ 알림 기준: ±{FUNDING_THRESHOLD*100:.2f}%")
    print(f"⏱️ 체크 간격: {interval}초")

    # 시작 알림
    send_telegram(f"🚀 <b>펀딩비 트래커 시작</b>\n\n추적: {', '.join(COINS)}\n알림 기준: ±{FUNDING_THRESHOLD*100:.2f}%")

    while True:
        try:
            check_funding_rates()
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 펀딩비 트래커 종료")
            break
        except Exception as e:
            print(f"❌ 에러: {e}")
            time.sleep(60)  # 에러 시 1분 후 재시도

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # 한 번만 실행
        check_funding_rates()
    else:
        # 계속 모니터링
        run_monitor()
