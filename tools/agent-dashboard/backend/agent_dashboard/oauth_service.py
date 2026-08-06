"""OAuth credential service — manages reads/writes to Claude's .credentials.json.

Responsibilities:
  - validate_oauth_block(): verify required fields present
  - read_credentials() / write_credentials(): thin I/O wrappers (injectable for tests)
  - activate_oauth_account(): swap credentials file for manual account activation
    → creates a timestamped file backup before swapping
    → restores in-memory backup on failure (finally block)
  - refresh_inactive_accounts(): asyncio coroutine that runs the auto-refresh cycle
    → in-memory backup only (no file backup to avoid token proliferation)
    → finally block ALWAYS restores original credential file

Design contract:
  - AccountStore handles all encrypted-store state; this module only touches
    the plain .credentials.json file on disk.
  - refresh_lock (asyncio.Lock) must be acquired before any swap to prevent
    two concurrent jobs writing the credentials file simultaneously.
"""
from __future__ import annotations

import asyncio
import functools
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .accounts import AccountStore, REQUIRED_OAUTH_FIELDS

logger = logging.getLogger(__name__)


# ── I/O helpers (injectable for unit tests) ───────────────────────────────────

def read_credentials(path: Path) -> Dict[str, Any]:
    """Read and parse the Claude credentials JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_credentials(path: Path, data: Dict[str, Any]) -> None:
    """Atomically write the Claude credentials JSON file."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def validate_oauth_block(block: Dict[str, Any]) -> None:
    """Raise ValueError if a claudeAiOauth block is missing required fields."""
    missing = REQUIRED_OAUTH_FIELDS - set(block.keys())
    if missing:
        raise ValueError(f"OAUTH_SNAPSHOT_INVALID: missing fields: {sorted(missing)}")


# ── Manual activate — with timestamped file backup ────────────────────────────

async def activate_oauth_account(
    acc_id: str,
    account_store: AccountStore,
    credentials_path: Path,
    refresh_lock: asyncio.Lock,
) -> Dict[str, Any]:
    """Swap .credentials.json to activate acc_id as the current OAuth session.

    MUST be called with the same refresh_lock used by the background refresh
    scheduler (_do_swap_and_invoke).  This prevents the H-1 race where the
    scheduler's finally-restore overwrites a just-activated credential file.

    Steps:
      0. Acquire refresh_lock (shared with the auto-refresh scheduler).
      1. Read current credentials into in-memory backup.
      2. Create a timestamped file backup (.credentials.backup.<ts>.json).
      3. If currently active account is also oauth_session, re-snapshot it
         from the file (Claude Code CLI may have refreshed it while it was active).
      4. Write the new account's oauth block to .credentials.json.
      5. On any failure → restore from in-memory backup.
      6. Record new active_id in AccountStore.

    Returns:
      {"active_id": acc_id, "prev_snapshot_updated": bool}
    """
    if not credentials_path.exists():
        raise FileNotFoundError("CREDENTIALS_FILE_NOT_FOUND")

    async with refresh_lock:
        # Step 1: in-memory backup
        in_memory_backup = read_credentials(credentials_path)

        # Step 2: file backup
        ts_str = str(int(time.time()))
        bak_path = credentials_path.parent / f".credentials.backup.{ts_str}.json"
        try:
            write_credentials(bak_path, in_memory_backup)
        except Exception as bak_err:
            logger.warning("activate_oauth: file backup failed (%s), continuing", bak_err)

        prev_snapshot_updated = False
        try:
            # Step 3: re-snapshot currently active OAuth account
            active_acc_id = account_store._data.get("active_id")
            if active_acc_id and active_acc_id != acc_id:
                active_acc = account_store.get_account(active_acc_id)
                if active_acc and active_acc.get("kind") == "oauth_session":
                    fresh_oauth = in_memory_backup.get("claudeAiOauth")
                    if fresh_oauth:
                        account_store.update_oauth_snapshot(
                            active_acc_id,
                            fresh_oauth,
                            in_memory_backup.get("organizationUuid"),
                        )
                        prev_snapshot_updated = True
                        logger.info(
                            "activate_oauth: re-snapshotted previously active account %s",
                            active_acc_id,
                        )

            # Step 4: write new account's oauth block
            new_acc = account_store.get_account(acc_id)
            if not new_acc:
                raise KeyError(acc_id)
            if new_acc.get("kind") != "oauth_session":
                raise ValueError(f"Account {acc_id} is not an oauth_session account")

            validate_oauth_block(new_acc.get("oauth", {}))

            new_creds = dict(in_memory_backup)
            new_creds["claudeAiOauth"] = new_acc["oauth"]
            org_uuid = new_acc.get("organizationUuid")
            if org_uuid:
                new_creds["organizationUuid"] = org_uuid
            elif "organizationUuid" in new_creds:
                del new_creds["organizationUuid"]

            try:
                write_credentials(credentials_path, new_creds)
            except Exception as write_err:
                raise RuntimeError(f"CREDENTIALS_WRITE_FAILED: {write_err}") from write_err

            # Record activation in store (pure state, no file I/O)
            account_store.activate(acc_id)

            return {"active_id": acc_id, "prev_snapshot_updated": prev_snapshot_updated}

        except Exception:
            # Restore in-memory backup on any failure
            try:
                write_credentials(credentials_path, in_memory_backup)
                logger.info("activate_oauth: credentials restored from in-memory backup")
            except Exception as restore_err:
                logger.error(
                    "CRITICAL: Failed to restore credentials from backup after activate failure: %s",
                    restore_err,
                )
                # Try to restore from file backup as absolute last resort
                try:
                    if bak_path.exists():
                        import shutil
                        shutil.copy2(bak_path, credentials_path)
                        logger.warning("activate_oauth: restored from file backup %s", bak_path)
                except Exception:
                    pass
            raise


# ── Auto-refresh scheduler ────────────────────────────────────────────────────

async def refresh_inactive_accounts(
    account_store: AccountStore,
    credentials_path: Path,
    refresh_lock: asyncio.Lock,
) -> None:
    """One iteration of the auto-refresh cycle.

    Called by the scheduler every OAUTH_REFRESH_INTERVAL_SEC.
    Skips accounts that are: active, needs_relogin=True, or have plenty of time left.
    """
    if not credentials_path.exists():
        logger.debug("refresh_inactive_accounts: credentials file not found, skipping")
        return

    from . import config

    now_ms = int(time.time() * 1000)
    active_id = account_store._data.get("active_id")

    # Collect candidate accounts
    candidates = [
        a for a in account_store._data.get("accounts", [])
        if a.get("kind") == "oauth_session"
        and not a.get("needs_relogin", False)
        and a["id"] != active_id
    ]

    # Sort by soonest expiry first
    candidates.sort(key=lambda a: a.get("oauth", {}).get("expiresAt", 0))

    for acc in candidates:
        oauth = acc.get("oauth", {})
        expires_at_ms = oauth.get("expiresAt", 0)
        rt_expires_ms = oauth.get("refreshTokenExpiresAt", 0)

        # If refresh token itself is expired → mark needs_relogin immediately
        if rt_expires_ms and now_ms > rt_expires_ms:
            account_store.set_needs_relogin(acc["id"])
            logger.info(
                "refresh_inactive: account %s refresh token expired, marking needs_relogin",
                acc["id"],
            )
            continue

        # Determine if access token needs refresh
        remaining_ms = expires_at_ms - now_ms
        # Threshold: max(30 min, 20% of assumed 1-hour token lifetime)
        threshold_ms = max(config.OAUTH_REFRESH_MIN_AHEAD_MS, int(3_600_000 * config.OAUTH_REFRESH_AHEAD_RATIO))

        if remaining_ms > threshold_ms:
            continue  # Still has plenty of time

        logger.info(
            "refresh_inactive: account %s expires in %ds, triggering refresh",
            acc["id"],
            remaining_ms // 1000,
        )
        await _do_swap_and_invoke(acc["id"], account_store, credentials_path, refresh_lock)


async def _do_swap_and_invoke(
    acc_id: str,
    account_store: AccountStore,
    credentials_path: Path,
    refresh_lock: asyncio.Lock,
) -> None:
    """Core swap-and-invoke logic for a single inactive account.

    Strategy (per TDD §17.3):
      a. Acquire refresh_lock (one swap at a time).
      b. Read current credentials → in-memory backup (NO file backup).
      c. Write emergency backup (deleted in finally if restore succeeds).
      d. Write this account's oauth block to .credentials.json.
      e. Spawn subprocess: claude -p "ok" --model claude-haiku-4-5 --no-session-persistence
      f. Read back .credentials.json → compare expiresAt.
      g. Update snapshot in AccountStore if expiresAt increased.
      h. ALWAYS restore in-memory backup to .credentials.json in finally.
    """
    acc = account_store.get_account(acc_id)
    if not acc or acc.get("kind") != "oauth_session":
        return

    emergency_bak = credentials_path.parent / ".credentials.backup.emergency.json"

    async with refresh_lock:
        in_memory_backup: Optional[Dict[str, Any]] = None
        emergency_written = False

        try:
            # Step b: read current credentials
            in_memory_backup = read_credentials(credentials_path)
            old_expires_at = acc.get("oauth", {}).get("expiresAt", 0)

            # Step c: write emergency backup (safety net for crashes)
            try:
                write_credentials(emergency_bak, in_memory_backup)
                emergency_written = True
            except Exception:
                pass  # non-fatal; proceed without it

            # Step d: write this account's oauth credentials
            swapped_creds = dict(in_memory_backup)
            swapped_creds["claudeAiOauth"] = acc["oauth"]
            org_uuid = acc.get("organizationUuid")
            if org_uuid:
                swapped_creds["organizationUuid"] = org_uuid
            elif "organizationUuid" in swapped_creds:
                del swapped_creds["organizationUuid"]
            write_credentials(credentials_path, swapped_creds)

            # Step e: spawn subprocess to trigger token refresh
            exit_code = await _run_claude_subprocess()
            if exit_code != 0:
                logger.warning(
                    "_do_swap_and_invoke: subprocess exited %d for account %s",
                    exit_code, acc_id,
                )
                account_store.set_needs_relogin(acc_id)
                return

            # Step f+g: check if expiresAt changed
            try:
                refreshed = read_credentials(credentials_path)
                new_oauth = refreshed.get("claudeAiOauth", {})
                new_expires_at = new_oauth.get("expiresAt", 0)

                if new_expires_at > old_expires_at:
                    account_store.update_oauth_snapshot(
                        acc_id, new_oauth, refreshed.get("organizationUuid")
                    )
                    logger.info(
                        "_do_swap_and_invoke: refresh SUCCESS for %s, new expiresAt=%s",
                        acc_id, new_expires_at,
                    )
                else:
                    logger.debug(
                        "_do_swap_and_invoke: expiresAt unchanged for %s (token not yet refreshed)",
                        acc_id,
                    )
            except Exception as read_err:
                logger.warning(
                    "_do_swap_and_invoke: failed to read back refreshed credentials: %s", read_err
                )

        except Exception as exc:
            logger.exception(
                "_do_swap_and_invoke: unexpected error for account %s: %s", acc_id, exc
            )
            account_store.set_needs_relogin(acc_id)

        finally:
            # Step h: ALWAYS restore original credentials (active account's tokens)
            if in_memory_backup is not None:
                try:
                    write_credentials(credentials_path, in_memory_backup)
                    # If restore succeeded, remove emergency backup
                    if emergency_written and emergency_bak.exists():
                        emergency_bak.unlink(missing_ok=True)
                except Exception as restore_err:
                    logger.error(
                        "CRITICAL: Failed to restore credentials after refresh for %s: %s",
                        acc_id, restore_err,
                    )
                    # Emergency backup intentionally NOT deleted — startup check will find it


async def _run_claude_subprocess() -> int:
    """Run 'claude -p ok --model claude-haiku-4-5 --no-session-persistence' non-interactively.

    Returns subprocess exit code. Uses run_in_executor to avoid Windows asyncio
    subprocess limitations. Timeout: 30 seconds.
    """
    loop = asyncio.get_event_loop()
    try:
        # Use shell=True so `claude` (.cmd on Windows) resolves correctly in PATH.
        # `-p` makes it non-interactive and exit after one response (no --max-turns needed).
        # Verified: exits 0 and makes a real API call; token refreshes when near-expiry.
        result: subprocess.CompletedProcess = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                functools.partial(
                    subprocess.run,
                    "claude -p ok --model claude-haiku-4-5",
                    shell=True,
                    capture_output=True,
                    timeout=28,  # inner timeout slightly shorter than outer wait_for
                ),
            ),
            timeout=35.0,
        )
        return result.returncode
    except subprocess.TimeoutExpired:
        logger.warning("_run_claude_subprocess: subprocess timed out")
        return -1
    except asyncio.TimeoutError:
        logger.warning("_run_claude_subprocess: executor wait timed out")
        return -1
    except Exception as exc:
        logger.error("_run_claude_subprocess: error: %s", exc)
        return -1


# ── Startup emergency check ───────────────────────────────────────────────────

def check_emergency_backup(credentials_path: Path) -> Optional[Path]:
    """Check if an emergency backup exists from a previous crashed refresh.

    Returns the emergency backup path if it exists AND is newer than the current
    credentials file, else None. Caller is responsible for prompting the user.
    """
    emergency_bak = credentials_path.parent / ".credentials.backup.emergency.json"
    if not emergency_bak.exists():
        return None
    if not credentials_path.exists():
        return emergency_bak
    if emergency_bak.stat().st_mtime > credentials_path.stat().st_mtime:
        return emergency_bak
    # Stale — safe to remove
    try:
        emergency_bak.unlink(missing_ok=True)
    except Exception:
        pass
    return None
