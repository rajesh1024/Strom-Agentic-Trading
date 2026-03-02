from typing import Dict, List, Optional
from src.agents.base_agent import BaseAgent
from src.config import settings
import structlog

logger = structlog.get_logger(__name__)

class MaxAgentsException(Exception):
    pass

class AgentRegistry:
    def __init__(self, max_agents: int = settings.max_agents):
        self.max_agents = max_agents
        self._agents: Dict[str, BaseAgent] = {}

    def spawn(self, agent: BaseAgent) -> BaseAgent:
        """Spawn a new agent and add it to registry. Rejects if max limit reached."""
        if len(self._agents) >= self.max_agents:
            raise MaxAgentsException(f"Maximum number of agents ({self.max_agents}) reached.")
        
        if agent.agent_id in self._agents:
            raise ValueError(f"Agent with ID {agent.agent_id} already exists.")
            
        self._agents[agent.agent_id] = agent
        return agent

    async def retire(self, agent_id: str):
        """Retire an agent and remove it from the registry."""
        if agent_id in self._agents:
            agent = self._agents[agent_id]
            await agent.retire()
            del self._agents[agent_id]

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID."""
        return self._agents.get(agent_id)

    def list(self) -> List[BaseAgent]:
        """List all registered agents."""
        return list(self._agents.values())
