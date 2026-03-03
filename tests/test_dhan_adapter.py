import pytest
import asyncio
import time
from src.services.execution.dhan import DhanBrokerAdapter

@pytest.mark.asyncio
async def test_dhan_adapter_mock_order():
    adapter = DhanBrokerAdapter(mock=True)
    order = await adapter.place_order(
        instrument="NIFTY",
        side="BUY",
        qty=50,
        order_type="MARKET",
        price=None,
        trigger_price=None,
        tag="test_order_MIS"
    )
    assert order["order_id"] == "mock_ord_123"
    assert order["status"] == "PENDING"

@pytest.mark.asyncio
async def test_dhan_adapter_get_status():
    adapter = DhanBrokerAdapter(mock=True)
    status = await adapter.get_order_status("mock_ord_123")
    assert status["status"] == "FILLED"
    assert status["filled_qty"] == 10
    assert status["avg_fill_price"] == 105.5

@pytest.mark.asyncio
async def test_dhan_adapter_cancel_order():
    adapter = DhanBrokerAdapter(mock=True)
    result = await adapter.cancel_order("mock_ord_123")
    assert result["cancelled"] is True

@pytest.mark.asyncio
async def test_dhan_adapter_get_positions():
    adapter = DhanBrokerAdapter(mock=True)
    positions = await adapter.get_positions()
    assert len(positions) > 0
    assert positions[0]["instrument"] == "NIFTY23MAR17500CE"

@pytest.mark.asyncio
async def test_dhan_adapter_get_margins():
    adapter = DhanBrokerAdapter(mock=True)
    margins = await adapter.get_margins()
    assert margins["available"] == 150000
    assert margins["used"] == 50000

@pytest.mark.asyncio
async def test_dhan_adapter_rate_limit():
    adapter = DhanBrokerAdapter(mock=True)
    # Reset request times for a clean test
    adapter._request_times = []
    
    # We should be able to make 10 requests rapidly
    for _ in range(10):
        await adapter.get_margins()
    
    # The 11th request within 1 second should fail
    with pytest.raises(Exception, match="Rate limit exceeded"):
        await adapter.get_margins()

@pytest.mark.asyncio
async def test_dhan_instrument_mapping():
    adapter = DhanBrokerAdapter(mock=True)
    # Check if internal mapping exists
    assert adapter._instrument_map["NIFTY"] == "13"
    assert adapter._instrument_map["BANKNIFTY"] == "25"
    
    # Verify place_order uses mapping
    # This is a bit hard to verify without mocking _make_request, but let's ensure it runs
    order = await adapter.place_order(
        instrument="NIFTY",
        side="BUY",
        qty=50,
        order_type="MARKET",
        price=None,
        trigger_price=None,
        tag="test"
    )
    assert order["order_id"] == "mock_ord_123"
