"""Run this with: python examples/example_run.py

Shows a 2-agent chain: an LLMAgent (backed by MockBackend, no API key
needed) hands its output to an EchoAgent, and prints the full trip.
"""

from jarvis import Agent, AgentContext, AgentRegistry, Orchestrator, Route, Router, Task
from jarvis.agents import EchoAgent, LLMAgent
from jarvis.llm import MockBackend


class UppercaseAgent(Agent):
    """A custom agent — subclass Agent, implement run(), done."""

    name = "uppercase"
    description = "Uppercases whatever the previous agent produced"

    def run(self, context: AgentContext):
        from jarvis.core.task import TaskResult

        previous = context.last_output() or context.task.input
        return TaskResult(task_id=context.task.id, agent_name=self.name, output=previous.upper())


def main() -> None:
    registry = AgentRegistry()
    registry.register(LLMAgent("summarizer", backend=MockBackend(), prompt_template="Summarize: {input}"))
    registry.register(UppercaseAgent())
    registry.register(EchoAgent())

    router = Router(default_agents=["echo"])
    router.add(
        Route.keyword(
            name="summarize-and-shout",
            agents=["summarizer", "uppercase"],
            keywords=["summarize"],
            priority=10,
        )
    )

    orchestrator = Orchestrator(registry, router)
    task = Task(input="please summarize this quarter's incident postmortems")
    report = orchestrator.dispatch(task)

    print(f"route: {report.route_name}")
    print(f"chain: {' -> '.join(report.agent_chain)}")
    for result in report.results:
        print(f"  [{result.agent_name}] -> {result.output!r}")
    print(f"final: {report.final_output}")


if __name__ == "__main__":
    main()
