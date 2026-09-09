"""
Synthetic Test Suite for Canonical Market Scenarios.
Explicitly verifies:
1. Fresh Breakout Setup (High BEM, low exhaustion, breakout confirmed).
2. Overextended Momentum Stock (High raw momentum, high exhaustion, BEM suppressed, Chase Alert active).
3. High-Volume Distribution Trap (Price down + volume up -> distribution flagged, Action Avoid).
4. Consolidation Reset (Exhaustion drops while BEM remains healthy, Buy on Dip).
"""

import pytest
import pandas as pd
import numpy as np
from bem_engine import BEM100Engine, StockDataInput, ActionState


def test_scenario_1_fresh_breakout_setup():
    """
    Scenario 1: Fresh Breakout Setup.
    Stock has a solid intermediate base (460 to 500), consolidates tightly around 500,
    then breaks out powerfully to 525 (+5% surge through 505 resistance)
    on 2.2x volume expansion with 55% delivery backing.
    Expected: BEM >= 80, Exhaustion <= 5, Action in [Strong Buy, Buy on Breakout], Chase Alert False.
    """
    n = 60
    prices = [460.0 + (1.0 * i) for i in range(40)]
    prices += [500.0 + (1.5 * np.sin(i / 2.0)) for i in range(19)]
    prices.append(525.0)

    volumes = [100000.0] * (n - 1) + [220000.0]  # 2.2x volume expansion
    deliveries = [35.0] * (n - 1) + [55.0]       # 55% delivery backing

    opens = [p - 1.0 for p in prices[:-1]] + [506.0]
    highs = [p + 2.0 for p in prices[:-1]] + [527.0]
    lows = [p - 2.0 for p in prices[:-1]] + [504.0]

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": prices,
        "volume": volumes,
        "delivery_pct": deliveries
    })

    nifty_df = pd.DataFrame({
        "close": [22000.0 * (1.0 + 0.0005 * i) for i in range(n)]
    })

    stock_input = StockDataInput(
        symbol="FRESHBREAK",
        df=df,
        nifty_df=nifty_df,
        fii_dii_signal="strong"
    )

    result = BEM100Engine.analyze(stock_input)

    assert result.bem_score >= 80.0, f"Expected BEM >= 80, got {result.bem_score}"
    assert result.exhaustion.exhaustion_score <= 5.0, f"Expected low exhaustion <= 5, got {result.exhaustion.exhaustion_score}"
    assert result.chase_alert.is_chase_risk is False
    assert result.breakout_quality.is_breakout is True
    assert result.volume_expansion.is_volume_expanding is True
    assert result.action in [ActionState.STRONG_BUY, ActionState.BUY_ON_BREAKOUT]
    assert result.momentum_potential.level.value in ["High", "Medium"]


def test_scenario_2_overextended_momentum_stock():
    """
    Scenario 2: Overextended Momentum Stock.
    Stock has exploded vertically (+35% in 10 sessions), sitting 18% above its 20 DMA.
    Volume is tapering on the final push.
    Expected: Raw momentum high, Exhaustion >= 12, BEM suppressed, Chase Alert ACTIVE (DO NOT CHASE).
    """
    n = 60
    base = 1000.0
    # Flat base for 49 days, then explosive vertical surge in final 11 days
    prices = [base] * 49
    for i in range(11):
        prices.append(base * (1.0 + 0.035 * (i + 1)))

    # Declining volume during final 4 sessions (volume tapering)
    volumes = [100000.0] * 56 + [90000.0, 75000.0, 55000.0, 35000.0]
    deliveries = [30.0] * n

    opens = [p * 0.99 for p in prices]
    highs = [p * 1.02 for p in prices]
    lows = [p * 0.98 for p in prices]

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": prices,
        "volume": volumes,
        "delivery_pct": deliveries
    })

    stock_input = StockDataInput(symbol="EXTENDED", df=df)
    result = BEM100Engine.analyze(stock_input)

    assert result.exhaustion.exhaustion_score >= 12.0, f"Expected Exhaustion >= 12, got {result.exhaustion.exhaustion_score}"
    assert result.exhaustion.bem_contribution <= 3.0, "Exhaustion penalty must suppress BEM"
    assert result.chase_alert.is_chase_risk is True
    assert result.chase_alert.severity == "HIGH"
    assert "DO NOT CHASE" in result.chase_alert.reason
    assert result.action == ActionState.DONT_CHASE


def test_scenario_3_high_volume_distribution_trap():
    """
    Scenario 3: High-Volume Distribution Trap.
    Stock drops sharply (-6%) on massive 2.5x volume and 58% delivery.
    Expected: Distribution flagged, Volume and Delivery capped, Action = Avoid.
    """
    n = 60
    prices = [800.0] * (n - 1) + [752.0]  # -6% cliff drop
    volumes = [100000.0] * (n - 1) + [250000.0]  # 2.5x volume dumping
    deliveries = [30.0] * (n - 1) + [58.0]        # High delivery sell-off

    opens = [800.0] * (n - 1) + [802.0]
    highs = [805.0] * (n - 1) + [803.0]
    lows = [795.0] * (n - 1) + [748.0]

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": prices,
        "volume": volumes,
        "delivery_pct": deliveries
    })

    stock_input = StockDataInput(symbol="DISTRIP", df=df)
    result = BEM100Engine.analyze(stock_input)

    assert result.volume_expansion.distribution_detected is True
    assert result.delivery_strength.distribution_flag is True
    assert result.volume_expansion.score <= 5.0
    assert result.delivery_strength.score <= 5.0
    assert result.action == ActionState.AVOID
    assert "distribution" in result.trade_setup.rationale.lower()


def test_scenario_4_consolidation_reset():
    """
    Scenario 4: Consolidation Reset.
    Stock had a strong advance from 100 to 142 over 54 days, then pulled back gently
    for 6 sessions from 142 to 137 (touching rising 20 DMA support) on light contracted volume.
    Exhaustion has reset to low levels (<= 4), and overall momentum remains healthy.
    Expected: Exhaustion low (<= 4), BEM healthy, Action in [Buy on Dip, Buy, Watch], Chase Alert quiet.
    """
    n = 60
    prices = [100.0 + (0.78 * i) for i in range(54)]
    for i in range(1, 7):
        prices.append(142.0 - (0.83 * i))

    volumes = [150000.0] * 54 + [60000.0] * 6  # Light volume on pullback
    deliveries = [30.0] * n  # Normal calm delivery on pullback

    opens = [p * 0.995 for p in prices]
    highs = [p * 1.01 for p in prices]
    lows = [p * 0.99 for p in prices]

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": prices,
        "volume": volumes,
        "delivery_pct": deliveries
    })

    stock_input = StockDataInput(
        symbol="RESETSTOCK",
        df=df,
        fii_dii_signal="improving"
    )
    result = BEM100Engine.analyze(stock_input)

    assert result.exhaustion.exhaustion_score <= 4.0, f"Exhaustion should reset, got {result.exhaustion.exhaustion_score}"
    assert result.exhaustion.bem_contribution >= 11.0
    assert result.chase_alert.is_chase_risk is False
    assert result.action in [ActionState.BUY_ON_DIP, ActionState.BUY, ActionState.WATCH]
