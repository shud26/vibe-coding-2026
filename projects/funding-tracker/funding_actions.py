#!/usr/bin/env python3
"""
GitHub Actions용 펀딩비 체커
- 환경 변수에서 텔레그램 설정 읽음
- 1시간마다 실행
"""

import urllib.request
import json
import ssl
import os
from datetime import datetime, timezone, timedelta

# ============================================================
# 설정 (환경 변수에서 읽기)
# ============================================================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

COINS = ["BTC", "ETH", "SOL"]
SINGLE_THRESHOLD = 0.01      # ±0.01% 이상
ARBITRAGE_THRESHOLD = 0.02   # 차이 0.02% 이상

# ============================================================
# 유틸리티
# ============================================================

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def api_request(url, method="GET", data=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    if data:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, context=get_ssl_context(), timeout=15) as resp:
        return json.loads(resp.read().decode())

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("텔레그램 설정 없음")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        api_request(url, "POST", {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        })
        return True
    except Exception as e:
        print(f"텔레그램 오류: {e}")
        return False

# ============================================================
# DEX별 펀딩비 조회
# ============================================================

def get_hyperliquid():
    result = {}
    try:
        data = api_request("https://api.hyperliquid.xyz/info", "POST", {"type": "metaAndAssetCtxs"})
        names = [a["name"] for a in data[0]["universe"]]
        for i, ctx in enumerate(data[1]):
            if names[i] in COINS:
                f = float(ctx["funding"])
                result[names[i]] = {"rate": f * 100, "price": float(ctx["markPx"])}
    except Exception as e:
        print(f"Hyperliquid 오류: {e}")
    return result

def get_pacifica():
    result = {}
    for coin in COINS:
        try:
            data = api_request(f"https://api.pacifica.fi/api/v1/funding_rate/history?symbol={coin}&limit=1")
            if data.get("success") and data.get("data"):
                f = float(data["data"][0]["funding_rate"])
                result[coin] = {"rate": f * 100, "price": float(data["data"][0]["oracle_price"])}
        except Exception as e:
            print(f"Pacifica {coin} 오류: {e}")
    return result

def get_variational():
    result = {}
    try:
        data = api_request("https://omni-client-api.prod.ap-northeast-1.variational.io/metadata/stats")
        for listing in data.get("listings", []):
            ticker = listing.get("ticker", "")
            if ticker in COINS:
                f = float(listing["funding_rate"]) / 8  # 8시간 → 1시간
                result[ticker] = {"rate": f, "price": float(listing["mark_price"])}
    except Exception as e:
        print(f"Variational 오류: {e}")
    return result

# ============================================================
# 메인
# ============================================================

def main():
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst).strftime("%m/%d %H:%M KST")

    print(f"🔍 펀딩비 체크: {now}")

    # 데이터 수집
    hl = get_hyperliquid()
    pc = get_pacifica()
    vr = get_variational()

    # 결과 출력
    print(f"{'코인':<5} {'HL':>10} {'Pacifica':>10} {'Variational':>10}")
    print("-" * 45)

    alerts = []

    for coin in COINS:
        hl_r = f"{hl[coin]['rate']:+.4f}%" if coin in hl else "N/A"
        pc_r = f"{pc[coin]['rate']:+.4f}%" if coin in pc else "N/A"
        vr_r = f"{vr[coin]['rate']:+.4f}%" if coin in vr else "N/A"
        print(f"{coin:<5} {hl_r:>10} {pc_r:>10} {vr_r:>10}")

        # 고펀딩 체크
        rates = []
        if coin in hl: rates.append(("Hyperliquid", hl[coin]['rate'], hl[coin]['price']))
        if coin in pc: rates.append(("Pacifica", pc[coin]['rate'], pc[coin]['price']))
        if coin in vr: rates.append(("Variational", vr[coin]['rate'], vr[coin]['price']))

        for dex, rate, price in rates:
            if abs(rate) >= SINGLE_THRESHOLD:
                direction = "🔴 숏 유리" if rate > 0 else "🟢 롱 유리"
                alerts.append(f"⚠️ <b>{coin}</b> [{dex}]\n펀딩비: <b>{rate:+.4f}%</b>\n{direction}\n가격: ${price:,.2f}")

        # 차익거래 체크
        if len(rates) >= 2:
            rates.sort(key=lambda x: x[1], reverse=True)
            high_dex, high_rate, _ = rates[0]
            low_dex, low_rate, _ = rates[-1]
            diff = high_rate - low_rate

            if diff >= ARBITRAGE_THRESHOLD:
                alerts.append(f"💰 <b>{coin} 차익 기회!</b>\n{high_dex}: {high_rate:+.4f}% (숏)\n{low_dex}: {low_rate:+.4f}% (롱)\n차이: <b>{diff:.4f}%</b>")

    # 알림 전송
    if alerts:
        print(f"\n📨 {len(alerts)}개 알림 전송")
        header = f"📊 <b>펀딩비 알림</b> ({now})\n\n"
        message = header + "\n\n".join(alerts)
        send_telegram(message)
    else:
        print("\n✅ 특이사항 없음")

if __name__ == "__main__":
    main()
