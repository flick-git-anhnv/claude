from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from jarvis.core.agent import AgentContext
from jarvis.core.registry import AgentRegistry
from jarvis.core.router import Router
from jarvis.core.task import Task, TaskResult

logger = logging.getLogger("jarvis.orchestrator")


class NoRouteError(Exception):
    """Raised when a task matches no route and no default chain is set."""


@dataclass
class RunReport:
    """Full record of a task's trip through the agent chain."""

    task: Task
    route_name: Optional[str]
    agent_chain: list[str]
    results: list[TaskResult] = field(default_factory=list)

    @property
    def final_output(self):
        return self.results[-1].output if self.results else None

    @property
    def succeeded(self) -> bool:
        return bool(self.results) and all(r.success for r in self.results)


class Orchestrator:
    """Routes a Task to the right agent chain and runs it, agent by agent.

    This is the generic analogue of the "Dispatcher" pattern: given a task,
    decide which agents apply, run them in sequence, and pass each agent's
    output forward as context for the next — never silently skipping a step,
    never letting one agent's failure vanish before the caller sees it.
    """

    def __init__(self, registry: AgentRegistry, router: Router) -> None:
        self.registry = registry
        self.router = router

    def dispatch(self, task: Task, *, stop_on_failure: bool = True) -> RunReport:
        route, chain = self.router.resolve(task)
        if not chain:
            raise NoRouteError(
                f"No route matched task {task.id!r} and no default agent chain is configured"
            )

        report = RunReport(task=task, route_name=route.name if route else None, agent_chain=chain)
        context = AgentContext(task=task)

        for agent_name in chain:
            agent = self.registry.require(agent_name)
            logger.info("dispatch: task=%s agent=%s", task.id, agent_name)
            try:
                result = agent.run(context)
            except Exception as exc:  # noqa: BLE001 - surface any agent failure
                result = TaskResult(
                    task_id=task.id,
                    agent_name=agent_name,
                    output=None,
                    success=False,
                    error=str(exc),
                )
                logger.exception("agent %s failed on task %s", agent_name, task.id)

            report.results.append(result)
            context.history.append(result)

            if not result.success and stop_on_failure:
                logger.warning(
                    "stopping chain: agent=%s task=%s error=%s",
                    agent_name,
                    task.id,
                    result.error,
                )
                break

        return report
