"""Usage service — fetch Anthropic API quota usage via REST (Sprint 5 / FR-A).

Endpoint: GET https://api.anthropic.com/api/oauth/usage
Auth    : Authorization: Bearer <oauth_access_token>
Cache   : in-memory dict {account_id → (expires_at_unix, UsageInfo)}, TTL = 60 s.

Only OAuth accounts have Anthropic session quota. API-key accounts return
``error="api_key"`` without an HTTP call.
"""
from __future__ import annotations

import time
from typing import Optional, TypedDict

import httpx

USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
CACHE_TTL = 60.0    # seconds — matches frontend polling interval
HTTP_TIMEOUT = 5.0  # seconds — same as bundled claude SDK default


class UsageInfo(TypedDict, total=False):
    """Usage quota snapshot for one OAuth account."""

    account_id: str
    five_hour_pct: Optional[float]       # 0..100, or None if not available
    seven_day_pct: Optional[float]
    seven_day_opus_pct: Optional[float]
    seven_day_sonnet_pct: Optional[float]
    resets_at: Optional[int]             # unix seconds — 5-hour window reset
    seven_day_resets_at: Optional[int]   # unix seconds — 7-day window reset
    rate_limit_type: Optional[str]       # "five_hour" | "seven_day" | …
    overage_status: Optional[str]
    fetched_at: int                      # unix seconds — when this snapshot was taken
    error: Optional[str]                 # "api_key" | "no_oauth" | "unauthorized"
    #                                      "timeout" | "network" | "http_NNN"


# {account_id: (cache_expires_at_unix, UsageInfo)}
_cache: dict[str, tuple[float, UsageInfo]] = {}


async def get_usage(
    account_id: str,
    access_token: str,
    *,
    force: bool = False,
) -> UsageInfo:
    """Return UsageInfo for *account_id*, using cached result when fresh.

    Args:
        account_id:   Unique account identifier (used as cache key).
        access_token: OAuth Bearer token from AccountStore.
        force:        When True, bypass cache and always call the API.

    Returns:
        UsageInfo dict. On error, ``error`` key is set and percentage fields
        are absent (callers should treat missing pct fields as None).
    """
    now = time.time()
    if not force:
        cached = _cache.get(account_id)
        if cached and cached[0] > now:
            return cached[1]

    info: UsageInfo = {"account_id": account_id, "fetched_at": int(now)}
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            r = await client.get(
                USAGE_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )
        if r.status_code == 401:
            info["error"] = "unauthorized"
        elif r.status_code >= 500:
            info["error"] = f"http_{r.status_code}"
        elif r.status_code != 200:
            info["error"] = f"http_{r.status_code}"
        else:
            data = r.json()
            info["five_hour_pct"]         = _pct(data.get("five_hour"))
            info["seven_day_pct"]         = _pct(data.get("seven_day"))
            info["seven_day_opus_pct"]    = _pct(data.get("seven_day_opus"))
            info["seven_day_sonnet_pct"]  = _pct(data.get("seven_day_sonnet"))
            info["resets_at"]             = data.get("resets_at")
            info["seven_day_resets_at"]   = data.get("seven_day_resets_at")
            info["rate_limit_type"]       = data.get("rate_limit_type")
            info["overage_status"]        = data.get("overage_status")
    except httpx.TimeoutException:
        info["error"] = "timeout"
    except httpx.HTTPError:
        info["error"] = "network"

    _cache[account_id] = (now + CACHE_TTL, info)
    return info


def invalidate_cache(account_id: Optional[str] = None) -> None:
    """Invalidate the in-memory cache.

    Args:
        account_id: When given, evict only that account's entry.
                    When None, clear the entire cache.
    """
    if account_id is None:
        _cache.clear()
    else:
        _cache.pop(account_id, None)


def _pct(v: object) -> Optional[float]:
    """Convert a raw API utilisation value to a 0..100 percentage.

    The Anthropic API appears to return values in 0..1 ratio form based on the
    SDK source (verified via binary analysis of claude.exe). We handle both
    0..1 and 0..100 defensively: if the value is ≤ 1.0 we treat it as a ratio
    and multiply by 100.
    """
    if v is None:
        return None
    try:
        f = float(v)  # type: ignore[arg-type]
        return round(f * 100, 1) if f <= 1.0 else round(f, 1)
    except (TypeError, ValueError):
        return None
