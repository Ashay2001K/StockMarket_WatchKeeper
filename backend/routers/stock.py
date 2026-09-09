"""
Stock Momentum Analysis Endpoint.
Provides deep quantitative scorecard, breakdowns, risk levels, and setups for any NSE/BSE ticker.
Fast reads (<50ms) from precomputed tables, with automatic on-demand calculation for unlisted symbols.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException

from bem_engine.pipeline import BEM100Engine
from data_provider.composite_provider import CompositeMarketDataProvider
from database.supabase_client import SupabaseClient
from backend.config import settings

router = APIRouter(prefix="/api/v1/stock", tags=["Stock Analysis"])
logger = logging.getLogger(__name__)

supabase = SupabaseClient(settings.supabase_url, settings.supabase_key)
data_provider = CompositeMarketDataProvider()


def _get_from_local_cache(symbol: str) -> Optional[Dict[str, Any]]:
    """Checks local precomputed JSON cache."""
    cache_path = os.path.join(settings.cache_dir, "precomputed_screener.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                clean = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
                for item in data:
                    if item.get("symbol") == clean:
                        return item
        except Exception as e:
            logger.error(f"Error reading local cache: {e}")
    return None


@router.get("/{ticker}")
async def get_stock_analysis(ticker: str):
    """
    Returns the comprehensive 100-point BEM scorecard for a given ticker.
    """
    clean_sym = ticker.upper().replace(".NS", "").replace(".BO", "").strip()

    # 1. Check Supabase precomputed store first
    db_record = supabase.get_stock_score(clean_sym)
    if db_record:
        return {"source": "precomputed_db", "data": db_record}

    # 2. Check local file cache
    local_record = _get_from_local_cache(clean_sym)
    if local_record:
        return {"source": "precomputed_cache", "data": local_record}

    # 3. Fallback: Run live on-demand calculation
    logger.info(f"Ticker {clean_sym} not in precomputed store; executing live BEM 100 calculation...")
    try:
        stock_input = data_provider.get_stock_data(clean_sym)
        if stock_input is None:
            raise HTTPException(status_code=404, detail=f"Stock data for '{clean_sym}' could not be found.")

        analysis = BEM100Engine.analyze(stock_input)

        response_data = {
            "symbol": analysis.symbol,
            "timestamp": analysis.timestamp,
            "close_price": analysis.current_price,
            "day_change_pct": analysis.day_change_pct,
            "bem_score": analysis.bem_score,
            "action": analysis.action.value,
            "price_momentum_score": analysis.score_breakdown.price_momentum,
            "volume_expansion_score": analysis.score_breakdown.volume_expansion,
            "delivery_score": analysis.score_breakdown.delivery_strength,
            "breakout_score": analysis.score_breakdown.breakout_quality,
            "institutional_score": analysis.score_breakdown.institutional,
            "exhaustion_adjustment": analysis.score_breakdown.exhaustion_adjustment,
            "raw_exhaustion_score": analysis.score_breakdown.raw_exhaustion_score,
            "chase_alert_active": analysis.chase_alert.is_chase_risk,
            "chase_alert_severity": analysis.chase_alert.severity,
            "chase_alert_reason": analysis.chase_alert.reason,
            "chase_strategy": analysis.chase_alert.recommended_strategy,
            "potential_level": analysis.momentum_potential.level.value,
            "potential_probability_pct": analysis.momentum_potential.probability_pct,
            "potential_narrative": analysis.momentum_potential.narrative,
            "preferred_buy_min": analysis.trade_setup.preferred_buy_zone_min,
            "preferred_buy_max": analysis.trade_setup.preferred_buy_zone_max,
            "breakout_entry": analysis.trade_setup.breakout_entry_price,
            "stop_loss": analysis.trade_setup.stop_loss,
            "stop_loss_pct": analysis.trade_setup.stop_loss_pct,
            "target_1": analysis.trade_setup.target_1,
            "target_1_pct": analysis.trade_setup.target_1_pct,
            "target_2": analysis.trade_setup.target_2,
            "target_2_pct": analysis.trade_setup.target_2_pct,
            "stretch_target": analysis.trade_setup.stretch_target,
            "stretch_target_pct": analysis.trade_setup.stretch_target_pct,
            "risk_reward_t1": analysis.trade_setup.risk_reward_ratio_t1,
            "risk_reward_t2": analysis.trade_setup.risk_reward_ratio_t2,
            "confidence": analysis.confidence.value,
            "metadata": {
                "rationale": analysis.trade_setup.rationale,
                "confidence_notes": analysis.data_confidence_notes,
                "price_momentum_notes": analysis.price_momentum.notes,
                "volume_expansion_notes": analysis.volume_expansion.notes,
                "delivery_notes": analysis.delivery_strength.notes,
                "breakout_notes": analysis.breakout_quality.notes,
                "exhaustion_notes": analysis.exhaustion.notes,
                "market_regime": analysis.market_regime.regime.value,
                "dma_20": analysis.price_momentum.dma_20,
                "dma_50": analysis.price_momentum.dma_50,
                "dma_200": analysis.price_momentum.dma_200,
                "return_20d": analysis.price_momentum.return_20d,
                "return_50d": analysis.price_momentum.return_50d,
                "rsi_14": analysis.exhaustion.rsi_14,
                "volume_ratio": analysis.volume_expansion.volume_ratio_20d,
                "delivery_pct": analysis.delivery_strength.current_delivery_pct,
                "key_resistance": analysis.breakout_quality.key_resistance_price,
                "resistance_type": analysis.breakout_quality.resistance_type,
            }
        }
        return {"source": "live_computed", "data": response_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed live calculation for {clean_sym}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
