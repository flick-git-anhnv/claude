"""Configuration — all tunables in one place. Override via environment variables."""
from __future__ import annotations

import os
import pathlib
import sys

# ── Server ────────────────────────────────────────────────────────────────────
DASHBOARD_PORT: int = int(os.getenv("DASHBOARD_PORT", "7770"))
DASHBOARD_HOST: str = os.getenv("DASHBOARD_HOST", "0.0.0.0")

# ── State machine thresholds (seconds) ───────────────────────────────────────
IDLE_THRESHOLD_SEC: int = int(os.getenv("IDLE_THRESHOLD_SEC", "300"))    # 5 min
ENDED_THRESHOLD_SEC: int = int(os.getenv("ENDED_THRESHOLD_SEC", "1800"))  # 30 min

# ── Paths — use pathlib, NO hardcoded backslashes ────────────────────────────
_home = pathlib.Path.home()

# Windows: prefer USERPROFILE env var (same as Path.home() on modern Python,
# but explicit for clarity)
if sys.platform == "win32" and os.getenv("USERPROFILE"):
    _home = pathlib.Path(os.environ["USERPROFILE"])

CLAUDE_PROJECTS_DIR: pathlib.Path = _home / ".claude" / "projects"

# Resolve data dir relative to this package's parent (backend/)
_backend_dir = pathlib.Path(__file__).parent.parent
DATA_DIR: pathlib.Path = pathlib.Path(os.getenv("DATA_DIR", str(_backend_dir / "data")))
DB_PATH: pathlib.Path = DATA_DIR / "dashboard.db"
ACCOUNTS_FILE: pathlib.Path = DATA_DIR / "accounts.enc"

# ── Watcher ───────────────────────────────────────────────────────────────────
# Polling interval for watchdog PollingObserver (Windows fallback), ms
POLLING_INTERVAL_MS: int = int(os.getenv("POLLING_INTERVAL_MS", "500"))

# ── WebSocket / state ticker ──────────────────────────────────────────────────
STATE_TICKER_INTERVAL_SEC: int = int(os.getenv("STATE_TICKER_INTERVAL_SEC", "30"))

# ── Account reveal rate-limit ─────────────────────────────────────────────────
REVEAL_RATE_LIMIT_COUNT: int = 5   # max calls
REVEAL_RATE_LIMIT_WINDOW: int = 60  # per N seconds

# ── OAuth / credentials ───────────────────────────────────────────────────────
# Claude Code stores OAuth tokens in this file (Windows/macOS/Linux)
CLAUDE_CREDENTIALS_FILE: pathlib.Path = _home / ".claude" / ".credentials.json"

# Auto-refresh: run every N seconds; skip account if token lifetime ratio < 20% or < 30 min left
OAUTH_REFRESH_INTERVAL_SEC: int = int(os.getenv("OAUTH_REFRESH_INTERVAL_SEC", "1800"))
OAUTH_REFRESH_AHEAD_RATIO: float = 0.20   # refresh when <20% of token lifetime remains
OAUTH_REFRESH_MIN_AHEAD_MS: int = 30 * 60 * 1000  # or <30 min (in milliseconds)
