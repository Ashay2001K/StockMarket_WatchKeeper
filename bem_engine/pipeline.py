"""
BEM 100 v2.0 - Master Pipeline Engine.
Orchestrates all quantitative modules to produce the final 100-point BEM result,
breakdowns, trade setups, risk alerts, and data confidence indicators.
"""

from datetime import datetime
from typing import Optional, List
import pandas as pd
import numpy as np

from bem_engine.types import (
    StockDataInput,
    BEMResult,
    BEMScoreBreakdown,
    ConfidenceLevel,
)
from bem_engine.price_momentum import PriceMomentumScorer
from bem_engine.volume_expansion import VolumeExpansionScorer
from bem_engine.delivery_strength import DeliveryScorer
from bem_engine.breakout_quality import BreakoutScorer
from bem_engine.institutional import InstitutionalScorer
from bem_engine.momentum_exhaustion import ExhaustionScorer
from bem_engine.chase_alert import ChaseAlertEngine
from bem_engine.action_engine import ActionEngine, calculate_atr
from bem_engine.momentum_potential import MomentumPotentialEngine
from bem_engine.market_regime import MarketRegimeEvaluator


class BEM100Engine:
    """
    Main entry point for BEM 100 v2.0 quantitative momentum screening.
    """

    @classmethod
    def analyze(cls, input_data: StockDataInput) -> BEMResult:
        df = input_data.df.copy()
        if len(df) == 0:
            raise ValueError(f"Input DataFrame for {input_data.symbol} is empty.")

        # Ensure standard column names in lowercase
        df.columns = [c.lower() for c in df.columns]

        current_price = float(df['close'].iloc[-1])
        prev_close = float(df['close'].iloc[-2]) if len(df) >= 2 else current_price
        day_change_pct = ((current_price - prev_close) / prev_close) * 100.0 if prev_close > 0 else 0.0

        confidence_notes: List[str] = []
        confidence = ConfidenceLevel.HIGH

        # 1. Price Momentum (Max 25 pts)
        price_momentum = PriceMomentumScorer.calculate(df, nifty_df=input_data.nifty_df)

        # 2. Volume Expansion (Max 20 pts)
        volume_expansion = VolumeExpansionScorer.calculate(df)

        # 3. Delivery Strength (Max 15 pts)
        delivery_strength = DeliveryScorer.calculate(df)
        if not delivery_strength.delivery_available:
            confidence = ConfidenceLevel.MEDIUM
            confidence_notes.append("Delivery data N/A; confidence downgraded to Medium.")

        # 4. Breakout Quality (Max 15 pts)
        deliv_pct = delivery_strength.current_delivery_pct or 0.0
        breakout_quality = BreakoutScorer.calculate(
            df=df,
            volume_ratio=volume_expansion.volume_ratio_20d,
            delivery_pct=deliv_pct
        )

        # 5. Institutional / FII / DII Participation (Max 10 pts)
        institutional = InstitutionalScorer.calculate(
            df=df,
            fii_dii_signal=input_data.fii_dii_signal
        )
        if not institutional.data_available and confidence == ConfidenceLevel.HIGH:
            # If institutional is estimated, keep confidence at Medium if no derivatives data
            confidence_notes.append("Direct institutional flow estimated from volume/price structure.")

        # 6. Momentum Exhaustion (0 to 15 Base Points -> Contributes 15 - Exhaustion Score)
        exhaustion = ExhaustionScorer.calculate(df)

        # 7. Chase Alert Engine
        chase_alert = ChaseAlertEngine.evaluate(
            exhaustion=exhaustion,
            volume_res=volume_expansion
        )

        # 8. Calculate Core 100-Point Score
        # Formula: Price Mom (25) + Vol Exp (20) + Delivery (15) + Breakout (15) + Inst (10) + (15 - Exhaustion)
        raw_total = (
            price_momentum.score +
            volume_expansion.score +
            delivery_strength.score +
            breakout_quality.score +
            institutional.score +
            exhaustion.bem_contribution
        )
        bem_score = round(max(0.0, min(100.0, raw_total)), 1)

        score_breakdown = BEMScoreBreakdown(
            price_momentum=price_momentum.score,
            volume_expansion=volume_expansion.score,
            delivery_strength=delivery_strength.score,
            breakout_quality=breakout_quality.score,
            institutional=institutional.score,
            exhaustion_adjustment=exhaustion.bem_contribution,
            raw_exhaustion_score=exhaustion.exhaustion_score,
            total_score=bem_score
        )

        # 9. Market Regime & Sector RS
        market_regime = MarketRegimeEvaluator.evaluate(
            nifty_df=input_data.nifty_df,
            india_vix=input_data.india_vix,
            stock_20d_ret=price_momentum.return_20d,
            sector_df=input_data.sector_df
        )

        # 10. Action Engine & Trade Setup
        trade_setup = ActionEngine.evaluate(
            df=df,
            bem_score=bem_score,
            breakout=breakout_quality,
            exhaustion=exhaustion,
            chase_alert=chase_alert,
            volume_res=volume_expansion,
            delivery_res=delivery_strength
        )

        # 11. 10%+ 2-Week Momentum Potential Engine
        atr_14 = calculate_atr(df, period=14)
        momentum_potential = MomentumPotentialEngine.estimate(
            current_price=current_price,
            atr_14=atr_14,
            breakout=breakout_quality,
            volume_res=volume_expansion,
            delivery_res=delivery_strength,
            exhaustion=exhaustion,
            regime=market_regime
        )

        # Check history length
        if len(df) < 30:
            confidence = ConfidenceLevel.LOW
            confidence_notes.append(f"Short trading history ({len(df)} sessions). Model confidence is Low.")

        timestamp_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        return BEMResult(
            symbol=input_data.symbol.upper(),
            timestamp=timestamp_str,
            current_price=round(current_price, 2),
            day_change_pct=round(day_change_pct, 2),
            bem_score=bem_score,
            action=trade_setup.action_state,
            score_breakdown=score_breakdown,
            price_momentum=price_momentum,
            volume_expansion=volume_expansion,
            delivery_strength=delivery_strength,
            breakout_quality=breakout_quality,
            institutional=institutional,
            exhaustion=exhaustion,
            chase_alert=chase_alert,
            trade_setup=trade_setup,
            momentum_potential=momentum_potential,
            market_regime=market_regime,
            confidence=confidence,
            data_confidence_notes=confidence_notes
        )
