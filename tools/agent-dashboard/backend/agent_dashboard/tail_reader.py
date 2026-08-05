"""Per-file cursor reader — only yields complete lines (ending with \\n).

Key invariants:
  - offset is always in BYTES (not characters), so multi-byte UTF-8 is safe.
  - Partial last line (no trailing \\n) is NOT yielded — deferred to next read.
  - File truncation (offset > size) → reset cursor to 0 and re-read from start.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class TailReader:
    """Maintains per-file byte offset; returns only fully-written lines."""

    def __init__(self) -> None:
        self._cursors: Dict[str, int] = {}  # absolute path -> last committed byte offset

    # ── Public API ─────────────────────────────────────────────────────────────

    def restore_cursors(self, cursors: dict[str, int]) -> None:
        """Seed offsets from DB on startup (survival across restarts)."""
        self._cursors.update(cursors)

    def get_cursor(self, file_path: str) -> int:
        return self._cursors.get(file_path, 0)

    def set_cursor(self, file_path: str, offset: int) -> None:
        """Allow external code to forcibly set cursor (e.g., after DB save)."""
        self._cursors[file_path] = offset

    def read_new_lines(self, file_path: str) -> List[str]:
        """
        Read bytes after last committed offset.
        Returns list of complete lines (each includes the trailing '\\n').
        Updates internal cursor to byte position after last complete line.
        """
        path = Path(file_path)
        if not path.exists():
            return []

        current_offset = self._cursors.get(file_path, 0)

        try:
            with open(path, "rb") as fh:
                # Detect file size first to handle truncation
                file_size = fh.seek(0, 2)

                if current_offset > file_size:
                    # File was truncated / rotated → restart from beginning
                    logger.warning("File shrunk, resetting cursor: %s", file_path)
                    current_offset = 0

                fh.seek(current_offset)
                new_bytes = fh.read()
        except OSError as exc:
            logger.warning("Cannot read %s: %s", file_path, exc)
            return []

        if not new_bytes:
            return []

        # Find byte position of the LAST newline
        last_nl = new_bytes.rfind(b"\n")
        if last_nl == -1:
            # No complete line yet — nothing to yield
            return []

        # Only process bytes up to (and including) the last newline
        complete_bytes = new_bytes[: last_nl + 1]
        new_offset = current_offset + last_nl + 1
        self._cursors[file_path] = new_offset

        # Decode with error replacement (not 'ignore') so offsets stay consistent
        text = complete_bytes.decode("utf-8", errors="replace")

        # Split and re-attach newline so callers don't have to worry about it
        lines = [ln + "\n" for ln in text.split("\n") if ln]
        return lines
