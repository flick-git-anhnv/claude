from __future__ import annotations

from typing import Optional

from jarvis.core.agent import Agent, AgentContext
from jarvis.core.task import TaskResult
from jarvis.llm.base import LLMBackend


class LLMAgent(Agent):
    """Agent that delegates to an `LLMBackend` to produce its output.

    `prompt_template` may reference `{input}` (the upstream output, or the
    original task input if this agent runs first) and `{task_input}` (always
    the original task input, regardless of chain position).
    """

    def __init__(
        self,
        name: str,
        backend: LLMBackend,
        *,
        system: Optional[str] = None,
        prompt_template: str = "{input}",
        description: str = "",
    ) -> None:
        super().__init__(name=name, description=description)
        self.backend = backend
        self.system = system
        self.prompt_template = prompt_template

    def run(self, context: AgentContext) -> TaskResult:
        upstream = context.last_output()
        current_input = upstream if upstream is not None else context.task.input
        prompt = self.prompt_template.format(
            input=current_input, task_input=context.task.input
        )
        output = self.backend.complete(prompt, system=self.system)
        return TaskResult(task_id=context.task.id, agent_name=self.name, output=output)
