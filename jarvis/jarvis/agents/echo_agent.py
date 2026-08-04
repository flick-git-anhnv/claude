from __future__ import annotations

from jarvis.core.agent import Agent, AgentContext
from jarvis.core.task import TaskResult


class EchoAgent(Agent):
    """Trivial agent used for wiring tests and CLI smoke checks.

    Returns the task input (or the previous agent's output, if this agent
    is not first in the chain) unchanged.
    """

    name = "echo"
    description = "Echoes its input back — useful for testing the pipeline"

    def run(self, context: AgentContext) -> TaskResult:
        previous = context.last_output()
        output = previous if previous is not None else context.task.input
        return TaskResult(task_id=context.task.id, agent_name=self.name, output=output)
