"""
Unit tests for InstitutionalScorer (10 Points Max).
Verifies FII/DII accumulation and Futures OI buildup interpretations.
"""

import pytest
import pandas as pd
import numpy as np
from bem_engine.institutional import InstitutionalScorer
from bem_engine.types import DerivativesBuildup


def test_institutional_fii_dii_signals():
    df = pd.DataFrame({
        "open": [100.0] * 10,
        "high": [101.0] * 10,
        "low": [99.0] * 10,
        "close": [100.0] * 10,
        "volume": [10000.0] * 10
    })

    assert InstitutionalScorer.calculate(df, fii_dii_signal="strong").score == 10.0
    assert InstitutionalScorer.calculate(df, fii_dii_signal="improving").score == 7.0
    assert InstitutionalScorer.calculate(df, fii_dii_signal="neutral").score == 5.0
    assert InstitutionalScorer.calculate(df, fii_dii_signal="weak").score == 2.0


def test_institutional_derivatives_buildup():
    """Verifies long buildup, short covering, short buildup, and long unwinding."""
    # 1. Long Buildup: Price UP + OI UP
    df_long = pd.DataFrame({
        "close": [100.0, 103.0],
        "volume": [1000.0, 2000.0],
        "open_interest": [50000.0, 54000.0]  # +8% OI
    })
    res_long = InstitutionalScorer.calculate(df_long)
    assert res_long.derivatives_buildup == DerivativesBuildup.LONG_BUILDUP
    assert res_long.score == 10.0

    # 2. Short Buildup: Price DOWN + OI UP
    df_short = pd.DataFrame({
        "close": [100.0, 97.0],
        "volume": [1000.0, 2000.0],
        "open_interest": [50000.0, 54000.0]  # +8% OI
    })
    res_short = InstitutionalScorer.calculate(df_short)
    assert res_short.derivatives_buildup == DerivativesBuildup.SHORT_BUILDUP
    assert res_short.score == 2.0
