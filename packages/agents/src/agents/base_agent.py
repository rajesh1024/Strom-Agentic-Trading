from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
import asyncio

from src.events.event_bus import EventBus
from src.events.stream_names import AGENTS_LIFECYCLE
from src.config import settings

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: str, model: str = "llama-3.1-8b-instant", event_bus: EventBus = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.model = model
        self.state = "SPAWNING"
        self.last_activity = datetime.now(timezone.utc)
        self.last_heartbeat = datetime.now(timezone.utc)
        self.event_bus = event_bus or EventBus(url=settings.redis_url)
        self._heartbeat_task = None

    async def start(self):
        self.state = "ACTIVE"
        await self._publish_lifecycle_event("active")
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        try:
            while self.state in ("ACTIVE", "IDLE", "BLOCKED"):
                # Transition to IDLE if idle threshold crossed
                if self.state == "ACTIVE" and self.is_idle:
                    self.state = "IDLE"
                    await self._publish_lifecycle_event("idle")
                
                # Transition to RETIRED if retire threshold crossed
                if self.should_retire:
                    await self.retire()
                    break

                await self._publish_heartbeat()
                self.last_heartbeat = datetime.now(timezone.utc)
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass

    def touch(self):
        """Call on every task to reset idle timer."""
        self.last_activity = datetime.now(timezone.utc)
        if self.state == "IDLE":
            self.state = "ACTIVE"
            asyncio.create_task(self._publish_lifecycle_event("active"))

    @property
    def is_idle(self) -> bool:
        return (datetime.now(timezone.utc) - self.last_activity) > timedelta(seconds=settings.agent_idle_timeout_sec)

    @property
    def should_retire(self) -> bool:
        return (datetime.now(timezone.utc) - self.last_activity) > timedelta(seconds=settings.agent_retire_timeout_sec)

    async def retire(self):
        if self.state != "RETIRED":
            self.state = "RETIRED"
            await self._publish_lifecycle_event("retired")
            if self._heartbeat_task and not self._heartbeat_task.done():
                self._heartbeat_task.cancel()
            await self._cleanup()

    @abstractmethod
    async def handle_task(self, task: dict) -> dict:
        """Process a task. Must be implemented by each agent."""
        pass

    @abstractmethod
    async def _cleanup(self):
        """Cleanup resources on retirement."""
        pass

    async def _publish_lifecycle_event(self, event_type: str):
        payload = {
            "agent_id": self.agent_id,
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await self.event_bus.publish(AGENTS_LIFECYCLE, payload)

    async def _publish_heartbeat(self):
        """Publish heartbeat to agents.lifecycle stream."""
        await self._publish_lifecycle_event("heartbeat")
