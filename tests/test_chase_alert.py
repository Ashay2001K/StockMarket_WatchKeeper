"""
Unit tests for ChaseAlertEngine.
Verifies HIGH CHASE RISK / DO NOT CHASE triggers on multi-condition velocity and extension.
"""

import pytest
from bem_engine.chase_alert import ChaseAlertEngine
from bem_engine.types import MomentumExhaustionResult, VolumeExpansionResult


def test_chase_alert_triggers_on_rapid_velocity_and_extension():
    """Stock up 9% in 2 sessions and 12% above 20 DMA."""
    exhaustion = MomentumExhaustionResult(
        exhaustion_score=13.0,
        bem_contribution=2.0,
        return_2d=9.2,
        return_5d=16.0,
        return_10d=28.0,
        pct_above_20_dma=12.5,
        pct_above_50_dma=22.0,
        rsi_14=84.0,
        consecutive_up_days=5,
        parabolic_volume_tapering=False,
        is_parabolic=True,
        notes=[]
    )
    volume_res = VolumeExpansionResult(
        score=20.0,
        current_volume=200000.0,
        volume_sma_5=180000.0,
        volume_sma_20=100000.0,
        volume_ratio_20d=2.0,
        is_volume_expanding=True,
        distribution_detected=False
    )

    alert = ChaseAlertEngine.evaluate(exhaustion, volume_res)
    assert alert.is_chase_risk is True
    assert alert.severity == "HIGH"
    assert "DO NOT CHASE" in alert.reason
    assert "Consolidation -> Volume Contraction" in alert.recommended_strategy


def test_chase_alert_quiet_on_orderly_breakout():
    """Fresh breakout stock: orderly velocity (+4% in 2 sessions, 3% above 20 DMA)."""
    exhaustion = MomentumExhaustionResult(
        exhaustion_score=2.0,
        bem_contribution=13.0,
        return_2d=3.5,
        return_5d=6.0,
        return_10d=8.0,
        pct_above_20_dma=2.8,
        pct_above_50_dma=5.0,
        rsi_14=62.0,
        consecutive_up_days=2,
        parabolic_volume_tapering=False,
        is_parabolic=False,
        notes=[]
    )
    volume_res = VolumeExpansionResult(
        score=20.0,
        current_volume=250000.0,
        volume_sma_5=150000.0,
        volume_sma_20=100000.0,
        volume_ratio_20d=2.5,
        is_volume_expanding=True,
        distribution_detected=False
    )

    alert = ChaseAlertEngine.evaluate(exhaustion, volume_res)
    assert alert.is_chase_risk is False
    assert alert.severity == "NONE"
