# Jarvis

A lightweight, generic multi-agent orchestration framework in Python — route
a task to the right chain of specialized agents, run them in order, and pass
each agent's output forward as context for the next.

Not tied to any particular domain: bring your own agents (each one just
subclasses `Agent` and implements `run`), your own routing rules, and
optionally your own LLM backend.

## Core concepts

| Concept | What it is |
|---|---|
| `Task` | A unit of work — input text plus arbitrary metadata |
| `Agent` | One focused unit of behavior; implements `run(context) -> TaskResult` |
| `AgentContext` | What an agent sees when it runs: the task, and every prior agent's output in this chain |
| `AgentRegistry` | Where agents are registered by name |
| `Router` / `Route` | Decides which agent chain handles a given task (keyword match by default; write custom `matches` for anything else) |
| `Orchestrator` | Resolves the route, runs the chain agent-by-agent, stops on failure by default, and returns a full `RunReport` |

## Install

```bash
pip install -e .
# or, with Anthropic backend support:
pip install -e ".[anthropic]"
```

## Quick start

```python
from jarvis import Agent, AgentContext, AgentRegistry, Orchestrator, Route, Router, Task
from jarvis.core.task import TaskResult

class ShoutAgent(Agent):
    name = "shout"

    def run(self, context: AgentContext) -> TaskResult:
        text = context.last_output() or context.task.input
        return TaskResult(task_id=context.task.id, agent_name=self.name, output=text.upper())

registry = AgentRegistry()
registry.register(ShoutAgent())

router = Router(default_agents=["shout"])
orchestrator = Orchestrator(registry, router)

report = orchestrator.dispatch(Task(input="hello there"))
print(report.final_output)  # "HELLO THERE"
```

See `examples/example_run.py` for a multi-agent chain (an `LLMAgent` handing
off to a custom agent), and `examples/routing.yaml` for a config-driven
routing table.

## CLI

```bash
python -m jarvis.cli "hello there"
# or, once installed:
jarvis "hello there"
```

By default it loads `examples/routing.yaml`; pass `--config path/to/routing.yaml`
to use your own.

## Design notes

- **Agents are dumb about routing.** An agent never decides whether it should
  run — the `Router` does that. This keeps agent logic testable in isolation.
- **Context accumulates, it doesn't get thrown away.** Every agent in a chain
  sees every prior agent's output via `AgentContext.history`, so a later
  agent never has to re-derive what an earlier one already established.
- **Failures don't vanish.** `Orchestrator.dispatch` catches agent exceptions,
  wraps them in a failed `TaskResult`, and by default stops the chain there —
  callers always get a full `RunReport`, not a stack trace mid-flight.
- **LLM use is optional and swappable.** `LLMAgent` depends only on the
  `LLMBackend` interface. `MockBackend` needs no API key (tests, demos);
  `AnthropicBackend` wraps the real Anthropic Messages API.

## Testing

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
