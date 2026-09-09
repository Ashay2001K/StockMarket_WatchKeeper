"""
Unit tests for ExhaustionScorer (0 to 15 Base Scale).
Verifies exhaustion progression from fresh bases to extreme vertical parabolic blow-offs,
ensuring (15 - Exhaustion Score) maps accurately.
"""

import pytest
import pandas as pd
import numpy as np
from bem_engine.momentum_exhaustion import ExhaustionScorer


def test_exhaustion_fresh_orderly_trend():
    """Stock in a steady, unextended base with natural minor fluctuations."""
    n = 30
    prices = [100.0 + (0.5 * np.sin(i / 2.0)) for i in range(n)]
    df = pd.DataFrame({
        "open": prices,
        "high": [p * 1.005 for p in prices],
        "low": [p * 0.995 for p in prices],
        "close": prices,
        "volume": [100000.0] * n
    })

    res = ExhaustionScorer.calculate(df)
    assert res.exhaustion_score <= 4.0
    assert res.bem_contribution >= 11.0
    assert not res.is_parabolic


def test_exhaustion_ten_session_gain_brackets():
    """Stock up >15% over 10 sessions, but <= 20% in an orderly move."""
    n = 30
    prices = [100.0] * 19
    for i in range(11):
        prices.append(100.0 + (1.65 * i) + (0.2 if i % 2 == 0 else -0.2))

    df = pd.DataFrame({
        "open": prices,
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices,
        "volume": [100000.0] * n
    })

    res = ExhaustionScorer.calculate(df)
    assert 6.0 <= res.exhaustion_score <= 8.0
    assert 7.0 <= res.bem_contribution <= 9.0


def test_exhaustion_severely_extended():
    """Stock up > 25% in 10 sessions and extended > 10% above 20 DMA."""
    n = 30
    prices = [100.0] * 19 + [100.0 * (1.0 + 0.03 * i) for i in range(11)]  # > 30% gain
    df = pd.DataFrame({
        "open": prices,
        "high": [p * 1.02 for p in prices],
        "low": [p * 0.98 for p in prices],
        "close": prices,
        "volume": [100000.0] * n
    })

    res = ExhaustionScorer.calculate(df)
    assert res.exhaustion_score >= 12.0
    assert res.bem_contribution <= 3.0
    assert res.is_parabolic is True


def test_exhaustion_parabolic_divergence():
    """Price advances rapidly on strictly declining volume (volume tapering)."""
    n = 30
    # Fast move from 100 to 125 over 10 days
    prices = [100.0] * 20 + [100.0 + (2.5 * i) for i in range(10)]
    # Shrinking volume on final 4 days
    volumes = [100000.0] * 26 + [80000.0, 60000.0, 40000.0, 20000.0]
    df = pd.DataFrame({
        "open": prices,
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices,
        "volume": volumes
    })

    res = ExhaustionScorer.calculate(df)
    assert res.parabolic_volume_tapering is True
    assert res.exhaustion_score >= 13.0
