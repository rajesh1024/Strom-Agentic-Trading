from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Dict, List, Optional
from .base import Underlying, Regime

class OptionStrike(BaseModel):
    strike: int
    ce_ltp: float
    pe_ltp: float
    ce_oi: int
    pe_oi: int
    ce_iv: float
    pe_iv: float
    ce_greeks: Dict = Field(default_factory=dict)
    pe_greeks: Dict = Field(default_factory=dict)

class OptionChainResponse(BaseModel):
    underlying: Underlying
    spot_price: float
    timestamp: datetime
    expiry: date
    chain: List[OptionStrike]
    stale: bool = False

class RegimeFeatures(BaseModel):
    volatility_rank: float
    trend_strength: float
    mean_reversion_score: float

class FeatureVector(BaseModel):
    pcr: float
    iv_skew: float
    max_pain: int
    oi_change_ce_top5: List[Dict]
    oi_change_pe_top5: List[Dict]
    vwap_deviation: float
    atr_14: float
    rsi_14: float
    regime_features: RegimeFeatures

# Added Crypto Orderbook as requested by user even though it wasn't in SPECS.md
class DepthLevel(BaseModel):
    price: float
    qty: float

class CryptoOrderbook(BaseModel):
    symbol: str
    bids: List[DepthLevel]
    asks: List[DepthLevel]
    timestamp: datetime
    last_update_id: int
