import asyncio
import json
import pytest
import pytest_asyncio
import structlog
from src.events.event_bus import EventBus
from src.events.stream_names import MARKET_TICKS

logger = structlog.get_logger(__name__)

@pytest_asyncio.fixture
async def event_bus():
    eb = EventBus()
    await eb.connect()
    # Cleanup for testing
    streams = await eb.redis.keys("*")
    if streams:
        await eb.redis.delete(*streams)
    yield eb
    await eb.redis.aclose()

@pytest.mark.asyncio
async def test_health_check(event_bus):
    assert await event_bus.health_check() is True

@pytest.mark.asyncio
async def test_publish_and_ack(event_bus):
    stream = "test_stream"
    data = {"hello": "world"}
    msg_id = await event_bus.publish(stream, data)
    assert msg_id is not None
    
    # Check if stream exists
    length = await event_bus.redis.xlen(stream)
    assert length == 1

@pytest.mark.asyncio
async def test_subscribe_with_group(event_bus):
    stream = "test_stream_subscribe"
    group = "test_group"
    consumer = "test_consumer_1"
    
    processed = []
    async def handler(msg_id, data):
        processed.append(data)
        await event_bus.ack(stream, group, msg_id)

    # Start subscriber in a task
    task = asyncio.create_task(event_bus.subscribe(stream, group, consumer, handler, block_ms=100))
    
    # Wait for group creation
    await asyncio.sleep(0.5)
    
    # Publish msg
    data = {"test": "data"}
    await event_bus.publish(stream, data)
    
    # Give some time to process
    await asyncio.sleep(1)
    
    assert len(processed) == 1
    assert processed[0] == data
    
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_backpressure_trigger(event_bus):
    stream = "test_backpressure"
    group = "test_group_laggy"
    await event_bus.create_group(stream, group)
    
    # Inject 101 records into the consumer group without ACK
    for i in range(101):
        # We publish to the stream. Any group on the stream will increase its pending count if it's read but not acked.
        # Redis Stream pending count is increased when a message is read by xreadgroup but not xack'd.
        await event_bus.publish(stream, {"i": i})
    
    # Read them from the consumer group to make them PENDING
    await event_bus.redis.xreadgroup(group, "lazy_consumer", {stream: ">"}, count=101)
    
    # Verify they are pending
    groups = await event_bus.redis.xinfo_groups(stream)
    assert any(g["name"] == group and g["pending"] == 101 for g in groups)
    
    # This should trigger the warning log in publish()
    await event_bus.publish(stream, {"i": 102})

@pytest.mark.asyncio
async def test_consumer_group_isolation(event_bus):
    stream = "test_isolation"
    group_a = "group_a"
    group_b = "group_b"
    
    processed_a = []
    processed_b = []
    
    async def handler_a(msg_id, data):
        processed_a.append(data)
        await event_bus.ack(stream, group_a, msg_id)
        
    async def handler_b(msg_id, data):
        processed_b.append(data)
        await event_bus.ack(stream, group_b, msg_id)

    task_a = asyncio.create_task(event_bus.subscribe(stream, group_a, "c1", handler_a, block_ms=100))
    task_b = asyncio.create_task(event_bus.subscribe(stream, group_b, "c1", handler_b, block_ms=100))
    
    await asyncio.sleep(0.5)
    await event_bus.publish(stream, {"msg": 1})
    await asyncio.sleep(1)
    
    assert len(processed_a) == 1
    assert len(processed_b) == 1
    
    task_a.cancel()
    task_b.cancel()
