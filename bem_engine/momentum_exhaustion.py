"""
Momentum Exhaustion Scorer (0 to 15 Points Base Scale).
Calculates exhaustion penalty and contributes (15 - Exhaustion Score) to the 100-point BEM total.
Distinguishes between a stock starting a powerful move and one that is overextended after a powerful move.
"""

from typing import List
import pandas as pd
import numpy as np
from bem_engine.types import MomentumExhaustionResult


def calculate_rsi(series: pd.Series, period: int = 14) -> float:
    """Computes standard Relative Strength Index (RSI)."""
    if len(series) < period + 1:
        return 50.0
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Standard Exponential / Wilder's Smoothing for RSI
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    last_gain = float(avg_gain.iloc[-1])
    last_loss = float(avg_loss.iloc[-1])

    if last_loss == 0:
        return 100.0 if last_gain > 0 else 50.0
    rs = last_gain / last_loss
    return float(100.0 - (100.0 / (1.0 + rs)))


class ExhaustionScorer:
    """
    Evaluates momentum overextension:
    - Base Exhaustion Score: 0 (Fresh / Unexhausted) to 15 (Extreme Parabolic / Vertical Blow-off)
    - Contribution to BEM: (15 - Exhaustion Score)
      - Normal trend: 0-2 exhaustion -> +13 to +15 pts
      - Strong but orderly trend: 3-5 exhaustion -> +10 to +12 pts
      - > 15% in 10 sessions: 6-8 exhaustion -> +7 to +9 pts
      - > 20% in 10 sessions: 9-11 exhaustion -> +4 to +6 pts
      - > 25% in 10 sessions + >10% over 20 DMA: 12-13 exhaustion -> +2 to +3 pts
      - Vertical/parabolic rise, repeated upper circuits, RSI > 85: 14-15 exhaustion -> 0 to +1 pt
    """

    @staticmethod
    def calculate(df: pd.DataFrame) -> MomentumExhaustionResult:
        notes: List[str] = []
        n = len(df)
        if n == 0:
            raise ValueError("DataFrame cannot be empty.")

        close = df['close']
        volume = df['volume']
        curr_price = float(close.iloc[-1])

        # Short-term returns
        ret_2d = ((curr_price - float(close.iloc[-3])) / float(close.iloc[-3])) * 100.0 if n >= 3 else 0.0
        ret_5d = ((curr_price - float(close.iloc[-6])) / float(close.iloc[-6])) * 100.0 if n >= 6 else 0.0
        ret_10d = ((curr_price - float(close.iloc[-11])) / float(close.iloc[-11])) * 100.0 if n >= 11 else 0.0

        # Moving Averages
        dma_20 = float(close.rolling(window=min(20, n)).mean().iloc[-1])
        dma_50 = float(close.rolling(window=min(50, n)).mean().iloc[-1])

        pct_above_20dma = ((curr_price - dma_20) / dma_20) * 100.0 if dma_20 > 0 else 0.0
        pct_above_50dma = ((curr_price - dma_50) / dma_50) * 100.0 if dma_50 > 0 else 0.0

        # RSI (14)
        rsi = calculate_rsi(close, period=14)

        # Consecutive Up Days
        consecutive_up = 0
        for i in range(1, min(10, n)):
            if float(close.iloc[-i]) > float(close.iloc[-i-1]):
                consecutive_up += 1
            else:
                break

        # Parabolic Volume Tapering: Price continues up over last 3 sessions, but volume strictly declining
        parabolic_volume_tapering = False
        if n >= 4:
            c1, c2, c3 = float(close.iloc[-1]), float(close.iloc[-2]), float(close.iloc[-3])
            v1, v2, v3 = float(volume.iloc[-1]), float(volume.iloc[-2]), float(volume.iloc[-3])
            if c1 > c2 > c3 and v1 < v2 < v3 and ret_5d > 8.0:
                parabolic_volume_tapering = True
                notes.append("Volume Tapering: Price advancing on shrinking volume (exhaustion divergence).")

        # Base Exhaustion Calculation according to prompt specification table
        if ret_10d > 25.0 and pct_above_20dma > 10.0:
            raw_exhaustion = 12.5
            notes.append(f"Severely Extended: +{ret_10d:.1f}% in 10 sessions and {pct_above_20dma:.1f}% above 20 DMA.")
        elif ret_10d > 20.0:
            raw_exhaustion = 10.0
            notes.append(f"Rapid Acceleration: +{ret_10d:.1f}% in 10 sessions.")
        elif ret_10d > 15.0:
            raw_exhaustion = 7.0
            notes.append(f"Strong 10-session move (+{ret_10d:.1f}%).")
        elif ret_10d > 5.0:
            raw_exhaustion = 4.0
            notes.append("Orderly trend advance.")
        else:
            raw_exhaustion = 1.0
            notes.append("Fresh, unexhausted momentum base.")

        # Vertical Parabolic Blow-off (14-15 pts):
        # Requires true high-velocity surge (>20% in 10d or >15% in 5d or >8% in 2d)
        # COMBINED with extreme overbought signals (RSI > 82 or upper circuits / extension > 15% above 20 DMA)
        high_velocity = (ret_10d > 20.0 or ret_5d > 15.0 or ret_2d > 8.0)
        extreme_condition = (rsi > 82.0 or pct_above_20dma > 15.0 or (consecutive_up >= 5 and ret_5d > 15.0))

        if high_velocity and extreme_condition:
            raw_exhaustion = max(raw_exhaustion, 14.5)
            notes.append(f"Vertical blow-off condition: Surge with RSI {rsi:.1f}, {pct_above_20dma:.1f}% above 20 DMA.")

        if parabolic_volume_tapering and high_velocity:
            raw_exhaustion = min(15.0, raw_exhaustion + 1.5)

        # Cap exhaustion score strictly between 0 and 15
        exhaustion_score = round(max(0.0, min(15.0, raw_exhaustion)), 2)
        bem_contribution = round(15.0 - exhaustion_score, 2)
        is_parabolic = exhaustion_score >= 12.0

        return MomentumExhaustionResult(
            exhaustion_score=exhaustion_score,
            bem_contribution=bem_contribution,
            return_2d=round(ret_2d, 2),
            return_5d=round(ret_5d, 2),
            return_10d=round(ret_10d, 2),
            pct_above_20_dma=round(pct_above_20dma, 2),
            pct_above_50_dma=round(pct_above_50dma, 2),
            rsi_14=round(rsi, 2),
            consecutive_up_days=consecutive_up,
            parabolic_volume_tapering=parabolic_volume_tapering,
            is_parabolic=is_parabolic,
            notes=notes
        )
