"""Dataclasses for Failover Engine (Sprint 7).

FailoverState    — engine state machine states (string literals)
TriggerReason    — why a failover was triggered
FailoverResult   — outcome of a failover attempt
ChainSnapshot    — account state snapshot stored per-event in DB
FailoverEvent    — in-memory representation of a logged failover event
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional


# ── State machine states ───────────────────────────────────────────────────────

FailoverState = Literal["idle", "detecting", "swapping", "waiting", "retrying", "paused"]

# ── Trigger reasons ────────────────────────────────────────────────────────────

TriggerReason = Literal[
    "http_429",
    "quota_5h_full",
    "quota_7d_full",
    "jsonl_rate_limit",
    "api_wide_suspected",
    "manual_override",
]

# ── Failover results ───────────────────────────────────────────────────────────

FailoverResult = Literal[
    "success",
    "swap_failed",
    "wait_and_retry_scheduled",
    "wait_and_retry_success",
    "wait_and_retry_failed",
    "api_wide_suspected",
    "retry_cancelled_by_manual",
]

# ── Chain snapshot (per-account, serialised to chain_snapshot_json column) ────

@dataclass
class ChainSnapshot:
    """State of one account at the moment a failover event is recorded.

    SECURITY: Only safe (non-credential) fields are included — this maps
    directly to db.failover.serialize_chain_snapshot() whitelist.
    """
    id: str
    name: str
    priority: int
    include_in_chain: bool
    five_hour_pct: Optional[float] = None
    seven_day_pct: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority,
            "include_in_chain": self.include_in_chain,
            "five_hour_pct": self.five_hour_pct,
            "seven_day_pct": self.seven_day_pct,
        }


@dataclass
class FailoverEvent:
    """In-memory representation before writing to DB."""
    failover_id: str
    occurred_at: str                           # ISO 8601 UTC with ms
    trigger_reason: TriggerReason
    result: FailoverResult
    from_account_id: Optional[str] = None
    from_account_name: Optional[str] = None
    to_account_id: Optional[str] = None
    to_account_name: Optional[str] = None
    swap_latency_ms: Optional[int] = None
    next_retry_at: Optional[str] = None        # ISO 8601 UTC
    retry_attempt: Optional[int] = None        # 1..3
    error_message: Optional[str] = None
    chain_snapshots: List[ChainSnapshot] = field(default_factory=list)
