from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict
from .trading import TradeSignal

class RiskCheck(BaseModel):
    rule: str
    passed: bool
    detail: str

class RiskDecision(BaseModel):
    approved: bool
    risk_score: float
    checks: List[RiskCheck]
    modified_signal: Optional[TradeSignal] = None
    timestamp: datetime

# Added RiskParams for validation in sample_risk_params.json
class RiskParams(BaseModel):
    max_position_size: int = 4
    max_portfolio_delta: float = 0.5
    max_daily_loss: float = 20000.0
    max_drawdown: float = 0.1
    margin_check: float = 0.9
    time_of_day: Dict[str, str] = {"start": "09:20", "end": "15:15"}
    correlation_limit: float = 0.8
    single_concentration: float = 0.4
