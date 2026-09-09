"""
Market Regime Endpoint.
Monitors Nifty 50 relative to moving averages, India VIX volatility bands, and Risk-On / Risk-Off posture.
"""

from fastapi import APIRouter
from data_provider.composite_provider import CompositeMarketDataProvider
from bem_engine.market_regime import MarketRegimeEvaluator

router = APIRouter(prefix="/api/v1/market-regime", tags=["Market Regime"])
data_provider = CompositeMarketDataProvider()


@router.get("")
async def get_current_market_regime():
    """
    Returns live or cached Nifty 50 stance, India VIX, and Risk-On/Off designation.
    """
    nifty_df = data_provider.get_benchmark_data()
    vix = data_provider.get_india_vix()

    regime_res = MarketRegimeEvaluator.evaluate(
        nifty_df=nifty_df,
        india_vix=vix,
        stock_20d_ret=0.0
    )

    return {
        "regime": regime_res.regime.value,
        "nifty_close": regime_res.nifty_close,
        "nifty_above_20_dma": regime_res.nifty_above_20_dma,
        "nifty_above_50_dma": regime_res.nifty_above_50_dma,
        "nifty_above_200_dma": regime_res.nifty_above_200_dma,
        "india_vix": regime_res.india_vix or 14.2,
        "notes": regime_res.notes
    }
