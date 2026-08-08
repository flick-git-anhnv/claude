#!/usr/bin/env python3
"""Re-ingest recent sessions để fix lỗi encoding payload_json trên Windows.

Root cause: trên Windows, locale.getpreferredencoding() = 'cp1252'. Nếu bất kỳ
code path nào dùng open() KHÔNG chỉ định encoding, file UTF-8 sẽ bị đọc sai
(cp1252 hoặc errors='surrogateescape'), gây mojibake trong payload_json.

Script này đọc lại từng file JSONL với encoding="utf-8", errors="replace" rồi
UPDATE payload_json trong events table cho các event type='user'. Cũng cập nhật
sessions.title nếu tìm thấy ai-title mới hơn.

Chỉ cần chạy 1 lần. Server phải đang DỪNG khi chạy script (tránh race condition).

Cách dùng:
    cd tools/agent-dashboard/backend
    python scripts/reingest_recent_sessions.py [--days 7] [--dry-run] [--all]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

# Cần import aiosqlite — nếu chưa có: pip install aiosqlite
try:
    import aiosqlite
except ImportError:
    print("ERROR: aiosqlite không tìm thấy. Chạy: pip install aiosqlite", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).parent.parent
_DATA_DIR = _BACKEND_DIR / "data"
DB_PATH = _DATA_DIR / "dashboard.db"


async def _reingest_session(
    conn: aiosqlite.Connection,
    session_id: str,
    file_path: str,
    dry_run: bool,
) -> tuple[int, int]:
    """Re-read 1 JSONL file, update payload_json + title nếu khác.

    Returns: (events_updated, title_updated) count.
    """
    p = Path(file_path)
    if not p.exists():
        logger.debug("File không tồn tại: %s", file_path)
        return 0, 0

    # Đọc file với encoding="utf-8" tường minh — đây là fix chính
    try:
        raw_text = p.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError) as exc:
        logger.warning("Không thể đọc %s: %s", file_path, exc)
        return 0, 0

    lines = raw_text.splitlines()

    # Xây dựng ts → [raw_json, ...] cho user events
    ts_to_payloads: dict[str, list[str]] = defaultdict(list)
    latest_ai_title: str | None = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        msg_type: str = data.get("type", "")
        ts: str = data.get("timestamp") or data.get("ts") or ""

        if msg_type == "user" and ts:
            ts_to_payloads[ts].append(line[:2000])
        elif msg_type == "ai-title":
            title_val = data.get("aiTitle")
            if title_val:
                latest_ai_title = str(title_val)

    if not ts_to_payloads and latest_ai_title is None:
        return 0, 0

    # Lấy events từ DB
    async with conn.execute(
        """SELECT id, ts, payload_json
             FROM events
            WHERE session_id = ? AND type = 'user'
            ORDER BY ts ASC""",
        (session_id,),
    ) as cur:
        db_events = await cur.fetchall()

    occurrence: dict[str, int] = defaultdict(int)
    events_updated = 0

    for ev in db_events:
        ts = ev["ts"]
        occ = occurrence[ts]
        occurrence[ts] += 1

        candidates = ts_to_payloads.get(ts, [])
        if occ >= len(candidates):
            continue

        new_payload = candidates[occ]
        old_payload = ev["payload_json"] or ""

        # So sánh: nếu khác nhau thì update
        if new_payload == old_payload:
            continue

        # Kiểm tra có ký tự lỗi trong old_payload không
        has_surrogate = any(0xD800 <= ord(c) <= 0xDFFF for c in old_payload)
        has_nbsp = " " in old_payload or "­" in old_payload

        if not (has_surrogate or has_nbsp) and len(new_payload) == len(old_payload):
            # Nội dung giống nhau về độ dài và không có ký tự lỗi → bỏ qua
            continue

        if dry_run:
            logger.info(
                "[DRY-RUN] Event %d (session=%s, ts=%s): payload khác — "
                "surrogate=%s nbsp=%s old_len=%d new_len=%d",
                ev["id"], session_id[:8], ts,
                has_surrogate, has_nbsp, len(old_payload), len(new_payload),
            )
        else:
            await conn.execute(
                "UPDATE events SET payload_json = ? WHERE id = ?",
                (new_payload, ev["id"]),
            )
            logger.debug(
                "Updated event %d (session=%s ts=%s)", ev["id"], session_id[:8], ts
            )
        events_updated += 1

    title_updated = 0
    if latest_ai_title and not dry_run:
        cur = await conn.execute(
            """UPDATE sessions
                  SET title = ?
                WHERE session_id = ?
                  AND (title IS NULL OR title != ?)""",
            (latest_ai_title, session_id, latest_ai_title),
        )
        title_updated = cur.rowcount
        if title_updated:
            logger.debug("Updated title for session %s: %s", session_id[:8], latest_ai_title)

    if (events_updated or title_updated) and not dry_run:
        await conn.commit()

    return events_updated, title_updated


async def run(days: int, dry_run: bool, all_sessions: bool) -> None:
    if not DB_PATH.exists():
        logger.error("DB không tìm thấy: %s", DB_PATH)
        sys.exit(1)

    conn = await aiosqlite.connect(str(DB_PATH))
    conn.row_factory = aiosqlite.Row

    try:
        if all_sessions:
            async with conn.execute(
                "SELECT session_id, file_path FROM sessions ORDER BY last_event_at DESC"
            ) as cur:
                sessions = await cur.fetchall()
            logger.info("Chế độ --all: xử lý %d sessions", len(sessions))
        else:
            async with conn.execute(
                f"""SELECT session_id, file_path FROM sessions
                    WHERE last_event_at >= datetime('now', '-{days} days')
                       OR state IN ('Running', 'Idle')
                    ORDER BY last_event_at DESC"""
            ) as cur:
                sessions = await cur.fetchall()
            logger.info(
                "Xử lý %d sessions (--days %d + Running/Idle)", len(sessions), days
            )

        total_events = 0
        total_titles = 0

        for sess in sessions:
            n_ev, n_ti = await _reingest_session(
                conn,
                sess["session_id"],
                sess["file_path"],
                dry_run=dry_run,
            )
            if n_ev or n_ti:
                logger.info(
                    "%s%s: events=%d titles=%d",
                    "[DRY-RUN] " if dry_run else "",
                    sess["session_id"][:8],
                    n_ev,
                    n_ti,
                )
            total_events += n_ev
            total_titles += n_ti

        action = "Sẽ update" if dry_run else "Đã update"
        logger.info("%s %d events, %d titles.", action, total_events, total_titles)

        if dry_run and (total_events or total_titles):
            logger.info("Chạy lại KHÔNG có --dry-run để áp dụng thay đổi.")
        elif not total_events and not total_titles:
            logger.info("Không có dữ liệu nào cần cập nhật — DB đã sạch.")

    finally:
        await conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Re-ingest JSONL sessions để fix encoding payload_json trong DB."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Xử lý sessions có hoạt động trong N ngày gần nhất (default: 7)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chỉ báo cáo, không ghi vào DB",
    )
    parser.add_argument(
        "--all",
        dest="all_sessions",
        action="store_true",
        help="Xử lý TẤT CẢ sessions (bỏ qua --days)",
    )
    args = parser.parse_args()
    asyncio.run(run(days=args.days, dry_run=args.dry_run, all_sessions=args.all_sessions))
