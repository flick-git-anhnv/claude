from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jarvis.agents.echo_agent import EchoAgent
from jarvis.config.loader import load_router_from_yaml
from jarvis.core.orchestrator import NoRouteError, Orchestrator
from jarvis.core.registry import AgentRegistry
from jarvis.core.router import Router
from jarvis.core.task import Task

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "examples" / "routing.yaml"


def build_default_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(EchoAgent())
    return registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jarvis", description="Run a task through Jarvis")
    parser.add_argument("input", help="Task input text")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to a routing YAML file (default: examples/routing.yaml)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Print the full run report as JSON"
    )
    args = parser.parse_args(argv)

    registry = build_default_registry()
    router: Router = load_router_from_yaml(args.config) if args.config.exists() else Router(
        default_agents=["echo"]
    )
    orchestrator = Orchestrator(registry, router)

    task = Task(input=args.input)
    try:
        report = orchestrator.dispatch(task)
    except NoRouteError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "task_id": report.task.id,
                    "route": report.route_name,
                    "agent_chain": report.agent_chain,
                    "results": [
                        {
                            "agent": r.agent_name,
                            "success": r.success,
                            "output": r.output,
                            "error": r.error,
                        }
                        for r in report.results
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"route: {report.route_name or '(default)'}")
        print(f"chain: {' -> '.join(report.agent_chain)}")
        print(f"output: {report.final_output}")

    return 0 if report.succeeded else 2


if __name__ == "__main__":
    raise SystemExit(main())
