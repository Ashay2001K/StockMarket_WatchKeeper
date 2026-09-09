"""
Unit tests for PriceMomentumScorer (25 Points Max).
"""

import pytest
import pandas as pd
import numpy as np
from bem_engine.price_momentum import PriceMomentumScorer


def test_price_momentum_bullish_maximum():
    """Stock with strong 20d (+18%), 50d (+30%), outperforming Nifty (+12%), MA stacked, at 52W high."""
    n = 100
    prices = [100.0 * (1.0 + 0.005 * i) for i in range(n)]
    # Push last 20 sessions to ensure >15% return
    for i in range(80, n):
        prices[i] = prices[79] * (1.0 + 0.01 * (i - 79))
    
    df = pd.DataFrame({
        "open": prices,
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices,
        "volume": [100000.0] * n
    })
    
    nifty_prices = [20000.0 * (1.0 + 0.001 * i) for i in range(n)]
    nifty_df = pd.DataFrame({
        "open": nifty_prices,
        "high": nifty_prices,
        "low": nifty_prices,
        "close": nifty_prices,
        "volume": [500000.0] * n
    })
    
    res = PriceMomentumScorer.calculate(df, nifty_df=nifty_df)
    assert res.score <= 25.0
    assert res.score >= 20.0
    assert res.return_20d_pts == 8.0  # return > 15%
    assert res.return_50d_pts == 5.0  # return > 25%
    assert res.rs_pts == 5.0          # RS > 10%
    assert res.ma_alignment_pts == 4.0 # Bullish MA stack
    assert res.proximity_pts == 3.0   # At 52W high


def test_price_momentum_bearish_minimum():
    """Stock falling continuously, below all moving averages, far from 52W high."""
    n = 100
    prices = [200.0 * (1.0 - 0.005 * i) for i in range(n)]
    df = pd.DataFrame({
        "open": prices,
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices,
        "volume": [100000.0] * n
    })
    
    res = PriceMomentumScorer.calculate(df)
    assert res.score == 0.0
    assert res.return_20d < 0.0
    assert res.return_20d_pts == 0.0
    assert res.return_50d_pts == 0.0
    assert res.ma_alignment_pts == 0.0
    assert res.proximity_pts == 0.0
