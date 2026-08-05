"""Unit tests for parser.py — one JSONL line at a time."""
from __future__ import annotations

import json
import pathlib

import pytest

from agent_dashboard.parser import parse_line


_FAKE_PATH = str(pathlib.Path("proj-abc") / "session-uuid-001.jsonl")


# ── Happy path ────────────────────────────────────────────────────────────────

def test_parse_user_message():
    line = json.dumps({
        "type": "user",
        "timestamp": "2026-08-05T10:00:00.000Z",
        "message": {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.msg_type == "user"
    assert result.session_id == "session-uuid-001"
    assert result.project == "proj-abc"
    assert result.input_tokens == 0


def test_parse_assistant_with_usage():
    line = json.dumps({
        "type": "assistant",
        "timestamp": "2026-08-05T10:00:01.000Z",
        "message": {
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [{"type": "text", "text": "Hi"}],
            "usage": {
                "input_tokens": 150,
                "output_tokens": 75,
                "cache_creation_input_tokens": 10,
                "cache_read_input_tokens": 500,
            },
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.msg_type == "assistant"
    assert result.input_tokens == 150
    assert result.output_tokens == 75
    assert result.cache_creation == 10
    assert result.cache_read == 500
    assert result.agent_type == "claude-sonnet-4-6"
    assert result.tool_name is None


def test_parse_tool_use_in_content():
    """Tool use embedded in content blocks → msg_type should become 'tool_use'."""
    line = json.dumps({
        "type": "assistant",
        "timestamp": "2026-08-05T10:00:05.000Z",
        "message": {
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [{"type": "tool_use", "id": "t1", "name": "Read", "input": {}}],
            "usage": {"input_tokens": 200, "output_tokens": 30,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 1000},
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.msg_type == "tool_use"
    assert result.tool_name == "Read"


def test_parse_sample_fixture(sample_jsonl_path):
    """All lines in the fixture file parse without error."""
    lines = sample_jsonl_path.read_text(encoding="utf-8").splitlines(keepends=True)
    results = [parse_line(line, str(sample_jsonl_path)) for line in lines if line.strip()]
    assert all(r is not None for r in results), "Some fixture lines failed to parse"
    # Second line has usage
    assert results[1].input_tokens == 150
    assert results[1].output_tokens == 75
    # Third line is tool_use
    assert results[2].msg_type == "tool_use"
    assert results[2].tool_name == "Read"


# ── Defensive behaviour ───────────────────────────────────────────────────────

def test_parse_malformed_json_returns_none():
    line = "{not valid json}\n"
    assert parse_line(line, _FAKE_PATH) is None


def test_parse_empty_line_returns_none():
    assert parse_line("\n", _FAKE_PATH) is None
    assert parse_line("   \n", _FAKE_PATH) is None


def test_parse_non_dict_returns_none():
    line = json.dumps([1, 2, 3]) + "\n"
    assert parse_line(line, _FAKE_PATH) is None


def test_parse_missing_fields_does_not_crash():
    """Minimal valid JSON object should not crash — missing fields get defaults."""
    line = json.dumps({"type": "system"}) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.input_tokens == 0
    assert result.tool_name is None


def test_raw_json_truncated_at_2000():
    big = {"type": "user", "data": "x" * 3000}
    line = json.dumps(big) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert len(result.raw_json) <= 2000
