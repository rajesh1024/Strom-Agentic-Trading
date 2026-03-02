from datetime import datetime
from typing import Any, Optional
from sqlalchemy import BigInteger, DateTime, Index, func, event
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from src.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    agent_id: Mapped[Optional[str]] = mapped_column(index=True)
    action: Mapped[str] = mapped_column(index=True)
    inputs: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    outputs: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    risk_decision: Mapped[Optional[str]]
    order_id: Mapped[Optional[str]]
    correlation_id: Mapped[Optional[str]] = mapped_column(index=True)
    context_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column("metadata", JSONB)
    
    # SPECS requirement: IMMUTABLE — no update/delete at app layer
    # We will enforce this via SQLAlchemy events
    @staticmethod
    @event.listens_for(Base, "before_update", propagate=True)
    def block_audit_update(mapper, connection, target):
        if isinstance(target, AuditLog):
            raise RuntimeError("audit_log records are immutable and cannot be updated")

    @staticmethod
    @event.listens_for(Base, "before_delete", propagate=True)
    def block_audit_delete(mapper, connection, target):
        if isinstance(target, AuditLog):
            raise RuntimeError("audit_log records are immutable and cannot be deleted")

# Implicit indexes via mapped_column(index=True) already include:
# idx_audit_log_time (timestamp)
# idx_audit_log_correlation (correlation_id)
# idx_audit_log_action (action)
