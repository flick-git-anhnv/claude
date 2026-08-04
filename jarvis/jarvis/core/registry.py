from __future__ import annotations

from typing import Iterator, Optional

from jarvis.core.agent import Agent


class AgentRegistry:
    """Registers agents by name so the Router/Orchestrator can look them up."""

    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent, *, replace: bool = False) -> None:
        if not replace and agent.name in self._agents:
            raise ValueError(
                f"Agent '{agent.name}' already registered — pass replace=True to override"
            )
        self._agents[agent.name] = agent

    def unregister(self, name: str) -> None:
        self._agents.pop(name, None)

    def get(self, name: str) -> Optional[Agent]:
        return self._agents.get(name)

    def require(self, name: str) -> Agent:
        agent = self.get(name)
        if agent is None:
            raise KeyError(f"No agent registered under name '{name}'")
        return agent

    def names(self) -> list[str]:
        return list(self._agents.keys())

    def __iter__(self) -> Iterator[Agent]:
        return iter(self._agents.values())

    def __len__(self) -> int:
        return len(self._agents)

    def __contains__(self, name: str) -> bool:
        return name in self._agents
