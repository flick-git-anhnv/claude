from __future__ import annotations

from pathlib import Path
from typing import Any, Union

import yaml

from jarvis.core.router import Route, Router


def load_router_from_yaml(path: Union[str, Path]) -> Router:
    """Build a Router from a YAML routing table.

    Expected shape::

        default_agents: [echo]
        routes:
          - name: greeting
            agents: [echo]
            keywords: [hello, hi]
            priority: 10
            description: "Say hi back"

    Only keyword-matched routes are supported from config — for anything
    needing custom logic, build the Route in Python with `Route(...)` and
    add it to the Router directly.
    """
    data: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}

    router = Router(default_agents=data.get("default_agents", []))
    for entry in data.get("routes", []):
        router.add(
            Route.keyword(
                name=entry["name"],
                agents=entry["agents"],
                keywords=entry.get("keywords", []),
                priority=entry.get("priority", 0),
                description=entry.get("description", ""),
            )
        )
    return router
