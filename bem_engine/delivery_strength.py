"""
Delivery Strength Scorer (15 Points Max).
Evaluates cash delivery percentage brackets, delivery trend, and distribution warning.
"""

from typing import Optional, List
import pandas as pd
import numpy as np
from bem_engine.types import DeliveryStrengthResult


class DeliveryScorer:
    """
    Computes Delivery Strength Score (Max 15 pts):
    - Delivery Percentage Brackets:
      < 20%: 2 pts
      20 - 30%: 5 pts
      30 - 40%: 8 pts
      40 - 50%: 11 pts
      50 - 60%: 13 pts
      > 60%: 15 pts
    - Distribution Rule:
      Price falling sharply (< -1.5%) + Delivery expanding (Delivery UP) ->
      Flag as "High delivery but falling price — possible distribution" and cap score at 5 pts.
    - Fallback:
      If delivery data is missing, score defaults to 7.5 (neutral) and flags delivery_available=False.
    """

    @staticmethod
    def calculate(df: pd.DataFrame) -> DeliveryStrengthResult:
        notes: List[str] = []
        n = len(df)
        if n == 0:
            raise ValueError("DataFrame cannot be empty.")

        # Check if delivery_pct column exists and has valid values
        has_delivery = 'delivery_pct' in df.columns and df['delivery_pct'].notna().any()

        if not has_delivery:
            notes.append("N/A - delivery data unavailable from source (neutral score assigned).")
            return DeliveryStrengthResult(
                score=7.5,
                current_delivery_pct=None,
                delivery_sma_5=None,
                delivery_sma_20=None,
                delivery_available=False,
                distribution_flag=False,
                notes=notes
            )

        deliv_series = df['delivery_pct'].dropna()
        if len(deliv_series) == 0:
            notes.append("N/A - delivery data unavailable from source.")
            return DeliveryStrengthResult(
                score=7.5,
                current_delivery_pct=None,
                delivery_sma_5=None,
                delivery_sma_20=None,
                delivery_available=False,
                distribution_flag=False,
                notes=notes
            )

        curr_deliv = float(deliv_series.iloc[-1])
        if curr_deliv <= 1.0 and curr_deliv > 0.0:
            curr_deliv *= 100.0

        # Moving Averages
        deliv_sma_5 = float(deliv_series.rolling(window=min(5, len(deliv_series))).mean().iloc[-1])
        deliv_sma_20 = float(deliv_series.rolling(window=min(20, len(deliv_series))).mean().iloc[-1])
        if deliv_sma_5 <= 1.0 and deliv_sma_5 > 0.0:
            deliv_sma_5 *= 100.0
        if deliv_sma_20 <= 1.0 and deliv_sma_20 > 0.0:
            deliv_sma_20 *= 100.0

        # Base scoring from bracket
        if curr_deliv > 60.0:
            base_score = 15.0
        elif curr_deliv >= 50.0:
            base_score = 13.0
        elif curr_deliv >= 40.0:
            base_score = 11.0
        elif curr_deliv >= 30.0:
            base_score = 8.0
        elif curr_deliv >= 20.0:
            base_score = 5.0
        else:
            base_score = 2.0

        # Price check for distribution
        close = df['close']
        open_p = df['open'] if 'open' in df.columns else close
        curr_close = float(close.iloc[-1])
        curr_open = float(open_p.iloc[-1])
        prev_close = float(close.iloc[-2]) if n >= 2 else curr_close
        day_ret_pct = ((curr_close - prev_close) / prev_close) * 100.0 if prev_close > 0 else 0.0

        # True Delivery UP on Price DOWN condition:
        # Price is falling noticeably (< -1.5%) and delivery is elevated (>= 50% or >= 1.2x 20d avg)
        delivery_elevated = (curr_deliv >= 50.0) or (curr_deliv >= deliv_sma_20 * 1.2 and curr_deliv >= 35.0)
        sharp_drop = (day_ret_pct < -1.5) or (curr_close < curr_open and day_ret_pct < -1.0)
        distribution_flag = False

        if sharp_drop and delivery_elevated:
            distribution_flag = True
            score = min(base_score, 5.0)
            notes.append("DISTRIBUTION WARNING: High delivery on falling price — possible distribution.")
        elif day_ret_pct < 0:
            score = max(2.0, base_score - 2.0)
            notes.append(f"Price soft with {curr_deliv:.1f}% delivery.")
        else:
            score = base_score
            notes.append(f"Cash Delivery: {curr_deliv:.1f}%")

        if curr_deliv > deliv_sma_20 and not distribution_flag:
            notes.append(f"Delivery above 20-day average ({deliv_sma_20:.1f}%).")

        return DeliveryStrengthResult(
            score=round(score, 2),
            current_delivery_pct=round(curr_deliv, 2),
            delivery_sma_5=round(deliv_sma_5, 2),
            delivery_sma_20=round(deliv_sma_20, 2),
            delivery_available=True,
            distribution_flag=distribution_flag,
            notes=notes
        )
