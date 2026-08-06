"""Pydantic models for REST API request/response bodies and internal dataclasses."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, field_validator


# ── Subagent display name mapping (Track B) ───────────────────────────────────

SUBAGENT_DISPLAY: dict[str, str] = {
    "cto":                    "CTO",
    "product-manager":        "Product Manager",
    "business-analyst":       "Business Analyst",
    "engineering-manager":    "Engineering Manager",
    "tech-lead":              "Tech Lead",
    "senior-developer":       "Senior Developer",
    "junior-developer":       "Junior Developer",
    "qa-lead":                "QA Lead",
    "qa-engineer":            "QA Engineer",
    "devops-lead":            "DevOps Lead",
    "devops-engineer":        "DevOps Engineer",
    "project-manager":        "Project Manager",
    "ui-ux-designer":         "UI/UX Designer",
    "ux-ui-reviewer":         "UX/UI Reviewer",
    "documentation-writer":   "Documentation Writer",
    "code-migrator":          "Code Migrator",
    "github-repo-researcher": "GitHub Repo Researcher",
    "task-planner":           "Task Planner",
    "md-optimizer":           "MD Optimizer",
}


def get_subagent_display_name(subagent_type: str) -> str:
    """Map subagent_type slug → display name. Falls back to title-case."""
    return SUBAGENT_DISPLAY.get(subagent_type) or subagent_type.replace("-", " ").title()


def decode_project_slug(slug: str) -> str:
    """Best-effort decode of Claude Code project slug → human-readable path.

    Convention (verified on repo c--Users-nguye-Desktop-Claude-Git-claude):
    - Leading ^[a-z]-- → Windows drive letter upper + ":\\"
    - '--' separates path components
    - Single '-' within a component is kept as-is (ambiguous)

    Example:
        'c--Users-nguye-Desktop-Claude-Git-claude'
        → 'C:\\\\Users-nguye-Desktop-Claude-Git-claude'

    Limitation: ambiguous single-dash segments cannot be decoded precisely;
    the original slug is always shown as a tooltip alongside this display value.
    """
    if re.match(r"^[a-z]--", slug):
        drive = slug[0].upper() + ":\\"
        remainder = slug[3:]
        parts = remainder.split("--")
        return drive + "\\".join(parts)
    return slug  # no Windows drive prefix → return slug unchanged


# ── Internal dataclasses (not Pydantic — used in pipeline) ───────────────────

@dataclass
class ParsedLine:
    session_id: str
    project: str
    file_path: str
    timestamp: str
    msg_type: str           # user | assistant | tool_use | tool_result | system
    tool_name: Optional[str]
    agent_type: Optional[str]   # model name if determinable
    input_tokens: int
    output_tokens: int
    cache_creation: int
    cache_read: int
    raw_json: str           # compact, truncated to 2000 chars for audit
    subagent_type: Optional[str] = None      # Track B: from tool_use Agent input.subagent_type
    subagent_activity: Optional[str] = None  # Track B: from tool_use Agent input.description
    # Sprint 3 fields
    ai_title: Optional[str] = None           # FR-003: from type="ai-title" aiTitle field
    first_user_text: Optional[str] = None    # FR-003: fallback from first user text block
    is_meta: bool = False                    # True for ai-title lines (no timestamp, no session create)
    is_subagent: bool = False                # True when file lives under <session>/subagents/ — hide from main list
    # Sprint 4 fields — subagent transcript linking
    parent_session_id: Optional[str] = None  # UUID of parent session (folder above "subagents/")
    attribution_agent: Optional[str] = None  # from JSONL field "attributionAgent" (e.g. "senior-developer")
    # Sprint 4b — Agent tool_use ID (for result matching)
    tool_use_id: Optional[str] = None        # block["id"] from Agent tool_use content block


@dataclass
class StateChange:
    session_id: str
    old_state: str
    new_state: str
    changed_at: str


@dataclass
class SessionInfo:
    session_id: str
    state: str              # Running | Idle | Ended
    last_event_at: datetime


# ── Account Pydantic models ───────────────────────────────────────────────────

class AccountCreate(BaseModel):
    name: str
    kind: str = "api_key"      # "api_key" | "oauth_session"
    api_key: Optional[str] = None  # required when kind == "api_key"

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, v: str) -> str:
        if v not in ("api_key", "oauth_session"):
            raise ValueError("kind must be 'api_key' or 'oauth_session'")
        return v

    def validate_for_kind(self) -> None:
        """Call after construction to enforce cross-field rules."""
        if self.kind == "api_key":
            if not self.api_key:
                raise ValueError("api_key is required when kind is 'api_key'")
            if not self.api_key.startswith("sk-"):
                raise ValueError("API key must start with 'sk-'")


class AccountUpdate(BaseModel):
    name: str


class AccountResponse(BaseModel):
    id: str
    name: str
    key_masked: str
    is_active: bool
    created_at: str


# ── Session Pydantic models ───────────────────────────────────────────────────

class SessionResponse(BaseModel):
    session_id: str
    project: str
    agent_type: Optional[str]
    state: str
    started_at: str
    last_event_at: str
    token_total: int


class SessionDetailResponse(BaseModel):
    session: dict[str, Any]
    events: list[dict[str, Any]]


class SessionHistoryResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int


# ── Token models ──────────────────────────────────────────────────────────────

class TokenBucket(BaseModel):
    label: str
    input: int
    output: int
    cache_creation: int
    cache_read: int


class TokenTotals(BaseModel):
    input: int
    output: int
    cache_creation: int
    cache_read: int
    grand_total: int


class TokenSummaryResponse(BaseModel):
    buckets: list[TokenBucket]
    totals: TokenTotals


# ── WebSocket message helpers ─────────────────────────────────────────────────

def make_delta(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "delta",
        "ts": datetime.utcnow().isoformat() + "Z",
        "payload": {"event": event_name, **payload},
    }


def make_snapshot(sessions: list, active_account: Optional[dict], watcher_alive: bool) -> dict[str, Any]:
    return {
        "type": "snapshot",
        "ts": datetime.utcnow().isoformat() + "Z",
        "payload": {
            "sessions": sessions,
            "active_account": active_account,
            "watcher_alive": watcher_alive,
        },
    }


# ── Error helpers ─────────────────────────────────────────────────────────────

def error_response(code: str, message: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message}}
