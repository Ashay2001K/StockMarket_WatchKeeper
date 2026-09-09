"""
Mobile Screener Endpoint.
Fast, precomputed screening over target universe.
Filterable by minimum BEM, max exhaustion, action state, sector, and 10%+ potential.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query

from database.supabase_client import SupabaseClient
from backend.config import settings

router = APIRouter(prefix="/api/v1/screener", tags=["Screener"])
logger = logging.getLogger(__name__)

supabase = SupabaseClient(settings.supabase_url, settings.supabase_key)


def _load_precomputed_data() -> List[Dict[str, Any]]:
    """Loads records from Supabase or local cache."""
    if supabase.is_configured:
        records = supabase.get_latest_scores(limit=250)
        if records:
            return records

    # Fallback to local JSON cache
    cache_path = os.path.join(settings.cache_dir, "precomputed_screener.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading local screener cache: {e}")
    return []


@router.get("")
async def run_screener(
    min_bem: float = Query(0.0, ge=0.0, le=100.0, description="Minimum BEM Score"),
    max_exhaustion: float = Query(15.0, ge=0.0, le=15.0, description="Maximum Raw Exhaustion Score"),
    action: Optional[str] = Query(None, description="Action State filter (e.g. Strong Buy, Buy, Buy on Breakout)"),
    potential: Optional[str] = Query(None, description="10%+ Potential tier (High, Medium, Low)"),
    no_chase_only: bool = Query(False, description="Exclude stocks flagged with Chase Alert"),
    limit: int = Query(50, ge=1, le=150)
):
    """
    Returns filtered and sorted stock cards for the mobile screener table.
    Default sort: BEM desc, Potential desc, Exhaustion asc.
    """
    data = _load_precomputed_data()

    filtered = []
    for item in data:
        bem = float(item.get("bem_score", 0))
        exhaustion = float(item.get("raw_exhaustion_score", 0))
        item_action = item.get("action", "")
        item_pot = item.get("potential_level", "")
        is_chase = bool(item.get("chase_alert_active", False))

        if bem < min_bem:
            continue
        if exhaustion > max_exhaustion:
            continue
        if action and action.lower() != "all" and item_action.lower() != action.lower():
            continue
        if potential and potential.lower() != "all" and item_pot.lower() != potential.lower():
            continue
        if no_chase_only and is_chase:
            continue

        filtered.append(item)

    # Sort: BEM desc, Potential desc, Exhaustion asc
    filtered.sort(
        key=lambda x: (
            -float(x.get("bem_score", 0)),
            -int(x.get("potential_probability_pct", 0)),
            float(x.get("raw_exhaustion_score", 0))
        )
    )

    return {
        "count": len(filtered[:limit]),
        "total_universe": len(data),
        "filters": {
            "min_bem": min_bem,
            "max_exhaustion": max_exhaustion,
            "action": action,
            "potential": potential,
            "no_chase_only": no_chase_only
        },
        "results": filtered[:limit]
    }
