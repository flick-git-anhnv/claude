from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from jarvis.core.task import Task, TaskResult


@dataclass
class AgentContext:
    """Shared context passed to an agent when it runs.

    Carries whatever upstream agents produced, so an agent never has to
    re-derive information another agent in the chain already established.
    """

    task: Task
    history: list[TaskResult] = field(default_factory=list)
    shared_state: dict[str, Any] = field(default_factory=dict)

    def last_output(self) -> Optional[Any]:
        return self.history[-1].output if self.history else None

    def outputs_by_agent(self, agent_name: str) -> list[Any]:
        return [r.output for r in self.history if r.agent_name == agent_name]


class Agent(ABC):
    """Base class every Jarvis agent must implement.

    Subclass this and implement `run`. Keep an agent focused on one domain —
    the Orchestrator is what composes agents into a workflow, not the agent
    itself.
    """

    #: Unique, stable name used for routing and registry lookup.
    name: str = "agent"
    #: One-line description shown in routing/introspection output.
    description: str = ""

    def __init__(self, name: Optional[str] = None, description: Optional[str] = None) -> None:
        if name:
            self.name = name
        if description:
            self.description = description

    @abstractmethod
    def run(self, context: AgentContext) -> TaskResult:
        """Execute this agent against the given context and return a result."""
        raise NotImplementedError

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<Agent name={self.name!r}>"
