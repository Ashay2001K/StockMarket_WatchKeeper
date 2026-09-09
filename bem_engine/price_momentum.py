"""
Price Momentum Scorer (25 Points Max).
Evaluates 20-day return, 50-day return, Relative Strength vs Nifty 50, Moving Average alignment, and 52W high proximity.
"""

from typing import Optional, List
import pandas as pd
import numpy as np
from bem_engine.types import PriceMomentumResult


class PriceMomentumScorer:
    """
    Computes Price Momentum Score (Max 25 pts):
    - 20-day return: max 8 pts
    - 50-day return: max 5 pts
    - Relative Strength vs Nifty 50: max 5 pts
    - Moving Average Alignment: max 4 pts
    - Proximity to 52-Week High: max 3 pts
    """

    @staticmethod
    def calculate(
        df: pd.DataFrame,
        nifty_df: Optional[pd.DataFrame] = None
    ) -> PriceMomentumResult:
        notes: List[str] = []
        close = df['close']
        n = len(close)

        if n == 0:
            raise ValueError("DataFrame cannot be empty.")

        current_price = float(close.iloc[-1])

        # 1. 20-Day Price Return (8 pts)
        if n >= 21:
            price_20d_ago = float(close.iloc[-21])
            return_20d = ((current_price - price_20d_ago) / price_20d_ago) * 100.0
        else:
            price_start = float(close.iloc[0])
            return_20d = ((current_price - price_start) / price_start) * 100.0
            notes.append(f"Insufficient history for full 20d return ({n} bars available).")

        if return_20d > 15.0:
            pts_20d = 8.0
        elif return_20d >= 10.0:
            pts_20d = 6.0
        elif return_20d >= 5.0:
            pts_20d = 4.0
        elif return_20d >= 0.0:
            pts_20d = 2.0
        else:
            pts_20d = 0.0

        # 2. 50-Day Price Return (5 pts)
        if n >= 51:
            price_50d_ago = float(close.iloc[-51])
            return_50d = ((current_price - price_50d_ago) / price_50d_ago) * 100.0
        else:
            price_start = float(close.iloc[0])
            return_50d = ((current_price - price_start) / price_start) * 100.0
            notes.append(f"Insufficient history for full 50d return ({n} bars available).")

        if return_50d > 25.0:
            pts_50d = 5.0
        elif return_50d >= 15.0:
            pts_50d = 4.0
        elif return_50d >= 5.0:
            pts_50d = 3.0
        elif return_50d >= 0.0:
            pts_50d = 1.0
        else:
            pts_50d = 0.0

        # 3. Relative Strength vs Nifty 50 (5 pts)
        rs_vs_nifty = 0.0
        pts_rs = 0.0
        if nifty_df is not None and len(nifty_df) >= 21:
            nifty_close = nifty_df['close']
            nifty_curr = float(nifty_close.iloc[-1])
            nifty_20d_ago = float(nifty_close.iloc[-21])
            nifty_20d_ret = ((nifty_curr - nifty_20d_ago) / nifty_20d_ago) * 100.0
            rs_vs_nifty = return_20d - nifty_20d_ret

            if rs_vs_nifty > 10.0:
                pts_rs = 5.0
            elif rs_vs_nifty >= 5.0:
                pts_rs = 4.0
            elif rs_vs_nifty >= 0.0:
                pts_rs = 2.0
            else:
                pts_rs = 0.0
            notes.append(f"RS vs Nifty 50: {rs_vs_nifty:+.2f}%")
        else:
            # Fallback when benchmark is missing: award neutral/proportional based on stock return
            if return_20d > 10.0:
                pts_rs = 3.5
            elif return_20d >= 0.0:
                pts_rs = 2.0
            else:
                pts_rs = 0.0
            notes.append("Nifty 50 data not provided; estimated RS.")

        # 4. Price relative to Moving Averages (4 pts)
        # DMA calculations
        dma_20 = float(close.rolling(window=min(20, n)).mean().iloc[-1])
        dma_50 = float(close.rolling(window=min(50, n)).mean().iloc[-1])
        dma_100 = float(close.rolling(window=min(100, n)).mean().iloc[-1])
        dma_200 = float(close.rolling(window=min(200, n)).mean().iloc[-1])

        if current_price > dma_20 > dma_50 > dma_100:
            pts_ma = 4.0
            notes.append("Bullish MA Stack: Price > 20 DMA > 50 DMA > 100 DMA")
        elif current_price > dma_20 and current_price > dma_50:
            pts_ma = 3.0
            notes.append("Above 20 & 50 DMA")
        elif current_price > dma_20:
            pts_ma = 2.0
            notes.append("Above 20 DMA only")
        elif current_price > dma_50:
            pts_ma = 1.0
            notes.append("Above 50 DMA only")
        else:
            pts_ma = 0.0
            notes.append("Bearish: Price below 20 and 50 DMA")

        # 5. Proximity to 52-Week High (3 pts)
        high_window = min(252, n)
        high_52w = float(df['high'].rolling(window=high_window).max().iloc[-1])
        if high_52w > 0:
            pct_below_52w = ((high_52w - current_price) / high_52w) * 100.0
        else:
            pct_below_52w = 0.0

        if pct_below_52w <= 3.0:
            pts_prox = 3.0
            notes.append(f"Within {pct_below_52w:.1f}% of 52-Week High")
        elif pct_below_52w <= 7.0:
            pts_prox = 2.0
            notes.append(f"Within {pct_below_52w:.1f}% of 52-Week High")
        elif pct_below_52w <= 15.0:
            pts_prox = 1.0
        else:
            pts_prox = 0.0

        total_score = min(25.0, pts_20d + pts_50d + pts_rs + pts_ma + pts_prox)

        return PriceMomentumResult(
            score=round(total_score, 2),
            return_20d=round(return_20d, 2),
            return_20d_pts=round(pts_20d, 2),
            return_50d=round(return_50d, 2),
            return_50d_pts=round(pts_50d, 2),
            rs_vs_nifty_20d=round(rs_vs_nifty, 2),
            rs_pts=round(pts_rs, 2),
            ma_alignment_pts=round(pts_ma, 2),
            dma_20=round(dma_20, 2),
            dma_50=round(dma_50, 2),
            dma_100=round(dma_100, 2),
            dma_200=round(dma_200, 2),
            proximity_52w_high_pct=round(pct_below_52w, 2),
            proximity_pts=round(pts_prox, 2),
            notes=notes
        )
