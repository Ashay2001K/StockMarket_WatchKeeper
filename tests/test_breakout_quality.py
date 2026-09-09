"""
Unit tests for BreakoutScorer (15 Points Max).
Verifies breakout quality conditions across resistance testing, low volume breakouts,
and high-volume + strong-delivery breakouts.
"""

import pytest
import pandas as pd
import numpy as np
from bem_engine.breakout_quality import BreakoutScorer


def test_breakout_below_resistance():
    """Stock trading well below prior 20-day resistance."""
    n = 30
    highs = [150.0] * (n - 1) + [130.0]
    closes = [145.0] * (n - 1) + [128.0]
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": [c - 2 for c in closes],
        "close": closes,
        "volume": [100000.0] * n
    })

    res = BreakoutScorer.calculate(df, volume_ratio=1.0, delivery_pct=30.0)
    assert res.score == 3.0
    assert not res.is_breakout
    assert not res.is_testing_resistance


def test_breakout_testing_resistance():
    """Stock pressing against prior resistance (within 1.5%)."""
    n = 30
    # Prior swing high is 150.0. Current close is 149.0 (0.67% below).
    highs = [150.0] * (n - 1) + [149.5]
    closes = [140.0] * (n - 1) + [149.0]
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": [c - 2 for c in closes],
        "close": closes,
        "volume": [100000.0] * n
    })

    res = BreakoutScorer.calculate(df, volume_ratio=1.2, delivery_pct=35.0)
    assert res.score == 7.0
    assert res.is_testing_resistance is True
    assert not res.is_breakout


def test_breakout_without_volume():
    """Stock closes above resistance but volume is weak (< 1.5x)."""
    n = 30
    # Prior high 150.0, current close 153.0. Volume ratio 1.1x.
    highs = [150.0] * (n - 1) + [154.0]
    closes = [140.0] * (n - 1) + [153.0]
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": [c - 2 for c in closes],
        "close": closes,
        "volume": [100000.0] * n
    })

    res = BreakoutScorer.calculate(df, volume_ratio=1.1, delivery_pct=30.0)
    assert res.score == 9.0
    assert res.is_breakout is True


def test_breakout_with_volume_only():
    """Stock closes above resistance with volume >= 1.5x, but low delivery (< 40%)."""
    n = 30
    highs = [150.0] * (n - 1) + [155.0]
    closes = [140.0] * (n - 1) + [154.0]
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": [c - 2 for c in closes],
        "close": closes,
        "volume": [100000.0] * n
    })

    res = BreakoutScorer.calculate(df, volume_ratio=1.8, delivery_pct=25.0)
    assert res.score == 13.0
    assert res.is_breakout is True


def test_breakout_confirmed_volume_and_delivery():
    """A+ breakout: Closes above resistance with volume >= 1.5x AND delivery >= 40%."""
    n = 30
    highs = [150.0] * (n - 1) + [156.0]
    closes = [140.0] * (n - 1) + [155.0]
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": [c - 2 for c in closes],
        "close": closes,
        "volume": [100000.0] * n
    })

    res = BreakoutScorer.calculate(df, volume_ratio=2.1, delivery_pct=52.0)
    assert res.score == 15.0
    assert res.is_breakout is True
