"""
Unit tests for data_provider package.
Verifies ticker cleaning, fallback handling, and composite provider data transformation.
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from data_provider.yfinance_provider import clean_ticker, YFinanceProvider
from data_provider.nse_bhavcopy_provider import NSEBhavcopyProvider
from data_provider.composite_provider import CompositeMarketDataProvider


def test_clean_ticker():
    assert clean_ticker("TCS") == "TCS.NS"
    assert clean_ticker("INFY.NS") == "INFY.NS"
    assert clean_ticker("TATAMOTORS.BO") == "TATAMOTORS.BO"
    assert clean_ticker("^NSEI") == "^NSEI"
    assert clean_ticker("^INDIAVIX") == "^INDIAVIX"


def test_nse_bhavcopy_graceful_fallback():
    """Provider should return None and not crash when network request fails or is blocked."""
    provider = NSEBhavcopyProvider()
    with patch.object(provider.session, 'get', side_effect=Exception("Cloudflare 403 Blocked")):
        deliv = provider.get_symbol_delivery("RELIANCE")
        assert deliv is None


def test_composite_provider_with_missing_delivery():
    """Composite provider should assign None to delivery_pct when delivery is unavailable, without error."""
    composite = CompositeMarketDataProvider()
    dummy_df = pd.DataFrame({
        "open": [100.0] * 30,
        "high": [102.0] * 30,
        "low": [98.0] * 30,
        "close": [101.0] * 30,
        "volume": [100000.0] * 30
    })

    with patch.object(composite.yf_provider, 'get_stock_ohlcv', return_value=dummy_df), \
         patch.object(composite.nse_provider, 'get_symbol_delivery', return_value=None), \
         patch.object(composite, 'get_benchmark_data', return_value=None), \
         patch.object(composite, 'get_india_vix', return_value=14.5):

        res = composite.get_stock_data("INFY")
        assert res is not None
        assert res.symbol == "INFY"
        assert res.df['delivery_pct'].iloc[-1] is None
        assert res.india_vix == 14.5
