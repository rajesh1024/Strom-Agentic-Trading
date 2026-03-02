import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import Date, DateTime, Numeric, Index, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base

class TradeLog(Base):
    __tablename__ = "trade_log"
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trade_date: Mapped[date_type] = mapped_column(Date, index=True)
    strategy_id: Mapped[str] = mapped_column(String(64), index=True)
    instrument: Mapped[str] = mapped_column(String(128))
    side: Mapped[str] = mapped_column(String(4)) # 'BUY' or 'SELL'
    qty: Mapped[int]
    entry_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    exit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    pnl: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    slippage: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    regime: Mapped[Optional[str]] = mapped_column(String(32))
    signal_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    broker_ref: Mapped[Optional[str]] = mapped_column(String(128))
    instrument: Mapped[str] = mapped_column(String(128))
    side: Mapped[str] = mapped_column(String(4))
    qty: Mapped[int]
    order_type: Mapped[str] = mapped_column(String(8))
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    trigger_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(16), default="PENDING")
    filled_qty: Mapped[int] = mapped_column(default=0)
    avg_fill_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    slippage: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    strategy_id: Mapped[Optional[str]] = mapped_column(String(64))
    signal_id: Mapped[Optional[str]] = mapped_column(String(64))
    risk_approval_id: Mapped[Optional[str]] = mapped_column(String(64))
    tag: Mapped[Optional[str]] = mapped_column(String(64))
    correlation_id: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Position(Base):
    __tablename__ = "positions"
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    instrument: Mapped[str] = mapped_column(String(128), unique=True)
    qty: Mapped[int] = mapped_column(default=0)
    avg_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    current_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    unrealized_pnl: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    realized_pnl: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    greeks: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB) # { delta, gamma, theta, vega }
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
