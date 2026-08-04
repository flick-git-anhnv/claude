from __future__ import annotations

import os
from typing import Optional

from jarvis.llm.base import LLMBackend

DEFAULT_MODEL = "claude-sonnet-5"


class AnthropicBackend(LLMBackend):
    """LLMBackend backed by the Anthropic Messages API.

    Requires the `anthropic` package (`pip install jarvis-agent[anthropic]`)
    and an API key, either passed in or read from ANTHROPIC_API_KEY.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 1024,
    ) -> None:
        try:
            import anthropic  # noqa: F401
        except ImportError as exc:  # pragma: no cover - exercised only without extra
            raise ImportError(
                "AnthropicBackend requires the 'anthropic' package. "
                "Install with: pip install jarvis-agent[anthropic]"
            ) from exc

        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError(
                "No Anthropic API key found. Pass api_key= or set ANTHROPIC_API_KEY."
            )

        self._client = anthropic.Anthropic(api_key=key)
        self.model = model
        self.max_tokens = max_tokens

    def complete(self, prompt: str, *, system: Optional[str] = None) -> str:
        kwargs = {}
        if system:
            kwargs["system"] = system
        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )
