"""Unit tests for tail_reader.py — byte-offset cursor, partial-line safety."""
from __future__ import annotations

import pathlib

import pytest

from agent_dashboard.tail_reader import TailReader


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write(path: pathlib.Path, content: bytes) -> None:
    path.write_bytes(content)


def _append(path: pathlib.Path, content: bytes) -> None:
    with open(path, "ab") as f:
        f.write(content)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_read_complete_lines(tmp_path):
    f = tmp_path / "test.jsonl"
    _write(f, b'{"type":"user"}\n{"type":"assistant"}\n')
    reader = TailReader()
    lines = reader.read_new_lines(str(f))
    assert len(lines) == 2
    assert lines[0].strip() == '{"type":"user"}'
    assert lines[1].strip() == '{"type":"assistant"}'


def test_skip_partial_last_line(tmp_path):
    f = tmp_path / "test.jsonl"
    # Last line has no trailing newline → incomplete, should not be yielded
    _write(f, b'{"type":"user"}\n{"partial"')
    reader = TailReader()
    lines = reader.read_new_lines(str(f))
    assert len(lines) == 1
    assert "user" in lines[0]


def test_incremental_reads(tmp_path):
    f = tmp_path / "test.jsonl"
    _write(f, b'{"type":"user"}\n')
    reader = TailReader()

    lines1 = reader.read_new_lines(str(f))
    assert len(lines1) == 1

    # Second read with no new data → empty
    lines2 = reader.read_new_lines(str(f))
    assert len(lines2) == 0

    # Append new line
    _append(f, b'{"type":"assistant"}\n')
    lines3 = reader.read_new_lines(str(f))
    assert len(lines3) == 1
    assert "assistant" in lines3[0]


def test_cursor_persists_across_reads(tmp_path):
    f = tmp_path / "test.jsonl"
    _write(f, b'line1\nline2\nline3\n')
    reader = TailReader()
    reader.read_new_lines(str(f))

    cursor = reader.get_cursor(str(f))
    assert cursor == len(b'line1\nline2\nline3\n')


def test_no_lines_when_no_newline(tmp_path):
    f = tmp_path / "test.jsonl"
    _write(f, b'incomplete without newline')
    reader = TailReader()
    lines = reader.read_new_lines(str(f))
    assert lines == []
    # Cursor should NOT advance (no committed byte)
    assert reader.get_cursor(str(f)) == 0


def test_file_truncation_resets_cursor(tmp_path):
    f = tmp_path / "test.jsonl"
    _write(f, b'{"type":"user"}\n{"type":"assistant"}\n')
    reader = TailReader()
    reader.read_new_lines(str(f))  # advance cursor

    # Simulate file truncation (new smaller content)
    _write(f, b'{"type":"system"}\n')
    lines = reader.read_new_lines(str(f))
    assert len(lines) == 1
    assert "system" in lines[0]


def test_nonexistent_file_returns_empty():
    reader = TailReader()
    lines = reader.read_new_lines("/nonexistent/path/session.jsonl")
    assert lines == []


def test_restore_cursors(tmp_path):
    f = tmp_path / "test.jsonl"
    _write(f, b'{"type":"user"}\n{"type":"assistant"}\n')
    # Pre-set cursor to skip first line
    reader = TailReader()
    reader.restore_cursors({str(f): len(b'{"type":"user"}\n')})
    lines = reader.read_new_lines(str(f))
    assert len(lines) == 1
    assert "assistant" in lines[0]


def test_multibyte_utf8_safe(tmp_path):
    """Multi-byte characters (Vietnamese) must not corrupt byte offsets."""
    f = tmp_path / "test.jsonl"
    line = '{"msg":"Xin chào thế giới"}\n'
    _write(f, line.encode("utf-8"))
    reader = TailReader()
    lines = reader.read_new_lines(str(f))
    assert len(lines) == 1
    assert "chào" in lines[0]
    # Cursor must equal exact byte length
    assert reader.get_cursor(str(f)) == len(line.encode("utf-8"))
