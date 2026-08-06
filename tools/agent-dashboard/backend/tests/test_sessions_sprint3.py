"""Sprint 3 sessions route tests — /api/sessions/{id}/chain endpoint."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from agent_dashboard.routes import sessions as sessions_router


# ── Minimal app with mocked DB ────────────────────────────────────────────────

def _make_app_client(chain_result):
    """Build a TestClient for a minimal FastAPI app with stubbed DB state."""
    app = FastAPI()
    app.include_router(sessions_router.router)
    # Set app.state.db BEFORE creating TestClient so the dependency finds it.
    # The actual DB call is mocked by patch(), so the object value doesn't matter.
    app.state.db = object()
    return app


# ── /api/sessions/{id}/chain — happy path ────────────────────────────────────

_SAMPLE_CHAIN = {
    "session_id": "abc-123",
    "session_state": "Running",
    "steps": [
        {
            "step_index": 0,
            "subagent_type": "product-manager",
            "subagent_display": "Product Manager",
            "description": "Viết PRD",
            "started_at": "2026-08-06T10:00:00Z",
            "status": "done",
        },
        {
            "step_index": 1,
            "subagent_type": "senior-developer",
            "subagent_display": "Senior Developer",
            "description": "Implement backend",
            "started_at": "2026-08-06T11:00:00Z",
            "status": "active",
        },
    ],
}


def test_chain_endpoint_returns_200():
    app = _make_app_client(_SAMPLE_CHAIN)
    with patch(
        "agent_dashboard.db.get_session_chain",
        new=AsyncMock(return_value=_SAMPLE_CHAIN),
    ):
        client = TestClient(app, raise_server_exceptions=True)
        response = client.get("/api/sessions/abc-123/chain")
    assert response.status_code == 200


def test_chain_endpoint_returns_expected_schema():
    app = _make_app_client(_SAMPLE_CHAIN)
    with patch(
        "agent_dashboard.db.get_session_chain",
        new=AsyncMock(return_value=_SAMPLE_CHAIN),
    ):
        client = TestClient(app, raise_server_exceptions=True)
        data = client.get("/api/sessions/abc-123/chain").json()

    assert data["session_id"] == "abc-123"
    assert data["session_state"] == "Running"
    assert len(data["steps"]) == 2


def test_chain_endpoint_step_fields():
    app = _make_app_client(_SAMPLE_CHAIN)
    with patch(
        "agent_dashboard.db.get_session_chain",
        new=AsyncMock(return_value=_SAMPLE_CHAIN),
    ):
        client = TestClient(app, raise_server_exceptions=True)
        data = client.get("/api/sessions/abc-123/chain").json()

    step0, step1 = data["steps"]
    assert step0["step_index"] == 0
    assert step0["subagent_type"] == "product-manager"
    assert step0["subagent_display"] == "Product Manager"
    assert step0["status"] == "done"
    assert step1["status"] == "active"


def test_chain_endpoint_empty_steps():
    chain_empty = {"session_id": "no-agents", "session_state": "Idle", "steps": []}
    app = _make_app_client(chain_empty)
    with patch(
        "agent_dashboard.db.get_session_chain",
        new=AsyncMock(return_value=chain_empty),
    ):
        client = TestClient(app, raise_server_exceptions=True)
        data = client.get("/api/sessions/no-agents/chain").json()

    assert data["steps"] == []


# ── /api/sessions/{id}/chain — 404 path ──────────────────────────────────────

def test_chain_endpoint_404_for_unknown_session():
    app = _make_app_client(None)
    with patch(
        "agent_dashboard.db.get_session_chain",
        new=AsyncMock(return_value=None),
    ):
        client = TestClient(app, raise_server_exceptions=True)
        response = client.get("/api/sessions/does-not-exist/chain")

    assert response.status_code == 404
    body = response.json()
    # FastAPI wraps HTTPException.detail as-is
    assert "SESSION_NOT_FOUND" in json.dumps(body)


# ── Route ordering: /chain must resolve before /{session_id} ─────────────────

def test_chain_route_not_shadowed_by_detail_route():
    """/chain must not be caught by the /{session_id} detail route."""
    # FastAPI path params don't contain '/', so /sessions/abc-123/chain matches
    # the explicit /sessions/{id}/chain route, not /{session_id}.
    # This test verifies the chain route is properly registered and reachable.
    app = _make_app_client(_SAMPLE_CHAIN)
    with patch(
        "agent_dashboard.db.get_session_chain",
        new=AsyncMock(return_value=_SAMPLE_CHAIN),
    ):
        client = TestClient(app, raise_server_exceptions=True)
        r_chain = client.get("/api/sessions/abc-123/chain")

    assert r_chain.status_code == 200
