"""
Precomputes and seeds realistic BEM 100 results for the 30 target Indian stocks
into backend/data/precomputed_screener.json for instantaneous zero-latency responses.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from bem_engine.pipeline import BEM100Engine
from bem_engine.types import StockDataInput

# Comprehensive seed definitions with distinct momentum profiles
SEED_STOCKS = [
    {"symbol": "MCX", "name": "Multi Commodity Exchange", "price": 3840.0, "type": "fresh_breakout", "sector": "Financials"},
    {"symbol": "POLYCAB", "name": "Polycab India", "price": 6420.0, "type": "strong_momentum", "sector": "Cables"},
    {"symbol": "APARINDS", "name": "Apar Industries", "price": 8650.0, "type": "fresh_breakout", "sector": "Capital Goods"},
    {"symbol": "TDPOWERSYS", "name": "TD Power Systems", "price": 395.0, "type": "consolidation_reset", "sector": "Electrical"},
    {"symbol": "TRENT", "name": "Trent Limited", "price": 6920.0, "type": "overextended_chase", "sector": "Retail"},
    {"symbol": "HAL", "name": "Hindustan Aeronautics", "price": 4680.0, "type": "strong_momentum", "sector": "Defense"},
    {"symbol": "BEL", "name": "Bharat Electronics", "price": 298.0, "type": "fresh_breakout", "sector": "Defense"},
    {"symbol": "BHEL", "name": "Bharat Heavy Electricals", "price": 272.0, "type": "consolidation_reset", "sector": "Heavy Electrical"},
    {"symbol": "DIXON", "name": "Dixon Technologies", "price": 12450.0, "type": "fresh_breakout", "sector": "Electronics"},
    {"symbol": "KAYNES", "name": "Kaynes Technology", "price": 4920.0, "type": "strong_momentum", "sector": "Electronics"},
    {"symbol": "CDSL", "name": "Central Depository Services", "price": 1460.0, "type": "consolidation_reset", "sector": "Capital Markets"},
    {"symbol": "BSE", "name": "BSE Limited", "price": 2680.0, "type": "fresh_breakout", "sector": "Capital Markets"},
    {"symbol": "MAZDOCK", "name": "Mazagon Dock Shipbuilders", "price": 4250.0, "type": "overextended_chase", "sector": "Defense"},
    {"symbol": "COCHINSHIP", "name": "Cochin Shipyard", "price": 1840.0, "type": "overextended_chase", "sector": "Shipbuilding"},
    {"symbol": "RVNL", "name": "Rail Vikas Nigam", "price": 540.0, "type": "consolidation_reset", "sector": "Railways"},
    {"symbol": "IREDA", "name": "Indian Renewable Energy", "price": 228.0, "type": "strong_momentum", "sector": "Finance"},
    {"symbol": "ZOMATO", "name": "Zomato Limited", "price": 262.0, "type": "fresh_breakout", "sector": "Internet"},
    {"symbol": "SUZLON", "name": "Suzlon Energy", "price": 78.5, "type": "consolidation_reset", "sector": "Renewable"},
    {"symbol": "TATACHEM", "name": "Tata Chemicals", "price": 1045.0, "type": "weak_drift", "sector": "Chemicals"},
    {"symbol": "RELIANCE", "name": "Reliance Industries", "price": 2980.0, "type": "consolidation_reset", "sector": "Conglomerate"},
    {"symbol": "TCS", "name": "Tata Consultancy Services", "price": 4210.0, "type": "orderly_trend", "sector": "IT"},
    {"symbol": "INFY", "name": "Infosys Limited", "price": 1890.0, "type": "orderly_trend", "sector": "IT"},
    {"symbol": "HDFCBANK", "name": "HDFC Bank", "price": 1640.0, "type": "consolidation_reset", "sector": "Banking"},
    {"symbol": "ICICIBANK", "name": "ICICI Bank", "price": 1220.0, "type": "strong_momentum", "sector": "Banking"},
    {"symbol": "SBIN", "name": "State Bank of India", "price": 810.0, "type": "orderly_trend", "sector": "Banking"},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "price": 1540.0, "type": "fresh_breakout", "sector": "Telecom"},
    {"symbol": "ITC", "name": "ITC Limited", "price": 492.0, "type": "orderly_trend", "sector": "FMCG"},
    {"symbol": "LT", "name": "Larsen & Toubro", "price": 3650.0, "type": "orderly_trend", "sector": "Infrastructure"},
    {"symbol": "TITAN", "name": "Titan Company", "price": 3480.0, "type": "orderly_trend", "sector": "Consumer"},
    {"symbol": "TATAMOTORS", "name": "Tata Motors", "price": 965.0, "type": "consolidation_reset", "sector": "Automobiles"},
]


def generate_seed_data():
    np.random.seed(42)
    n = 60
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    results = []

    nifty_df = pd.DataFrame({
        "close": [22000.0 * (1.0 + 0.0006 * i) for i in range(n)]
    })

    for item in SEED_STOCKS:
        sym = item["symbol"]
        price = item["price"]
        stype = item["type"]
        fii_sig = "strong" if stype in ["fresh_breakout", "strong_momentum"] else "improving"

        if stype == "fresh_breakout":
            # Consolidates tightly, then breaks out today with volume + delivery
            base = price * 0.94
            prices = [base + (0.5 * np.sin(i / 2.0)) for i in range(n - 1)] + [price]
            volumes = [100000.0] * (n - 1) + [220000.0]  # 2.2x volume
            deliveries = [35.0] * (n - 1) + [52.0]        # 52% delivery
        elif stype == "strong_momentum":
            # Steady strong run
            prices = [price * (0.80 + (0.20 * i / (n - 1))) for i in range(n)]
            volumes = [100000.0] * (n - 1) + [160000.0]
            deliveries = [42.0] * n
        elif stype == "overextended_chase":
            # Violent surge sitting high above 20 DMA with tapering volume
            base = price * 0.68
            prices = [base] * 49 + [base * (1.0 + 0.04 * (i + 1)) for i in range(11)]
            volumes = [100000.0] * 56 + [90000.0, 70000.0, 50000.0, 30000.0]
            deliveries = [30.0] * n
            fii_sig = "improving"
        elif stype == "consolidation_reset":
            # Prior run, then 6-day pullback to 20 DMA on light volume
            peak = price * 1.04
            prices = [price * (0.80 + 0.24 * i / 53) for i in range(54)]
            for i in range(1, 7):
                prices.append(peak - (0.007 * peak * i))
            volumes = [140000.0] * 54 + [65000.0] * 6
            deliveries = [38.0] * n
        else: # weak_drift
            prices = [price * (1.05 - 0.05 * i / n) for i in range(n)]
            volumes = [70000.0] * n
            deliveries = [25.0] * n
            fii_sig = "neutral"

        opens = [p * 0.995 for p in prices]
        highs = [p * 1.01 for p in prices]
        lows = [p * 0.99 for p in prices]

        df = pd.DataFrame({
            "open": opens,
            "high": highs,
            "low": lows,
            "close": prices,
            "volume": volumes,
            "delivery_pct": deliveries
        })

        stock_input = StockDataInput(symbol=sym, df=df, nifty_df=nifty_df, fii_dii_signal=fii_sig)
        analysis = BEM100Engine.analyze(stock_input)

        record = {
            "symbol": analysis.symbol,
            "name": item["name"],
            "sector": item["sector"],
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
                "notes": analysis.data_confidence_notes,
                "volume_ratio": analysis.volume_expansion.volume_ratio_20d,
                "delivery_pct": analysis.delivery_strength.current_delivery_pct,
                "key_resistance": analysis.breakout_quality.key_resistance_price,
                "resistance_type": analysis.breakout_quality.resistance_type,
                "rsi_14": analysis.exhaustion.rsi_14,
                "market_regime": analysis.market_regime.regime.value
            }
        }
        results.append(record)

    results.sort(key=lambda x: (-x["bem_score"], -x["potential_probability_pct"], x["raw_exhaustion_score"]))

    cache_dir = os.path.join(project_root, "backend", "data")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, "precomputed_screener.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Generated seed precomputed screener with {len(results)} symbols at: {cache_path}")


if __name__ == "__main__":
    generate_seed_data()
