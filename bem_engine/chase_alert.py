"""
Chase Alert Engine.
Detects high-velocity overextension and divergence, preventing retail FOMO and poor risk/reward entries.
"""

from typing import Optional
from bem_engine.types import ChaseAlertResult, MomentumExhaustionResult, VolumeExpansionResult


class ChaseAlertEngine:
    """
    Evaluates whether an entry carries high chase risk:
    Condition for HIGH CHASE RISK / DO NOT CHASE:
      (>= 8% rise in 2 sessions OR >= 15% rise in 5 sessions OR >= 25% rise in 10 sessions)
      AND
      (Price is >= 10% above 20 DMA OR volume is declining while price advances).
    """

    RECOMMENDED_BLUEPRINT = (
        "Consolidation -> Volume Contraction -> Support Formation -> Breakout -> Volume Expansion."
    )

    @classmethod
    def evaluate(
        cls,
        exhaustion: MomentumExhaustionResult,
        volume_res: VolumeExpansionResult
    ) -> ChaseAlertResult:
        # Check velocity trigger
        velocity_trigger = (
            exhaustion.return_2d >= 8.0 or
            exhaustion.return_5d >= 15.0 or
            exhaustion.return_10d >= 25.0
        )

        # Check extension or volume tapering trigger
        extension_trigger = exhaustion.pct_above_20_dma >= 10.0
        volume_tapering_trigger = exhaustion.parabolic_volume_tapering

        if velocity_trigger and (extension_trigger or volume_tapering_trigger):
            reasons = []
            if exhaustion.return_2d >= 8.0:
                reasons.append(f"+{exhaustion.return_2d:.1f}% surge in 2 sessions")
            elif exhaustion.return_5d >= 15.0:
                reasons.append(f"+{exhaustion.return_5d:.1f}% surge in 5 sessions")
            elif exhaustion.return_10d >= 25.0:
                reasons.append(f"+{exhaustion.return_10d:.1f}% surge in 10 sessions")

            if extension_trigger:
                reasons.append(f"extended {exhaustion.pct_above_20_dma:.1f}% above 20 DMA")
            if volume_tapering_trigger:
                reasons.append("diverging volume contraction on higher prices")

            reason_str = "DO NOT CHASE — " + " with ".join(reasons) + "."
            return ChaseAlertResult(
                is_chase_risk=True,
                severity="HIGH",
                reason=reason_str,
                recommended_strategy=cls.RECOMMENDED_BLUEPRINT
            )

        elif extension_trigger and exhaustion.exhaustion_score >= 8.0:
            return ChaseAlertResult(
                is_chase_risk=True,
                severity="MODERATE",
                reason=f"Caution: Extended {exhaustion.pct_above_20_dma:.1f}% above 20 DMA. Prefer waiting for a dip.",
                recommended_strategy="Wait for pullback towards 20 DMA support."
            )

        return ChaseAlertResult(
            is_chase_risk=False,
            severity="NONE",
            reason=None,
            recommended_strategy="Healthy technical base for structured entries."
        )
