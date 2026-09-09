"""
Abstract Base Class for Zero-Cost Market Data Providers.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List
import pandas as pd
from bem_engine.types import StockDataInput


class MarketDataProvider(ABC):
    """
    Abstract interface for stock market data fetching.
    Strict zero-cost requirement: no paid API dependencies.
    """

    @abstractmethod
    def get_stock_data(self, symbol: str, lookback_days: int = 250) -> Optional[StockDataInput]:
        """Fetches OHLCV, moving averages, delivery %, and benchmark data for a single symbol."""
        pass

    @abstractmethod
    def batch_fetch(self, symbols: List[str], lookback_days: int = 250) -> Dict[str, StockDataInput]:
        """Batch fetches data across a universe of symbols."""
        pass

    @abstractmethod
    def get_benchmark_data(self, lookback_days: int = 250) -> Optional[pd.DataFrame]:
        """Fetches Nifty 50 benchmark OHLCV."""
        pass

    @abstractmethod
    def get_india_vix(self) -> Optional[float]:
        """Fetches current India VIX index level."""
        pass
