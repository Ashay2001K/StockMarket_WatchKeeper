"""
Unit tests for ActionEngine.
Verifies action state determination, stop-loss calculations, multi-tier targets, and R:R ratios.
"""

import pytest
import pandas as pd
import numpy as np
from bem_engine.action_engine import ActionEngine
from bem_engine.types import (
    ActionState,
    BreakoutQualityResult,
    MomentumExhaustionResult,
    ChaseAlertResult,
    VolumeExpansionResult,
    DeliveryStrengthResult,
)


def test_action_engine_strong_buy():
    n = 30
    prices = [100.0 + i for i in range(n)]
    df = pd.DataFrame({
        "open": prices,
        "high": [p + 2.0 for p in prices],
        "low": [p - 2.0 for p in prices],
        "close": prices,
        "volume": [100000.0] * n
    })

    breakout = BreakoutQualityResult(
        score=15.0,
        key_resistance_price=125.0,
        resistance_type="52-Week High",
        is_breakout=True,
        is_testing_resistance=False,
        distance_to_resistance_pct=3.0
    )
    exhaustion = MomentumExhaustionResult(
        exhaustion_score=3.0,
        bem_contribution=12.0,
        return_2d=3.0,
        return_5d=6.0,
        return_10d=10.0,
        pct_above_20_dma=4.0,
        pct_above_50_dma=8.0,
        rsi_14=63.0,
        consecutive_up_days=2,
        parabolic_volume_tapering=False,
        is_parabolic=False
    )
    chase = ChaseAlertResult(is_chase_risk=False, severity="NONE")
    vol = VolumeExpansionResult(
        score=20.0, current_volume=200000.0, volume_sma_5=150000.0, volume_sma_20=100000.0,
        volume_ratio_20d=2.0, is_volume_expanding=True, distribution_detected=False
    )
    deliv = DeliveryStrengthResult(
        score=15.0, current_delivery_pct=65.0, delivery_sma_5=55.0, delivery_sma_20=50.0,
        delivery_available=True, distribution_flag=False
    )

    setup = ActionEngine.evaluate(
        df=df,
        bem_score=88.0,
        breakout=breakout,
        exhaustion=exhaustion,
        chase_alert=chase,
        volume_res=vol,
        delivery_res=deliv
    )

    assert setup.action_state == ActionState.STRONG_BUY
    assert setup.stop_loss < setup.current_price
    assert setup.target_1 > setup.current_price
    assert setup.target_2 > setup.target_1
    assert setup.stretch_target > setup.target_2
    assert setup.risk_reward_ratio_t2 >= 1.5


def test_action_engine_avoid_on_distribution():
    n = 30
    prices = [100.0] * n
    df = pd.DataFrame({
        "open": prices,
        "high": [102.0] * n,
        "low": [98.0] * n,
        "close": prices,
        "volume": [100000.0] * n
    })

    vol = VolumeExpansionResult(
        score=5.0, current_volume=300000.0, volume_sma_5=200000.0, volume_sma_20=100000.0,
        volume_ratio_20d=3.0, is_volume_expanding=True, distribution_detected=True
    )
    deliv = DeliveryStrengthResult(
        score=5.0, current_delivery_pct=60.0, delivery_sma_5=50.0, delivery_sma_20=45.0,
        delivery_available=True, distribution_flag=True
    )
    breakout = BreakoutQualityResult(
        score=3.0, key_resistance_price=110.0, resistance_type="20-Day High",
        is_breakout=False, is_testing_resistance=False, distance_to_resistance_pct=-10.0
    )
    exhaustion = MomentumExhaustionResult(
        exhaustion_score=5.0, bem_contribution=10.0, return_2d=-3.0, return_5d=-5.0,
        return_10d=-8.0, pct_above_20_dma=-5.0, pct_above_50_dma=-8.0, rsi_14=42.0,
        consecutive_up_days=0, parabolic_volume_tapering=False, is_parabolic=False
    )
    chase = ChaseAlertResult(is_chase_risk=False, severity="NONE")

    setup = ActionEngine.evaluate(
        df=df,
        bem_score=42.0,
        breakout=breakout,
        exhaustion=exhaustion,
        chase_alert=chase,
        volume_res=vol,
        delivery_res=deliv
    )

    assert setup.action_state == ActionState.AVOID
