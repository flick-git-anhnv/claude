"""File-system watcher — watchdog Observer bridged to asyncio queue.

Windows note: uses PollingObserver (500 ms) by default on win32 because the
native ReadDirectoryChangesW watcher can miss rapid writes on NTFS under heavy
load. Set env FORCE_NATIVE_WATCHER=1 to override (e.g. on macOS/Linux CI).
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from watchdog.events import FileCreatedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from . import config

logger = logging.getLogger(__name__)


class _JsonlHandler(FileSystemEventHandler):
    """Receives watchdog callbacks in the watchdog thread; pushes to asyncio queue."""

    def __init__(self, loop: asyncio.AbstractEventLoop, queue: asyncio.Queue) -> None:
        super().__init__()
        self._loop = loop
        self._queue = queue

    def _push(self, event_type: str, src_path: str) -> None:
        asyncio.run_coroutine_threadsafe(
            self._queue.put((event_type, src_path)),
            self._loop,
        )

    def on_created(self, event: FileCreatedEvent) -> None:  # type: ignore[override]
        if not event.is_directory and str(event.src_path).endswith(".jsonl"):
            self._push("created", event.src_path)

    def on_modified(self, event: FileModifiedEvent) -> None:  # type: ignore[override]
        if not event.is_directory and str(event.src_path).endswith(".jsonl"):
            self._push("modified", event.src_path)


class FileWatcher:
    """Manages a single watchdog Observer watching CLAUDE_PROJECTS_DIR."""

    def __init__(self) -> None:
        self._observer: Optional[Observer | PollingObserver] = None
        self._alive: bool = False

    @property
    def alive(self) -> bool:
        return self._alive and self._observer is not None and self._observer.is_alive()

    def start(self, loop: asyncio.AbstractEventLoop, queue: asyncio.Queue) -> None:
        watch_dir = config.CLAUDE_PROJECTS_DIR
        if not watch_dir.exists():
            logger.warning(
                "CLAUDE_PROJECTS_DIR does not exist yet: %s — "
                "watcher will not start until directory is created.",
                watch_dir,
            )
            # Do not crash — the dashboard may start before any Claude session runs.
            self._alive = False
            return

        use_polling = sys.platform == "win32" and not os.getenv("FORCE_NATIVE_WATCHER")
        if use_polling:
            obs: Observer | PollingObserver = PollingObserver(
                timeout=config.POLLING_INTERVAL_MS / 1000
            )
            logger.info("Using PollingObserver on Windows (interval=%dms)", config.POLLING_INTERVAL_MS)
        else:
            obs = Observer()
            logger.info("Using native Observer")

        handler = _JsonlHandler(loop, queue)
        obs.schedule(handler, str(watch_dir), recursive=True)
        obs.start()
        self._observer = obs
        self._alive = True
        logger.info("Watching %s", watch_dir)

    def stop(self) -> None:
        if self._observer and self._observer.is_alive():
            self._observer.stop()
            self._observer.join(timeout=5)
        self._alive = False
        logger.info("Watcher stopped")
