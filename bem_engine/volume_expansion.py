"""
Volume Expansion Scorer (20 Points Max).
Implements volume ratio brackets, volume trend, and distribution trap detection.
"""

from typing import List
import pandas as pd
import numpy as np
from bem_engine.types import VolumeExpansionResult


class VolumeExpansionScorer:
    """
    Computes Volume Expansion Score (Max 20 pts):
    - Volume / 20 DMA Ratio:
      < 0.75x: 0 pts
      0.75 - 1.00x: 5 pts
      1.00 - 1.25x: 10 pts
      1.25 - 1.50x: 14 pts
      >= 1.50x: 20 pts
    - Distribution Rule:
      If Close < Open (or Day Change < 0) and Volume >= 1.5x, flag as Potential Distribution,
      cap score at 5 pts and flag distribution.
    """

    @staticmethod
    def calculate(df: pd.DataFrame) -> VolumeExpansionResult:
        notes: List[str] = []
        n = len(df)
        if n == 0:
            raise ValueError("DataFrame cannot be empty.")

        volume = df['volume']
        close = df['close']
        open_p = df['open'] if 'open' in df.columns else close

        curr_vol = float(volume.iloc[-1])
        curr_close = float(close.iloc[-1])
        curr_open = float(open_p.iloc[-1])
        prev_close = float(close.iloc[-2]) if n >= 2 else curr_close
        day_ret_pct = ((curr_close - prev_close) / prev_close) * 100.0 if prev_close > 0 else 0.0

        # Moving Averages
        vol_sma_5 = float(volume.rolling(window=min(5, n)).mean().iloc[-1])
        vol_sma_20 = float(volume.rolling(window=min(20, n)).mean().iloc[-1])

        if vol_sma_20 > 0:
            vol_ratio = curr_vol / vol_sma_20
        else:
            vol_ratio = 1.0

        # Base scoring from ratio
        if vol_ratio >= 1.50:
            base_score = 20.0
            is_expanding = True
        elif vol_ratio >= 1.25:
            base_score = 14.0
            is_expanding = False
        elif vol_ratio >= 1.00:
            base_score = 10.0
            is_expanding = False
        elif vol_ratio >= 0.75:
            base_score = 5.0
            is_expanding = False
        else:
            base_score = 0.0
            is_expanding = False

        # Volume / Price Relationship: Distribution Trap Detection
        # Price down + Volume >= 1.5x -> Distribution trap
        price_falling = (day_ret_pct < -0.5) or (curr_close < curr_open and day_ret_pct <= 0)
        distribution_detected = False

        if vol_ratio >= 1.50 and price_falling:
            distribution_detected = True
            # Penalize: Cap score at 5 pts
            score = min(base_score, 5.0)
            notes.append("DISTRIBUTION WARNING: Heavy volume (>=1.5x) on falling price.")
        elif is_expanding and not price_falling:
            score = base_score
            notes.append(f"Bullish Volume Expansion ({vol_ratio:.2f}x 20 DMA).")
        else:
            score = base_score
            notes.append(f"Volume Ratio: {vol_ratio:.2f}x 20 DMA.")

        # Volume trend note (5d vs 20d)
        if vol_sma_5 > vol_sma_20:
            notes.append("5-day volume average running above 20-day average.")

        return VolumeExpansionResult(
            score=round(score, 2),
            current_volume=round(curr_vol, 2),
            volume_sma_5=round(vol_sma_5, 2),
            volume_sma_20=round(vol_sma_20, 2),
            volume_ratio_20d=round(vol_ratio, 2),
            is_volume_expanding=is_expanding,
            distribution_detected=distribution_detected,
            notes=notes
        )
