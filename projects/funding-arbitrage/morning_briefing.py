#!/usr/bin/env python3
"""
Morning Briefing Bot - 매일 아침 오늘의 일정 + 할 일 알림

매일 아침 텔레그램으로:
- 오늘 Google Calendar 일정
- 오늘 해야 할 일 목록
- 격려 메시지

사용법:
  python3 morning_briefing.py          # 바로 전송
  python3 morning_briefing.py --test   # 테스트 (전송 안함)
"""

import os
import sys
import json
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

# Google Calendar imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Telegram 설정
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "7881191796:AAEB4mN7dMIj3jEN0PoWAo46z6TPX-hawfI")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "6329588659")

# 파일 경로
BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"
TODOS_FILE = BASE_DIR / "todos.json"

# Google Calendar 권한 (기존 토큰과 호환)
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# 격려 메시지들
ENCOURAGEMENTS = [
    "오늘도 화이팅! 작은 것부터 시작해봐요 💪",
    "P성향이라도 괜찮아요! 하나씩 해보자 ✨",
    "완벽하지 않아도 돼요. 시작하는 게 중요해요!",
    "오늘의 나는 어제보다 성장할 거예요 🌱",
    "쉬엄쉬엄 해도 괜찮아요. 꾸준함이 힘이에요!",
    "할 수 있어요! 일단 첫 번째 할 일만 해봐요 🎯",
    "오늘 하루도 즐겁게! 코딩은 재밌으니까 😊",
    "작은 진전도 진전이에요. 자신을 믿어요!",
]


def send_telegram(message: str) -> bool:
    """텔레그램 알림"""
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            },
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")
        return False


def get_calendar_service():
    """Google Calendar 서비스 인증 및 반환"""
    creds = None

    # 저장된 토큰 확인
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # 토큰이 없거나 만료됐으면
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print("❌ credentials.json 파일이 없어요!")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        # 토큰 저장
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def get_today_events(service) -> list:
    """오늘의 Google Calendar 일정 가져오기"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=today_start.isoformat() + 'Z',
        timeMax=today_end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime',
        timeZone='Asia/Seoul'
    ).execute()

    events = events_result.get('items', [])

    parsed_events = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', '(제목 없음)')

        # 시간 파싱
        if 'T' in start:  # 시간이 있는 이벤트
            time_str = datetime.fromisoformat(start.replace('Z', '+00:00')).strftime('%H:%M')
        else:  # 종일 이벤트
            time_str = "종일"

        parsed_events.append({
            'time': time_str,
            'title': summary
        })

    return parsed_events


def get_today_todos() -> list:
    """오늘 해야 할 일 가져오기"""
    if not TODOS_FILE.exists():
        return []

    with open(TODOS_FILE, 'r', encoding='utf-8') as f:
        todos = json.load(f)

    today = datetime.now().strftime('%Y-%m-%d')

    # 미완료 + 오늘 또는 이전 날짜인 것들
    pending_todos = []
    for todo in todos:
        if todo.get('done'):
            continue

        todo_date = todo.get('date', '')
        if todo_date <= today:  # 오늘이거나 지난 것
            pending_todos.append({
                'title': todo['title'],
                'date': todo_date,
                'time': todo.get('time'),
                'overdue': todo_date < today
            })

    return pending_todos


def format_briefing(events: list, todos: list) -> str:
    """브리핑 메시지 포맷팅"""
    now = datetime.now()
    weekday = ['월', '화', '수', '목', '금', '토', '일'][now.weekday()]

    msg = f"☀️ <b>Good Morning!</b>\n"
    msg += f"📅 {now.strftime('%Y년 %m월 %d일')} ({weekday})\n"
    msg += "\n" + "─" * 20 + "\n"

    # 오늘의 일정
    msg += "\n📆 <b>오늘의 일정</b>\n"
    if events:
        for event in events:
            time_emoji = "⏰" if event['time'] != "종일" else "📌"
            msg += f"  {time_emoji} {event['time']} - {event['title']}\n"
    else:
        msg += "  • 일정 없음 (여유로운 하루!)\n"

    # 오늘의 할 일
    msg += "\n✅ <b>오늘의 할 일</b>\n"
    if todos:
        for i, todo in enumerate(todos, 1):
            overdue_mark = " ⚠️" if todo['overdue'] else ""
            time_str = f" ({todo['time']})" if todo.get('time') else ""
            msg += f"  {i}. {todo['title']}{time_str}{overdue_mark}\n"

        if any(t['overdue'] for t in todos):
            msg += "\n  ⚠️ = 기한 지남\n"
    else:
        msg += "  • 할 일 없음 (오늘은 쉬는 날?)\n"

    # 요약
    msg += "\n" + "─" * 20 + "\n"
    msg += f"📊 일정 {len(events)}개 | 할 일 {len(todos)}개\n"

    # 격려 메시지
    msg += f"\n💬 {random.choice(ENCOURAGEMENTS)}"

    return msg


def main():
    parser = argparse.ArgumentParser(description="Morning Briefing Bot")
    parser.add_argument('--test', action='store_true', help='테스트 모드 (전송 안함)')
    args = parser.parse_args()

    print("🌅 Morning Briefing 준비 중...")

    # Google Calendar 연결
    service = get_calendar_service()
    if not service:
        print("❌ Google Calendar 연결 실패")
        sys.exit(1)

    # 데이터 수집
    print("📆 일정 가져오는 중...")
    events = get_today_events(service)
    print(f"   → {len(events)}개 일정 발견")

    print("✅ 할 일 가져오는 중...")
    todos = get_today_todos()
    print(f"   → {len(todos)}개 할 일 발견")

    # 메시지 생성
    message = format_briefing(events, todos)

    print("\n" + "=" * 40)
    print(message.replace('<b>', '').replace('</b>', ''))
    print("=" * 40)

    # 전송
    if args.test:
        print("\n🧪 테스트 모드 - 전송하지 않음")
    else:
        print("\n📤 텔레그램 전송 중...")
        if send_telegram(message):
            print("✅ 전송 완료!")
        else:
            print("❌ 전송 실패")
            sys.exit(1)


if __name__ == "__main__":
    main()
