"""
Unit tests for BEM100Engine Pipeline Invariants and Resilience.
Verifies score limits, exact score breakdown sum, confidence downgrading, and edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from bem_engine import BEM100Engine, StockDataInput, ConfidenceLevel


def test_bem_score_boundary_invariants(synthetic_flat_df, synthetic_uptrend_df, synthetic_nifty_df):
    """Verifies that BEM Score is strictly clamped within [0.0, 100.0] across different inputs."""
    for df in [synthetic_flat_df, synthetic_uptrend_df]:
        input_data = StockDataInput(symbol="TEST", df=df, nifty_df=synthetic_nifty_df)
        res = BEM100Engine.analyze(input_data)

        assert 0.0 <= res.bem_score <= 100.0
        assert 0.0 <= res.score_breakdown.price_momentum <= 25.0
        assert 0.0 <= res.score_breakdown.volume_expansion <= 20.0
        assert 0.0 <= res.score_breakdown.delivery_strength <= 15.0
        assert 0.0 <= res.score_breakdown.breakout_quality <= 15.0
        assert 0.0 <= res.score_breakdown.institutional <= 10.0
        assert 0.0 <= res.score_breakdown.exhaustion_adjustment <= 15.0
        assert 0.0 <= res.score_breakdown.raw_exhaustion_score <= 15.0

        # Exact mathematical sum invariant
        calc_sum = (
            res.score_breakdown.price_momentum +
            res.score_breakdown.volume_expansion +
            res.score_breakdown.delivery_strength +
            res.score_breakdown.breakout_quality +
            res.score_breakdown.institutional +
            res.score_breakdown.exhaustion_adjustment
        )
        assert abs(res.bem_score - round(calc_sum, 1)) <= 0.2


def test_bem_confidence_downgrade_when_delivery_missing(synthetic_uptrend_df):
    """When delivery data is missing, confidence must be downgraded to Medium with clear notes."""
    df_no_delivery = synthetic_uptrend_df.drop(columns=['delivery_pct'])
    input_data = StockDataInput(symbol="NODELIV", df=df_no_delivery)
    res = BEM100Engine.analyze(input_data)

    assert res.delivery_strength.delivery_available is False
    assert res.confidence == ConfidenceLevel.MEDIUM
    assert any("Delivery data N/A" in note for note in res.data_confidence_notes)


def test_bem_confidence_downgrade_on_short_history():
    """History < 30 bars must trigger ConfidenceLevel.LOW."""
    short_df = pd.DataFrame({
        "open": [100.0] * 15,
        "high": [102.0] * 15,
        "low": [98.0] * 15,
        "close": [101.0] * 15,
        "volume": [10000.0] * 15
    })
    input_data = StockDataInput(symbol="SHORT", df=short_df)
    res = BEM100Engine.analyze(input_data)

    assert res.confidence == ConfidenceLevel.LOW
    assert any("Short trading history" in note for note in res.data_confidence_notes)
