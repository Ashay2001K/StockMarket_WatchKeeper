"""
Unit tests for DeliveryScorer (15 Points Max).
Verifies delivery percentage brackets, distribution flags, and missing data fallbacks.
"""

import pytest
import pandas as pd
import numpy as np
from bem_engine.delivery_strength import DeliveryScorer


@pytest.mark.parametrize("deliv_val, expected_score", [
    (15.0, 2.0),   # < 20% -> 2 pts
    (25.0, 5.0),   # 20 - 30% -> 5 pts
    (35.0, 8.0),   # 30 - 40% -> 8 pts
    (45.0, 11.0),  # 40 - 50% -> 11 pts
    (55.0, 13.0),  # 50 - 60% -> 13 pts
    (68.0, 15.0),  # > 60% -> 15 pts
])
def test_delivery_percentage_brackets(deliv_val, expected_score):
    n = 30
    df = pd.DataFrame({
        "open": [100.0] * n,
        "high": [102.0] * n,
        "low": [99.0] * n,
        "close": [101.0] * n,
        "volume": [100000.0] * n,
        "delivery_pct": [30.0] * (n - 1) + [deliv_val]
    })

    res = DeliveryScorer.calculate(df)
    assert res.score == expected_score
    assert res.delivery_available is True
    assert not res.distribution_flag


def test_delivery_distribution_warning():
    """High delivery percentage (e.g. 58%) on a sharply falling red candle."""
    n = 30
    df = pd.DataFrame({
        "open": [100.0] * (n - 1) + [100.0],
        "high": [101.0] * n,
        "low": [94.0] * n,
        "close": [100.0] * (n - 1) + [94.0],  # -6% selloff
        "volume": [100000.0] * n,
        "delivery_pct": [30.0] * (n - 1) + [58.0]
    })

    res = DeliveryScorer.calculate(df)
    assert res.distribution_flag is True
    assert res.score <= 5.0  # Capped at 5 pts due to distribution
    assert any("DISTRIBUTION WARNING" in note for note in res.notes)


def test_delivery_missing_data_fallback():
    """When delivery data is completely missing or NaN, fallback safely to neutral."""
    n = 30
    df = pd.DataFrame({
        "open": [100.0] * n,
        "high": [102.0] * n,
        "low": [99.0] * n,
        "close": [101.0] * n,
        "volume": [100000.0] * n
    })

    res = DeliveryScorer.calculate(df)
    assert res.delivery_available is False
    assert res.score == 7.5  # Neutral default
    assert res.current_delivery_pct is None
