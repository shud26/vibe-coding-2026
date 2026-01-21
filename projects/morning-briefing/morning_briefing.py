#!/usr/bin/env python3
"""
🌅 AI 모닝 브리핑
매일 아침 텔레그램으로 오늘의 정보를 보내줍니다!

- 오늘 할 일 (Google Calendar)
- 크립토 시황 (가격 + 펀딩비 기회)
- 날씨 정보

사용법:
  python3 morning_briefing.py          # 브리핑 전송
  python3 morning_briefing.py --test   # 테스트 (전송 안 함)
"""

import requests
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# === 설정 ===
TELEGRAM_TOKEN = "7881191796:AAEB4mN7dMIj3jEN0PoWAo46z6TPX-hawfI"
TELEGRAM_CHAT_ID = "6329588659"

# Google Calendar (토큰 파일 경로 또는 환경변수)
TOKEN_FILE = Path(__file__).parent.parent / "funding-arbitrage" / "token.json"
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# 환경변수에서 토큰 정보 읽기 (GitHub Actions용)
import os
GOOGLE_TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON", "")

# 날씨 설정
CITY = "Seoul"
COUNTRY = "KR"


def get_greeting():
    """시간대별 인사말"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"


def get_calendar_events():
    """오늘의 Google Calendar 이벤트 가져오기"""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        import json

        # 환경변수에서 토큰 읽기 (GitHub Actions용)
        if GOOGLE_TOKEN_JSON:
            token_data = json.loads(GOOGLE_TOKEN_JSON)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        elif TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        else:
            return None, "캘린더 토큰 없음"
        service = build('calendar', 'v3', credentials=creds)

        # 오늘 시작~끝
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=today.isoformat() + 'Z',
            timeMax=tomorrow.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        return events, None

    except Exception as e:
        return None, str(e)


def format_calendar_events(events):
    """캘린더 이벤트 포맷팅"""
    if not events:
        return "  오늘 일정 없음 - 자유로운 하루! 🎉"

    lines = []
    for event in events[:10]:  # 최대 10개
        summary = event.get('summary', '(제목 없음)')

        # 시간 파싱
        start = event['start'].get('dateTime', event['start'].get('date'))
        if 'T' in start:
            # 시간 있는 이벤트
            time_str = start.split('T')[1][:5]
            lines.append(f"  • {time_str} {summary}")
        else:
            # 종일 이벤트
            lines.append(f"  • {summary} (종일)")

    return "\n".join(lines)


def get_crypto_prices():
    """크립토 가격 가져오기 (CoinGecko)"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,solana",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        prices = {
            "BTC": {
                "price": data["bitcoin"]["usd"],
                "change": data["bitcoin"]["usd_24h_change"]
            },
            "ETH": {
                "price": data["ethereum"]["usd"],
                "change": data["ethereum"]["usd_24h_change"]
            },
            "SOL": {
                "price": data["solana"]["usd"],
                "change": data["solana"]["usd_24h_change"]
            }
        }
        return prices, None
    except Exception as e:
        return None, str(e)


def format_crypto_prices(prices):
    """크립토 가격 포맷팅"""
    if not prices:
        return "  가격 정보 없음"

    lines = []
    for coin, data in prices.items():
        price = data["price"]
        change = data["change"]

        # 가격 포맷
        if price >= 1000:
            price_str = f"${price:,.0f}"
        else:
            price_str = f"${price:.2f}"

        # 변동률 표시
        if change >= 0:
            change_str = f"+{change:.1f}%"
            emoji = "📈"
        else:
            change_str = f"{change:.1f}%"
            emoji = "📉"

        lines.append(f"  • {coin}: {price_str} ({change_str}) {emoji}")

    return "\n".join(lines)


def get_funding_opportunities():
    """펀딩비 차익거래 기회 (Hyperliquid vs Binance)"""
    try:
        # Hyperliquid
        hl_url = "https://api.hyperliquid.xyz/info"
        hl_response = requests.post(hl_url, json={"type": "metaAndAssetCtxs"}, timeout=10)
        hl_data = hl_response.json()

        hl_rates = {}
        universe = hl_data[0]["universe"]
        contexts = hl_data[1]
        for i, asset in enumerate(universe):
            coin = asset["name"]
            hl_rates[coin] = float(contexts[i]["funding"]) * 100

        # Binance
        bn_url = "https://fapi.binance.com/fapi/v1/premiumIndex"
        bn_response = requests.get(bn_url, timeout=10)
        bn_data = bn_response.json()

        bn_rates = {}
        for item in bn_data:
            symbol = item["symbol"]
            if symbol.endswith("USDT"):
                coin = symbol.replace("USDT", "")
                bn_rates[coin] = float(item["lastFundingRate"]) * 100

        # 기회 찾기
        opportunities = []
        for coin in ["BTC", "ETH", "SOL", "APT", "ARB", "OP", "SUI"]:
            if coin in hl_rates and coin in bn_rates:
                spread = abs(hl_rates[coin] - bn_rates[coin])
                annual = spread * 3 * 365
                if spread >= 0.01:  # 0.01% 이상
                    opportunities.append({
                        "coin": coin,
                        "spread": spread,
                        "annual": annual
                    })

        opportunities.sort(key=lambda x: x["spread"], reverse=True)
        return opportunities[:3], None  # 상위 3개

    except Exception as e:
        return None, str(e)


def format_funding_opportunities(opps):
    """펀딩비 기회 포맷팅"""
    if not opps:
        return "  오늘은 특별한 기회 없음"

    lines = []
    for opp in opps:
        emoji = "🔥" if opp["annual"] > 15 else "✨"
        lines.append(f"  • {opp['coin']}: 연 {opp['annual']:.1f}% {emoji}")

    return "\n".join(lines)


def get_weather():
    """날씨 정보 가져오기 (wttr.in - API 키 불필요)"""
    try:
        url = f"https://wttr.in/{CITY}?format=j1"
        response = requests.get(url, timeout=10)
        data = response.json()

        current = data["current_condition"][0]
        today = data["weather"][0]

        weather = {
            "temp": current["temp_C"],
            "feels_like": current["FeelsLikeC"],
            "desc": current["weatherDesc"][0]["value"],
            "humidity": current["humidity"],
            "max_temp": today["maxtempC"],
            "min_temp": today["mintempC"],
        }
        return weather, None
    except Exception as e:
        return None, str(e)


def format_weather(weather):
    """날씨 포맷팅"""
    if not weather:
        return "  날씨 정보 없음"

    # 날씨 이모지
    desc = weather["desc"].lower()
    if "sun" in desc or "clear" in desc:
        emoji = "☀️"
    elif "cloud" in desc:
        emoji = "☁️"
    elif "rain" in desc:
        emoji = "🌧️"
    elif "snow" in desc:
        emoji = "❄️"
    else:
        emoji = "🌤️"

    lines = [
        f"  • 현재 {weather['temp']}°C (체감 {weather['feels_like']}°C) {emoji}",
        f"  • {weather['desc']}",
        f"  • 최고 {weather['max_temp']}°C / 최저 {weather['min_temp']}°C",
    ]

    return "\n".join(lines)


def build_briefing():
    """모닝 브리핑 메시지 생성"""
    greeting = get_greeting()
    today = datetime.now().strftime("%Y년 %m월 %d일 %A")

    # 각 섹션 데이터 수집
    events, cal_err = get_calendar_events()
    prices, price_err = get_crypto_prices()
    funding, fund_err = get_funding_opportunities()
    weather, weather_err = get_weather()

    # 메시지 구성
    msg = f"🌅 {greeting}, shud!\n"
    msg += f"📆 {today}\n"
    msg += "\n" + "─" * 25 + "\n\n"

    # 오늘 할 일
    msg += "📋 오늘 일정\n"
    if cal_err:
        msg += f"  (오류: {cal_err})\n"
    else:
        msg += format_calendar_events(events) + "\n"
    msg += "\n"

    # 크립토 시황
    msg += "💰 크립토 시황\n"
    if price_err:
        msg += f"  (오류: {price_err})\n"
    else:
        msg += format_crypto_prices(prices) + "\n"
    msg += "\n"

    # 펀딩비 기회
    msg += "📊 펀딩비 차익거래 기회\n"
    if fund_err:
        msg += f"  (오류: {fund_err})\n"
    else:
        msg += format_funding_opportunities(funding) + "\n"
    msg += "\n"

    # 날씨
    msg += f"🌤️ 날씨 ({CITY})\n"
    if weather_err:
        msg += f"  (오류: {weather_err})\n"
    else:
        msg += format_weather(weather) + "\n"

    msg += "\n" + "─" * 25 + "\n"
    msg += "오늘도 화이팅! 💪"

    return msg


def send_telegram(message):
    """텔레그램 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json().get("ok", False)
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="AI 모닝 브리핑")
    parser.add_argument("--test", action="store_true", help="테스트 모드 (전송 안 함)")
    args = parser.parse_args()

    print("🌅 모닝 브리핑 생성 중...\n")

    briefing = build_briefing()

    print(briefing)
    print()

    if args.test:
        print("📝 테스트 모드 - 전송하지 않음")
    else:
        print("📤 텔레그램 전송 중...")
        if send_telegram(briefing):
            print("✅ 전송 완료!")
        else:
            print("❌ 전송 실패")


if __name__ == "__main__":
    main()
