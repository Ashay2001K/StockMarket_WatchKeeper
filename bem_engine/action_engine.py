"""
Action Engine.
Generates structured trade setups with Preferred Buy Zones, Breakout Entry,
ATR-based/Swing Stop Loss (strictly non-arbitrary), Multi-tier Targets, and Risk/Reward ratios.
"""

from typing import Tuple
import pandas as pd
import numpy as np
from bem_engine.types import (
    ActionState,
    TradeSetup,
    BreakoutQualityResult,
    MomentumExhaustionResult,
    ChaseAlertResult,
    VolumeExpansionResult,
    DeliveryStrengthResult,
)


def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    """Calculates standard Average True Range (ATR)."""
    n = len(df)
    if n < 2:
        curr_price = float(df['close'].iloc[-1])
        return max(curr_price * 0.02, 1.0)

    high = df['high']
    low = df['low']
    close = df['close']
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr_series = tr.rolling(window=min(period, n), min_periods=1).mean()
    atr_val = float(atr_series.iloc[-1])
    return max(atr_val, float(close.iloc[-1]) * 0.01)


class ActionEngine:
    """
    Synthesizes momentum score, breakout quality, exhaustion, and chase flags
    into clear, actionable states and mathematically sound price boundaries.
    """

    @classmethod
    def evaluate(
        cls,
        df: pd.DataFrame,
        bem_score: float,
        breakout: BreakoutQualityResult,
        exhaustion: MomentumExhaustionResult,
        chase_alert: ChaseAlertResult,
        volume_res: VolumeExpansionResult,
        delivery_res: DeliveryStrengthResult
    ) -> TradeSetup:
        close = df['close']
        curr_price = float(close.iloc[-1])
        dma_20 = float(close.rolling(window=min(20, len(df))).mean().iloc[-1])
        dma_50 = float(close.rolling(window=min(50, len(df))).mean().iloc[-1])
        atr = calculate_atr(df, period=14)

        # True distribution requires heavy volume expansion on falling price
        # OR confirmed delivery distribution with volume confirmation
        is_true_distribution = (
            volume_res.distribution_detected or
            (delivery_res.distribution_flag and volume_res.volume_ratio_20d >= 1.2)
        )

        # 1. Determine Action State
        if is_true_distribution:
            action = ActionState.AVOID
            rationale = "Heavy distribution detected on falling price. Capital preservation priority."
        elif chase_alert.severity == "HIGH":
            action = ActionState.DONT_CHASE
            rationale = chase_alert.reason or "Extended velocity. Wait for volume contraction base."
        elif bem_score >= 80.0 and exhaustion.exhaustion_score <= 5.0:
            if breakout.is_breakout:
                action = ActionState.STRONG_BUY
                rationale = f"High BEM ({bem_score:.0f}) with confirmed breakout above ₹{breakout.key_resistance_price:.2f} and low exhaustion."
            elif breakout.is_testing_resistance:
                action = ActionState.BUY_ON_BREAKOUT
                rationale = f"Pressing against resistance ₹{breakout.key_resistance_price:.2f}. Prepare entry upon confirmation."
            else:
                action = ActionState.STRONG_BUY
                rationale = f"Robust overall momentum ({bem_score:.0f}/100) and healthy trend structure."
        elif bem_score >= 65.0 and exhaustion.exhaustion_score <= 5.0 and abs(curr_price - dma_20) / dma_20 <= 0.04 and curr_price >= dma_50:
            action = ActionState.BUY_ON_DIP
            rationale = f"Consolidation pullback near 20 DMA support (₹{dma_20:.2f}) with reset exhaustion ({exhaustion.exhaustion_score:.1f})."
        elif bem_score >= 70.0 and exhaustion.exhaustion_score <= 7.0:
            if breakout.is_testing_resistance or breakout.is_breakout:
                action = ActionState.BUY_ON_BREAKOUT
                rationale = f"Testing breakout zone ₹{breakout.key_resistance_price:.2f}."
            else:
                action = ActionState.BUY
                rationale = f"Favorable momentum profile ({bem_score:.0f}/100)."
        elif bem_score >= 55.0:
            action = ActionState.WATCH
            rationale = f"Moderate momentum ({bem_score:.0f}/100). Awaiting volume/breakout trigger."
        elif bem_score >= 40.0:
            if curr_price >= dma_50:
                action = ActionState.WATCH
                rationale = f"Consolidating above 50 DMA ({bem_score:.0f}/100). Orderly volume contraction, awaiting expansion trigger."
            else:
                action = ActionState.WAIT
                rationale = f"Subdued score ({bem_score:.0f}/100). Awaiting setup."
        else:
            action = ActionState.AVOID
            rationale = f"Weak structure ({bem_score:.0f}/100). Below intermediate moving averages without momentum support."

        # 2. Compute Price Levels
        recent_low = float(df['low'].tail(min(10, len(df))).min()) if len(df) >= 2 else curr_price - 1.5 * atr
        atr_stop = curr_price - (1.5 * atr)

        stop_loss = max(recent_low, atr_stop)
        if stop_loss >= curr_price * 0.995:
            stop_loss = curr_price - (1.5 * atr)

        stop_loss_pct = round(((curr_price - stop_loss) / curr_price) * 100.0, 2)
        risk = max(curr_price - stop_loss, 0.01)

        # Preferred Buy Zone
        buy_zone_min = round(min(curr_price, max(dma_20, curr_price - (0.8 * atr))), 2)
        buy_zone_max = round(max(curr_price, curr_price + (0.3 * atr)), 2)

        # Breakout Entry
        breakout_entry = round(max(curr_price, breakout.key_resistance_price * 1.002), 2)

        # Targets based on ATR multiples
        target_1 = round(curr_price + (1.5 * atr), 2)
        target_2 = round(curr_price + (3.0 * atr), 2)
        stretch_target = round(curr_price + (5.0 * atr), 2)

        t1_pct = round(((target_1 - curr_price) / curr_price) * 100.0, 2)
        t2_pct = round(((target_2 - curr_price) / curr_price) * 100.0, 2)
        stretch_pct = round(((stretch_target - curr_price) / curr_price) * 100.0, 2)

        rr_t1 = round((target_1 - curr_price) / risk, 2)
        rr_t2 = round((target_2 - curr_price) / risk, 2)

        return TradeSetup(
            action_state=action,
            current_price=round(curr_price, 2),
            preferred_buy_zone_min=buy_zone_min,
            preferred_buy_zone_max=buy_zone_max,
            breakout_entry_price=breakout_entry,
            stop_loss=round(stop_loss, 2),
            stop_loss_pct=stop_loss_pct,
            target_1=target_1,
            target_1_pct=t1_pct,
            target_2=target_2,
            target_2_pct=t2_pct,
            stretch_target=stretch_target,
            stretch_target_pct=stretch_pct,
            risk_reward_ratio_t1=rr_t1,
            risk_reward_ratio_t2=rr_t2,
            rationale=rationale
        )
