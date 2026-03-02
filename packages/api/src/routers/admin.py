from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from src.models import get_db, AuditLog
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/admin", tags=["admin"])

class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    agent_id: Optional[str]
    action: str
    inputs: Optional[dict]
    outputs: Optional[dict]
    correlation_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    agent_id: Optional[str] = None,
    action: Optional[str] = None,
    correlation_id: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    query = select(AuditLog).order_by(desc(AuditLog.timestamp))
    
    if agent_id:
        query = query.where(AuditLog.agent_id == agent_id)
    if action:
        query = query.where(AuditLog.action.ilike(f"%{action}%"))
    if correlation_id:
        query = query.where(AuditLog.correlation_id == correlation_id)
        
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    return result.scalars().all()
