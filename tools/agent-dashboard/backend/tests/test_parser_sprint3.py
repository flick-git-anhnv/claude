"""Sprint 3 parser tests — BUG-003 fix + FR-003 (ai-title + first_user_text)."""
from __future__ import annotations

import json
import pathlib

import pytest

from agent_dashboard.parser import parse_line


_FAKE_PATH = str(pathlib.Path("proj-abc") / "session-uuid-sprint3.jsonl")


# ── BUG-003: early-return for missing timestamp ───────────────────────────────

def test_no_timestamp_returns_none():
    """Any line without timestamp (except ai-title) must return None (BUG-003)."""
    line = json.dumps({"type": "last-prompt", "content": "some text"}) + "\n"
    assert parse_line(line, _FAKE_PATH) is None


def test_empty_timestamp_returns_none():
    """Explicit empty string timestamp must also return None."""
    line = json.dumps({"type": "user", "timestamp": "", "message": {}}) + "\n"
    assert parse_line(line, _FAKE_PATH) is None


def test_null_timestamp_returns_none():
    """Null timestamp must return None."""
    line = json.dumps({"type": "assistant", "timestamp": None, "message": {}}) + "\n"
    assert parse_line(line, _FAKE_PATH) is None


def test_zero_timestamp_value_treated_as_missing():
    """Falsy timestamp (empty string from or-chain) → None."""
    # data.get("timestamp") or data.get("ts") or "" — if both missing → ""
    line = json.dumps({"type": "user", "message": {}}) + "\n"
    assert parse_line(line, _FAKE_PATH) is None


# ── FR-003: ai-title lines ────────────────────────────────────────────────────

def test_ai_title_line_returns_is_meta_true():
    """type='ai-title' must return ParsedLine with is_meta=True, no crash."""
    line = json.dumps({
        "type": "ai-title",
        "aiTitle": "Sprint 3 implementation task",
        "sessionId": "session-uuid-sprint3",
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.is_meta is True
    assert result.ai_title == "Sprint 3 implementation task"
    assert result.session_id == "session-uuid-sprint3"


def test_ai_title_line_sets_correct_session_id_from_filename():
    """session_id comes from file stem, not from aiTitle.sessionId."""
    line = json.dumps({
        "type": "ai-title",
        "aiTitle": "Some title",
        "sessionId": "unrelated-id",
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.session_id == "session-uuid-sprint3"  # from file stem


def test_ai_title_line_with_empty_ai_title():
    """ai-title with no aiTitle field still returns is_meta=True, ai_title=None."""
    line = json.dumps({"type": "ai-title", "sessionId": "x"}) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.is_meta is True
    assert result.ai_title is None


def test_ai_title_line_has_zero_tokens():
    """is_meta lines must have 0 for all token fields."""
    line = json.dumps({"type": "ai-title", "aiTitle": "Title"}) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.input_tokens == 0
    assert result.output_tokens == 0
    assert result.cache_creation == 0
    assert result.cache_read == 0


def test_ai_title_line_has_no_tool_name():
    """is_meta lines must not set tool_name / agent_type."""
    line = json.dumps({"type": "ai-title", "aiTitle": "Title"}) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.tool_name is None
    assert result.agent_type is None


def test_regular_user_message_is_not_meta():
    """Normal user message with timestamp → is_meta=False."""
    line = json.dumps({
        "type": "user",
        "timestamp": "2026-08-06T10:00:00.000Z",
        "message": {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.is_meta is False


# ── FR-003: first_user_text extraction ───────────────────────────────────────

def test_user_message_extracts_first_text_block():
    """first_user_text must be set from the first text block in user content."""
    line = json.dumps({
        "type": "user",
        "timestamp": "2026-08-06T10:00:00.000Z",
        "message": {
            "role": "user",
            "content": [{"type": "text", "text": "Implement the dashboard feature"}],
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.first_user_text == "Implement the dashboard feature"


def test_user_message_truncates_text_at_60_chars():
    """first_user_text must be truncated to 60 characters."""
    long_text = "A" * 100
    line = json.dumps({
        "type": "user",
        "timestamp": "2026-08-06T10:00:00.000Z",
        "message": {
            "role": "user",
            "content": [{"type": "text", "text": long_text}],
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.first_user_text is not None
    assert len(result.first_user_text) == 60


def test_user_message_skips_non_text_blocks():
    """If first content block is image/tool_result, must find the first text block."""
    line = json.dumps({
        "type": "user",
        "timestamp": "2026-08-06T10:00:00.000Z",
        "message": {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "x", "content": "result"},
                {"type": "text", "text": "Now please continue"},
            ],
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.first_user_text == "Now please continue"


def test_user_message_no_text_block_gives_none():
    """User message with only tool_result blocks → first_user_text=None."""
    line = json.dumps({
        "type": "user",
        "timestamp": "2026-08-06T10:00:00.000Z",
        "message": {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": "x", "content": "r"}],
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.first_user_text is None


def test_user_message_whitespace_only_text_gives_none():
    """Text block containing only whitespace → first_user_text=None."""
    line = json.dumps({
        "type": "user",
        "timestamp": "2026-08-06T10:00:00.000Z",
        "message": {
            "role": "user",
            "content": [{"type": "text", "text": "   \n  "}],
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.first_user_text is None


def test_assistant_message_has_no_first_user_text():
    """Assistant messages must never set first_user_text."""
    line = json.dumps({
        "type": "assistant",
        "timestamp": "2026-08-06T10:00:01.000Z",
        "message": {
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [{"type": "text", "text": "Sure, I can help."}],
            "usage": {"input_tokens": 50, "output_tokens": 10,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.first_user_text is None
