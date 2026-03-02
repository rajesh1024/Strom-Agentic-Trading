import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from src.main import app
from src.models import AuditLog, AsyncSessionLocal, engine

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    # Cleanup any leftovers
    await engine.dispose()

@pytest.mark.asyncio
async def test_audit_log_creation(async_client):
    # Make a state-changing POST request
    data = {"instrument": "NIFTY", "side": "BUY", "api_key": "secret123"}
    response = await async_client.post("/test-audit", json=data, headers={"X-Correlation-ID": "test-corr-audit"})
    
    assert response.status_code == 200
    
    # Wait a bit for middleware to finish commit (it's actually awaited in dispatch)
    async with AsyncSessionLocal() as session:
        stmt = select(AuditLog).where(AuditLog.correlation_id == "test-corr-audit")
        result = await session.execute(stmt)
        audit_entry = result.scalars().first()
        
        assert audit_entry is not None
        assert audit_entry.action == "POST /test-audit"
        
        # Verify sanitization
        inputs = audit_entry.inputs or {}
        assert inputs["instrument"] == "NIFTY"
        assert inputs["api_key"] == "[REDACTED]"

@pytest.mark.asyncio
async def test_admin_get_audit_logs(async_client):
    # Correlation ID is already set from previous test possibly, or we create a new one
    corr_id = "test-corr-admin-check"
    await async_client.post("/test-audit", json={"foo": "bar"}, headers={"X-Correlation-ID": corr_id})
    
    response = await async_client.get(f"/admin/audit-logs?correlation_id={corr_id}")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) >= 1
    assert logs[0]["correlation_id"] == corr_id
    assert "inputs" in logs[0]
    assert "outputs" in logs[0]

@pytest.mark.asyncio
async def test_audit_no_get_logs(async_client):
    # GET requests should NOT be logged
    corr_id = "test-corr-no-log"
    await async_client.get("/health", headers={"X-Correlation-ID": corr_id})
    
    async with AsyncSessionLocal() as session:
        stmt = select(AuditLog).where(AuditLog.correlation_id == corr_id)
        result = await session.execute(stmt)
        entry = result.scalar()
        assert entry is None
