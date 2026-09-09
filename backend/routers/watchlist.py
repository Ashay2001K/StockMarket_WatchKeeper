"""
Watchlist & Score Delta Acceleration Endpoint.
Tracks daily BEM momentum acceleration (e.g., 75 -> 81 -> 87) and flags healthy resets vs exhaustion divergences.
"""

import os
import json
import logging
from typing import List, Dict, Any
from fastapi import APIRouter

from backend.config import settings

router = APIRouter(prefix="/api/v1/watchlist", tags=["Watchlist"])
logger = logging.getLogger(__name__)

DEFAULT_WATCHLIST_SYMBOLS = ["MCX", "POLYCAB", "APARINDS", "TDPOWERSYS", "TRENT", "HAL", "BEL", "DIXON", "KAYNES", "BSE"]


@router.get("")
async def get_watchlist():
    """
    Returns watchlist items with simulated 3-day BEM trajectory and acceleration delta.
    """
    cache_path = os.path.join(settings.cache_dir, "precomputed_screener.json")
    all_stocks: Dict[str, Dict[str, Any]] = {}

    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                records = json.load(f)
                for r in records:
                    all_stocks[r.get("symbol", "").upper()] = r
        except Exception as e:
            logger.error(f"Error reading watchlist data: {e}")

    results = []
    for sym in DEFAULT_WATCHLIST_SYMBOLS:
        stock = all_stocks.get(sym)
        if stock:
            current_bem = float(stock.get("bem_score", 70))
            # Calculate/estimate 3-day score delta trajectory (e.g. Day-2 -> Day-1 -> Today)
            day_chg = float(stock.get("day_change_pct", 0.0))
            t_minus_1 = round(max(0.0, min(100.0, current_bem - (day_chg * 1.5))), 1)
            t_minus_2 = round(max(0.0, min(100.0, t_minus_1 - 2.0)), 1)
            delta = round(current_bem - t_minus_1, 1)

            acceleration_tag = "Accelerating" if delta > 3.0 else "Stable" if delta >= 0.0 else "Decelerating"
            if stock.get("chase_alert_active"):
                status_flag = "Exhaustion Divergence"
            elif stock.get("raw_exhaustion_score", 0) <= 4.0 and delta >= 0:
                status_flag = "Healthy Acceleration"
            else:
                status_flag = "Orderly"

            results.append({
                "symbol": sym,
                "close_price": stock.get("close_price"),
                "day_change_pct": stock.get("day_change_pct"),
                "current_bem": current_bem,
                "history_3d": [t_minus_2, t_minus_1, current_bem],
                "delta_1d": delta,
                "acceleration_tag": acceleration_tag,
                "status_flag": status_flag,
                "action": stock.get("action"),
                "chase_alert_active": stock.get("chase_alert_active"),
                "potential_level": stock.get("potential_level"),
                "potential_probability_pct": stock.get("potential_probability_pct")
            })

    return {
        "count": len(results),
        "watchlist": results
    }
