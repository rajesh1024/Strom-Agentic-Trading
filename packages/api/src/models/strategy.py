import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import Date, DateTime, Numeric, String, Uuid, func, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base

class StrategyRegistry(Base):
    __tablename__ = "strategy_registry"
    
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    version: Mapped[int] = mapped_column(default=1)
    type: Mapped[str] = mapped_column(String(32))
    underlying: Mapped[str] = mapped_column(String(32))
    regime_affinity: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String(32)), default=[])
    params: Mapped[dict[str, Any]] = mapped_column(JSONB)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    backtest_summary: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class StrategyPerformance(Base):
    __tablename__ = "strategy_performance"
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    strategy_id: Mapped[str] = mapped_column(String(64), ForeignKey("strategy_registry.id"))
    period_start: Mapped[date_type] = mapped_column(Date)
    period_end: Mapped[date_type] = mapped_column(Date)
    total_trades: Mapped[Optional[int]]
    win_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    total_pnl: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    sharpe_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    max_drawdown: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    avg_slippage: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    regime_distribution: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
