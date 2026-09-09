"""
Breakout Quality Scorer (15 Points Max).
Identifies resistance levels, breakout confirmation by closing price, volume multiplier, and delivery backing.
"""

from typing import List, Tuple
import pandas as pd
import numpy as np
from bem_engine.types import BreakoutQualityResult


class BreakoutScorer:
    """
    Computes Breakout Quality Score (Max 15 pts):
    - Below resistance: 3 pts
    - Testing resistance (within 1.5% below resistance): 7 pts
    - Breakout without volume confirmation (Close > resistance, Vol < 1.5x): 9 pts
    - Breakout + >= 1.5x volume: 13 pts
    - Breakout + >= 1.5x volume + strong delivery (>= 40%): 15 pts
    """

    @staticmethod
    def calculate(
        df: pd.DataFrame,
        volume_ratio: float,
        delivery_pct: float = 0.0
    ) -> BreakoutQualityResult:
        notes: List[str] = []
        n = len(df)
        if n == 0:
            raise ValueError("DataFrame cannot be empty.")

        close = df['close']
        high = df['high']
        curr_close = float(close.iloc[-1])
        curr_high = float(high.iloc[-1])

        # Find key resistance from prior bars (excluding current bar)
        if n > 1:
            prior_df = df.iloc[:-1]
            high_20d = float(prior_df['high'].tail(min(20, len(prior_df))).max())
            high_50d = float(prior_df['high'].tail(min(50, len(prior_df))).max())
            high_52w = float(prior_df['high'].tail(min(252, len(prior_df))).max())
        else:
            high_20d = curr_high
            high_50d = curr_high
            high_52w = curr_high

        # Determine most relevant key resistance
        if curr_close >= high_52w or curr_high >= high_52w:
            resistance = high_52w
            res_type = "52-Week High"
        elif curr_close >= high_50d or curr_high >= high_50d:
            resistance = high_50d
            res_type = "50-Day High"
        else:
            resistance = high_20d
            res_type = "20-Day Swing High"

        # Check distance to resistance
        if resistance > 0:
            dist_pct = ((curr_close - resistance) / resistance) * 100.0
        else:
            dist_pct = 0.0

        is_breakout = curr_close > resistance
        # Testing resistance: within 1.5% below resistance, or intraday breach but close below
        is_testing = (not is_breakout) and (dist_pct >= -1.5 or curr_high >= resistance)

        # Scoring
        if is_breakout:
            if volume_ratio >= 1.5 and delivery_pct >= 40.0:
                score = 15.0
                notes.append(f"A+ Breakout: Closed above {res_type} with {volume_ratio:.1f}x volume & {delivery_pct:.1f}% delivery.")
            elif volume_ratio >= 1.5:
                score = 13.0
                notes.append(f"Confirmed Breakout: Closed above {res_type} with {volume_ratio:.1f}x volume expansion.")
            else:
                score = 9.0
                notes.append(f"Low-Volume Breakout: Closed above {res_type} but volume ({volume_ratio:.1f}x) lacks confirmation.")
        elif is_testing:
            score = 7.0
            notes.append(f"Testing Resistance: Pressing against {res_type} (₹{resistance:.2f}, {dist_pct:+.1f}%).")
        else:
            score = 3.0
            notes.append(f"Below Resistance: ₹{resistance:.2f} ({dist_pct:+.1f}% from current price).")

        return BreakoutQualityResult(
            score=round(score, 2),
            key_resistance_price=round(resistance, 2),
            resistance_type=res_type,
            is_breakout=is_breakout,
            is_testing_resistance=is_testing,
            distance_to_resistance_pct=round(dist_pct, 2),
            notes=notes
        )
