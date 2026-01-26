#!/usr/bin/env python3
"""
Hyperliquid SDK 래퍼
- 주문 실행 (시장가/지정가)
- 포지션 조회
- 잔액 조회
- 펀딩비 조회
"""

import eth_account
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants


class HyperliquidClient:
    def __init__(self, private_key: str, wallet_address: str, testnet: bool = False):
        self.wallet_address = wallet_address
        base_url = constants.TESTNET_API_URL if testnet else constants.MAINNET_API_URL

        self.info = Info(base_url, skip_ws=True)
        wallet = eth_account.Account.from_key(private_key)
        self.exchange = Exchange(wallet, base_url, account_address=wallet_address)

    def get_funding_rates(self) -> dict[str, float]:
        """모든 코인의 현재 펀딩비 조회 (8시간 기준, % 단위)"""
        data = self.info.meta_and_asset_ctxs()
        universe = data[0]["universe"]
        asset_contexts = data[1]

        rates = {}
        for i, asset in enumerate(universe):
            coin = asset["name"]
            funding = float(asset_contexts[i]["funding"]) * 100
            rates[coin] = funding
        return rates

    def get_mark_prices(self) -> dict[str, float]:
        """모든 코인의 마크 가격 조회"""
        data = self.info.meta_and_asset_ctxs()
        universe = data[0]["universe"]
        asset_contexts = data[1]

        prices = {}
        for i, asset in enumerate(universe):
            coin = asset["name"]
            mark_px = asset_contexts[i].get("markPx")
            if mark_px:
                prices[coin] = float(mark_px)
        return prices

    def get_sz_decimals(self) -> dict[str, int]:
        """코인별 수량 소수점 자릿수"""
        data = self.info.meta_and_asset_ctxs()
        universe = data[0]["universe"]
        return {asset["name"]: asset["szDecimals"] for asset in universe}

    def get_balance(self) -> dict:
        """계정 잔액 조회"""
        state = self.info.user_state(self.wallet_address)
        summary = state.get("crossMarginSummary", state.get("marginSummary", {}))
        return {
            "account_value": float(summary.get("accountValue", 0)),
            "total_margin_used": float(summary.get("totalMarginUsed", 0)),
            "withdrawable": float(state.get("withdrawable", 0)),
        }

    def get_positions(self) -> list[dict]:
        """현재 포지션 조회"""
        state = self.info.user_state(self.wallet_address)
        positions = []
        for pos_data in state.get("assetPositions", []):
            pos = pos_data["position"]
            szi = float(pos["szi"])
            if szi == 0:
                continue
            positions.append({
                "coin": pos["coin"],
                "size": abs(szi),
                "side": "LONG" if szi > 0 else "SHORT",
                "entry_price": float(pos.get("entryPx", 0)),
                "unrealized_pnl": float(pos.get("unrealizedPnl", 0)),
                "margin_used": float(pos.get("marginUsed", 0)),
                "leverage": pos.get("leverage", {}),
            })
        return positions

    def get_position(self, coin: str) -> dict | None:
        """특정 코인의 포지션 조회"""
        for pos in self.get_positions():
            if pos["coin"] == coin:
                return pos
        return None

    def place_market_order(self, coin: str, is_buy: bool, size: float, slippage: float = 0.05) -> dict:
        """시장가 주문
        Args:
            coin: 코인 심볼 (e.g. "BTC")
            is_buy: True=롱, False=숏
            size: 주문 수량 (코인 단위)
            slippage: 슬리피지 허용치 (기본 5%)
        Returns:
            주문 결과
        """
        result = self.exchange.market_open(coin, is_buy, size, slippage=slippage)
        return self._parse_order_result(result)

    def place_limit_order(self, coin: str, is_buy: bool, size: float, price: float) -> dict:
        """지정가 주문 (GTC)"""
        result = self.exchange.order(
            coin, is_buy, size, price,
            order_type={"limit": {"tif": "Gtc"}}
        )
        return self._parse_order_result(result)

    def close_position(self, coin: str, slippage: float = 0.05) -> dict:
        """포지션 전체 청산 (시장가)"""
        result = self.exchange.market_close(coin, slippage=slippage)
        if result is None:
            return {"success": False, "error": f"No open position for {coin}"}
        return self._parse_order_result(result)

    def cancel_order(self, coin: str, oid: int) -> dict:
        """주문 취소"""
        result = self.exchange.cancel(coin, oid)
        return {"success": True, "result": result}

    def cancel_all_orders(self, coin: str) -> list[dict]:
        """특정 코인의 모든 미체결 주문 취소"""
        open_orders = self.info.open_orders(self.wallet_address)
        results = []
        for order in open_orders:
            if order.get("coin") == coin:
                result = self.cancel_order(coin, order["oid"])
                results.append(result)
        return results

    def set_leverage(self, coin: str, leverage: int, is_cross: bool = True) -> dict:
        """레버리지 설정"""
        result = self.exchange.update_leverage(leverage, coin, is_cross)
        return {"success": True, "result": result}

    def _parse_order_result(self, result: dict) -> dict:
        """주문 결과 파싱"""
        if result.get("status") == "ok":
            response = result.get("response", {})
            if response.get("type") == "order":
                statuses = response.get("data", {}).get("statuses", [])
                if statuses:
                    status = statuses[0]
                    if "resting" in status:
                        return {
                            "success": True,
                            "status": "resting",
                            "oid": status["resting"]["oid"],
                        }
                    elif "filled" in status:
                        return {
                            "success": True,
                            "status": "filled",
                            "oid": status["filled"]["oid"],
                            "avg_price": float(status["filled"].get("avgPx", 0)),
                            "filled_size": float(status["filled"].get("totalSz", 0)),
                        }
                    elif "error" in status:
                        return {"success": False, "error": status["error"]}
            return {"success": True, "result": response}
        return {"success": False, "error": result.get("response", str(result))}
