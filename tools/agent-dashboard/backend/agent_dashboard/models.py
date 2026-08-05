"""Pydantic models for REST API request/response bodies and internal dataclasses."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, field_validator


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
    api_key: str

    @field_validator("api_key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not v.startswith("sk-"):
            raise ValueError("API key must start with 'sk-'")
        return v


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
