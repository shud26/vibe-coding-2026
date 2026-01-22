#!/usr/bin/env python3
"""
업비트 신규 상장 알림 봇
- 10분마다 업비트 마켓 리스트 체크
- 새 코인 상장되면 텔레그램 알림
"""

import requests
import json
import os
from datetime import datetime

# 텔레그램 설정
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7881191796:AAEB4mN7dMIj3jEN0PoWAo46z6TPX-hawfI")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6329588659")

# 파일 경로
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MARKETS_FILE = os.path.join(SCRIPT_DIR, "known_markets.json")


def send_telegram(message: str) -> bool:
    """텔레그램 메시지 전송"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")
        return False


def get_upbit_markets() -> dict:
    """업비트 전체 마켓 리스트 가져오기"""
    try:
        url = "https://api.upbit.com/v1/market/all"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        markets = {}
        for item in response.json():
            market = item["market"]
            markets[market] = {
                "korean_name": item["korean_name"],
                "english_name": item["english_name"]
            }
        return markets
    except Exception as e:
        print(f"업비트 API 에러: {e}")
        return {}


def load_known_markets() -> dict:
    """저장된 마켓 리스트 불러오기"""
    if os.path.exists(MARKETS_FILE):
        with open(MARKETS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_known_markets(markets: dict):
    """마켓 리스트 저장"""
    with open(MARKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(markets, f, ensure_ascii=False, indent=2)


def check_new_listings():
    """새 상장 체크"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 업비트 상장 체크 중...")

    # 현재 마켓 리스트 가져오기
    current_markets = get_upbit_markets()
    if not current_markets:
        print("마켓 리스트를 가져올 수 없습니다.")
        return

    print(f"현재 마켓 수: {len(current_markets)}")

    # 저장된 마켓 리스트 불러오기
    known_markets = load_known_markets()

    # 처음 실행인 경우
    if not known_markets:
        print("첫 실행! 현재 마켓 리스트를 저장합니다.")
        save_known_markets(current_markets)

        # 첫 실행 알림
        msg = "🚀 <b>업비트 상장 알림 봇 시작!</b>\n\n"
        msg += f"📊 현재 등록된 마켓: {len(current_markets)}개\n"
        msg += "새 코인이 상장되면 알림을 보내드릴게요!"
        send_telegram(msg)
        return

    # 새 상장 코인 찾기
    new_listings = []
    for market, info in current_markets.items():
        if market not in known_markets:
            new_listings.append({
                "market": market,
                "korean_name": info["korean_name"],
                "english_name": info["english_name"]
            })

    # 상장 폐지된 코인 찾기
    delisted = []
    for market in known_markets:
        if market not in current_markets:
            delisted.append(market)

    # 새 상장이 있으면 알림
    if new_listings:
        print(f"🎉 새 상장 발견: {len(new_listings)}개")

        # KRW 마켓 우선 표시
        krw_coins = [c for c in new_listings if c["market"].startswith("KRW-")]
        btc_coins = [c for c in new_listings if c["market"].startswith("BTC-")]
        usdt_coins = [c for c in new_listings if c["market"].startswith("USDT-")]

        msg = "🚨 <b>업비트 신규 상장!</b> 🚨\n\n"

        if krw_coins:
            msg += "💰 <b>KRW 마켓 (원화 직접 거래)</b>\n"
            for coin in krw_coins:
                symbol = coin["market"].replace("KRW-", "")
                msg += f"  • <b>{symbol}</b> - {coin['korean_name']}\n"
            msg += "\n"

        if btc_coins:
            msg += "🔶 <b>BTC 마켓</b>\n"
            for coin in btc_coins:
                symbol = coin["market"].replace("BTC-", "")
                msg += f"  • {symbol} - {coin['korean_name']}\n"
            msg += "\n"

        if usdt_coins:
            msg += "💵 <b>USDT 마켓</b>\n"
            for coin in usdt_coins:
                symbol = coin["market"].replace("USDT-", "")
                msg += f"  • {symbol} - {coin['korean_name']}\n"
            msg += "\n"

        msg += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        msg += "\n💡 신규 상장 초기에 변동성이 클 수 있으니 주의하세요!"

        send_telegram(msg)
    else:
        print("새 상장 없음")

    # 상장 폐지 알림
    if delisted:
        print(f"⚠️ 상장 폐지: {delisted}")
        msg = "⚠️ <b>업비트 상장 폐지</b>\n\n"
        for market in delisted:
            msg += f"• {market}\n"
        msg += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_telegram(msg)

    # 마켓 리스트 업데이트
    save_known_markets(current_markets)


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="업비트 신규 상장 알림 봇")
    parser.add_argument("--once", action="store_true", help="한 번만 실행")
    parser.add_argument("--interval", type=int, default=10, help="체크 간격 (분)")
    args = parser.parse_args()

    print("=" * 50)
    print("🔔 업비트 신규 상장 알림 봇")
    print("=" * 50)

    if args.once:
        check_new_listings()
    else:
        import time
        print(f"⏱️ {args.interval}분마다 체크합니다...")
        while True:
            check_new_listings()
            print(f"다음 체크: {args.interval}분 후")
            time.sleep(args.interval * 60)


if __name__ == "__main__":
    main()
