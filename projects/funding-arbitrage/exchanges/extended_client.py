#!/usr/bin/env python3
"""
Extended (x10) SDK 래퍼
- 주문 실행 (시장가/지정가)
- 포지션 조회
- 잔액 조회
- 펀딩비 조회 (REST API)
"""

import asyncio
import requests
from decimal import Decimal

from x10.perpetual.accounts import StarkPerpetualAccount
from x10.perpetual.configuration import MAINNET_CONFIG, TESTNET_CONFIG
from x10.perpetual.trading_client import PerpetualTradingClient
from x10.perpetual.orders import OrderSide


# Extended REST API base URLs
EXT_API_MAINNET = "https://api.starknet.extended.exchange"
EXT_API_TESTNET = "https://api.starknet.sepolia.extended.exchange"

# 코인 심볼 매핑 (HL 이름 → Extended 이름)
COIN_MAP = {
    "PEPE": "1000PEPE",
    "BONK": "1000BONK",
    "SHIB": "1000SHIB",
}
COIN_MAP_REVERSE = {v: k for k, v in COIN_MAP.items()}


class ExtendedClient:
    def __init__(self, api_key: str, stark_private_key: str, stark_public_key: str,
                 vault: int, testnet: bool = False):
        self.testnet = testnet
        self.api_base = EXT_API_TESTNET if testnet else EXT_API_MAINNET
        config = TESTNET_CONFIG if testnet else MAINNET_CONFIG

        stark_account = StarkPerpetualAccount(
            vault=vault,
            private_key=stark_private_key,
            public_key=stark_public_key,
            api_key=api_key,
        )
        self.trading_client = PerpetualTradingClient.create(config, stark_account)
        self._api_key = api_key

    def _run_async(self, coro):
        """동기 래퍼: async 함수를 동기적으로 실행"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, coro).result()
            return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    def _api_headers(self) -> dict:
        return {
            "User-Agent": "funding-arb-bot/1.0",
            "Accept": "application/json",
        }

    def _coin_to_market(self, coin: str) -> str:
        """코인 심볼을 Extended 마켓 이름으로 변환 (e.g. BTC -> BTC-USD)"""
        ext_coin = COIN_MAP.get(coin, coin)
        return f"{ext_coin}-USD"

    def get_funding_rates(self) -> dict[str, float]:
        """모든 마켓의 현재 펀딩비 조회 (% 단위, 8시간 기준 환산)
        Extended는 1시간 기준 펀딩비를 사용하므로 ×8 해서 8시간 기준으로 맞춤
        """
        try:
            url = f"{self.api_base}/api/v1/info/markets"
            resp = requests.get(url, headers=self._api_headers(), timeout=10)
            result = resp.json()
            markets = result.get("data", result)

            rates = {}
            if isinstance(markets, list):
                for market in markets:
                    name = market.get("name", "")
                    if not name.endswith("-USD"):
                        continue
                    ext_coin = name.replace("-USD", "")
                    coin = COIN_MAP_REVERSE.get(ext_coin, ext_coin)
                    market_stats = market.get("marketStats", {})
                    funding_rate = market_stats.get("fundingRate")
                    if funding_rate is None:
                        # fallback: stats endpoint
                        stats_url = f"{self.api_base}/api/v1/info/markets/{name}/stats"
                        stats_resp = requests.get(stats_url, headers=self._api_headers(), timeout=10)
                        stats_result = stats_resp.json()
                        stats = stats_result.get("data", stats_result)
                        funding_rate = stats.get("fundingRate")
                    if funding_rate is not None:
                        rates[coin] = float(funding_rate) * 8 * 100
            return rates
        except Exception as e:
            print(f"[Extended 에러] 펀딩비 조회 실패: {e}")
            return {}

    def get_funding_rates_batch(self, coins: list[str]) -> dict[str, float]:
        """특정 코인들의 펀딩비만 조회 (API 호출 최소화)"""
        rates = {}
        for coin in coins:
            try:
                market = self._coin_to_market(coin)
                url = f"{self.api_base}/api/v1/info/markets/{market}/stats"
                resp = requests.get(url, headers=self._api_headers(), timeout=10)
                if resp.status_code == 200:
                    result = resp.json()
                    stats = result.get("data", result)
                    funding_rate = stats.get("fundingRate")
                    if funding_rate is not None:
                        rates[coin] = float(funding_rate) * 8 * 100
            except Exception as e:
                print(f"[Extended 에러] {coin} 펀딩비 조회 실패: {e}")
        return rates

    def get_mark_price(self, coin: str) -> float | None:
        """특정 코인의 마크 가격 조회"""
        try:
            market = self._coin_to_market(coin)
            url = f"{self.api_base}/api/v1/info/markets/{market}/stats"
            resp = requests.get(url, headers=self._api_headers(), timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                stats = result.get("data", result)
                return float(stats.get("markPrice", 0))
        except Exception as e:
            print(f"[Extended 에러] {coin} 가격 조회 실패: {e}")
        return None

    def get_balance(self) -> dict:
        """계정 잔액 조회"""
        try:
            balance = self._run_async(self.trading_client.account.get_balance())
            return {
                "equity": float(getattr(balance, "equity", 0)),
                "available": float(getattr(balance, "available_balance", 0)),
                "margin_used": float(getattr(balance, "margin_used", 0)),
            }
        except Exception as e:
            print(f"[Extended 에러] 잔액 조회 실패: {e}")
            return {"equity": 0, "available": 0, "margin_used": 0}

    def get_positions(self) -> list[dict]:
        """현재 포지션 조회"""
        try:
            positions_data = self._run_async(self.trading_client.account.get_positions())
            positions = []
            items = positions_data.data if hasattr(positions_data, "data") else positions_data
            if not items:
                return []
            for pos in items:
                size = float(getattr(pos, "size", 0))
                if size == 0:
                    continue
                market = getattr(pos, "market", "")
                coin = market.replace("-USD", "") if market else ""
                positions.append({
                    "coin": coin,
                    "size": abs(size),
                    "side": str(getattr(pos, "side", "")).upper(),
                    "entry_price": float(getattr(pos, "open_price", 0)),
                    "unrealized_pnl": float(getattr(pos, "unrealised_pnl", 0)),
                    "leverage": float(getattr(pos, "leverage", 1)),
                })
            return positions
        except Exception as e:
            print(f"[Extended 에러] 포지션 조회 실패: {e}")
            return []

    def get_position(self, coin: str) -> dict | None:
        """특정 코인의 포지션 조회"""
        for pos in self.get_positions():
            if pos["coin"] == coin:
                return pos
        return None

    def place_market_order(self, coin: str, is_buy: bool, size: float, slippage: float = 0.05) -> dict:
        """시장가 주문 (공격적 지정가로 구현)
        Extended SDK에 시장가 주문이 없으므로 슬리피지를 포함한 지정가 주문으로 대체
        """
        try:
            mark_price = self.get_mark_price(coin)
            if not mark_price:
                return {"success": False, "error": f"Cannot get mark price for {coin}"}

            if is_buy:
                price = mark_price * (1 + slippage)
            else:
                price = mark_price * (1 - slippage)

            market = self._coin_to_market(coin)
            side = OrderSide.BUY if is_buy else OrderSide.SELL

            result = self._run_async(
                self.trading_client.place_order(
                    market_name=market,
                    amount_of_synthetic=Decimal(str(size)),
                    price=Decimal(str(round(price, 2))),
                    side=side,
                )
            )
            return {
                "success": True,
                "status": "placed",
                "order_id": getattr(result, "id", None),
                "price": price,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def place_limit_order(self, coin: str, is_buy: bool, size: float, price: float) -> dict:
        """지정가 주문"""
        try:
            market = self._coin_to_market(coin)
            side = OrderSide.BUY if is_buy else OrderSide.SELL

            result = self._run_async(
                self.trading_client.place_order(
                    market_name=market,
                    amount_of_synthetic=Decimal(str(size)),
                    price=Decimal(str(price)),
                    side=side,
                )
            )
            return {
                "success": True,
                "status": "placed",
                "order_id": getattr(result, "id", None),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def close_position(self, coin: str, slippage: float = 0.05) -> dict:
        """포지션 전체 청산"""
        pos = self.get_position(coin)
        if not pos:
            return {"success": False, "error": f"No open position for {coin}"}

        is_buy = pos["side"] == "SHORT"  # 숏이면 매수로 청산
        return self.place_market_order(coin, is_buy, pos["size"], slippage)

    def cancel_order(self, order_id) -> dict:
        """주문 취소"""
        try:
            self._run_async(
                self.trading_client.orders.cancel_order(order_id=order_id)
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cancel_all_orders(self, coin: str | None = None) -> dict:
        """미체결 주문 전체 취소"""
        try:
            open_orders = self._run_async(
                self.trading_client.account.get_open_orders()
            )
            items = open_orders.data if hasattr(open_orders, "data") else open_orders
            if not items:
                return {"success": True, "cancelled": 0}

            order_ids = []
            for order in items:
                if coin:
                    market = getattr(order, "market", "")
                    if market != self._coin_to_market(coin):
                        continue
                order_ids.append(order.id)

            if order_ids:
                self._run_async(
                    self.trading_client.orders.mass_cancel(order_ids=order_ids)
                )
            return {"success": True, "cancelled": len(order_ids)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def set_leverage(self, coin: str, leverage: int) -> dict:
        """레버리지 설정"""
        try:
            market = self._coin_to_market(coin)
            self._run_async(
                self.trading_client.account.update_leverage(
                    market_name=market,
                    leverage=Decimal(str(leverage)),
                )
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
