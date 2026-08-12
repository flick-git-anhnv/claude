"""Failover package — Auto-Failover Anthropic account rotation (Sprint 7).

Sub-modules:
    models    — dataclasses: FailoverEvent, ChainSnapshot
    detector  — usage_poll_loop + jsonl_signal_hook
    engine    — FailoverEngine state machine
    scheduler — wait-and-retry background task
"""
from .engine import FailoverEngine

__all__ = ["FailoverEngine"]
