"""
Institutional / FII / DII Participation Scorer (10 Points Max).
Evaluates institutional accumulation signals and Futures Open Interest (OI) buildup dynamics.
"""

from typing import Optional, List
import pandas as pd
import numpy as np
from bem_engine.types import InstitutionalResult, DerivativesBuildup


class InstitutionalScorer:
    """
    Computes Institutional Participation Score (Max 10 pts):
    - Weak / falling: 2 pts
    - Neutral: 5 pts
    - Improving: 7 pts
    - Strong accumulation: 10 pts
    - Derivatives confirmation:
      - Long Buildup (Price UP + OI UP): Strong confirmation
      - Short Covering (Price UP + OI DOWN): Mild confirmation
      - Short Buildup (Price DOWN + OI UP): Bearish signal
      - Long Unwinding (Price DOWN + OI DOWN): Bearish signal
    """

    @staticmethod
    def calculate(
        df: pd.DataFrame,
        fii_dii_signal: Optional[str] = None
    ) -> InstitutionalResult:
        notes: List[str] = []
        n = len(df)
        has_oi = 'open_interest' in df.columns and df['open_interest'].notna().sum() >= 2

        buildup = DerivativesBuildup.NOT_AVAILABLE
        oi_score_override: Optional[float] = None

        if has_oi:
            oi_series = df['open_interest'].dropna()
            close_series = df['close']
            if len(oi_series) >= 2:
                curr_oi = float(oi_series.iloc[-1])
                prev_oi = float(oi_series.iloc[-2])
                curr_c = float(close_series.iloc[-1])
                prev_c = float(close_series.iloc[-2])

                oi_chg_pct = ((curr_oi - prev_oi) / prev_oi) * 100.0 if prev_oi > 0 else 0.0
                price_chg_pct = ((curr_c - prev_c) / prev_c) * 100.0 if prev_c > 0 else 0.0

                if price_chg_pct > 0.3 and oi_chg_pct > 2.0:
                    buildup = DerivativesBuildup.LONG_BUILDUP
                    oi_score_override = 10.0
                    notes.append(f"Futures OI: Long Buildup (+{oi_chg_pct:.1f}% OI on price advance).")
                elif price_chg_pct > 0.3 and oi_chg_pct < -2.0:
                    buildup = DerivativesBuildup.SHORT_COVERING
                    oi_score_override = 7.0
                    notes.append(f"Futures OI: Short Covering ({oi_chg_pct:.1f}% OI reduction).")
                elif price_chg_pct < -0.3 and oi_chg_pct > 2.0:
                    buildup = DerivativesBuildup.SHORT_BUILDUP
                    oi_score_override = 2.0
                    notes.append(f"Futures OI: Short Buildup (+{oi_chg_pct:.1f}% OI on price decline).")
                elif price_chg_pct < -0.3 and oi_chg_pct < -2.0:
                    buildup = DerivativesBuildup.LONG_UNWINDING
                    oi_score_override = 2.0
                    notes.append(f"Futures OI: Long Unwinding ({oi_chg_pct:.1f}% OI exit on falling price).")

        # Prioritize direct institutional signal if provided, else use OI, else Neutral default
        data_available = True
        if fii_dii_signal:
            sig = fii_dii_signal.strip().lower()
            if sig in ["strong", "strong accumulation", "heavy_buying"]:
                score = 10.0
                label = "Strong Accumulation"
                notes.append("FII/DII net aggressive accumulation detected.")
            elif sig in ["improving", "buying", "moderate"]:
                score = 7.0
                label = "Improving"
                notes.append("FII/DII positive net inflow.")
            elif sig in ["weak", "falling", "heavy_selling"]:
                score = 2.0
                label = "Weak / Falling"
                notes.append("FII/DII net outflow / distribution.")
            else:
                score = 5.0
                label = "Neutral"
        elif oi_score_override is not None:
            score = oi_score_override
            if score == 10.0:
                label = "Strong Accumulation"
            elif score == 7.0:
                label = "Improving"
            else:
                label = "Weak / Falling"
        else:
            score = 5.0
            label = "Neutral"
            data_available = False
            notes.append("Institutional flow data not available; neutral benchmark (5/10) assigned.")

        return InstitutionalResult(
            score=round(score, 2),
            signal_label=label,
            derivatives_buildup=buildup,
            data_available=data_available,
            notes=notes
        )
