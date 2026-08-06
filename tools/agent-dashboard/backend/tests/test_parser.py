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


# ── Track B: Agent tool_use subagent extraction ──────────────────────────────

def test_parse_agent_tool_use_extracts_subagent():
    """tool_use with name=='Agent' must populate subagent_type + subagent_activity."""
    line = json.dumps({
        "type": "assistant",
        "timestamp": "2026-08-06T10:00:00.000Z",
        "message": {
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [{
                "type": "tool_use",
                "id": "tu1",
                "name": "Agent",
                "input": {
                    "subagent_type": "senior-developer",
                    "description": "Implement the parser changes",
                },
            }],
            "usage": {"input_tokens": 100, "output_tokens": 20,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.tool_name == "Agent"
    assert result.msg_type == "tool_use"
    assert result.subagent_type == "senior-developer"
    assert result.subagent_activity == "Implement the parser changes"


def test_parse_non_agent_tool_use_does_not_set_subagent():
    """tool_use with name!='Agent' must leave subagent_type/activity as None."""
    line = json.dumps({
        "type": "assistant",
        "timestamp": "2026-08-06T10:00:01.000Z",
        "message": {
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [{
                "type": "tool_use",
                "id": "tu2",
                "name": "Read",
                "input": {"file_path": "/some/file.py"},
            }],
            "usage": {"input_tokens": 50, "output_tokens": 10,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.tool_name == "Read"
    assert result.subagent_type is None
    assert result.subagent_activity is None


def test_parse_agent_tool_use_missing_input_fields():
    """Agent tool_use without subagent_type/description must not crash; fields stay None."""
    line = json.dumps({
        "type": "assistant",
        "timestamp": "2026-08-06T10:00:02.000Z",
        "message": {
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [{"type": "tool_use", "id": "tu3", "name": "Agent", "input": {}}],
            "usage": {"input_tokens": 10, "output_tokens": 5,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.subagent_type is None
    assert result.subagent_activity is None


def test_parse_agent_tool_use_null_input():
    """Agent tool_use with null input block must not crash."""
    line = json.dumps({
        "type": "assistant",
        "timestamp": "2026-08-06T10:00:03.000Z",
        "message": {
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [{"type": "tool_use", "id": "tu4", "name": "Agent", "input": None}],
            "usage": {"input_tokens": 10, "output_tokens": 5,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
        },
    }) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert result.subagent_type is None


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
    """Lines without timestamp now return None (BUG-003 fix — early-return guard).

    Previously this test expected a non-None result. After the Sprint 3 fix,
    any line without a timestamp (except ai-title) returns None to prevent
    started_at='' being written to the DB ('Invalid Date' bug).
    """
    line = json.dumps({"type": "system"}) + "\n"
    result = parse_line(line, _FAKE_PATH)
    # BUG-003 fix: no timestamp → None, does not crash
    assert result is None


def test_raw_json_truncated_at_2000():
    # Must include timestamp so BUG-003 early-return does not fire
    big = {"type": "user", "timestamp": "2026-08-05T10:00:00.000Z",
           "message": {}, "data": "x" * 3000}
    line = json.dumps(big) + "\n"
    result = parse_line(line, _FAKE_PATH)
    assert result is not None
    assert len(result.raw_json) <= 2000


# ── BUG-FIX: subagent transcript nested under session-uuid folder ─────────────
# Watcher is recursive over CLAUDE_PROJECTS_DIR; subagent transcripts live at
#   <projects>/<project-slug>/<session-uuid>/subagents/agent-*.jsonl
# Parser must attribute to <project-slug>, NOT "subagents".

def test_parse_subagent_transcript_attributes_to_parent_project(tmp_path, monkeypatch):
    from agent_dashboard import config as _cfg
    monkeypatch.setattr(_cfg, "CLAUDE_PROJECTS_DIR", tmp_path)
    sub_dir = tmp_path / "c--Users-nguye-Desktop-Claude-Git-claude" / "session-uuid" / "subagents"
    sub_dir.mkdir(parents=True)
    fp = sub_dir / "agent-a0b0914afcc8591f1.jsonl"
    fp.write_text("")
    line = json.dumps({
        "type": "user",
        "timestamp": "2026-08-06T03:20:41.430Z",
        "isSidechain": True,
        "agentId": "a0b0914afcc8591f1",
        "sessionId": "session-uuid",
        "message": {"role": "user", "content": "hi"},
    }) + "\n"
    result = parse_line(line, str(fp))
    assert result is not None
    assert result.project == "c--Users-nguye-Desktop-Claude-Git-claude"
    assert result.project != "subagents"
    assert result.session_id == "agent-a0b0914afcc8591f1"
