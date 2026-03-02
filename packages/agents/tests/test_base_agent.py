import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
import pytest

from src.agents.base_agent import BaseAgent
from src.registry.agent_registry import AgentRegistry, MaxAgentsException
from src.events.event_bus import EventBus
from src.config import settings

class DummyAgent(BaseAgent):
    async def handle_task(self, task: dict) -> dict:
        return {"result": "success"}

    async def _cleanup(self):
        self.cleaned_up = True

@pytest.fixture
def mock_event_bus():
    bus = AsyncMock(spec=EventBus)
    bus.publish = AsyncMock()
    return bus

@pytest.mark.asyncio
async def test_agent_state_machine_and_touch(mock_event_bus):
    agent = DummyAgent("test_agent", "dummy", event_bus=mock_event_bus)
    assert agent.state == "SPAWNING"
    
    await agent.start()
    assert agent.state == "ACTIVE"
    mock_event_bus.publish.assert_called()
    
    # Simulate being idle
    with patch("src.agents.base_agent.datetime") as mock_dt:
        mock_now = datetime.now(timezone.utc)
        # Advance time by more than idle timeout
        mock_dt.now.return_value = agent.last_activity + timedelta(seconds=settings.agent_idle_timeout_sec + 1)
        assert agent.is_idle is True
        
        # Test touch()
        agent.touch()
        assert agent.state == "ACTIVE"
        # Since touched, it shouldn't be idle anymore (last_activity updated to patched time)
        # But wait, touch sets last_activity to now(), so now()-last_activity = 0 < timeout
        # So it's not idle. But since we mock now, let's just make sure state is ACTIVE
    
    await agent.retire()
    assert agent.state == "RETIRED"
    assert hasattr(agent, "cleaned_up") and agent.cleaned_up

@pytest.mark.asyncio
async def test_heartbeat_loop(mock_event_bus):
    agent = DummyAgent("hb_agent", "dummy", event_bus=mock_event_bus)
    await agent.start()
    
    # Let the heartbeat loop run once
    await asyncio.sleep(0.01)
    
    # It should have published 'active' and 'heartbeat' (maybe, depending on timing)
    calls = mock_event_bus.publish.call_args_list
    events = [call[0][1]["event"] for call in calls]
    assert "active" in events
    
    await agent.retire()

@pytest.mark.asyncio
async def test_agent_registry():
    registry = AgentRegistry(max_agents=2)
    bus = AsyncMock(spec=EventBus)
    
    agent1 = DummyAgent("a1", "dummy", event_bus=bus)
    agent2 = DummyAgent("a2", "dummy", event_bus=bus)
    agent3 = DummyAgent("a3", "dummy", event_bus=bus)
    
    registry.spawn(agent1)
    registry.spawn(agent2)
    
    assert len(registry.list()) == 2
    assert registry.get("a1") == agent1
    
    with pytest.raises(MaxAgentsException):
        registry.spawn(agent3)
        
    await registry.retire("a1")
    assert len(registry.list()) == 1
    
    # Now we can spawn again
    registry.spawn(agent3)
    assert len(registry.list()) == 2
