"""
10%+ 2-Week Momentum Potential Engine.
Produces an independent probability estimate for a +10% move within 10-14 trading sessions,
synthesizing ATR capacity, breakout state, volume expansion, delivery backing, and exhaustion.
"""

from bem_engine.types import (
    PotentialLevel,
    MomentumPotentialResult,
    BreakoutQualityResult,
    VolumeExpansionResult,
    DeliveryStrengthResult,
    MomentumExhaustionResult,
    MarketRegimeResult,
    MarketRegime
)


class MomentumPotentialEngine:
    """
    Estimates probability of a 10%+ upward swing over a 2-week window.
    Output: High / Medium / Low + calibrated probability percentage.
    """

    @staticmethod
    def estimate(
        current_price: float,
        atr_14: float,
        breakout: BreakoutQualityResult,
        volume_res: VolumeExpansionResult,
        delivery_res: DeliveryStrengthResult,
        exhaustion: MomentumExhaustionResult,
        regime: MarketRegimeResult
    ) -> MomentumPotentialResult:
        # Base probability baseline: 35%
        prob = 35.0

        # 1. ATR Volatility Capacity
        atr_pct = (atr_14 / current_price) * 100.0 if current_price > 0 else 2.0
        # If daily ATR is >= 2.5%, a 10% move over 10 sessions is easily within standard volatility bands
        if atr_pct >= 3.0:
            prob += 15.0
        elif atr_pct >= 2.0:
            prob += 10.0
        elif atr_pct < 1.2:
            prob -= 10.0  # Slow mover

        # 2. Breakout Status
        if breakout.is_breakout and breakout.score >= 13.0:
            prob += 18.0
        elif breakout.is_testing_resistance:
            prob += 10.0

        # 3. Volume Expansion
        if volume_res.is_volume_expanding:
            prob += 12.0
        elif volume_res.volume_ratio_20d < 0.8:
            prob -= 8.0

        # 4. Delivery Strength
        if delivery_res.delivery_available and delivery_res.current_delivery_pct:
            if delivery_res.current_delivery_pct >= 45.0:
                prob += 8.0
            elif delivery_res.current_delivery_pct < 25.0:
                prob -= 5.0

        # 5. Exhaustion Penalty (Overextended stocks have high odds of mean-reverting rather than surging another 10%)
        if exhaustion.exhaustion_score >= 12.0:
            prob -= 30.0
        elif exhaustion.exhaustion_score >= 8.0:
            prob -= 15.0
        elif exhaustion.exhaustion_score <= 3.0:
            prob += 8.0  # Fresh unexhausted springboard

        # 6. Distribution Penalty
        if volume_res.distribution_detected or delivery_res.distribution_flag:
            prob -= 25.0

        # 7. Market Regime
        if regime.regime == MarketRegime.RISK_OFF:
            prob -= 10.0
        elif regime.regime == MarketRegime.RISK_ON:
            prob += 5.0

        # Clamp between 10% and 88% (never claim 100% or 0% certainty in financial markets)
        final_prob = int(max(10.0, min(88.0, round(prob))))

        if final_prob >= 65:
            level = PotentialLevel.HIGH
            narrative = f"{final_prob}% model estimate — High probability of +10% move over 2-week horizon based on fresh volatility & expansion."
        elif final_prob >= 45:
            level = PotentialLevel.MEDIUM
            narrative = f"{final_prob}% model estimate — Moderate setup; depends on breakout follow-through and broader market support."
        else:
            level = PotentialLevel.LOW
            narrative = f"{final_prob}% model estimate — Low probability; constrained by exhaustion, low volatility, or distribution."

        return MomentumPotentialResult(
            level=level,
            probability_pct=final_prob,
            narrative=narrative
        )
