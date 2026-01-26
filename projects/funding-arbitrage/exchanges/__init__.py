"""Exchange client wrappers for funding arbitrage bot."""

from .hyperliquid_client import HyperliquidClient
from .extended_client import ExtendedClient

__all__ = ["HyperliquidClient", "ExtendedClient"]
