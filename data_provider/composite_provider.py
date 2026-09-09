"""
Composite Market Data Provider.
Combines YFinance price data with public NSE delivery bhavcopy data into unified StockDataInput objects.
Gracefully degrades with Confidence: Medium and N/A flags when delivery or benchmark data is unavailable.
"""

import logging
from typing import Optional, Dict, List
import pandas as pd
from data_provider.base import MarketDataProvider
from data_provider.yfinance_provider import YFinanceProvider
from data_provider.nse_bhavcopy_provider import NSEBhavcopyProvider
from bem_engine.types import StockDataInput

logger = logging.getLogger(__name__)


class CompositeMarketDataProvider(MarketDataProvider):
    """
    Main data provider unifying free Yahoo Finance OHLCV and official NSE Bhavcopy delivery.
    Strictly Zero-Cost: completely free-tier compliant.
    """

    def __init__(self):
        self.yf_provider = YFinanceProvider()
        self.nse_provider = NSEBhavcopyProvider()
        self._nifty_cache: Optional[pd.DataFrame] = None
        self._vix_cache: Optional[float] = None

    def get_benchmark_data(self, lookback_days: int = 250) -> Optional[pd.DataFrame]:
        """Returns cached Nifty 50 OHLCV."""
        if self._nifty_cache is None:
            self._nifty_cache = self.yf_provider.get_nifty50_ohlcv(period="1y")
        return self._nifty_cache

    def get_india_vix(self) -> Optional[float]:
        """Returns current India VIX reading."""
        if self._vix_cache is None:
            self._vix_cache = self.yf_provider.get_india_vix()
        return self._vix_cache

    def get_delivery_data(self, symbol: str) -> Optional[float]:
        """Fetches latest delivery percentage from NSE bhavcopy."""
        return self.nse_provider.get_symbol_delivery(symbol)

    def get_stock_data(self, symbol: str, lookback_days: int = 250) -> Optional[StockDataInput]:
        """
        Fetches full stock data input including OHLCV, attached delivery %, and Nifty benchmark.
        """
        clean_symbol = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
        df = self.yf_provider.get_stock_ohlcv(clean_symbol, period="1y")
        if df is None or len(df) == 0:
            return None

        # Fetch and attach latest delivery percentage
        deliv_pct = self.get_delivery_data(clean_symbol)
        if deliv_pct is not None:
            # Set on the latest bar, or backfill neutral for historical
            df['delivery_pct'] = None
            df.loc[df.index[-1], 'delivery_pct'] = deliv_pct
        else:
            df['delivery_pct'] = None

        nifty_df = self.get_benchmark_data()
        india_vix = self.get_india_vix()

        return StockDataInput(
            symbol=clean_symbol,
            df=df,
            nifty_df=nifty_df,
            india_vix=india_vix
        )

    def batch_fetch(self, symbols: List[str], lookback_days: int = 250) -> Dict[str, StockDataInput]:
        """
        Batch fetches target universe using multithreaded chunk downloads.
        Applies pre-downloaded NSE daily delivery data to each ticker.
        """
        # 1. Ensure daily delivery bhavcopy is downloaded once for the entire batch
        self.nse_provider.fetch_daily_delivery_bhavcopy()

        # 2. Fetch Nifty 50 and India VIX once
        nifty_df = self.get_benchmark_data()
        india_vix = self.get_india_vix()

        # 3. Multithreaded chunked OHLCV download
        ohlcv_dict = self.yf_provider.batch_download_chunks(symbols, chunk_size=50)

        inputs: Dict[str, StockDataInput] = {}
        for sym, df in ohlcv_dict.items():
            clean_sym = sym.upper().replace(".NS", "").replace(".BO", "").strip()
            deliv = self.get_delivery_data(clean_sym)

            df['delivery_pct'] = None
            if deliv is not None:
                df.loc[df.index[-1], 'delivery_pct'] = deliv

            inputs[clean_sym] = StockDataInput(
                symbol=clean_sym,
                df=df,
                nifty_df=nifty_df,
                india_vix=india_vix
            )

        return inputs
