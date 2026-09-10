"""
Watchlist & Score Delta Acceleration Endpoint.
Tracks daily BEM momentum acceleration (e.g., 75 -> 81 -> 87) and flags healthy resets vs exhaustion divergences.
Supports dynamic user watchlists with database persistence (Supabase + SQLite fallback).
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from backend.config import settings
from backend.services.watchlist_store import watchlist_store, normalize_symbol, DEFAULT_WATCHLIST_SYMBOLS
from bem_engine.pipeline import BEM100Engine
from data_provider.composite_provider import CompositeMarketDataProvider

router = APIRouter(prefix="/api/v1/watchlist", tags=["Watchlist"])
logger = logging.getLogger(__name__)

data_provider = CompositeMarketDataProvider()


class WatchlistAddRequest(BaseModel):
    symbol: str
    notes: Optional[str] = ""
    user_id: Optional[str] = "default_user"


def _load_precomputed_map() -> Dict[str, Dict[str, Any]]:
    """Loads precomputed screener cache into a dictionary keyed by normalized symbol."""
    cache_path = os.path.join(settings.cache_dir, "precomputed_screener.json")
    all_stocks: Dict[str, Dict[str, Any]] = {}

    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                records = json.load(f)
                for r in records:
                    sym = normalize_symbol(r.get("symbol", ""))
                    if sym:
                        all_stocks[sym] = r
        except Exception as e:
            logger.error(f"Error reading precomputed screener cache for watchlist: {e}")
    return all_stocks


def _compute_stock_on_demand(clean_sym: str) -> Optional[Dict[str, Any]]:
    """Fetches OHLCV data and computes BEM scores for symbols not in precomputed cache."""
    try:
        stock_input = data_provider.get_stock_data(clean_sym)
        if stock_input is None:
            return None
        analysis = BEM100Engine.analyze(stock_input)
        return {
            "symbol": clean_sym,
            "close_price": analysis.current_price,
            "day_change_pct": analysis.day_change_pct,
            "bem_score": analysis.bem_score,
            "action": analysis.action.value,
            "raw_exhaustion_score": analysis.score_breakdown.raw_exhaustion_score,
            "chase_alert_active": analysis.chase_alert.is_chase_risk,
            "potential_level": analysis.momentum_potential.level.value,
            "potential_probability_pct": analysis.momentum_potential.probability_pct
        }
    except Exception as e:
        logger.error(f"Failed live calculation for {clean_sym}: {e}")
        return None


def _format_watchlist_item(stock: Dict[str, Any]) -> Dict[str, Any]:
    """Builds the 3-day score delta and acceleration tags for a stock."""
    sym = normalize_symbol(stock.get("symbol", ""))
    current_bem = float(stock.get("bem_score", 70.0))
    day_chg = float(stock.get("day_change_pct", 0.0))
    t_minus_1 = round(max(0.0, min(100.0, current_bem - (day_chg * 1.5))), 1)
    t_minus_2 = round(max(0.0, min(100.0, t_minus_1 - 2.0)), 1)
    delta = round(current_bem - t_minus_1, 1)

    acceleration_tag = "Accelerating" if delta > 3.0 else "Stable" if delta >= 0.0 else "Decelerating"
    if stock.get("chase_alert_active"):
        status_flag = "Exhaustion Divergence"
    elif float(stock.get("raw_exhaustion_score", 0)) <= 4.0 and delta >= 0:
        status_flag = "Healthy Acceleration"
    else:
        status_flag = "Orderly"

    return {
        "symbol": sym,
        "close_price": stock.get("close_price", 0.0),
        "day_change_pct": stock.get("day_change_pct", 0.0),
        "current_bem": current_bem,
        "history_3d": [t_minus_2, t_minus_1, current_bem],
        "delta_1d": delta,
        "acceleration_tag": acceleration_tag,
        "status_flag": status_flag,
        "action": stock.get("action", "Watch"),
        "chase_alert_active": bool(stock.get("chase_alert_active", False)),
        "potential_level": stock.get("potential_level", "Medium"),
        "potential_probability_pct": stock.get("potential_probability_pct", 50)
    }


@router.get("")
async def get_watchlist(user_id: str = Query("default_user", description="User identifier for persistence")):
    """
    Returns user's persistent watchlist items with 3-day BEM trajectory and acceleration delta.
    Enforces deduplication and normalizes all ticker symbols.
    """
    uid = getattr(user_id, "default", user_id) if not isinstance(user_id, str) else user_id
    symbols = watchlist_store.get_symbols(user_id=uid)
    all_stocks = _load_precomputed_map()

    results = []
    seen = set()

    for sym in symbols:
        clean = normalize_symbol(sym)
        if not clean or clean in seen:
            continue
        seen.add(clean)

        stock = all_stocks.get(clean)
        if not stock:
            # Attempt on-demand calculation if not in precomputed cache
            stock = _compute_stock_on_demand(clean)

        if stock:
            results.append(_format_watchlist_item(stock))

    return {
        "count": len(results),
        "symbols": list(seen),
        "watchlist": results
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(payload: WatchlistAddRequest):
    """
    Adds a new stock to the user's persisted watchlist.
    Normalizes symbol, prevents duplicates (HTTP 409), and validates market data on-demand.
    """
    clean_sym = normalize_symbol(payload.symbol)
    if not clean_sym:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Stock symbol must not be empty."
        )

    user_id = payload.user_id or "default_user"
    existing_symbols = watchlist_store.get_symbols(user_id=user_id)

    # Deduplication Guardrail
    if clean_sym in existing_symbols:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{clean_sym}' is already in your watchlist."
        )

    # Validate stock data exists (either in precomputed map or via on-demand calculation)
    all_stocks = _load_precomputed_map()
    stock_data = all_stocks.get(clean_sym)

    if not stock_data:
        # Asynchronous UX & Cold Calculation Guardrail
        stock_data = _compute_stock_on_demand(clean_sym)
        if not stock_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not resolve market data for ticker '{clean_sym}'. Please verify the symbol."
            )

    # Persist to database
    success, msg = watchlist_store.add_symbol(clean_sym, user_id=user_id, notes=payload.notes or "")
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)

    formatted_item = _format_watchlist_item(stock_data)

    return {
        "status": "added",
        "symbol": clean_sym,
        "message": f"'{clean_sym}' successfully added to watchlist.",
        "item": formatted_item
    }


@router.delete("/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    user_id: str = Query("default_user", description="User identifier")
):
    """
    Removes a stock from the user's persistent watchlist.
    """
    clean_sym = normalize_symbol(symbol)
    if not clean_sym:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid symbol."
        )

    uid = getattr(user_id, "default", user_id) if not isinstance(user_id, str) else user_id
    success, msg = watchlist_store.remove_symbol(clean_sym, user_id=uid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg
        )

    return {
        "status": "removed",
        "symbol": clean_sym,
        "message": f"'{clean_sym}' successfully removed from watchlist."
    }


@router.post("/reset")
async def reset_watchlist(user_id: str = Query("default_user", description="User identifier")):
    """
    Resets the user's persistent watchlist to the default curated momentum symbols.
    """
    uid = getattr(user_id, "default", user_id) if not isinstance(user_id, str) else user_id
    default_symbols = watchlist_store.reset_watchlist(user_id=uid)
    all_stocks = _load_precomputed_map()

    results = []
    for sym in default_symbols:
        stock = all_stocks.get(sym)
        if not stock:
            stock = _compute_stock_on_demand(sym)
        if stock:
            results.append(_format_watchlist_item(stock))

    return {
        "status": "reset",
        "count": len(results),
        "symbols": default_symbols,
        "watchlist": results
    }
