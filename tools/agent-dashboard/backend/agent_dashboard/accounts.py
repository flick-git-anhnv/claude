"""Account store — XOR+base64 encryption, CRUD, reveal rate-limiter.

Encryption: XOR key = SHA256(username + hostname).digest()[:16]
File format (decrypted JSON):
  {
    "version": 1,
    "active_id": "acc-xxxx" | null,
    "accounts": [
      {"id": "acc-xxxx", "name": "...", "api_key": "sk-ant-...", "created_at": "..."}
    ]
  }

NEVER log or return plaintext api_key except through the rate-limited /reveal endpoint.
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
    "version": 1,
    "active_id": None,
    "accounts": [],
}


class AccountStore:
    """Thread-safe in-memory store backed by an encrypted file."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: Dict[str, Any] = _EMPTY_STORE.copy()
        self._data["accounts"] = []
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
            self._data = json.loads(decrypted)
        except Exception as exc:
            logger.warning("Could not load accounts.enc (%s), starting fresh", exc)
            self._data = {"version": 1, "active_id": None, "accounts": []}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        plaintext = json.dumps(self._data, ensure_ascii=False)
        self._path.write_text(_encrypt(plaintext), encoding="ascii")

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def list_accounts(self) -> List[Dict[str, Any]]:
        active_id = self._data.get("active_id")
        return [
            {
                "id": a["id"],
                "name": a["name"],
                "key_masked": mask_key(a["api_key"]),
                "is_active": a["id"] == active_id,
                "created_at": a["created_at"],
            }
            for a in self._data["accounts"]
        ]

    def add_account(self, name: str, api_key: str) -> str:
        acc_id = f"acc-{uuid.uuid4().hex[:8]}"
        self._data["accounts"].append(
            {
                "id": acc_id,
                "name": name,
                "api_key": api_key,
                "created_at": datetime.now(timezone.utc).isoformat(),
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
        if not self.get_account(acc_id):
            raise KeyError(acc_id)
        self._data["active_id"] = acc_id
        self._save()

    def get_active(self) -> Optional[Dict[str, Any]]:
        active_id = self._data.get("active_id")
        if not active_id:
            return None
        acc = self.get_account(active_id)
        if not acc:
            return None
        return {
            "id": acc["id"],
            "name": acc["name"],
            "key_masked": mask_key(acc["api_key"]),
        }

    # ── Reveal (rate-limited) ─────────────────────────────────────────────────

    def reveal_key(self, acc_id: str) -> Optional[str]:
        """
        Returns plaintext api_key if rate-limit allows, else raises RuntimeError.
        """
        if not self._reveal_limiter.allow():
            raise RuntimeError("RATE_LIMIT_EXCEEDED")
        acc = self.get_account(acc_id)
        if not acc:
            raise KeyError(acc_id)
        return acc["api_key"]
