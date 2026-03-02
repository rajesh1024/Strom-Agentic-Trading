import asyncio
import json
from typing import Any, Callable, Dict, Optional
import structlog
from redis.asyncio import Redis, from_url
from redis.exceptions import ResponseError

from src.config import settings

logger = structlog.get_logger(__name__)

class EventBus:
    def __init__(self, url: str = settings.redis_url):
        self.url = url
        self.redis: Optional[Redis] = None
        self._backpressure_threshold = 100

    async def connect(self):
        if not self.redis:
            self.redis = from_url(self.url, decode_responses=True)

    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def publish(self, stream: str, data: Dict[str, Any]) -> str:
        """Publish message to stream. Returns message ID."""
        await self.connect()
        
        # Check backpressure - check all consumer groups for the stream
        groups = await self.redis.xinfo_groups(stream) if await self.redis.exists(stream) else []
        for g in groups:
            pending = int(g.get("pending", 0))
            if pending > self._backpressure_threshold:
                logger.warning(
                    "backpressure_trigger",
                    stream=stream,
                    group=g.get("name"),
                    pending=pending,
                    threshold=self._backpressure_threshold
                )
                # In a real scenario, we might want to wait or slow down 
                # For this task, we'll implement a small pause
                await asyncio.sleep(0.1) 

        # Redis Streams store key-value pairs. Wrap the dict in a single 'data' key.
        # We JSON-encode it to preserve types other than strings.
        payload = {"data": json.dumps(data)}
        msg_id = await self.redis.xadd(stream, payload)
        return msg_id

    async def create_group(self, stream: str, group: str):
        """Create consumer group for stream."""
        await self.connect()
        try:
            # Create stream if it doesn't exist ($ means only new messages)
            await self.redis.xgroup_create(stream, group, id="0", mkstream=True)
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise e

    async def subscribe(
        self, 
        stream: str, 
        group: str, 
        consumer: str,
        handler: Callable[[str, Dict[str, Any]], Any], 
        block_ms: int = 5000
    ):
        """Subscribe to stream with consumer group. Calls handler(message_id, data) for each."""
        await self.connect()
        await self.create_group(stream, group)
        
        while True:
            try:
                # Read new messages (">" means messages not yet delivered to other consumers in group)
                # This could be polled or run as a background task. 
                # For this implementation, we read in a loop.
                messages = await self.redis.xreadgroup(group, consumer, {stream: ">"}, count=10, block=block_ms)
                
                if not messages:
                    continue
                
                for stream_name, msgs in messages:
                    for msg_id, payload in msgs:
                        # Decode the JSON payload
                        data = json.loads(payload.get("data", "{}"))
                        # Call handler
                        try:
                            await handler(msg_id, data)
                        except Exception as e:
                            logger.error("handler_error", stream=stream, group=group, msg_id=msg_id, error=str(e))
                            # Depending on config, you might want to retry or skip
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("subscribe_error", stream=stream, group=group, error=str(e))
                await asyncio.sleep(1) # Wait before retry

    async def ack(self, stream: str, group: str, message_id: str):
        """Acknowledge message processing."""
        await self.connect()
        await self.redis.xack(stream, group, message_id)

    async def health_check(self) -> bool:
        """Return True if Redis is reachable."""
        try:
            await self.connect()
            return await self.redis.ping()
        except Exception as e:
            logger.error("redis_health_check_failed", error=str(e))
            return False
