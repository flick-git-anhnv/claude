from __future__ import annotations

from typing import Callable, Optional

from jarvis.llm.base import LLMBackend


class MockBackend(LLMBackend):
    """Deterministic backend for tests and offline demos — no API key needed.

    By default echoes the prompt back with a fixed prefix; pass `responder`
    to control output precisely (e.g. in unit tests).
    """

    def __init__(self, responder: Optional[Callable[[str, Optional[str]], str]] = None) -> None:
        self._responder = responder

    def complete(self, prompt: str, *, system: Optional[str] = None) -> str:
        if self._responder:
            return self._responder(prompt, system)
        return f"[mock-response] {prompt}"
