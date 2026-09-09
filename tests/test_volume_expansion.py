"""
Unit tests for VolumeExpansionScorer (20 Points Max).
Verifies exact volume ratio brackets and distribution trap penalties.
"""

import pytest
import pandas as pd
import numpy as np
from bem_engine.volume_expansion import VolumeExpansionScorer


@pytest.mark.parametrize("multiplier, expected_score, expected_expanding", [
    (0.50, 0.0, False),    # < 0.75x -> 0 pts
    (0.85, 5.0, False),    # 0.75 - 1.00x -> 5 pts
    (1.10, 10.0, False),   # 1.00 - 1.25x -> 10 pts
    (1.35, 14.0, False),   # 1.25 - 1.50x -> 14 pts
    (1.60, 20.0, True),    # >= 1.50x -> 20 pts
    (2.50, 20.0, True),    # >= 1.50x -> 20 pts
])
def test_volume_ratio_brackets(multiplier, expected_score, expected_expanding):
    n = 30
    base_vol = 100000.0
    volumes = [base_vol] * (n - 1) + [base_vol * multiplier]
    prices = [100.0] * n  # flat or slightly up
    # Make last day close slightly above open
    opens = [100.0] * (n - 1) + [99.5]
    closes = [100.0] * (n - 1) + [101.0]

    df = pd.DataFrame({
        "open": opens,
        "high": [102.0] * n,
        "low": [99.0] * n,
        "close": closes,
        "volume": volumes
    })

    res = VolumeExpansionScorer.calculate(df)
    assert res.score == expected_score
    assert res.is_volume_expanding == expected_expanding
    assert not res.distribution_detected


def test_volume_distribution_trap():
    """When volume explodes (>= 1.5x) but price drops heavily, it must be flagged as distribution."""
    n = 30
    base_vol = 100000.0
    volumes = [base_vol] * (n - 1) + [base_vol * 2.2]  # 2.2x volume surge
    # Price plummets
    opens = [100.0] * (n - 1) + [100.0]
    closes = [100.0] * (n - 1) + [95.0]  # -5% red candle

    df = pd.DataFrame({
        "open": opens,
        "high": [101.0] * n,
        "low": [94.0] * n,
        "close": closes,
        "volume": volumes
    })

    res = VolumeExpansionScorer.calculate(df)
    assert res.distribution_detected is True
    assert res.score <= 5.0  # Capped at 5 pts penalty instead of 20
    assert any("DISTRIBUTION WARNING" in note for note in res.notes)
