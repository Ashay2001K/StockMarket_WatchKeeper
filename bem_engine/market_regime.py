"""
Market Regime and Sector Relative Strength Evaluator.
Evaluates broader Indian market backdrop (Nifty 50 vs 20/50/200 DMA + India VIX)
and dual-layer Relative Strength (Stock vs Nifty and Stock vs Sector).
"""

from typing import Optional, List
import pandas as pd
import numpy as np
from bem_engine.types import MarketRegimeResult, MarketRegime


class MarketRegimeEvaluator:
    """
    Evaluates market regime (Risk-On / Risk-Off / Neutral) based on:
    - Nifty 50 position relative to 20, 50, and 200 DMA
    - India VIX level (<15 = Low/Safe, 15-20 = Moderate, >20 = High/Risk-Off)
    - Sector relative outperformance
    """

    @staticmethod
    def evaluate(
        nifty_df: Optional[pd.DataFrame] = None,
        india_vix: Optional[float] = None,
        stock_20d_ret: float = 0.0,
        sector_df: Optional[pd.DataFrame] = None
    ) -> MarketRegimeResult:
        notes: List[str] = []
        nifty_close = 0.0
        above_20 = False
        above_50 = False
        above_200 = False

        if nifty_df is not None and len(nifty_df) > 0:
            c = nifty_df['close']
            nifty_close = float(c.iloc[-1])
            n = len(c)
            dma_20 = float(c.rolling(window=min(20, n)).mean().iloc[-1])
            dma_50 = float(c.rolling(window=min(50, n)).mean().iloc[-1])
            dma_200 = float(c.rolling(window=min(200, n)).mean().iloc[-1])

            above_20 = nifty_close > dma_20
            above_50 = nifty_close > dma_50
            above_200 = nifty_close > dma_200

            notes.append(f"Nifty 50: ₹{nifty_close:.1f} (20 DMA: ₹{dma_20:.1f}, 50 DMA: ₹{dma_50:.1f})")
        else:
            notes.append("Nifty 50 data not provided; assuming neutral baseline.")
            above_20 = True
            above_50 = True
            above_200 = True

        # VIX Interpretation
        vix_risk_off = False
        if india_vix is not None:
            if india_vix > 20.0:
                vix_risk_off = True
                notes.append(f"India VIX Elevated ({india_vix:.1f} > 20.0) — High Market Volatility / Risk-Off.")
            elif india_vix < 15.0:
                notes.append(f"India VIX Calm ({india_vix:.1f} < 15.0) — Favorable Volatility Regime.")
            else:
                notes.append(f"India VIX Moderate ({india_vix:.1f}).")

        # Determine Regime
        if not above_50 or vix_risk_off:
            regime = MarketRegime.RISK_OFF
        elif above_20 and above_50 and (india_vix is None or india_vix <= 18.0):
            regime = MarketRegime.RISK_ON
        else:
            regime = MarketRegime.NEUTRAL

        # Sector Relative Strength
        stock_vs_sector_rs: Optional[float] = None
        if sector_df is not None and len(sector_df) >= 21:
            sec_c = sector_df['close']
            sec_curr = float(sec_c.iloc[-1])
            sec_20d = float(sec_c.iloc[-21])
            sec_20d_ret = ((sec_curr - sec_20d) / sec_20d) * 100.0
            stock_vs_sector_rs = round(stock_20d_ret - sec_20d_ret, 2)
            if stock_vs_sector_rs > 0:
                notes.append(f"Outperforming Sector Index by {stock_vs_sector_rs:+.1f}% over 20 sessions (Sector RS Leader).")
            else:
                notes.append(f"Underperforming Sector Index by {stock_vs_sector_rs:.1f}% over 20 sessions.")

        return MarketRegimeResult(
            regime=regime,
            nifty_close=round(nifty_close, 2),
            nifty_above_20_dma=above_20,
            nifty_above_50_dma=above_50,
            nifty_above_200_dma=above_200,
            india_vix=india_vix,
            stock_vs_sector_rs=stock_vs_sector_rs,
            notes=notes
        )
