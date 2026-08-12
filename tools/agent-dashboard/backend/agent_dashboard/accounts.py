"""Account store — XOR+base64 encryption, CRUD, reveal rate-limiter.

Encryption: XOR key = SHA256(username + hostname).digest()[:16]
File format v2 (decrypted JSON):
  {
    "version": 2,
    "active_id": "acc-xxxx" | null,
    "accounts": [
      {
        "id": "acc-xxxx",
        "kind": "api_key",             // "api_key" | "oauth_session"
        "name": "...",
        "api_key": "sk-ant-...",       // only when kind == "api_key"
        "created_at": "..."
      },
      {
        "id": "acc-yyyy",
        "kind": "oauth_session",
        "name": "...",
        "oauth": {                     // snapshot from .credentials.json claudeAiOauth block
          "accessToken": "...",
          "refreshToken": "...",
          "expiresAt": 1735000000000,
          "refreshTokenExpiresAt": 1737500000000,
          "scopes": [...],
          "subscriptionType": "...",
          "rateLimitTier": "..."
        },
        "organizationUuid": "...",     // optional, top-level in .credentials.json
        "needs_relogin": false,
        "last_refreshed_at": "...",
        "created_at": "..."
      }
    ]
  }

NEVER log or return plaintext api_key / accessToken / refreshToken except through
the rate-limited /reveal endpoint (api_key accounts only).
"""
from __future__ import annotations

import base64
import collections
import getpass
import hashlib
import json
import logging
import platform
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Encryption helpers ────────────────────────────────────────────────────────

def _xor_key() -> bytes:
    user = getpass.getuser()
    host = platform.node()
    return hashlib.sha256((user + host).encode()).digest()[:16]


def _encrypt(plaintext: str) -> str:
    key = _xor_key()
    data = plaintext.encode("utf-8")
    encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return base64.b64encode(encrypted).decode("ascii")


def _decrypt(ciphertext: str) -> str:
    key = _xor_key()
    encrypted = base64.b64decode(ciphertext.encode("ascii"))
    decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
    return decrypted.decode("utf-8")


def mask_key(api_key: str) -> str:
    """Return sk-ant-****XXXX (last 4 chars visible)."""
    if len(api_key) < 4:
        return "sk-ant-****"
    return f"sk-ant-api03-****{api_key[-4:]}"


def mask_oauth_token(token: str) -> str:
    """Return sk-ant-****XXXX (last 4 chars visible) for OAuth access/refresh tokens."""
    if len(token) < 4:
        return "sk-ant-****"
    return f"sk-ant-****{token[-4:]}"


# ── Rate limiter ──────────────────────────────────────────────────────────────

class _RevealRateLimiter:
    """Sliding-window rate limiter for the reveal endpoint."""

    def __init__(self, max_calls: int = 5, window_sec: int = 60) -> None:
        self._max = max_calls
        self._window = window_sec
        self._calls: Deque[float] = collections.deque()

    def allow(self) -> bool:
        now = time.monotonic()
        # Purge old entries
        while self._calls and self._calls[0] < now - self._window:
            self._calls.popleft()
        if len(self._calls) >= self._max:
            return False
        self._calls.append(now)
        return True


# ── Account store ─────────────────────────────────────────────────────────────

_EMPTY_STORE: Dict[str, Any] = {
    "version": 2,
    "active_id": None,
    "accounts": [],
}

# Required OAuth fields when importing from .credentials.json
REQUIRED_OAUTH_FIELDS = {"accessToken", "refreshToken", "expiresAt", "refreshTokenExpiresAt"}


class AccountStore:
    """Thread-safe in-memory store backed by an encrypted file."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: Dict[str, Any] = {"version": 2, "active_id": None, "accounts": []}
        self._reveal_limiter = _RevealRateLimiter(
            max_calls=5, window_sec=60
        )
        self._load()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            raw = self._path.read_text(encoding="ascii")
            decrypted = _decrypt(raw)
            data = json.loads(decrypted)
            # Migration v1 → v2
            if data.get("version", 1) == 1:
                data = self._migrate_v1_to_v2(data)
            # Migration v2 → v3 (Sprint 7: priority + include_in_chain)
            if data.get("version", 2) == 2:
                data = self._migrate_v2_to_v3(data)
            self._data = data
        except Exception as exc:
            logger.warning("Could not load accounts.enc (%s), starting fresh", exc)
            self._data = {"version": 3, "active_id": None, "accounts": []}

    def _migrate_v2_to_v3(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add priority + include_in_chain to all accounts; bump version to 3.

        Idempotent: safe to call multiple times — only sets fields that are missing.
        priority default = position in list (1-based, so first account = highest priority).
        include_in_chain default = True.
        """
        accounts = data.get("accounts", [])
        for i, acc in enumerate(accounts):
            if "priority" not in acc:
                acc["priority"] = i + 1
            if "include_in_chain" not in acc:
                acc["include_in_chain"] = True

        data["version"] = 3

        try:
            plaintext = json.dumps(data, ensure_ascii=False)
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(_encrypt(plaintext), encoding="ascii")
            logger.info(
                "Migration v2→v3: %d accounts upgraded (priority + include_in_chain)",
                len(accounts),
            )
        except Exception as save_err:
            logger.warning("Migration v2→v3: save failed (%s)", save_err)

        return data

    def _migrate_v1_to_v2(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add kind='api_key' discriminator to all v1 records; bump version to 2.

        Idempotent: safe to call multiple times. Creates accounts.v1.bak before
        writing the upgraded file (so user can restore if something goes wrong).
        """
        # Backup the current (v1) encrypted file before upgrading
        bak_path = self._path.with_suffix(".v1.bak")
        try:
            if self._path.exists():
                bak_path.write_text(self._path.read_text(encoding="ascii"), encoding="ascii")
                logger.info("Migration v1→v2: backed up accounts.enc → %s", bak_path)
        except Exception as bak_err:
            logger.warning("Migration v1→v2: backup failed (%s), continuing anyway", bak_err)

        # Add kind discriminator to all existing records
        for acc in data.get("accounts", []):
            if "kind" not in acc:
                acc["kind"] = "api_key"

        data["version"] = 2

        # Persist migrated data
        try:
            plaintext = json.dumps(data, ensure_ascii=False)
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(_encrypt(plaintext), encoding="ascii")
            logger.info(
                "Migration v1→v2: %d accounts upgraded, saved to %s",
                len(data.get("accounts", [])),
                self._path,
            )
        except Exception as save_err:
            logger.warning("Migration v1→v2: save failed (%s)", save_err)

        return data

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        plaintext = json.dumps(self._data, ensure_ascii=False)
        self._path.write_text(_encrypt(plaintext), encoding="ascii")

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _safe_expires_in_sec(self, expires_at_ms: int) -> int:
        """Convert millisecond UNIX timestamp to seconds remaining (clamped to 0)."""
        now_ms = int(time.time() * 1000)
        return max(0, (expires_at_ms - now_ms) // 1000)

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def _name_exists(self, name: str) -> bool:
        """Return True if any existing account has the same name (case-insensitive)."""
        return any(a["name"].lower() == name.lower() for a in self._data["accounts"])

    def list_accounts(self) -> List[Dict[str, Any]]:
        active_id = self._data.get("active_id")
        result = []
        for a in self._data["accounts"]:
            kind = a.get("kind", "api_key")
            entry: Dict[str, Any] = {
                "id": a["id"],
                "kind": kind,
                "name": a["name"],
                "is_active": a["id"] == active_id,
                "created_at": a["created_at"],
            }
            if kind == "api_key":
                entry["key_masked"] = mask_key(a.get("api_key", ""))
            else:  # oauth_session
                oauth = a.get("oauth", {})
                access_token = oauth.get("accessToken", "")
                entry["oauth_masked"] = mask_oauth_token(access_token)
                entry["needs_relogin"] = a.get("needs_relogin", False)
                entry["last_refreshed_at"] = a.get("last_refreshed_at")
                expires_at_ms = oauth.get("expiresAt", 0)
                rt_expires_ms = oauth.get("refreshTokenExpiresAt", 0)
                entry["expires_in_sec"] = self._safe_expires_in_sec(expires_at_ms)
                entry["refresh_expires_in_sec"] = self._safe_expires_in_sec(rt_expires_ms)
            result.append(entry)
        return result

    def add_account(self, name: str, api_key: str) -> str:
        """Add an API-key account. Returns the new account id.

        Raises ValueError("ACCOUNT_NAME_DUPLICATE") if name already exists
        (case-insensitive).
        """
        if self._name_exists(name):
            raise ValueError("ACCOUNT_NAME_DUPLICATE")
        acc_id = f"acc-{uuid.uuid4().hex[:8]}"
        self._data["accounts"].append(
            {
                "id": acc_id,
                "kind": "api_key",
                "name": name,
                "api_key": api_key,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._save()
        return acc_id

    def add_oauth_account(self, name: str, oauth_block: Dict[str, Any], org_uuid: Optional[str]) -> str:
        """Add an OAuth-session account from a .credentials.json snapshot.

        Raises ValueError("ACCOUNT_NAME_DUPLICATE") if name already exists
        (case-insensitive).

        Sprint 7: new accounts automatically get priority = len(accounts) + 1
        (lowest priority — appended to chain tail) and include_in_chain = True.
        """
        if self._name_exists(name):
            raise ValueError("ACCOUNT_NAME_DUPLICATE")
        missing = REQUIRED_OAUTH_FIELDS - set(oauth_block.keys())
        if missing:
            raise ValueError(f"OAUTH_SNAPSHOT_INVALID: missing fields {missing}")

        acc_id = f"acc-{uuid.uuid4().hex[:8]}"
        default_priority = len(self._data["accounts"]) + 1
        self._data["accounts"].append(
            {
                "id": acc_id,
                "kind": "oauth_session",
                "name": name,
                "oauth": dict(oauth_block),  # store a copy
                "organizationUuid": org_uuid,
                "needs_relogin": False,
                "last_refreshed_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                # Sprint 7: failover chain fields
                "priority": default_priority,
                "include_in_chain": True,
            }
        )
        self._save()
        return acc_id

    def get_account(self, acc_id: str) -> Optional[Dict[str, Any]]:
        for a in self._data["accounts"]:
            if a["id"] == acc_id:
                return a
        return None

    def update_account(self, acc_id: str, name: str) -> bool:
        for a in self._data["accounts"]:
            if a["id"] == acc_id:
                a["name"] = name
                self._save()
                return True
        return False

    def update_oauth_snapshot(
        self,
        acc_id: str,
        oauth_block: Dict[str, Any],
        org_uuid: Optional[str],
    ) -> bool:
        """Replace oauth snapshot for an oauth_session account (called after successful refresh)."""
        for a in self._data["accounts"]:
            if a["id"] == acc_id and a.get("kind") == "oauth_session":
                a["oauth"] = dict(oauth_block)
                if org_uuid is not None:
                    a["organizationUuid"] = org_uuid
                a["last_refreshed_at"] = datetime.now(timezone.utc).isoformat()
                a["needs_relogin"] = False
                self._save()
                return True
        return False

    def set_needs_relogin(self, acc_id: str) -> bool:
        """Mark an oauth account as needing manual re-login."""
        for a in self._data["accounts"]:
            if a["id"] == acc_id and a.get("kind") == "oauth_session":
                a["needs_relogin"] = True
                self._save()
                return True
        return False

    # ── Sprint 7: Failover chain management ──────────────────────────────────

    def set_priority(self, acc_id: str, priority: int) -> bool:
        """Set failover priority for an account.  Lower number = higher priority.

        Returns True on success, False if account not found.
        Raises ValueError if priority < 1.
        """
        if priority < 1:
            raise ValueError("Priority must be >= 1")
        for a in self._data["accounts"]:
            if a["id"] == acc_id:
                a["priority"] = priority
                self._save()
                return True
        return False

    def set_include_in_chain(self, acc_id: str, include: bool) -> bool:
        """Toggle whether an account participates in the failover chain.

        Returns True on success, False if account not found.
        Raises ValueError("CHAIN_MUST_HAVE_ONE_INCLUDED") if this would leave
        zero included OAuth accounts in the chain.
        """
        for a in self._data["accounts"]:
            if a["id"] == acc_id:
                if not include:
                    # Guard: at least 1 included must remain
                    included_count = sum(
                        1 for x in self._data["accounts"]
                        if x.get("kind") == "oauth_session"
                        and x.get("include_in_chain", True)
                        and x["id"] != acc_id
                    )
                    if included_count == 0:
                        raise ValueError("CHAIN_MUST_HAVE_ONE_INCLUDED")
                a["include_in_chain"] = include
                self._save()
                return True
        return False

    def get_failover_chain(self) -> List[Dict[str, Any]]:
        """Return OAuth accounts eligible for failover, sorted by priority (ascending).

        Filters:
          - kind == "oauth_session"
          - include_in_chain == True
          - needs_relogin == False

        Returns list of raw account dicts (mutable — callers should not mutate).
        """
        chain = [
            a for a in self._data["accounts"]
            if a.get("kind") == "oauth_session"
            and a.get("include_in_chain", True)
            and not a.get("needs_relogin", False)
        ]
        chain.sort(key=lambda a: a.get("priority", 999))
        return chain

    def delete_account(self, acc_id: str) -> None:
        """Raises ValueError if account is currently active."""
        if self._data.get("active_id") == acc_id:
            raise ValueError("ACCOUNT_ACTIVE_CANNOT_DELETE")
        before = len(self._data["accounts"])
        self._data["accounts"] = [a for a in self._data["accounts"] if a["id"] != acc_id]
        if len(self._data["accounts"]) == before:
            raise KeyError(acc_id)
        self._save()

    def activate(self, acc_id: str) -> None:
        """Record acc_id as the active account (pure storage, no credential file I/O)."""
        if not self.get_account(acc_id):
            raise KeyError(acc_id)
        self._data["active_id"] = acc_id
        self._save()

    def get_active(self) -> Optional[Dict[str, Any]]:
        """Return masked summary of the active account, or None."""
        active_id = self._data.get("active_id")
        if not active_id:
            return None
        acc = self.get_account(active_id)
        if not acc:
            return None
        kind = acc.get("kind", "api_key")
        result: Dict[str, Any] = {"id": acc["id"], "name": acc["name"], "kind": kind}
        if kind == "api_key":
            result["key_masked"] = mask_key(acc.get("api_key", ""))
        else:
            oauth = acc.get("oauth", {})
            result["oauth_masked"] = mask_oauth_token(oauth.get("accessToken", ""))
        return result

    def get_oauth_status(self, acc_id: str) -> Optional[Dict[str, Any]]:
        """Return OAuth token status for one account."""
        acc = self.get_account(acc_id)
        if not acc or acc.get("kind") != "oauth_session":
            return None
        oauth = acc.get("oauth", {})
        return {
            "expires_in_sec": self._safe_expires_in_sec(oauth.get("expiresAt", 0)),
            "refresh_expires_in_sec": self._safe_expires_in_sec(oauth.get("refreshTokenExpiresAt", 0)),
            "needs_relogin": acc.get("needs_relogin", False),
            "last_refreshed_at": acc.get("last_refreshed_at"),
        }

    # ── Reveal (rate-limited, api_key accounts only) ──────────────────────────

    def reveal_key(self, acc_id: str) -> Optional[str]:
        """
        Returns plaintext api_key if rate-limit allows, else raises RuntimeError.
        Only valid for kind='api_key' accounts.
        """
        if not self._reveal_limiter.allow():
            raise RuntimeError("RATE_LIMIT_EXCEEDED")
        acc = self.get_account(acc_id)
        if not acc:
            raise KeyError(acc_id)
        if acc.get("kind", "api_key") != "api_key":
            raise ValueError("REVEAL_NOT_SUPPORTED_FOR_OAUTH")
        return acc["api_key"]
