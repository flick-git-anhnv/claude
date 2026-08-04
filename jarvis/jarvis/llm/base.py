from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class LLMBackend(ABC):
    """Pluggable LLM backend used by `LLMAgent`.

    Implement this against any provider (Anthropic, OpenAI, a local model,
    ...). Agents depend on this interface, never on a specific SDK, so
    swapping providers never touches agent code.
    """

    @abstractmethod
    def complete(self, prompt: str, *, system: Optional[str] = None) -> str:
        """Return the model's completion for `prompt`."""
        raise NotImplementedError
