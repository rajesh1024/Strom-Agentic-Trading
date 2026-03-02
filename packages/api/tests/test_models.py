import pytest
import pytest_asyncio
from sqlalchemy import select
from src.models import AuditLog, Order, StrategyRegistry, AsyncSessionLocal, engine

@pytest_asyncio.fixture
async def session():
    async with AsyncSessionLocal() as session:
        yield session
    # Cleanup any leftovers
    await engine.dispose()

@pytest.mark.asyncio
async def test_audit_log_immutability(session):
    # Create a record
    log = AuditLog(
        action="TEST_ACTION",
        inputs={"test": 1},
        correlation_id="test_corr_1"
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    
    # Try to update (should fail)
    log.action = "UPDATED_ACTION"
    with pytest.raises(RuntimeError, match="audit_log records are immutable and cannot be updated"):
        await session.commit()
    
    await session.rollback() # Clear failed state
    
    # Try to delete (should fail)
    await session.delete(log)
    with pytest.raises(RuntimeError, match="audit_log records are immutable and cannot be deleted"):
        await session.commit()
        
    await session.rollback()

@pytest.mark.asyncio
async def test_create_and_query_trading_models(session):
    # Test Strategy
    strategy = StrategyRegistry(
        id="test_strat_unique_2",
        name="Test Strategy",
        type="trending",
        underlying="NIFTY",
        params={"threshold": 0.5},
        regime_affinity=[]
    )
    session.add(strategy)
    
    # Test Order
    order = Order(
        id="ord_unique_2",
        instrument="NIFTY24DEC25000CE",
        side="BUY",
        qty=50,
        order_type="LIMIT",
        price=150.0,
        status="PENDING",
        strategy_id="test_strat_unique_2"
    )
    session.add(order)
    
    await session.commit()
    
    # Query back
    stmt = select(Order).where(Order.id == "ord_unique_2")
    result = await session.execute(stmt)
    queried_order = result.scalar_one()
    assert queried_order.instrument == "NIFTY24DEC25000CE"
    assert queried_order.qty == 50
    
    # Clean up
    await session.delete(queried_order)
    await session.delete(strategy)
    await session.commit()
