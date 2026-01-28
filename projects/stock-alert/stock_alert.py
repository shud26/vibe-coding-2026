#!/usr/bin/env python3
"""
상한가 종목 알림봇
- KOSPI + KOSDAQ 상한가 종목 자동 추출
- 종목별 뉴스 검색 (네이버)
- 텔레그램 알림

사용법:
  python3 stock_alert.py                    # 오늘 상한가 조회 + 텔레그램 전송
  python3 stock_alert.py --date 20260127    # 특정 날짜 조회
  python3 stock_alert.py --test             # 테스트 (텔레그램 미전송)
"""

import argparse
import json
import os
import ssl
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pykrx import stock

# ─── 설정 ────────────────────────────────────────────────────

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

KST = timezone(timedelta(hours=9))
UPPER_LIMIT_PCT = 29.0  # 상한가 기준 (30%가 상한가, 29%+ 잡으면 충분)


# ─── 유틸리티 ─────────────────────────────────────────────────

def now_kst() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")


def send_telegram(message: str) -> bool:
    """텔레그램 메시지 전송 (4096자 제한 자동 분할)"""
    MAX_LEN = 4000
    messages = []

    if len(message) <= MAX_LEN:
        messages = [message]
    else:
        # 줄 단위로 분할
        lines = message.split("\n")
        chunk = ""
        for line in lines:
            if len(chunk) + len(line) + 1 > MAX_LEN:
                messages.append(chunk)
                chunk = line
            else:
                chunk += ("\n" if chunk else "") + line
        if chunk:
            messages.append(chunk)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    success = True

    for msg in messages:
        data = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
        }).encode("utf-8")

        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(
                url, data=data,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, context=ctx, timeout=10)
        except Exception as e:
            print(f"[TG] 전송 실패: {e}")
            success = False

        time.sleep(0.3)

    return success


# ─── 거래일 찾기 ──────────────────────────────────────────────

def find_trading_day(date_str: str = None) -> str:
    """거래일 찾기 (주말/공휴일이면 직전 거래일 반환)"""
    if date_str:
        dt = datetime.strptime(date_str, "%Y%m%d")
    else:
        dt = datetime.now(KST)

    for _ in range(7):
        d = dt.strftime("%Y%m%d")
        try:
            df = stock.get_market_ohlcv_by_ticker(d, market="KOSPI")
            if not df.empty and df["거래량"].sum() > 0:
                return d
        except Exception:
            pass
        dt -= timedelta(days=1)

    # 7일 내 거래일 못 찾으면 그냥 반환
    return dt.strftime("%Y%m%d")


# ─── 상한가 종목 추출 ────────────────────────────────────────

def get_upper_limit_stocks(date: str) -> list:
    """KOSPI + KOSDAQ 상한가 종목 추출"""
    results = []

    for market_name in ["KOSPI", "KOSDAQ"]:
        try:
            df = stock.get_market_ohlcv_by_ticker(date, market=market_name)
            if df.empty:
                print(f"  [{market_name}] 데이터 없음")
                continue

            # 등락률 29%+ 필터
            upper = df[df["등락률"] >= UPPER_LIMIT_PCT]
            print(f"  [{market_name}] 전체: {len(df)}개, 상한가: {len(upper)}개")

            for ticker, row in upper.iterrows():
                name = stock.get_market_ticker_name(ticker)
                results.append({
                    "ticker": ticker,
                    "name": name,
                    "market": market_name,
                    "close": int(row["종가"]),
                    "change_pct": round(float(row["등락률"]), 2),
                    "volume": int(row["거래량"]),
                    "amount_억": round(int(row.get("거래대금", 0)) / 100_000_000, 1),
                })
        except Exception as e:
            print(f"  [{market_name}] 조회 에러: {e}")

    # 등락률 내림차순
    results.sort(key=lambda x: x["change_pct"], reverse=True)
    return results


# ─── 뉴스 검색 ───────────────────────────────────────────────

def search_news(stock_name: str, max_count: int = 2) -> list:
    """네이버 뉴스에서 종목 관련 기사 제목 검색"""
    headlines = []
    try:
        query = urllib.parse.quote(stock_name)
        url = f"https://search.naver.com/search.naver?where=news&query={query}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        }
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        for item in soup.select("a.news_tit")[:max_count]:
            title = item.get_text(strip=True)
            headlines.append(title)

        time.sleep(0.5)  # rate limit 방지
    except Exception as e:
        print(f"  [뉴스] {stock_name} 검색 에러: {e}")

    return headlines


# ─── 리포트 생성 ──────────────────────────────────────────────

def format_report(date: str, stocks: list, news_map: dict) -> str:
    """텔레그램 메시지 포맷"""
    date_fmt = f"{date[:4]}-{date[4:6]}-{date[6:8]}"

    if not stocks:
        return f"📊 {date_fmt} 상한가 종목 없음"

    lines = [f"📈 <b>{date_fmt} 상한가 종목 ({len(stocks)}개)</b>"]
    lines.append("")

    for i, s in enumerate(stocks, 1):
        close_str = f"{s['close']:,}"

        line = (
            f"<b>{i}. {s['name']}</b> ({s['ticker']}) [{s['market']}]\n"
            f"   종가: {close_str}원 (+{s['change_pct']}%)\n"
            f"   거래대금: {s['amount_억']}억원"
        )

        # 뉴스 추가
        news = news_map.get(s["ticker"], [])
        if news:
            for headline in news:
                line += f"\n   → {headline}"
        else:
            line += "\n   → 관련 뉴스 없음"

        lines.append(line)

    return "\n\n".join(lines)


# ─── 콘솔 출력 ───────────────────────────────────────────────

def print_report(date: str, stocks: list, news_map: dict):
    """콘솔 출력 (표 형태)"""
    date_fmt = f"{date[:4]}-{date[4:6]}-{date[6:8]}"

    print(f"\n{'='*60}")
    print(f"  {date_fmt} 상한가 종목 ({len(stocks)}개)")
    print(f"{'='*60}")

    if not stocks:
        print("  상한가 종목 없음")
        return

    for i, s in enumerate(stocks, 1):
        close_str = f"{s['close']:,}"
        print(f"\n  {i}. {s['name']} ({s['ticker']}) [{s['market']}]")
        print(f"     종가: {close_str}원 (+{s['change_pct']}%)")
        print(f"     거래대금: {s['amount_억']}억원 | 거래량: {s['volume']:,}")

        news = news_map.get(s["ticker"], [])
        if news:
            for headline in news:
                print(f"     → {headline}")
        else:
            print(f"     → 관련 뉴스 없음")

    print(f"\n{'='*60}")


# ─── 메인 ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="상한가 종목 알림봇")
    parser.add_argument("--date", type=str, help="조회 날짜 (YYYYMMDD)")
    parser.add_argument("--test", action="store_true", help="테스트 (텔레그램 미전송)")

    args = parser.parse_args()

    print("=" * 60)
    print("  상한가 종목 알림봇 (KOSPI + KOSDAQ)")
    print(f"  시간: {now_kst()}")
    print("=" * 60)

    # 1) 거래일 찾기
    print("\n거래일 확인 중...")
    date = find_trading_day(args.date)
    print(f"조회 날짜: {date}")

    # 2) 상한가 종목 추출
    print("\n상한가 종목 조회 중...")
    stocks = get_upper_limit_stocks(date)
    print(f"\n총 {len(stocks)}개 종목 발견")

    # 3) 종목별 뉴스 검색
    news_map = {}
    if stocks:
        print("\n뉴스 검색 중...")
        for s in stocks:
            news = search_news(s["name"])
            news_map[s["ticker"]] = news
            status = f"✓ {len(news)}건" if news else "✗ 없음"
            print(f"  {s['name']}: {status}")

    # 4) 결과 출력
    print_report(date, stocks, news_map)

    # 5) 텔레그램 전송
    if not args.test:
        report = format_report(date, stocks, news_map)
        if send_telegram(report):
            print("✓ 텔레그램 전송 완료!")
        else:
            print("✗ 텔레그램 전송 실패")
    else:
        print("[TEST] 텔레그램 전송 건너뜀")


if __name__ == "__main__":
    main()
