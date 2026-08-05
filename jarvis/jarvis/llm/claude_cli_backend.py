from __future__ import annotations

import subprocess
from typing import Optional

from jarvis.llm.base import LLMBackend


class ClaudeCliBackend(LLMBackend):
    """LLMBackend that shells out to the `claude` CLI in headless mode.

    Useful when running inside an already-authenticated Claude Code
    environment (no separate ANTHROPIC_API_KEY needed) — this is what makes
    LLMAgent usable for real reasoning tasks without provisioning API keys.
    """

    def __init__(self, timeout: int = 120, extra_args: Optional[list[str]] = None) -> None:
        self.timeout = timeout
        self.extra_args = extra_args or []

    def complete(self, prompt: str, *, system: Optional[str] = None) -> str:
        cmd = ["claude", "-p", prompt, "--output-format", "text", *self.extra_args]
        if system:
            cmd += ["--append-system-prompt", system]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(f"claude CLI failed (exit {result.returncode}): {result.stderr.strip()}")
        return result.stdout.strip()
