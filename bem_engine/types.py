"""
BEM 100 v2.0 - Core Types and Data Models.
Defines strong typing for inputs, outputs, score breakdowns, setups, and alert states.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd


class MarketRegime(str, Enum):
    RISK_ON = "Risk-On"
    RISK_OFF = "Risk-Off"
    NEUTRAL = "Neutral"


class ActionState(str, Enum):
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    BUY_ON_BREAKOUT = "Buy on Breakout"
    BUY_ON_DIP = "Buy on Dip"
    WATCH = "Watch"
    WAIT = "Wait"
    DONT_CHASE = "Don't Chase"
    AVOID = "Avoid"


class PotentialLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class DerivativesBuildup(str, Enum):
    LONG_BUILDUP = "Long Buildup"
    SHORT_COVERING = "Short Covering"
    SHORT_BUILDUP = "Short Buildup"
    LONG_UNWINDING = "Long Unwinding"
    NOT_AVAILABLE = "N/A"


@dataclass
class PriceBar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    delivery_pct: Optional[float] = None
    delivery_qty: Optional[float] = None
    open_interest: Optional[float] = None


@dataclass
class StockDataInput:
    symbol: str
    df: pd.DataFrame  # Expected columns: open, high, low, close, volume, optional delivery_pct, delivery_qty, oi
    nifty_df: Optional[pd.DataFrame] = None  # Nifty 50 OHLCV for relative strength
    sector_df: Optional[pd.DataFrame] = None  # Sector OHLCV for sector relative strength
    fii_dii_signal: Optional[str] = None  # "strong", "improving", "neutral", "weak"
    india_vix: Optional[float] = None


@dataclass
class PriceMomentumResult:
    score: float  # max 25
    return_20d: float
    return_20d_pts: float  # max 8
    return_50d: float
    return_50d_pts: float  # max 5
    rs_vs_nifty_20d: float
    rs_pts: float  # max 5
    ma_alignment_pts: float  # max 4
    dma_20: float
    dma_50: float
    dma_100: float
    dma_200: float
    proximity_52w_high_pct: float
    proximity_pts: float  # max 3
    notes: List[str] = field(default_factory=list)


@dataclass
class VolumeExpansionResult:
    score: float  # max 20
    current_volume: float
    volume_sma_5: float
    volume_sma_20: float
    volume_ratio_20d: float
    is_volume_expanding: bool  # volume >= 1.5x 20d avg
    distribution_detected: bool  # high volume on down close
    notes: List[str] = field(default_factory=list)


@dataclass
class DeliveryStrengthResult:
    score: float  # max 15
    current_delivery_pct: Optional[float]
    delivery_sma_5: Optional[float]
    delivery_sma_20: Optional[float]
    delivery_available: bool
    distribution_flag: bool  # high delivery on falling price
    notes: List[str] = field(default_factory=list)


@dataclass
class BreakoutQualityResult:
    score: float  # max 15
    key_resistance_price: float
    resistance_type: str  # e.g., "52W High", "20-Day High", "Recent Swing High"
    is_breakout: bool
    is_testing_resistance: bool
    distance_to_resistance_pct: float
    notes: List[str] = field(default_factory=list)


@dataclass
class InstitutionalResult:
    score: float  # max 10
    signal_label: str  # Strong Accumulation, Improving, Neutral, Weak
    derivatives_buildup: DerivativesBuildup
    data_available: bool
    notes: List[str] = field(default_factory=list)


@dataclass
class MomentumExhaustionResult:
    exhaustion_score: float  # 0 to 15 (higher means more exhausted)
    bem_contribution: float  # 15 - exhaustion_score (0 to 15)
    return_2d: float
    return_5d: float
    return_10d: float
    pct_above_20_dma: float
    pct_above_50_dma: float
    rsi_14: float
    consecutive_up_days: int
    parabolic_volume_tapering: bool
    is_parabolic: bool
    notes: List[str] = field(default_factory=list)


@dataclass
class ChaseAlertResult:
    is_chase_risk: bool
    severity: str  # "NONE", "MODERATE", "HIGH"
    reason: Optional[str] = None
    recommended_strategy: str = ""


@dataclass
class TradeSetup:
    action_state: ActionState
    current_price: float
    preferred_buy_zone_min: float
    preferred_buy_zone_max: float
    breakout_entry_price: float
    stop_loss: float
    stop_loss_pct: float
    target_1: float
    target_1_pct: float
    target_2: float
    target_2_pct: float
    stretch_target: float
    stretch_target_pct: float
    risk_reward_ratio_t1: float
    risk_reward_ratio_t2: float
    rationale: str


@dataclass
class MomentumPotentialResult:
    level: PotentialLevel
    probability_pct: int
    narrative: str


@dataclass
class MarketRegimeResult:
    regime: MarketRegime
    nifty_close: float
    nifty_above_20_dma: bool
    nifty_above_50_dma: bool
    nifty_above_200_dma: bool
    india_vix: Optional[float]
    stock_vs_sector_rs: Optional[float]
    notes: List[str] = field(default_factory=list)


@dataclass
class BEMScoreBreakdown:
    price_momentum: float  # max 25
    volume_expansion: float  # max 20
    delivery_strength: float  # max 15
    breakout_quality: float  # max 15
    institutional: float  # max 10
    exhaustion_adjustment: float  # max 15 (equals 15 - raw exhaustion)
    raw_exhaustion_score: float  # 0 to 15
    total_score: float  # 0 to 100


@dataclass
class BEMResult:
    symbol: str
    timestamp: str
    current_price: float
    day_change_pct: float
    bem_score: float  # 0 to 100
    action: ActionState
    score_breakdown: BEMScoreBreakdown
    price_momentum: PriceMomentumResult
    volume_expansion: VolumeExpansionResult
    delivery_strength: DeliveryStrengthResult
    breakout_quality: BreakoutQualityResult
    institutional: InstitutionalResult
    exhaustion: MomentumExhaustionResult
    chase_alert: ChaseAlertResult
    trade_setup: TradeSetup
    momentum_potential: MomentumPotentialResult
    market_regime: MarketRegimeResult
    confidence: ConfidenceLevel
    data_confidence_notes: List[str] = field(default_factory=list)
