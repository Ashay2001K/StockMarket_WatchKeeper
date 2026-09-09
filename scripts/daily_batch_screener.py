"""
Daily BEM 100 Batch Screener Script.
Designed to run in GitHub Actions (Mon-Fri 16:00 IST / 10:30 UTC post-market).
Batch processes Nifty 100/200 + Momentum Watchlist in multithreaded chunks.
Saves precomputed results to Supabase and local JSON cache at zero server compute cost.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data_provider.composite_provider import CompositeMarketDataProvider
from bem_engine.pipeline import BEM100Engine
from database.supabase_client import SupabaseClient

# Target automated universe: Nifty 100 liquid leaders + high-beta momentum watchlist
TARGET_UNIVERSE = [
    # Personal Watchlist & Breakout Leaders
    "MCX", "POLYCAB", "APARINDS", "TDPOWERSYS", "TRENT", "HAL", "BEL", "BHEL",
    "COALINDIA", "POWERGRID", "NTPC", "DIXON", "SUZLON", "TATACHEM", "KAYNES",
    "CDSL", "BSE", "MAZDOCK", "COCHINSHIP", "RVNL", "IREDA", "ZOMATO",
    # Core Nifty Large Caps & Momentum Movers
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL",
    "ITC", "LT", "SUNPHARMA", "TITAN", "MARUTI", "BAJFINANCE", "TATAMOTORS",
    "ASIANPAINT", "ULTRACEMCO", "AXISBANK", "KOTAKBANK", "ADANIENT", "ADANIPORTS",
    "TATASTEEL", "JSWSTEEL", "HINDALCO", "GRASIM", "TECHM", "WIPRO", "HCLTECH",
    "ONGC", "BPCL", "IOC", "HEROMOTOCO", "EICHERMOT", "BAJAJ-AUTO", "DIVISLAB",
    "CIPLA", "DRREDDY", "APOLLOHOSP", "INDUSINDBK", "SBILIFE", "HDFCLIFE",
    "LTIM", "BRITANNIA", "NESTLEIND", "TATACONSUM", "SHRIRAMFIN", "CHOLAFIN",
    "MUTHOOTFIN", "PERSISTENT", "COFORGE", "KPITTECH"
]


def run_batch_screening(symbols: List[str] = TARGET_UNIVERSE) -> List[Dict[str, Any]]:
    start_time = time.time()
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    print(f"[{datetime.utcnow()}] Starting BEM 100 batch run for {len(symbols)} symbols...")

    data_provider = CompositeMarketDataProvider()
    supabase = SupabaseClient()

    # 1. Batch download data in multithreaded chunks
    inputs_dict = data_provider.batch_fetch(symbols, lookback_days=250)
    print(f"Data retrieved for {len(inputs_dict)}/{len(symbols)} symbols.")

    results: List[Dict[str, Any]] = []
    db_records: List[Dict[str, Any]] = []

    for sym, stock_input in inputs_dict.items():
        try:
            analysis = BEM100Engine.analyze(stock_input)

            # JSON serializable summary
            record = {
                "symbol": analysis.symbol,
                "date": today_str,
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
                "potential_level": analysis.momentum_potential.level.value,
                "potential_probability_pct": analysis.momentum_potential.probability_pct,
                "preferred_buy_min": analysis.trade_setup.preferred_buy_zone_min,
                "preferred_buy_max": analysis.trade_setup.preferred_buy_zone_max,
                "breakout_entry": analysis.trade_setup.breakout_entry_price,
                "stop_loss": analysis.trade_setup.stop_loss,
                "stop_loss_pct": analysis.trade_setup.stop_loss_pct,
                "target_1": analysis.trade_setup.target_1,
                "target_2": analysis.trade_setup.target_2,
                "stretch_target": analysis.trade_setup.stretch_target,
                "risk_reward_t1": analysis.trade_setup.risk_reward_ratio_t1,
                "risk_reward_t2": analysis.trade_setup.risk_reward_ratio_t2,
                "confidence": analysis.confidence.value,
                "metadata": {
                    "rationale": analysis.trade_setup.rationale,
                    "notes": analysis.data_confidence_notes,
                    "volume_ratio": analysis.volume_expansion.volume_ratio_20d,
                    "delivery_pct": analysis.delivery_strength.current_delivery_pct,
                    "key_resistance": analysis.breakout_quality.key_resistance_price,
                    "resistance_type": analysis.breakout_quality.resistance_type,
                    "rsi_14": analysis.exhaustion.rsi_14
                }
            }
            results.append(record)
            db_records.append(record)
        except Exception as e:
            print(f"Error analyzing {sym}: {e}")

    # Sort results: BEM score desc, Potential desc, Exhaustion asc
    results.sort(key=lambda x: (-x["bem_score"], -x["potential_probability_pct"], x["raw_exhaustion_score"]))

    # 2. Persist locally to backend data cache
    cache_dir = os.path.join(project_root, "backend", "data")
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, "precomputed_screener.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {len(results)} records to local cache: {cache_file}")

    # 3. Upsert to Supabase if configured
    if supabase.is_configured and db_records:
        success = supabase.upsert_daily_scores(db_records)
        print(f"Supabase upsert status: {'Success' if success else 'Failed'}")

    elapsed = round(time.time() - start_time, 2)
    print(f"BEM 100 batch run completed in {elapsed}s. Processed {len(results)} symbols.")
    return results


if __name__ == "__main__":
    run_batch_screening()
