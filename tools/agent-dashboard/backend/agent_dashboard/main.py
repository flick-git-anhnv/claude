"""FastAPI application factory — wires all components together."""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from . import config, db as db_module
from .accounts import AccountStore
from .models import get_subagent_display_name, make_delta, make_snapshot
from .parser import parse_line
from .state_manager import SessionStateManager
from .tail_reader import TailReader
from .watcher import FileWatcher
from .ws import ConnectionManager
from .routes import sessions as sessions_router
from .routes import tokens as tokens_router
from .routes import accounts as accounts_router
from .routes import pipeline as pipeline_router

logger = logging.getLogger(__name__)

# ── Global objects (initialised in lifespan) ──────────────────────────────────
_watcher = FileWatcher()
_tail_reader = TailReader()
_state_mgr = SessionStateManager()
_ws_manager = ConnectionManager()
_file_event_queue: asyncio.Queue[tuple[str, str]] = asyncio.Queue()
_oauth_refresh_lock = asyncio.Lock()


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB, load state, start watcher + background tasks."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. DB
    conn = await db_module.init(config.DB_PATH)
    app.state.db = conn

    # 2. Account store
    store = AccountStore(config.ACCOUNTS_FILE)
    app.state.account_store = store

    # 3. Expose managers, credentials path, and shared lock on app state for routes
    app.state.ws_manager = _ws_manager
    app.state.credentials_path = config.CLAUDE_CREDENTIALS_FILE
    app.state.oauth_refresh_lock = _oauth_refresh_lock

    # 4. Restore file cursors + seed state machine from DB
    cursors = await db_module.load_cursors(conn)
    _tail_reader.restore_cursors(cursors)

    active_sessions = await db_module.get_active_sessions(conn, include_subagents=True)
    startup_changes = _state_mgr.initialize_from_db(active_sessions)
    logger.info(
        "State machine seeded with %d sessions; %d stale-state corrections",
        len(active_sessions),
        len(startup_changes),
    )

    # Persist any stale-state corrections to DB immediately — don't wait for
    # the first ticker tick (STATE_TICKER_INTERVAL_SEC = 30 s).  Without this,
    # a WebSocket client connecting in the first 30 s after startup would see
    # hundreds of "Running" sessions that have actually been idle for hours.
    for change in startup_changes:
        ended_at = change.changed_at if change.new_state == "Ended" else None
        await db_module.update_session_state(
            conn, change.session_id, change.new_state, ended_at
        )
    if startup_changes:
        logger.info(
            "Startup: persisted %d state corrections to DB", len(startup_changes)
        )

    # 5. Startup scan — queue existing files for backlog processing
    loop = asyncio.get_event_loop()
    await _startup_scan(cursors)

    # 6. Start watchdog (thread)
    _watcher.start(loop, _file_event_queue)

    # 7. Start asyncio background tasks
    pipeline_task = asyncio.create_task(_pipeline_processor(conn), name="pipeline")
    ticker_task = asyncio.create_task(_state_ticker(conn), name="state_ticker")
    oauth_task = asyncio.create_task(
        _oauth_refresh_scheduler(store), name="oauth_refresh"
    )
    sync_task = asyncio.create_task(
        _credentials_sync_scheduler(store), name="credentials_sync"
    )

    # Log emergency backup warning if present from previous crash
    from .oauth_service import check_emergency_backup
    emerg = check_emergency_backup(config.CLAUDE_CREDENTIALS_FILE)
    if emerg:
        logger.warning(
            "STARTUP WARNING: Emergency credentials backup found at %s "
            "(newer than .credentials.json). A previous auto-refresh may have crashed. "
            "Inspect and manually restore if Claude login is broken.",
            emerg,
        )

    logger.info("Agent Dashboard started on port %d", config.DASHBOARD_PORT)

    yield  # app is running

    # Shutdown
    pipeline_task.cancel()
    ticker_task.cancel()
    oauth_task.cancel()
    sync_task.cancel()
    _watcher.stop()
    await conn.close()
    logger.info("Agent Dashboard stopped")


# ── Startup scan ──────────────────────────────────────────────────────────────

async def _startup_scan(known_cursors: dict[str, int]) -> None:
    """Queue known and new JSONL files so backlog is processed on startup."""
    # Known files (may have new bytes since last run)
    for fp in known_cursors:
        if Path(fp).exists():
            await _file_event_queue.put(("modified", fp))

    # Discover new files not yet in cursors — rglob includes subagent transcripts
    # (<project>/<session-uuid>/subagents/agent-*.jsonl) that glob("*/*.jsonl") misses.
    if config.CLAUDE_PROJECTS_DIR.exists():
        for jsonl in config.CLAUDE_PROJECTS_DIR.rglob("*.jsonl"):
            fp = str(jsonl)
            if fp not in known_cursors:
                await _file_event_queue.put(("created", fp))


# ── Pipeline processor ────────────────────────────────────────────────────────

async def _pipeline_processor(conn: Any) -> None:
    """Drain file-event queue; parse → DB → state → broadcast."""
    while True:
        try:
            event_type, file_path = await _file_event_queue.get()
            await _process_file(conn, file_path)
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.exception("Pipeline error: %s", exc)
        finally:
            try:
                _file_event_queue.task_done()
            except ValueError:
                pass


async def _process_file(conn: Any, file_path: str) -> None:
    lines = _tail_reader.read_new_lines(file_path)
    if not lines:
        return

    for line in lines:
        parsed = parse_line(line, file_path)
        if parsed is None:
            continue

        # ── Sprint 3: handle ai-title meta lines (FR-003) ────────────────────
        # is_meta=True lines have no timestamp and must NOT create a session.
        # They only update the title of an already-known session.
        if parsed.is_meta:
            if parsed.ai_title:
                await db_module.update_title(
                    conn, parsed.session_id, parsed.ai_title, source="ai_title"
                )
                await _ws_manager.broadcast(make_delta("session_title_changed", {
                    "session_id": parsed.session_id,
                    "title":      parsed.ai_title,
                    "source":     "ai_title",
                }))
            continue

        # ── Sprint 3: snapshot last_* params (FR-002) — only for messages with usage
        # input_tokens > 0 indicates an assistant message with usage data.
        snap_kwargs: dict = {}
        if parsed.input_tokens > 0:
            snap_kwargs = {
                "last_input_tokens":          parsed.input_tokens,
                "last_cache_creation_tokens": parsed.cache_creation,
                "last_cache_read_tokens":     parsed.cache_read,
                "last_usage_at":              parsed.timestamp,
            }

        # DB: upsert session + insert event + token usage
        is_new = await db_module.upsert_session(
            conn,
            session_id=parsed.session_id,
            project=parsed.project,
            file_path=file_path,
            agent_type=parsed.agent_type,
            timestamp=parsed.timestamp,
            input_tokens=parsed.input_tokens,
            output_tokens=parsed.output_tokens,
            cache_creation=parsed.cache_creation,
            cache_read=parsed.cache_read,
            is_subagent=parsed.is_subagent,
            # Sprint 4: subagent transcript linking
            parent_session_id=parsed.parent_session_id,
            attribution_agent=parsed.attribution_agent,
            **snap_kwargs,
        )

        # ── Sprint 3: set fallback title from first user text (FR-003) ───────
        if parsed.first_user_text:
            updated = await db_module.update_title_if_null(
                conn, parsed.session_id, parsed.first_user_text, source="user_text"
            )
            if updated:
                await _ws_manager.broadcast(make_delta("session_title_changed", {
                    "session_id": parsed.session_id,
                    "title":      parsed.first_user_text,
                    "source":     "user_text",
                }))

        await db_module.insert_event(
            conn,
            session_id=parsed.session_id,
            ts=parsed.timestamp,
            msg_type=parsed.msg_type,
            tool_name=parsed.tool_name,
            payload_json=parsed.raw_json,
            # FR-001 fix: persist subagent info at ingest — payload_json truncation
            # at 2000 chars often corrupts Agent tool_use lines with large prompts.
            subagent_type=parsed.subagent_type if parsed.tool_name == "Agent" else None,
            subagent_description=parsed.subagent_activity if parsed.tool_name == "Agent" else None,
            # Sprint 4b: store tool_use_id at ingest so result lookup can use it
            # without re-parsing the JSONL file.
            tool_use_id=parsed.tool_use_id if parsed.tool_name == "Agent" else None,
        )

        has_tokens = any([
            parsed.input_tokens, parsed.output_tokens,
            parsed.cache_creation, parsed.cache_read,
        ])
        if has_tokens:
            await db_module.insert_token_usage(
                conn,
                session_id=parsed.session_id,
                ts=parsed.timestamp,
                input_tokens=parsed.input_tokens,
                output_tokens=parsed.output_tokens,
                cache_creation=parsed.cache_creation,
                cache_read=parsed.cache_read,
            )

        # State machine update
        change = _state_mgr.update_activity(parsed.session_id, parsed.timestamp)

        # WebSocket deltas
        if is_new:
            await _ws_manager.broadcast(make_delta("agent_started", {
                "session_id": parsed.session_id,
                "project":    parsed.project,
                "agent_type": parsed.agent_type,
                "started_at": parsed.timestamp,
            }))
        else:
            delta_payload: dict = {
                "session_id":    parsed.session_id,
                "last_event_at": parsed.timestamp,
            }
            if parsed.tool_name:
                delta_payload["tool_use"] = parsed.tool_name
            if has_tokens:
                delta_payload["tokens_added"] = {
                    "input":          parsed.input_tokens,
                    "output":         parsed.output_tokens,
                    "cache_creation": parsed.cache_creation,
                    "cache_read":     parsed.cache_read,
                }
            await _ws_manager.broadcast(make_delta("agent_update", delta_payload))

        # Sprint 5 — BUG-004: notify parent chain whenever a child transcript
        # has a new event, even before model/token data arrives (1-5s race window).
        # Frontend PipelineCard listens for chain_updated and refetches /chain
        # for the parent session so the active card is shown immediately.
        if parsed.is_subagent and parsed.parent_session_id:
            await _ws_manager.broadcast(make_delta("chain_updated", {
                "session_id":       parsed.parent_session_id,
                "child_session_id": parsed.session_id,
                "reason":           "child_event",
            }))

        # Track B: persist + broadcast subagent change (only for Agent tool calls)
        if parsed.subagent_type:
            await db_module.update_session_subagent(
                conn,
                session_id=parsed.session_id,
                subagent_type=parsed.subagent_type,
                subagent_activity=parsed.subagent_activity,
                at=parsed.timestamp,
            )
            await _ws_manager.broadcast(make_delta("subagent_changed", {
                "session_id": parsed.session_id,
                "subagent": {
                    "type":         parsed.subagent_type,
                    "display_name": get_subagent_display_name(parsed.subagent_type),
                    "activity":     parsed.subagent_activity,
                    "at":           parsed.timestamp,
                },
            }))

        if change and change.new_state != change.old_state:
            await _ws_manager.broadcast(make_delta("agent_state_changed", {
                "session_id": parsed.session_id,
                "state":      change.new_state,
            }))
            await db_module.update_session_state(conn, parsed.session_id, change.new_state)

        if has_tokens:
            from .config import resolve_max_context
            cumulative = await db_module.get_session_totals(conn, parsed.session_id)
            # Sprint 3 FR-002: include last-lượt context_pct in token_update delta
            last_total = parsed.input_tokens + parsed.cache_creation + parsed.cache_read
            max_ctx = resolve_max_context(parsed.agent_type or "")
            ctx_pct = round(last_total / max_ctx * 100, 1) if max_ctx > 0 else 0.0
            await _ws_manager.broadcast(make_delta("token_update", {
                "session_id": parsed.session_id,
                "delta": {
                    "input":          parsed.input_tokens,
                    "output":         parsed.output_tokens,
                    "cache_creation": parsed.cache_creation,
                    "cache_read":     parsed.cache_read,
                },
                "cumulative":     cumulative,
                "last_input_total": last_total,
                "max_context":    max_ctx,
                "context_pct":    ctx_pct,
            }))

    # Persist updated cursor to DB
    await db_module.save_cursor(conn, file_path, _tail_reader.get_cursor(file_path))


# ── State ticker ──────────────────────────────────────────────────────────────

async def _state_ticker(conn: Any) -> None:
    """Re-evaluate session states every STATE_TICKER_INTERVAL_SEC seconds."""
    while True:
        try:
            await asyncio.sleep(config.STATE_TICKER_INTERVAL_SEC)
            changes = _state_mgr.evaluate_all()
            for change in changes:
                ended_at = change.changed_at if change.new_state == "Ended" else None
                await db_module.update_session_state(
                    conn, change.session_id, change.new_state, ended_at
                )
                await _ws_manager.broadcast(make_delta("agent_state_changed", {
                    "session_id": change.session_id,
                    "state": change.new_state,
                }))
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.exception("State ticker error: %s", exc)


# ── OAuth refresh scheduler ──────────────────────────────────────────────────

async def _oauth_refresh_scheduler(store: Any) -> None:
    """Run auto-refresh cycle for inactive OAuth accounts every OAUTH_REFRESH_INTERVAL_SEC."""
    from .oauth_service import refresh_inactive_accounts

    while True:
        try:
            await asyncio.sleep(config.OAUTH_REFRESH_INTERVAL_SEC)
            await refresh_inactive_accounts(
                store,
                config.CLAUDE_CREDENTIALS_FILE,
                _oauth_refresh_lock,
            )
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.exception("OAuth refresh scheduler error: %s", exc)


# ── Credentials sync scheduler ───────────────────────────────────────────────

async def _credentials_sync_scheduler(store: Any) -> None:
    """Watch credentials file for manual login/logout and sync with store."""
    from .oauth_service import sync_credentials_with_store

    while True:
        try:
            await asyncio.sleep(3.0)  # poll file every 3 seconds
            changed = await sync_credentials_with_store(
                store,
                config.CLAUDE_CREDENTIALS_FILE,
                _oauth_refresh_lock,
            )
            if changed:
                # Broadcast the new active account state to all WS connections
                active = store.get_active()
                payload = make_delta(
                    "account_changed",
                    {
                        "active_id": active["id"] if active else None,
                        "name": active["name"] if active else None,
                        "kind": active["kind"] if active else None,
                        "key_masked": active.get("key_masked") if active and active.get("kind") == "api_key" else None,
                        "oauth_masked": active.get("oauth_masked") if active and active.get("kind") == "oauth_session" else None,
                    },
                )
                await _ws_manager.broadcast(payload)
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.exception("Credentials sync scheduler error: %s", exc)


# ── FastAPI app ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="Agent Dashboard",
        description="KZTEK Claude Code Agent Monitor",
        version="0.1.0",
        lifespan=lifespan,
    )

    # REST routes
    app.include_router(sessions_router.router)
    app.include_router(tokens_router.router)
    app.include_router(accounts_router.router)
    app.include_router(pipeline_router.router)

    # Health endpoint
    @app.get("/api/health")
    async def health():
        import time
        return {
            "status": "ok",
            "watcher_alive": _watcher.alive,
            "ws_clients": _ws_manager.client_count,
        }

    # WebSocket endpoint
    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        await _ws_manager.connect(ws)
        try:
            # Send snapshot immediately on connect
            sessions = await db_module.get_active_sessions(app.state.db)
            active_account = app.state.account_store.get_active()
            snapshot = make_snapshot(sessions, active_account, _watcher.alive)
            await _ws_manager.send_snapshot(ws, snapshot)

            # Handle incoming ping/pong — this returns when client disconnects
            await ConnectionManager.handle_incoming(ws)
        except WebSocketDisconnect:
            pass
        finally:
            _ws_manager.disconnect(ws)

    # Mount frontend static files if present (production local mode)
    _frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if _frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="static")
        logger.info("Serving frontend from %s", _frontend_dist)

    return app


# Singleton app instance (imported by uvicorn)
app = create_app()
