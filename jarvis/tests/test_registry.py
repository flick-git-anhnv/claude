import pytest

from jarvis import Agent, AgentContext, AgentRegistry
from jarvis.core.task import TaskResult


class DummyAgent(Agent):
    name = "dummy"

    def run(self, context: AgentContext) -> TaskResult:
        return TaskResult(task_id=context.task.id, agent_name=self.name, output="ok")


def test_register_and_get():
    registry = AgentRegistry()
    registry.register(DummyAgent())
    assert registry.get("dummy") is not None
    assert "dummy" in registry
    assert registry.names() == ["dummy"]


def test_duplicate_register_raises_without_replace():
    registry = AgentRegistry()
    registry.register(DummyAgent())
    with pytest.raises(ValueError):
        registry.register(DummyAgent())


def test_duplicate_register_allowed_with_replace():
    registry = AgentRegistry()
    registry.register(DummyAgent())
    registry.register(DummyAgent(), replace=True)
    assert len(registry) == 1


def test_require_raises_keyerror_for_missing_agent():
    registry = AgentRegistry()
    with pytest.raises(KeyError):
        registry.require("missing")
