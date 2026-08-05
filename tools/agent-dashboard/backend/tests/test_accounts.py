"""Unit tests for accounts.py — encryption, CRUD, rate-limit."""
from __future__ import annotations

import pathlib
import time

import pytest

from agent_dashboard.accounts import (
    AccountStore,
    _decrypt,
    _encrypt,
    mask_key,
)


# ── Encryption round-trip ─────────────────────────────────────────────────────

def test_encrypt_decrypt_roundtrip():
    original = '{"version":1,"active_id":null,"accounts":[]}'
    encrypted = _encrypt(original)
    assert encrypted != original          # must differ
    assert _decrypt(encrypted) == original  # must recover


def test_encrypt_produces_base64():
    import base64
    encrypted = _encrypt("hello")
    base64.b64decode(encrypted)  # should not raise


def test_different_strings_produce_different_ciphertext():
    assert _encrypt("abc") != _encrypt("xyz")


# ── Key masking ───────────────────────────────────────────────────────────────

def test_mask_key_shows_last_4():
    key = "sk-ant-api03-abcdef1234"
    masked = mask_key(key)
    assert masked.endswith("1234")
    assert "abcdef" not in masked  # middle hidden


def test_mask_key_short_key():
    masked = mask_key("sk")
    assert "****" in masked


# ── AccountStore CRUD ─────────────────────────────────────────────────────────

@pytest.fixture
def store(tmp_path) -> AccountStore:
    return AccountStore(tmp_path / "accounts.enc")


def test_empty_store_has_no_accounts(store):
    assert store.list_accounts() == []


def test_add_and_list(store):
    acc_id = store.add_account("Personal", "sk-ant-test-0001")
    accounts = store.list_accounts()
    assert len(accounts) == 1
    assert accounts[0]["id"] == acc_id
    assert accounts[0]["name"] == "Personal"
    assert "test-0001" not in accounts[0]["key_masked"]  # masked
    assert accounts[0]["is_active"] is False


def test_persist_across_reload(tmp_path):
    path = tmp_path / "accounts.enc"
    s1 = AccountStore(path)
    acc_id = s1.add_account("Saved", "sk-ant-persist-XXXX")

    s2 = AccountStore(path)  # reload
    accounts = s2.list_accounts()
    assert len(accounts) == 1
    assert accounts[0]["id"] == acc_id
    assert accounts[0]["name"] == "Saved"


def test_update_account_name(store):
    acc_id = store.add_account("Old Name", "sk-ant-test-0002")
    store.update_account(acc_id, "New Name")
    acc = store.get_account(acc_id)
    assert acc["name"] == "New Name"


def test_delete_inactive_account(store):
    acc_id = store.add_account("Delete Me", "sk-ant-test-0003")
    store.delete_account(acc_id)
    assert store.get_account(acc_id) is None


def test_delete_active_raises(store):
    acc_id = store.add_account("Active", "sk-ant-test-0004")
    store.activate(acc_id)
    with pytest.raises(ValueError, match="ACCOUNT_ACTIVE_CANNOT_DELETE"):
        store.delete_account(acc_id)


def test_delete_nonexistent_raises(store):
    with pytest.raises(KeyError):
        store.delete_account("acc-nonexistent")


def test_activate_sets_active(store):
    id1 = store.add_account("A1", "sk-ant-test-0005")
    id2 = store.add_account("A2", "sk-ant-test-0006")
    store.activate(id1)

    accounts = store.list_accounts()
    active = [a for a in accounts if a["is_active"]]
    assert len(active) == 1
    assert active[0]["id"] == id1

    # Activating second clears first
    store.activate(id2)
    accounts = store.list_accounts()
    active = [a for a in accounts if a["is_active"]]
    assert len(active) == 1
    assert active[0]["id"] == id2


def test_get_active_none_when_empty(store):
    assert store.get_active() is None


def test_get_active_returns_masked(store):
    acc_id = store.add_account("Active", "sk-ant-test-0007")
    store.activate(acc_id)
    active = store.get_active()
    assert active is not None
    assert "key_masked" in active
    assert "test-0007" not in active["key_masked"]


# ── Reveal + rate limit ───────────────────────────────────────────────────────

def test_reveal_returns_plaintext(store):
    key = "sk-ant-test-reveal-9999"
    acc_id = store.add_account("Rev", key)
    revealed = store.reveal_key(acc_id)
    assert revealed == key


def test_reveal_rate_limit_exceeded(store):
    acc_id = store.add_account("RL", "sk-ant-test-rate-0001")
    # Exhaust 5 allowed calls
    for _ in range(5):
        store.reveal_key(acc_id)
    # 6th call must be blocked
    with pytest.raises(RuntimeError, match="RATE_LIMIT_EXCEEDED"):
        store.reveal_key(acc_id)


def test_reveal_nonexistent_raises(store):
    with pytest.raises(KeyError):
        store.reveal_key("acc-nonexistent")
