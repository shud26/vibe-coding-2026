#!/usr/bin/env python3
"""
CEX/DEX 가격 갭 모니터링 봇
- Binance, Bybit, OKX, Bitget (CEX)
- Hyperliquid (DEX)
- 가격 차이 모니터링 + 텔레그램 알림
"""

import requests
import os
from datetime import datetime
from typing import Dict, Optional
import time

# 텔레그램 설정
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7881191796:AAEB4mN7dMIj3jEN0PoWAo46z6TPX-hawfI")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6329588659")

# 알림 임계값 (%)
GAP_THRESHOLD = 0.1  # 0.1% 이상 차이나면 알림

# 모니터링할 코인들
COINS = ["BTC", "ETH", "SOL", "DOGE", "XRP", "ARB", "SUI", "AVAX", "LINK"]


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


def get_binance_price(symbol: str) -> Optional[float]:
    """Binance 선물 가격"""
    try:
        url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}USDT"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return float(response.json()["price"])
    except:
        pass
    return None


def get_bybit_price(symbol: str) -> Optional[float]:
    """Bybit 선물 가격"""
    try:
        url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}USDT"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data["result"]["list"]:
                return float(data["result"]["list"][0]["lastPrice"])
    except:
        pass
    return None


def get_okx_price(symbol: str) -> Optional[float]:
    """OKX 선물 가격"""
    try:
        url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}-USDT-SWAP"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data["data"]:
                return float(data["data"][0]["last"])
    except:
        pass
    return None


def get_bitget_price(symbol: str) -> Optional[float]:
    """Bitget 선물 가격"""
    try:
        url = f"https://api.bitget.com/api/v2/mix/market/ticker?productType=USDT-FUTURES&symbol={symbol}USDT"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data["data"]:
                return float(data["data"][0]["lastPr"])
    except:
        pass
    return None


def get_hyperliquid_prices() -> Dict[str, float]:
    """Hyperliquid 전체 가격"""
    try:
        url = "https://api.hyperliquid.xyz/info"
        response = requests.post(url, json={"type": "allMids"}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {k: float(v) for k, v in data.items()}
    except:
        pass
    return {}


def get_all_prices(coin: str, hl_prices: Dict[str, float]) -> Dict[str, Optional[float]]:
    """모든 거래소에서 가격 가져오기"""
    prices = {
        "Binance": get_binance_price(coin),
        "Bybit": get_bybit_price(coin),
        "OKX": get_okx_price(coin),
        "Bitget": get_bitget_price(coin),
        "Hyperliquid": hl_prices.get(coin),
    }
    return prices


def calculate_gaps(prices: Dict[str, Optional[float]]) -> list:
    """가격 차이 계산"""
    valid_prices = {k: v for k, v in prices.items() if v is not None}
    if len(valid_prices) < 2:
        return []

    gaps = []
    exchanges = list(valid_prices.keys())

    for i in range(len(exchanges)):
        for j in range(i + 1, len(exchanges)):
            ex1, ex2 = exchanges[i], exchanges[j]
            p1, p2 = valid_prices[ex1], valid_prices[ex2]

            # 가격 차이 % 계산
            avg_price = (p1 + p2) / 2
            gap_pct = ((p1 - p2) / avg_price) * 100

            gaps.append({
                "exchange1": ex1,
                "exchange2": ex2,
                "price1": p1,
                "price2": p2,
                "gap_pct": gap_pct,
                "gap_abs": abs(gap_pct)
            })

    # 갭 크기로 정렬
    gaps.sort(key=lambda x: x["gap_abs"], reverse=True)
    return gaps


def format_price(price: float, coin: str) -> str:
    """가격 포맷팅"""
    if coin in ["BTC", "ETH"]:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.4f}"
    else:
        return f"${price:.6f}"


def check_price_gaps(alert_threshold: float = GAP_THRESHOLD, show_all: bool = False):
    """가격 갭 체크"""
    print(f"\n{'='*60}")
    print(f"📊 CEX/DEX 가격 갭 모니터링")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # Hyperliquid 가격 한번에 가져오기
    hl_prices = get_hyperliquid_prices()

    all_gaps = []

    for coin in COINS:
        prices = get_all_prices(coin, hl_prices)
        valid_count = sum(1 for v in prices.values() if v is not None)

        if valid_count < 2:
            continue

        gaps = calculate_gaps(prices)

        if gaps:
            top_gap = gaps[0]
            all_gaps.append({
                "coin": coin,
                "gap": top_gap
            })

            # 콘솔 출력
            gap_color = "🔴" if top_gap["gap_abs"] >= alert_threshold else "🟢"
            print(f"\n{gap_color} {coin}")

            for ex, price in prices.items():
                if price:
                    print(f"   {ex:12} {format_price(price, coin)}")

            print(f"   ➜ 최대 갭: {top_gap['exchange1']} vs {top_gap['exchange2']}: {top_gap['gap_pct']:+.4f}%")

    # 임계값 이상인 갭만 필터
    significant_gaps = [g for g in all_gaps if g["gap"]["gap_abs"] >= alert_threshold]

    if significant_gaps or show_all:
        # 텔레그램 알림
        msg = "📊 <b>CEX/DEX 가격 갭 리포트</b>\n\n"

        if significant_gaps:
            msg += f"🔔 <b>{alert_threshold}% 이상 갭 발견!</b>\n\n"

            for item in sorted(significant_gaps, key=lambda x: x["gap"]["gap_abs"], reverse=True):
                coin = item["coin"]
                gap = item["gap"]

                # 어디가 비싼지 표시
                if gap["gap_pct"] > 0:
                    expensive = gap["exchange1"]
                    cheap = gap["exchange2"]
                else:
                    expensive = gap["exchange2"]
                    cheap = gap["exchange1"]

                msg += f"<b>{coin}</b>: {gap['gap_abs']:.4f}%\n"
                msg += f"  📈 {expensive}: {format_price(max(gap['price1'], gap['price2']), coin)}\n"
                msg += f"  📉 {cheap}: {format_price(min(gap['price1'], gap['price2']), coin)}\n"
                msg += f"  💡 {cheap}에서 사서 {expensive}에서 팔기\n\n"
        else:
            msg += "✅ 유의미한 갭 없음\n\n"
            # 상위 3개 갭 표시
            msg += "📋 <b>현재 상위 갭:</b>\n"
            for item in sorted(all_gaps, key=lambda x: x["gap"]["gap_abs"], reverse=True)[:3]:
                coin = item["coin"]
                gap = item["gap"]
                msg += f"  • {coin}: {gap['gap_abs']:.4f}% ({gap['exchange1']} vs {gap['exchange2']})\n"

        msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

        if significant_gaps or show_all:
            send_telegram(msg)

    print(f"\n{'='*60}")
    print(f"✅ 체크 완료. {len(significant_gaps)}개 유의미한 갭 발견")

    return all_gaps


def main():
    import argparse

    parser = argparse.ArgumentParser(description="CEX/DEX 가격 갭 모니터링")
    parser.add_argument("--once", action="store_true", help="한 번만 실행")
    parser.add_argument("--interval", type=int, default=30, help="체크 간격 (초)")
    parser.add_argument("--threshold", type=float, default=GAP_THRESHOLD, help="알림 임계값 (%)")
    parser.add_argument("--show-all", action="store_true", help="항상 텔레그램 알림")
    args = parser.parse_args()

    if args.once:
        check_price_gaps(args.threshold, args.show_all)
    else:
        print(f"🔄 {args.interval}초마다 가격 갭 체크...")
        print(f"📢 {args.threshold}% 이상 갭 발견 시 알림")

        while True:
            try:
                check_price_gaps(args.threshold, False)
                print(f"\n⏳ 다음 체크: {args.interval}초 후...")
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\n👋 종료합니다.")
                break
            except Exception as e:
                print(f"❌ 에러: {e}")
                time.sleep(10)


if __name__ == "__main__":
    main()
