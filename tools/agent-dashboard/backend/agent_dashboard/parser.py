"""JSONL line parser — one-line-at-a-time, never throws on bad input."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from . import config
from .models import ParsedLine

logger = logging.getLogger(__name__)


def parse_line(line: str, file_path: str) -> Optional[ParsedLine]:
    """
    Parse one complete JSONL line (must end with '\\n').
    Returns None on any error — caller continues to next line.

    Claude Code JSONL format (observed):
      {
        "type": "user" | "assistant",
        "timestamp": "ISO8601",
        "message": {
          "role": "...",
          "content": [...],  # list of content blocks
          "model": "claude-...",  # assistant only
          "usage": {
            "input_tokens": N,
            "output_tokens": N,
            "cache_creation_input_tokens": N,
            "cache_read_input_tokens": N
          }
        }
      }

    Tool uses are embedded in content blocks with type == "tool_use".
    """
    line = line.strip()
    if not line:
        return None

    try:
        data = json.loads(line)
    except json.JSONDecodeError as exc:
        logger.debug("JSON parse error in %s: %s", file_path, exc)
        return None

    if not isinstance(data, dict):
        return None

    p = Path(file_path)
    session_id = p.stem           # filename without extension = session uuid
    # BUG-FIX: subagent transcripts live at
    #   <projects>/<project-slug>/<session-uuid>/subagents/agent-*.jsonl
    # Using p.parent.name would give "subagents" as project. Instead, resolve
    # to the FIRST path segment under CLAUDE_PROJECTS_DIR so subagent transcripts
    # are attributed to the top-level project of their parent session.
    try:
        rel = p.resolve().relative_to(config.CLAUDE_PROJECTS_DIR.resolve())
        project = rel.parts[0] if rel.parts else p.parent.name
    except (ValueError, OSError):
        project = p.parent.name

    msg_type: str = data.get("type", "unknown")

    # ── Sprint 3: handle ai-title meta lines (FR-003 / BUG-003) ──────────────
    # ai-title lines have no timestamp; they carry a session title update, not
    # a content event — return is_meta=True so the ingest loop can update the
    # title without creating a session record.
    if msg_type == "ai-title":
        ai_title_val: Optional[str] = data.get("aiTitle") or None
        return ParsedLine(
            session_id=session_id,
            project=project,
            file_path=file_path,
            timestamp="",
            msg_type="ai-title",
            tool_name=None,
            agent_type=None,
            input_tokens=0,
            output_tokens=0,
            cache_creation=0,
            cache_read=0,
            raw_json=line[:2000],
            ai_title=ai_title_val,
            is_meta=True,
        )

    # ── BUG-003 fix: early-return for any other line missing timestamp ────────
    # Lines without timestamp (e.g. "last-prompt") are metadata — they MUST NOT
    # create a session record (would set started_at="", causing "Invalid Date").
    timestamp: str = data.get("timestamp") or data.get("ts") or ""
    if not timestamp:
        return None

    message: dict = data.get("message") or {}
    usage: dict = message.get("usage") or {}

    input_tokens: int   = _int(usage.get("input_tokens", 0))
    output_tokens: int  = _int(usage.get("output_tokens", 0))
    cache_creation: int = _int(usage.get("cache_creation_input_tokens", 0))
    cache_read: int     = _int(usage.get("cache_read_input_tokens", 0))

    # ── FR-003: extract first user text as fallback title ────────────────────
    first_user_text: Optional[str] = None
    if msg_type == "user":
        content_blocks = message.get("content")
        if isinstance(content_blocks, list):
            for block in content_blocks:
                if isinstance(block, dict) and block.get("type") == "text":
                    raw_text: str = block.get("text") or ""
                    if raw_text.strip():
                        first_user_text = raw_text[:60]
                        break

    # Detect tool_use inside content blocks (assistant messages)
    tool_name: Optional[str] = None
    agent_type: Optional[str] = None
    subagent_type: Optional[str] = None
    subagent_activity: Optional[str] = None
    content = message.get("content")

    if msg_type == "assistant":
        agent_type = message.get("model")  # e.g. "claude-sonnet-4-6"
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_name = block.get("name")
                    msg_type = "tool_use"
                    # Track B: extract subagent info ONLY for Agent tool calls
                    if tool_name == "Agent":
                        tool_input = block.get("input") or {}
                        subagent_type = tool_input.get("subagent_type") or None
                        subagent_activity = tool_input.get("description") or None
                    break

    # Also handle top-level tool_name field (alternate format)
    if data.get("tool_name") and not tool_name:
        tool_name = data["tool_name"]
        if msg_type == "assistant":
            msg_type = "tool_use"

    raw_json = line[:2000]  # truncate for audit storage

    return ParsedLine(
        session_id=session_id,
        project=project,
        file_path=file_path,
        timestamp=timestamp,
        msg_type=msg_type,
        tool_name=tool_name,
        agent_type=agent_type,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_creation=cache_creation,
        cache_read=cache_read,
        raw_json=raw_json,
        subagent_type=subagent_type,
        subagent_activity=subagent_activity,
        first_user_text=first_user_text,
    )


def _int(val: object) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0
