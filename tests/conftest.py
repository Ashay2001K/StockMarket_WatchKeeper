"""
Pytest fixtures for BEM 100 v2.0 testing.
Provides synthetic OHLCV generators for various market conditions.
"""

import pytest
import pandas as pd
import numpy as np


def generate_ohlcv_series(
    n_bars: int = 100,
    base_price: float = 1000.0,
    trend: str = "flat",  # "flat", "uptrend", "downtrend", "consolidation"
    volume_base: float = 100000.0,
    delivery_base: float = 35.0,
    seed: int = 42
) -> pd.DataFrame:
    """Generates synthetic OHLCV data with realistic bars and delivery."""
    np.random.seed(seed)
    dates = pd.date_range(end="2026-03-31", periods=n_bars, freq="B")
    
    closes = []
    curr = base_price
    for i in range(n_bars):
        if trend == "uptrend":
            drift = 0.003
        elif trend == "downtrend":
            drift = -0.003
        elif trend == "consolidation":
            drift = 0.0005 * np.sin(i / 5.0)
        else:
            drift = 0.0
        
        noise = np.random.normal(0, 0.01)
        curr = max(10.0, curr * (1.0 + drift + noise))
        closes.append(curr)
    
    closes = np.array(closes)
    # Generate open, high, low around close
    opens = closes * (1.0 + np.random.normal(0, 0.004, n_bars))
    highs = np.maximum(opens, closes) * (1.0 + np.abs(np.random.normal(0, 0.006, n_bars)))
    lows = np.minimum(opens, closes) * (1.0 - np.abs(np.random.normal(0, 0.006, n_bars)))
    
    # Volumes with some randomness
    volumes = volume_base * (1.0 + np.random.normal(0, 0.15, n_bars))
    volumes = np.maximum(1000.0, volumes)
    
    # Deliveries
    deliveries = delivery_base + np.random.normal(0, 5.0, n_bars)
    deliveries = np.clip(deliveries, 5.0, 85.0)
    
    df = pd.DataFrame({
        "date": dates,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
        "delivery_pct": deliveries
    })
    return df


@pytest.fixture
def synthetic_flat_df():
    return generate_ohlcv_series(n_bars=100, trend="flat", seed=101)


@pytest.fixture
def synthetic_uptrend_df():
    return generate_ohlcv_series(n_bars=100, trend="uptrend", seed=102)


@pytest.fixture
def synthetic_nifty_df():
    return generate_ohlcv_series(n_bars=100, base_price=22000.0, trend="uptrend", seed=200)
