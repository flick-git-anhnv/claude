from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Optional

from jarvis.core.task import Task


@dataclass
class Route:
    """One routing rule: if `matches` says yes, run `agents` in order."""

    name: str
    agents: list[str]
    matches: Callable[[Task], bool]
    priority: int = 0
    description: str = ""

    @classmethod
    def keyword(
        cls,
        name: str,
        agents: list[str],
        keywords: list[str],
        *,
        priority: int = 0,
        description: str = "",
        flags: int = re.IGNORECASE,
    ) -> "Route":
        pattern = re.compile("|".join(re.escape(k) for k in keywords), flags)
        return cls(
            name=name,
            agents=agents,
            matches=lambda task: bool(pattern.search(task.input)),
            priority=priority,
            description=description,
        )


class Router:
    """Picks which agent chain handles a Task.

    Routes are evaluated in descending priority order; the first match wins.
    Falls back to `default_agents` if nothing matches.
    """

    def __init__(self, default_agents: Optional[list[str]] = None) -> None:
        self._routes: list[Route] = []
        self.default_agents = default_agents or []

    def add(self, route: Route) -> "Router":
        self._routes.append(route)
        self._routes.sort(key=lambda r: r.priority, reverse=True)
        return self

    def resolve(self, task: Task) -> tuple[Optional[Route], list[str]]:
        for route in self._routes:
            if route.matches(task):
                return route, route.agents
        return None, self.default_agents

    def routes(self) -> list[Route]:
        return list(self._routes)
