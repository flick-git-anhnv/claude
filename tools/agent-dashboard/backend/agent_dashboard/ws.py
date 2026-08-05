"""WebSocket connection manager — fan-out broadcasts, snapshot on connect."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Tracks all connected WebSocket clients.

    Protocol (server → client):
        {"type": "snapshot", "ts": "...", "payload": {...}}   on connect
        {"type": "delta",    "ts": "...", "payload": {...}}   on event

    Protocol (client → server):
        {"type": "ping"}  →  server replies {"type": "pong"}
    """

    def __init__(self) -> None:
        self._clients: List[WebSocket] = []

    # ── Connection lifecycle ──────────────────────────────────────────────────

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._clients.append(ws)
        logger.info("WS client connected (total=%d)", len(self._clients))

    def disconnect(self, ws: WebSocket) -> None:
        try:
            self._clients.remove(ws)
        except ValueError:
            pass
        logger.info("WS client disconnected (total=%d)", len(self._clients))

    # ── Send helpers ──────────────────────────────────────────────────────────

    async def send_snapshot(self, ws: WebSocket, snapshot: Dict[str, Any]) -> None:
        try:
            await ws.send_text(json.dumps(snapshot))
        except Exception as exc:
            logger.debug("send_snapshot failed: %s", exc)
            self.disconnect(ws)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Fan-out a delta to all connected clients; drop dead connections."""
        if not self._clients:
            return
        text = json.dumps(message)
        dead: List[WebSocket] = []
        for ws in list(self._clients):
            try:
                await ws.send_text(text)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    # ── Ping/pong handler ─────────────────────────────────────────────────────

    @staticmethod
    async def handle_incoming(ws: WebSocket) -> None:
        """Consume messages from the client (only ping is expected)."""
        try:
            async for raw in ws.iter_text():
                try:
                    msg = json.loads(raw)
                    if isinstance(msg, dict) and msg.get("type") == "ping":
                        await ws.send_text('{"type":"pong"}')
                except json.JSONDecodeError:
                    pass  # ignore malformed client messages
        except WebSocketDisconnect:
            pass
        except asyncio.CancelledError:
            raise

    @property
    def client_count(self) -> int:
        return len(self._clients)
