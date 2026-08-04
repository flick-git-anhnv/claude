from jarvis import Agent, AgentContext, AgentRegistry, Orchestrator, Route, Router, Task
from jarvis.core.orchestrator import NoRouteError
from jarvis.core.task import TaskResult


class UppercaseAgent(Agent):
    name = "uppercase"

    def run(self, context: AgentContext) -> TaskResult:
        previous = context.last_output() or context.task.input
        return TaskResult(task_id=context.task.id, agent_name=self.name, output=previous.upper())


class FailingAgent(Agent):
    name = "boom"

    def run(self, context: AgentContext) -> TaskResult:
        raise RuntimeError("simulated failure")


def make_orchestrator(default_agents=None):
    registry = AgentRegistry()
    registry.register(UppercaseAgent())
    registry.register(FailingAgent())
    router = Router(default_agents=default_agents or ["uppercase"])
    return Orchestrator(registry, router)


def test_default_chain_runs_when_no_route_matches():
    orchestrator = make_orchestrator()
    report = orchestrator.dispatch(Task(input="hello world"))

    assert report.route_name is None
    assert report.agent_chain == ["uppercase"]
    assert report.succeeded
    assert report.final_output == "HELLO WORLD"


def test_keyword_route_wins_over_default():
    registry = AgentRegistry()
    registry.register(UppercaseAgent())
    router = Router(default_agents=[])
    router.add(Route.keyword(name="shout", agents=["uppercase"], keywords=["shout"]))
    orchestrator = Orchestrator(registry, router)

    report = orchestrator.dispatch(Task(input="please shout this"))
    assert report.route_name == "shout"
    assert report.final_output == "PLEASE SHOUT THIS"


def test_chain_stops_on_failure_by_default():
    orchestrator = make_orchestrator()
    orchestrator.router.default_agents = ["boom", "uppercase"]

    report = orchestrator.dispatch(Task(input="anything"))

    assert not report.succeeded
    assert len(report.results) == 1
    assert report.results[0].agent_name == "boom"
    assert not report.results[0].success
    assert "simulated failure" in report.results[0].error


def test_no_route_raises_when_nothing_matches_and_no_default():
    registry = AgentRegistry()
    router = Router(default_agents=[])
    orchestrator = Orchestrator(registry, router)

    try:
        orchestrator.dispatch(Task(input="anything"))
        assert False, "expected NoRouteError"
    except NoRouteError:
        pass


def test_chain_passes_output_forward_between_agents():
    class AppendAgent(Agent):
        name = "append"

        def run(self, context: AgentContext) -> TaskResult:
            previous = context.last_output() or context.task.input
            return TaskResult(task_id=context.task.id, agent_name=self.name, output=previous + "!")

    registry = AgentRegistry()
    registry.register(UppercaseAgent())
    registry.register(AppendAgent())
    router = Router(default_agents=["uppercase", "append"])
    orchestrator = Orchestrator(registry, router)

    report = orchestrator.dispatch(Task(input="hi"))
    assert report.final_output == "HI!"
    assert [r.agent_name for r in report.results] == ["uppercase", "append"]
