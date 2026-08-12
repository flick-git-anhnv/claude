"""Unit tests for OAuth account support (Track A Sprint 2).

Coverage:
- Migration v1→v2: idempotent, creates backup, adds kind discriminator
- mask_oauth_token: never exposes full token
- add_oauth_account: stores snapshot, validates required fields
- list_accounts: OAuth-specific fields returned; raw tokens never leaked
- update_oauth_snapshot: replaces oauth block, bumps last_refreshed_at
- set_needs_relogin: sets flag, persists
- get_oauth_status: returns remaining-seconds counters
- activate: pure AccountStore.activate() still works unchanged
- backup/restore logic in oauth_service (file I/O mocked)
- refresh scheduler: skips active, skips needs_relogin, marks needs_relogin on subprocess fail
"""
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent_dashboard.accounts import (
    AccountStore,
    mask_oauth_token,
    REQUIRED_OAUTH_FIELDS,
)
from agent_dashboard.oauth_service import (
    activate_oauth_account,
    read_credentials,
    refresh_inactive_accounts,
    validate_oauth_block,
    write_credentials,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_oauth_block(expires_at: int = 9_999_999_999_000) -> dict:
    """Return a minimal valid claudeAiOauth block."""
    return {
        "accessToken": "sk-ant-oauth-ACCESSTOKEN-abcdef",
        "refreshToken": "sk-ant-oauth-REFRESHTOKEN-abcdef",
        "expiresAt": expires_at,
        "refreshTokenExpiresAt": expires_at + 30 * 24 * 3600 * 1000,
        "scopes": ["user:inference"],
        "subscriptionType": "pro",
        "rateLimitTier": "standard",
    }


def _make_credentials_file(tmp_path: Path, oauth_block: dict | None = None) -> Path:
    creds_path = tmp_path / ".credentials.json"
    data: dict = {}
    if oauth_block is not None:
        data["claudeAiOauth"] = oauth_block
    creds_path.write_text(json.dumps(data), encoding="utf-8")
    return creds_path


@pytest.fixture
def store(tmp_path) -> AccountStore:
    return AccountStore(tmp_path / "accounts.enc")


@pytest.fixture
def v1_store_path(tmp_path) -> Path:
    """Create a v1-format accounts.enc file on disk."""
    from agent_dashboard.accounts import _encrypt
    v1_data = {
        "version": 1,
        "active_id": None,
        "accounts": [
            {"id": "acc-aaa", "name": "Old Account", "api_key": "sk-ant-old-key-0001", "created_at": "2024-01-01T00:00:00Z"},
        ],
    }
    path = tmp_path / "accounts.enc"
    path.write_text(_encrypt(json.dumps(v1_data)), encoding="ascii")
    return path


# ── Token masking ─────────────────────────────────────────────────────────────

def test_mask_oauth_token_last4():
    tok = "sk-ant-oauth-abcdefghijklmn1234"
    assert mask_oauth_token(tok).endswith("1234")
    assert "abcdefghijklmn" not in mask_oauth_token(tok)


def test_mask_oauth_token_short():
    assert "****" in mask_oauth_token("sk")


# ── Migration v1 → v2 ─────────────────────────────────────────────────────────

def test_migration_adds_kind_api_key(v1_store_path):
    """Loading a v1 store upgrades all accounts to kind='api_key'."""
    store = AccountStore(v1_store_path)
    acc = store.get_account("acc-aaa")
    assert acc is not None
    assert acc["kind"] == "api_key"


def test_migration_version_bumped(v1_store_path):
    store = AccountStore(v1_store_path)
    # v1 stores cascade through every migration to the current version (v3 — Sprint 7 added priority/include_in_chain).
    assert store._data["version"] == 3


def test_migration_creates_backup(v1_store_path):
    bak = v1_store_path.with_suffix(".v1.bak")
    assert not bak.exists()
    AccountStore(v1_store_path)
    assert bak.exists()


def test_migration_idempotent(v1_store_path):
    """Running migration twice produces the same result, no duplicate backups needed."""
    store1 = AccountStore(v1_store_path)
    # Reload: should not re-migrate (version == 2 now)
    store2 = AccountStore(v1_store_path)
    accounts = store2.list_accounts()
    assert len(accounts) == 1
    assert accounts[0]["kind"] == "api_key"


def test_migration_preserves_accounts(v1_store_path):
    store = AccountStore(v1_store_path)
    acc = store.get_account("acc-aaa")
    assert acc["name"] == "Old Account"
    assert acc["api_key"] == "sk-ant-old-key-0001"


# ── add_oauth_account ─────────────────────────────────────────────────────────

def test_add_oauth_account_stores_snapshot(store):
    oauth = _make_oauth_block()
    acc_id = store.add_oauth_account("KZTEK OAuth", oauth, "org-uuid-123")
    acc = store.get_account(acc_id)
    assert acc is not None
    assert acc["kind"] == "oauth_session"
    assert acc["oauth"]["accessToken"] == oauth["accessToken"]
    assert acc["organizationUuid"] == "org-uuid-123"
    assert acc["needs_relogin"] is False


def test_add_oauth_account_missing_required_fields(store):
    bad_oauth = {"accessToken": "sk-ant-x"}  # missing 3 fields
    with pytest.raises(ValueError, match="OAUTH_SNAPSHOT_INVALID"):
        store.add_oauth_account("Bad", bad_oauth, None)


def test_add_oauth_account_no_org_uuid(store):
    acc_id = store.add_oauth_account("No Org", _make_oauth_block(), None)
    acc = store.get_account(acc_id)
    assert acc["organizationUuid"] is None


# ── list_accounts — raw tokens never leaked ───────────────────────────────────

def test_list_accounts_no_raw_access_token(store):
    store.add_oauth_account("Sec Test", _make_oauth_block(), None)
    for entry in store.list_accounts():
        if entry["kind"] == "oauth_session":
            assert "accessToken" not in entry
            assert "refreshToken" not in entry
            assert "oauth" not in entry


def test_list_accounts_oauth_masked_field(store):
    acc_id = store.add_oauth_account("Masked", _make_oauth_block(), None)
    entries = store.list_accounts()
    entry = next(e for e in entries if e["id"] == acc_id)
    assert "oauth_masked" in entry
    # Must not contain the raw token middle section
    assert "ACCESSTOKEN-abcdef" not in entry["oauth_masked"]


def test_list_accounts_api_key_unaffected(store):
    """Existing api_key accounts still return key_masked, unaffected by OAuth."""
    store.add_account("Legacy", "sk-ant-legacy-key-0001")
    entries = store.list_accounts()
    assert entries[0]["kind"] == "api_key"
    assert "key_masked" in entries[0]


def test_list_accounts_expires_in_sec_positive(store):
    far_future_ms = int(time.time() * 1000) + 3_600_000  # 1 hour from now
    oauth = _make_oauth_block(expires_at=far_future_ms)
    store.add_oauth_account("Future", oauth, None)
    entry = store.list_accounts()[0]
    assert entry["expires_in_sec"] > 0


def test_list_accounts_expires_in_sec_zero_when_past(store):
    past_ms = int(time.time() * 1000) - 60_000  # 1 min ago
    oauth = _make_oauth_block(expires_at=past_ms)
    store.add_oauth_account("Expired", oauth, None)
    entry = store.list_accounts()[0]
    assert entry["expires_in_sec"] == 0


# ── update_oauth_snapshot ─────────────────────────────────────────────────────

def test_update_oauth_snapshot_replaces_tokens(store):
    acc_id = store.add_oauth_account("Refresh", _make_oauth_block(), None)
    new_oauth = _make_oauth_block(expires_at=9_999_888_000_000)
    new_oauth["accessToken"] = "sk-ant-NEW-ACCESS-TOKEN-9999"
    ok = store.update_oauth_snapshot(acc_id, new_oauth, "org-new")
    assert ok is True
    acc = store.get_account(acc_id)
    assert acc["oauth"]["accessToken"] == "sk-ant-NEW-ACCESS-TOKEN-9999"
    assert acc["organizationUuid"] == "org-new"
    assert acc["last_refreshed_at"] is not None


def test_update_oauth_snapshot_wrong_kind_returns_false(store):
    acc_id = store.add_account("API", "sk-ant-api-key-0001")
    ok = store.update_oauth_snapshot(acc_id, _make_oauth_block(), None)
    assert ok is False


def test_update_oauth_snapshot_persists(tmp_path):
    path = tmp_path / "accounts.enc"
    s1 = AccountStore(path)
    acc_id = s1.add_oauth_account("Persist", _make_oauth_block(), None)
    new_oauth = _make_oauth_block()
    new_oauth["accessToken"] = "sk-ant-PERSISTED-9999"
    s1.update_oauth_snapshot(acc_id, new_oauth, None)

    s2 = AccountStore(path)  # reload from disk
    acc = s2.get_account(acc_id)
    assert acc["oauth"]["accessToken"] == "sk-ant-PERSISTED-9999"


# ── set_needs_relogin ─────────────────────────────────────────────────────────

def test_set_needs_relogin(store):
    acc_id = store.add_oauth_account("Expire", _make_oauth_block(), None)
    assert store.get_account(acc_id)["needs_relogin"] is False
    store.set_needs_relogin(acc_id)
    assert store.get_account(acc_id)["needs_relogin"] is True


def test_set_needs_relogin_api_key_returns_false(store):
    acc_id = store.add_account("API", "sk-ant-test-0001")
    ok = store.set_needs_relogin(acc_id)
    assert ok is False


# ── get_oauth_status ─────────────────────────────────────────────────────────

def test_get_oauth_status_returns_fields(store):
    acc_id = store.add_oauth_account("Status", _make_oauth_block(), None)
    status = store.get_oauth_status(acc_id)
    assert status is not None
    assert "expires_in_sec" in status
    assert "refresh_expires_in_sec" in status
    assert "needs_relogin" in status
    assert "last_refreshed_at" in status


def test_get_oauth_status_none_for_api_key(store):
    acc_id = store.add_account("API", "sk-ant-test-0002")
    assert store.get_oauth_status(acc_id) is None


# ── validate_oauth_block ──────────────────────────────────────────────────────

def test_validate_oauth_block_ok():
    validate_oauth_block(_make_oauth_block())  # should not raise


def test_validate_oauth_block_missing_fields():
    with pytest.raises(ValueError, match="OAUTH_SNAPSHOT_INVALID"):
        validate_oauth_block({"accessToken": "x"})


# ── oauth_service: activate_oauth_account ────────────────────────────────────

def test_activate_oauth_writes_credentials(tmp_path):
    """activate_oauth_account writes the new account's oauth block to .credentials.json."""
    store = AccountStore(tmp_path / "accounts.enc")
    oauth = _make_oauth_block()
    acc_id = store.add_oauth_account("New", oauth, "org-123")

    creds_path = _make_credentials_file(tmp_path, _make_oauth_block(expires_at=111))

    result = asyncio.get_event_loop().run_until_complete(
        activate_oauth_account(acc_id, store, creds_path, asyncio.Lock())
    )

    assert result["active_id"] == acc_id
    written = json.loads(creds_path.read_text())
    assert written["claudeAiOauth"]["accessToken"] == oauth["accessToken"]
    assert store._data["active_id"] == acc_id


def test_activate_oauth_resnapshots_previously_active(tmp_path):
    """Previous active OAuth account gets its snapshot updated from the current credentials file."""
    store = AccountStore(tmp_path / "accounts.enc")
    old_oauth = _make_oauth_block(expires_at=111_000)
    new_oauth = _make_oauth_block(expires_at=222_000)

    old_id = store.add_oauth_account("Old Active", old_oauth, None)
    new_id = store.add_oauth_account("New", new_oauth, None)

    # Set old as currently active
    store._data["active_id"] = old_id
    store._save()

    # Simulate that .credentials.json has a REFRESHED token for old_id
    refreshed_old_oauth = dict(old_oauth)
    refreshed_old_oauth["expiresAt"] = 999_000  # refreshed while active
    creds_path = _make_credentials_file(tmp_path, refreshed_old_oauth)

    asyncio.get_event_loop().run_until_complete(
        activate_oauth_account(new_id, store, creds_path, asyncio.Lock())
    )

    # Old account snapshot should have been updated with the refreshed token
    old_acc = store.get_account(old_id)
    assert old_acc["oauth"]["expiresAt"] == 999_000


def test_activate_oauth_restores_on_write_failure(tmp_path):
    """If writing new credentials fails, the original .credentials.json is restored."""
    store = AccountStore(tmp_path / "accounts.enc")
    # Account uses a DIFFERENT accessToken so the mock can distinguish the calls
    new_oauth = _make_oauth_block()
    new_oauth["accessToken"] = "sk-ant-DIFFERENT-NEW-TOKEN-9999"
    acc_id = store.add_oauth_account("Fail", new_oauth, None)

    original_oauth = _make_oauth_block(expires_at=777_000)
    # original_oauth["accessToken"] == "sk-ant-oauth-ACCESSTOKEN-abcdef"
    creds_path = _make_credentials_file(tmp_path, original_oauth)

    # Raise only when the NEW token is being written (not the restore)
    def bad_write(path, data):
        if data.get("claudeAiOauth", {}).get("accessToken") == "sk-ant-DIFFERENT-NEW-TOKEN-9999":
            raise IOError("Simulated write failure")
        # Allow backup write (bak_path) and restore write through
        path.write_text(json.dumps(data), encoding="utf-8")

    with patch("agent_dashboard.oauth_service.write_credentials", side_effect=bad_write):
        with pytest.raises((RuntimeError, IOError)):
            asyncio.get_event_loop().run_until_complete(
                activate_oauth_account(acc_id, store, creds_path, asyncio.Lock())
            )

    # Original should be restored
    restored = json.loads(creds_path.read_text())
    assert restored["claudeAiOauth"]["expiresAt"] == 777_000


def test_activate_oauth_file_not_found(tmp_path):
    store = AccountStore(tmp_path / "accounts.enc")
    acc_id = store.add_oauth_account("X", _make_oauth_block(), None)
    missing_path = tmp_path / "nonexistent.json"

    with pytest.raises(FileNotFoundError):
        asyncio.get_event_loop().run_until_complete(
            activate_oauth_account(acc_id, store, missing_path, asyncio.Lock())
        )


def test_activate_oauth_creates_file_backup(tmp_path):
    """A timestamped file backup is created during activate."""
    store = AccountStore(tmp_path / "accounts.enc")
    acc_id = store.add_oauth_account("Backup Test", _make_oauth_block(), None)
    creds_path = _make_credentials_file(tmp_path, _make_oauth_block())

    asyncio.get_event_loop().run_until_complete(
        activate_oauth_account(acc_id, store, creds_path, asyncio.Lock())
    )

    backups = list(tmp_path.glob(".credentials.backup.*.json"))
    assert len(backups) == 1


# ── oauth_service: refresh_inactive_accounts ─────────────────────────────────

def test_refresh_skips_active_account(tmp_path):
    """The active account is never swapped during auto-refresh."""
    store = AccountStore(tmp_path / "accounts.enc")
    near_expiry_ms = int(time.time() * 1000) + 60_000  # expiring in 1 min
    acc_id = store.add_oauth_account("Active", _make_oauth_block(expires_at=near_expiry_ms), None)
    store.activate(acc_id)

    creds_path = _make_credentials_file(tmp_path, _make_oauth_block())
    lock = asyncio.Lock()

    with patch("agent_dashboard.oauth_service._do_swap_and_invoke") as mock_swap:
        asyncio.get_event_loop().run_until_complete(
            refresh_inactive_accounts(store, creds_path, lock)
        )
        mock_swap.assert_not_called()


def test_refresh_skips_needs_relogin(tmp_path):
    """Accounts with needs_relogin=True are not refreshed."""
    store = AccountStore(tmp_path / "accounts.enc")
    near_expiry_ms = int(time.time() * 1000) + 60_000
    acc_id = store.add_oauth_account("Needs Relogin", _make_oauth_block(expires_at=near_expiry_ms), None)
    store.set_needs_relogin(acc_id)

    creds_path = _make_credentials_file(tmp_path, _make_oauth_block())
    lock = asyncio.Lock()

    with patch("agent_dashboard.oauth_service._do_swap_and_invoke") as mock_swap:
        asyncio.get_event_loop().run_until_complete(
            refresh_inactive_accounts(store, creds_path, lock)
        )
        mock_swap.assert_not_called()


def test_refresh_marks_needs_relogin_when_rt_expired(tmp_path):
    """If refreshTokenExpiresAt is in the past, mark needs_relogin without subprocess."""
    store = AccountStore(tmp_path / "accounts.enc")
    past_ms = int(time.time() * 1000) - 1_000  # 1 second ago
    expired_oauth = _make_oauth_block()
    expired_oauth["refreshTokenExpiresAt"] = past_ms
    expired_oauth["expiresAt"] = past_ms  # also expired
    acc_id = store.add_oauth_account("Expired RT", expired_oauth, None)

    creds_path = _make_credentials_file(tmp_path, _make_oauth_block())
    lock = asyncio.Lock()

    with patch("agent_dashboard.oauth_service._do_swap_and_invoke") as mock_swap:
        asyncio.get_event_loop().run_until_complete(
            refresh_inactive_accounts(store, creds_path, lock)
        )
        mock_swap.assert_not_called()

    assert store.get_account(acc_id)["needs_relogin"] is True


def test_refresh_invokes_swap_when_near_expiry(tmp_path):
    """Account near expiry (< 30 min) triggers _do_swap_and_invoke."""
    store = AccountStore(tmp_path / "accounts.enc")
    near_expiry_ms = int(time.time() * 1000) + 5 * 60 * 1000  # 5 minutes left
    far_rt_ms = int(time.time() * 1000) + 30 * 24 * 3600 * 1000
    oauth = _make_oauth_block(expires_at=near_expiry_ms)
    oauth["refreshTokenExpiresAt"] = far_rt_ms
    acc_id = store.add_oauth_account("Near Expiry", oauth, None)
    # NOT active

    creds_path = _make_credentials_file(tmp_path, _make_oauth_block())
    lock = asyncio.Lock()

    with patch(
        "agent_dashboard.oauth_service._do_swap_and_invoke",
        new_callable=AsyncMock,
    ) as mock_swap:
        asyncio.get_event_loop().run_until_complete(
            refresh_inactive_accounts(store, creds_path, lock)
        )
        mock_swap.assert_called_once_with(acc_id, store, creds_path, lock)


# ── H-1 regression: activate serialized with scheduler via shared lock ────────

def test_activate_and_scheduler_serialized_by_lock(tmp_path):
    """H-1 regression: activate_oauth_account acquires refresh_lock, preventing
    concurrent credential file corruption with the background refresh scheduler.

    Simulates two coroutines running concurrently:
      - scheduler_simulation: holds refresh_lock for 50 ms (like _do_swap_and_invoke),
        restores original credentials on exit.
      - activate_simulation: waits 10 ms, then calls activate_oauth_account which
        must block until the scheduler releases the lock.

    Verifies:
      1. Scheduler fully released the lock before activate completed.
      2. Final .credentials.json contains Account A's token (activate was last writer).
      3. AccountStore records Account A as active.
    """
    store = AccountStore(tmp_path / "accounts.enc")

    oauth_a = _make_oauth_block()
    oauth_a["accessToken"] = "sk-ant-TOKEN-A-ACTIVATE"
    acc_a = store.add_oauth_account("Account A", oauth_a, None)

    oauth_b = _make_oauth_block()
    oauth_b["accessToken"] = "sk-ant-TOKEN-B-ACTIVE"
    acc_b = store.add_oauth_account("Account B", oauth_b, None)

    # B is currently active — credentials file holds B's token
    store._data["active_id"] = acc_b
    store._save()
    creds_path = _make_credentials_file(tmp_path, oauth_b)

    lock = asyncio.Lock()
    execution_order: list[str] = []

    async def _run():
        async def scheduler_simulation():
            """Mimics _do_swap_and_invoke: acquires lock, does slow I/O, restores."""
            async with lock:
                execution_order.append("scheduler_lock_acquired")
                await asyncio.sleep(0.05)
                # Scheduler always restores the original credentials in its finally block
                write_credentials(creds_path, {"claudeAiOauth": oauth_b})
                execution_order.append("scheduler_lock_released")

        async def activate_simulation():
            # Slight delay so scheduler acquires the lock first
            await asyncio.sleep(0.01)
            execution_order.append("activate_waiting_for_lock")
            await activate_oauth_account(acc_a, store, creds_path, lock)
            execution_order.append("activate_completed")

        await asyncio.gather(scheduler_simulation(), activate_simulation())

    asyncio.get_event_loop().run_until_complete(_run())

    # 1. Scheduler must have released the lock before activate finished writing
    idx_released = execution_order.index("scheduler_lock_released")
    idx_completed = execution_order.index("activate_completed")
    assert idx_released < idx_completed, (
        f"activate completed before scheduler released lock — lock not acquired: {execution_order}"
    )

    # 2. activate was the last writer → credentials hold A's token
    final_creds = json.loads(creds_path.read_text())
    assert final_creds["claudeAiOauth"]["accessToken"] == "sk-ant-TOKEN-A-ACTIVATE", (
        "Credentials silently overwritten — H-1 race not fixed"
    )

    # 3. AccountStore reflects A as active
    assert store._data["active_id"] == acc_a


def test_sync_credentials_with_store(store, tmp_path):
    from agent_dashboard.oauth_service import sync_credentials_with_store, write_credentials
    import asyncio

    creds_path = tmp_path / ".credentials.json"
    lock = asyncio.Lock()

    # Setup stored accounts
    oauth_a = {
        "accessToken": "sk-ant-TOKEN-A",
        "refreshToken": "sk-ant-REFRESH-A",
        "expiresAt": 9999999999000,
        "refreshTokenExpiresAt": 9999999999000,
    }
    oauth_b = {
        "accessToken": "sk-ant-TOKEN-B",
        "refreshToken": "sk-ant-REFRESH-B",
        "expiresAt": 9999999999000,
        "refreshTokenExpiresAt": 9999999999000,
    }

    acc_a = store.add_oauth_account("Account A", oauth_a, "org-a")
    acc_b = store.add_oauth_account("Account B", oauth_b, "org-b")
    store.activate(acc_a)

    async def run_tests():
        # Scenario 1: File doesn't exist -> active account Acc A marked as needing relogin
        changed = await sync_credentials_with_store(store, creds_path, lock)
        assert changed is True
        assert store.get_account(acc_a)["needs_relogin"] is True

        # Scenario 2: User logs in with new tokens for Acc A -> needs_relogin cleared, tokens updated
        new_oauth_a = dict(oauth_a)
        new_oauth_a["accessToken"] = "sk-ant-TOKEN-A-NEW"
        write_credentials(creds_path, {"claudeAiOauth": new_oauth_a, "organizationUuid": "org-a"})

        changed = await sync_credentials_with_store(store, creds_path, lock)
        assert changed is True
        assert store.get_account(acc_a)["needs_relogin"] is False
        assert store.get_account(acc_a)["oauth"]["accessToken"] == "sk-ant-TOKEN-A-NEW"
        assert store._data["active_id"] == acc_a

        # Scenario 3: Swapping tokens on disk to match Acc B -> active pointer switches to Acc B
        write_credentials(creds_path, {"claudeAiOauth": oauth_b, "organizationUuid": "org-b"})
        changed = await sync_credentials_with_store(store, creds_path, lock)
        assert changed is True
        assert store._data["active_id"] == acc_b

        # Scenario 4: Writing a completely brand new token when Acc B is active (needs_relogin is False)
        # -> should auto-create a new account instead of overwriting Acc B
        new_oauth_c = {
            "accessToken": "sk-ant-TOKEN-C",
            "refreshToken": "sk-ant-REFRESH-C",
            "expiresAt": 9999999999000,
            "refreshTokenExpiresAt": 9999999999000,
        }
        write_credentials(creds_path, {"claudeAiOauth": new_oauth_c, "organizationUuid": "org-c"})
        changed = await sync_credentials_with_store(store, creds_path, lock)
        assert changed is True
        
        # The active account is now the new auto-created account
        new_active_id = store._data["active_id"]
        assert new_active_id != acc_b
        assert store.get_account(new_active_id)["name"] == "OAuth (Imported)"
        assert store.get_account(new_active_id)["oauth"]["accessToken"] == "sk-ant-TOKEN-C"
        # Acc B's token remains unchanged
        assert store.get_account(acc_b)["oauth"]["accessToken"] == "sk-ant-TOKEN-B"

    asyncio.get_event_loop().run_until_complete(run_tests())


# ── BUG-002: Duplicate account name validation ────────────────────────────────

def test_add_account_duplicate_name_raises(store):
    """add_account must reject a name that already exists (api_key accounts)."""
    store.add_account("My Account", "sk-ant-first-0001")
    with pytest.raises(ValueError, match="ACCOUNT_NAME_DUPLICATE"):
        store.add_account("My Account", "sk-ant-second-0002")


def test_add_account_duplicate_name_case_insensitive(store):
    """Name uniqueness check is case-insensitive."""
    store.add_account("kztek dev", "sk-ant-lower-0001")
    with pytest.raises(ValueError, match="ACCOUNT_NAME_DUPLICATE"):
        store.add_account("KZTEK DEV", "sk-ant-upper-0002")


def test_add_oauth_account_duplicate_name_raises(store):
    """add_oauth_account must reject a name that already exists (oauth_session accounts)."""
    store.add_oauth_account("OAuth Work", _make_oauth_block(), None)
    with pytest.raises(ValueError, match="ACCOUNT_NAME_DUPLICATE"):
        store.add_oauth_account("OAuth Work", _make_oauth_block(), None)


def test_add_account_duplicate_name_cross_kind(store):
    """Name collision is detected across different account kinds."""
    store.add_account("Shared Name", "sk-ant-api-0001")
    with pytest.raises(ValueError, match="ACCOUNT_NAME_DUPLICATE"):
        store.add_oauth_account("Shared Name", _make_oauth_block(), None)


def test_add_account_unique_names_succeed(store):
    """Two accounts with different names must both be created without error."""
    id1 = store.add_account("Account Alpha", "sk-ant-alpha-0001")
    id2 = store.add_account("Account Beta", "sk-ant-beta-0002")
    assert id1 != id2
    assert len(store.list_accounts()) == 2


def test_add_account_duplicate_does_not_persist(store):
    """A rejected duplicate-name call must not leave any partial record in the store."""
    store.add_account("Clean State", "sk-ant-first-0001")
    with pytest.raises(ValueError):
        store.add_account("Clean State", "sk-ant-second-0002")
    assert len(store.list_accounts()) == 1

