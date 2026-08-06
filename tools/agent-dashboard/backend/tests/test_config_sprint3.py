"""Sprint 3 config tests — MODEL_CONTEXT_WINDOW + resolve_max_context."""
from __future__ import annotations

from agent_dashboard.config import (
    MODEL_CONTEXT_WINDOW,
    DEFAULT_CONTEXT_WINDOW,
    resolve_max_context,
)


def test_sonnet5_is_1m():
    assert resolve_max_context("claude-sonnet-5") == 1_000_000


def test_opus5_is_1m():
    assert resolve_max_context("claude-opus-5") == 1_000_000


def test_fable5_is_1m():
    assert resolve_max_context("claude-fable-5") == 1_000_000


def test_haiku45_is_200k():
    assert resolve_max_context("claude-haiku-4-5") == 200_000


def test_sonnet46_legacy_is_200k():
    assert resolve_max_context("claude-sonnet-4-6") == 200_000


def test_opus47_legacy_is_200k():
    assert resolve_max_context("claude-opus-4-7") == 200_000


def test_unknown_model_returns_default():
    assert resolve_max_context("claude-unknown-future") == DEFAULT_CONTEXT_WINDOW
    assert resolve_max_context("") == DEFAULT_CONTEXT_WINDOW


def test_no_prefix_match_sonnet5_vs_sonnet46():
    """Exact match only — 'claude-sonnet-5' must NOT match 'claude-sonnet-4-6'."""
    assert resolve_max_context("claude-sonnet-5") == 1_000_000
    assert resolve_max_context("claude-sonnet-4-6") == 200_000
    # They must return different values
    assert resolve_max_context("claude-sonnet-5") != resolve_max_context("claude-sonnet-4-6")


def test_default_context_window_is_200k():
    assert DEFAULT_CONTEXT_WINDOW == 200_000


def test_model_context_window_keys_are_strings():
    """All keys must be strings (exact model identifiers)."""
    for key in MODEL_CONTEXT_WINDOW:
        assert isinstance(key, str)
        assert key.startswith("claude-")
