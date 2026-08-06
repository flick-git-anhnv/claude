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

    # 3. Expose managers + credentials path on app state for routes
    app.state.ws_manager = _ws_manager
    app.state.credentials_path = config.CLAUDE_CREDENTIALS_FILE

    # 4. Restore file cursors + seed state machine from DB
    cursors = await db_module.load_cursors(conn)
    _tail_reader.restore_cursors(cursors)

    active_sessions = await db_module.get_active_sessions(conn)
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

    # Discover new files not yet in cursors
    if config.CLAUDE_PROJECTS_DIR.exists():
        for jsonl in config.CLAUDE_PROJECTS_DIR.glob("*/*.jsonl"):
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

    path = Path(file_path)
    project = path.parent.name
    is_first_in_file = True

    for line in lines:
        parsed = parse_line(line, file_path)
        if parsed is None:
            continue

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
        )

        await db_module.insert_event(
            conn,
            session_id=parsed.session_id,
            ts=parsed.timestamp,
            msg_type=parsed.msg_type,
            tool_name=parsed.tool_name,
            payload_json=parsed.raw_json,
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
                "project": parsed.project,
                "agent_type": parsed.agent_type,
                "started_at": parsed.timestamp,
            }))
        else:
            delta_payload: dict = {
                "session_id": parsed.session_id,
                "last_event_at": parsed.timestamp,
            }
            if parsed.tool_name:
                delta_payload["tool_use"] = parsed.tool_name
            if has_tokens:
                delta_payload["tokens_added"] = {
                    "input": parsed.input_tokens,
                    "output": parsed.output_tokens,
                    "cache_creation": parsed.cache_creation,
                    "cache_read": parsed.cache_read,
                }
            await _ws_manager.broadcast(make_delta("agent_update", delta_payload))

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
                "state": change.new_state,
            }))
            await db_module.update_session_state(conn, parsed.session_id, change.new_state)

        if has_tokens:
            cumulative = await db_module.get_session_totals(conn, parsed.session_id)
            await _ws_manager.broadcast(make_delta("token_update", {
                "session_id": parsed.session_id,
                "delta": {
                    "input": parsed.input_tokens,
                    "output": parsed.output_tokens,
                    "cache_creation": parsed.cache_creation,
                    "cache_read": parsed.cache_read,
                },
                "cumulative": cumulative,
            }))

        is_first_in_file = False

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
