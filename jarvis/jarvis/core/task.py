from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Task:
    """A unit of work to be routed to one or more agents."""

    input: str
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    parent_id: Optional[str] = None

    def child(self, input: str, **metadata: Any) -> "Task":
        merged = {**self.metadata, **metadata}
        return Task(input=input, metadata=merged, parent_id=self.id)


@dataclass
class TaskResult:
    """Result produced by an agent for a given task."""

    task_id: str
    agent_name: str
    output: Any
    success: bool = True
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
