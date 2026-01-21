#!/usr/bin/env python3
"""
Todo + Google Calendar 연동 봇
할 일 추가하면 자동으로 캘린더에 이벤트 생성!

사용법:
  python3 todo_calendar.py add "회의 준비" --date 2026-01-21
  python3 todo_calendar.py add "코드 리뷰" --date tomorrow
  python3 todo_calendar.py add "점심약속" --date 2026-01-22 --time 12:00
  python3 todo_calendar.py list
  python3 todo_calendar.py done 1
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Google Calendar imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Telegram 설정
TELEGRAM_TOKEN = "7881191796:AAEB4mN7dMIj3jEN0PoWAo46z6TPX-hawfI"
TELEGRAM_CHAT_ID = "6329588659"

# 파일 경로
BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"
TODOS_FILE = BASE_DIR / "todos.json"

# Google Calendar 권한
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def send_telegram(message: str):
    """텔레그램 알림"""
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
    except:
        pass


def get_calendar_service():
    """Google Calendar 서비스 인증 및 반환"""
    creds = None

    # 저장된 토큰 확인
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # 토큰이 없거나 만료됐으면 새로 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print("❌ credentials.json 파일이 없어요!")
                print(f"   위치: {CREDENTIALS_FILE}")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        # 토큰 저장
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def load_todos() -> list:
    """저장된 할 일 목록 불러오기"""
    if TODOS_FILE.exists():
        with open(TODOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_todos(todos: list):
    """할 일 목록 저장"""
    with open(TODOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def parse_date(date_str: str) -> datetime:
    """날짜 문자열 파싱"""
    today = datetime.now()

    if date_str == "today":
        return today
    elif date_str == "tomorrow":
        return today + timedelta(days=1)
    elif date_str == "nextweek":
        return today + timedelta(days=7)
    else:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            print(f"⚠️ 날짜 형식 오류: {date_str}")
            print("   예시: 2026-01-21, today, tomorrow")
            sys.exit(1)


def add_todo(title: str, date_str: str = "today", time_str: str = None):
    """할 일 추가 + 캘린더 이벤트 생성"""

    # 날짜 파싱
    date = parse_date(date_str)

    # 시간 설정
    if time_str:
        hour, minute = map(int, time_str.split(':'))
        start_time = date.replace(hour=hour, minute=minute)
        end_time = start_time + timedelta(hours=1)

        event = {
            'summary': f'📋 {title}',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Seoul',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
    else:
        # 종일 이벤트
        event = {
            'summary': f'📋 {title}',
            'start': {
                'date': date.strftime('%Y-%m-%d'),
            },
            'end': {
                'date': (date + timedelta(days=1)).strftime('%Y-%m-%d'),
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 60 * 9},  # 당일 오전 9시
                ],
            },
        }

    # Google Calendar에 추가
    print("📅 Google Calendar 연결 중...")
    service = get_calendar_service()

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    event_id = created_event.get('id')
    event_link = created_event.get('htmlLink')

    # 로컬 저장
    todos = load_todos()
    todo = {
        'id': len(todos) + 1,
        'title': title,
        'date': date.strftime('%Y-%m-%d'),
        'time': time_str,
        'done': False,
        'calendar_event_id': event_id,
        'created_at': datetime.now().isoformat()
    }
    todos.append(todo)
    save_todos(todos)

    # 출력
    print(f"\n✅ 할 일 추가 완료!")
    print(f"   제목: {title}")
    print(f"   날짜: {date.strftime('%Y-%m-%d')} {'(' + time_str + ')' if time_str else '(종일)'}")
    print(f"   캘린더: {event_link}")

    # 텔레그램 알림
    msg = f"📋 새 할 일 추가!\n\n"
    msg += f"▸ {title}\n"
    msg += f"▸ {date.strftime('%Y-%m-%d')} {time_str or '(종일)'}\n"
    msg += f"\n캘린더에 추가됨 ✓"
    send_telegram(msg)


def list_todos():
    """할 일 목록 보기"""
    todos = load_todos()

    if not todos:
        print("\n📋 할 일이 없어요!")
        return

    print("\n" + "="*50)
    print("  📋 할 일 목록")
    print("="*50)

    pending = [t for t in todos if not t['done']]
    done = [t for t in todos if t['done']]

    if pending:
        print("\n▸ 해야 할 것:")
        for todo in pending:
            time_str = f" ({todo['time']})" if todo.get('time') else ""
            print(f"  [{todo['id']}] {todo['title']} - {todo['date']}{time_str}")

    if done:
        print("\n▸ 완료:")
        for todo in done:
            print(f"  [{todo['id']}] ✓ {todo['title']}")

    print("="*50)


def complete_todo(todo_id: int):
    """할 일 완료 처리"""
    todos = load_todos()

    for todo in todos:
        if todo['id'] == todo_id:
            todo['done'] = True
            todo['completed_at'] = datetime.now().isoformat()

            # 캘린더 이벤트 제목 업데이트 (완료 표시)
            if todo.get('calendar_event_id'):
                try:
                    service = get_calendar_service()
                    event = service.events().get(calendarId='primary', eventId=todo['calendar_event_id']).execute()
                    event['summary'] = f"✅ {todo['title']}"
                    service.events().update(calendarId='primary', eventId=todo['calendar_event_id'], body=event).execute()
                except:
                    pass

            save_todos(todos)

            print(f"\n✅ 완료: {todo['title']}")
            send_telegram(f"✅ 할 일 완료!\n\n▸ {todo['title']}")
            return

    print(f"⚠️ ID {todo_id}를 찾을 수 없어요")


def delete_todo(todo_id: int):
    """할 일 삭제"""
    todos = load_todos()

    for i, todo in enumerate(todos):
        if todo['id'] == todo_id:
            # 캘린더에서도 삭제
            if todo.get('calendar_event_id'):
                try:
                    service = get_calendar_service()
                    service.events().delete(calendarId='primary', eventId=todo['calendar_event_id']).execute()
                except:
                    pass

            removed = todos.pop(i)
            save_todos(todos)

            print(f"\n🗑️ 삭제: {removed['title']}")
            return

    print(f"⚠️ ID {todo_id}를 찾을 수 없어요")


def main():
    parser = argparse.ArgumentParser(description="Todo + Google Calendar 연동")
    subparsers = parser.add_subparsers(dest='command', help='명령어')

    # add 명령어
    add_parser = subparsers.add_parser('add', help='할 일 추가')
    add_parser.add_argument('title', help='할 일 제목')
    add_parser.add_argument('--date', '-d', default='today', help='날짜 (YYYY-MM-DD, today, tomorrow)')
    add_parser.add_argument('--time', '-t', help='시간 (HH:MM)')

    # list 명령어
    subparsers.add_parser('list', help='할 일 목록')

    # done 명령어
    done_parser = subparsers.add_parser('done', help='할 일 완료')
    done_parser.add_argument('id', type=int, help='할 일 ID')

    # delete 명령어
    del_parser = subparsers.add_parser('delete', help='할 일 삭제')
    del_parser.add_argument('id', type=int, help='할 일 ID')

    args = parser.parse_args()

    if args.command == 'add':
        add_todo(args.title, args.date, args.time)
    elif args.command == 'list':
        list_todos()
    elif args.command == 'done':
        complete_todo(args.id)
    elif args.command == 'delete':
        delete_todo(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
