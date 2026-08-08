"""Session chain (roster + dispatcher history) — the /chain endpoint.

Contains:
  - `_extract_user_turn_text` : parse user turn text from event payload_json
    (used to build Dispatcher history — 1 line per user turn, not per tool call)
  - `_backfill_chain_results` : one-shot lazy backfill of tool_use_id and
    result_summary/full on Agent events whose payload_json was truncated at
    ingest time.
  - `get_session_chain`       : main entry — returns roster with Dispatcher node.
"""
from __future__ import annotations

import json as _json
import logging
from typing import Any, Optional

import aiosqlite

logger = logging.getLogger(__name__)


def _sanitize_text(text: str) -> str:
    """Làm sạch text có thể chứa lone surrogates từ lỗi encoding cũ.

    Lone surrogates (U+DC80..U+DCFF) xuất hiện khi bytes đọc sai encoding rồi
    Python áp errors='surrogateescape' (VD: byte 0x9D → U+DC9D). Hàm encode lại
    về bytes gốc qua surrogateescape, sau đó decode UTF-8 với errors='replace' để
    thay thế byte không hợp lệ bằng U+FFFD thay vì giữ surrogate phá vỡ JSON.

    Với text KHÔNG có surrogate, hàm trả nguyên bản (fast path).
    """
    # Fast path: không có surrogate → không cần xử lý
    if not any(0xD800 <= ord(c) <= 0xDFFF for c in text):
        return text
    try:
        return text.encode("utf-8", "surrogateescape").decode("utf-8", "replace")
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Fallback: xóa toàn bộ surrogate, giữ phần còn lại
        return "".join(c for c in text if not (0xD800 <= ord(c) <= 0xDFFF))


def _extract_user_turn_text(payload_json: Optional[str]) -> Optional[str]:
    """Trích văn bản user thực từ payload JSONL (dùng cho dispatcher history).

    Trả về:
      - str[:120]  nếu event này là 1 lượt user thực (message.content chứa block
                   type='text' và không phải tool_result). Cắt 120 ký tự để hiển thị gọn.
      - None       nếu event là tool_result, meta message, hoặc không parse được.

    Đây là hành vi mong đợi ở fix vấn đề 3: mỗi user turn = 1 dòng history,
    description = nội dung yêu cầu thay vì tên tool.

    Encoding safety: text được làm sạch qua _sanitize_text() trước khi trả về —
    loại bỏ lone surrogates có thể xuất hiện trong dữ liệu cũ đọc sai encoding.
    """
    if not payload_json:
        return None
    try:
        data = _json.loads(payload_json)
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    message = data.get("message") or {}
    content = message.get("content")
    # Trường hợp content là string (user turn cũ format)
    if isinstance(content, str):
        s = _sanitize_text(content.strip())
        return s[:120] if s else None
    if not isinstance(content, list):
        return None
    has_tool_result = False
    text_parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get("type")
        if btype == "tool_result":
            has_tool_result = True
            break
        if btype == "text":
            t = block.get("text") or ""
            if t.strip():
                text_parts.append(t.strip())
    if has_tool_result or not text_parts:
        return None
    combined = " ".join(text_parts).strip()
    if not combined:
        return None
    sanitized = _sanitize_text(combined)
    return sanitized[:120] if sanitized else None


async def _backfill_chain_results(
    conn: aiosqlite.Connection,
    session_id: str,
    event_rows: list,
) -> None:
    """One-shot lazy backfill: read the session JSONL and populate tool_use_id +
    result_summary/full on Agent events that are still missing those fields.

    Strategy:
    1. Get file_path from sessions table.
    2. Read all lines from the JSONL file.
    3. Build {ts: [tool_use_id, ...]} for every Agent tool_use line in the file.
    4. For each event_row with result_summary=NULL:
       a. If tool_use_id is NULL: resolve it from the ts-based mapping.
       b. Call _extract_agent_result(lines, tool_use_id).
       c. Persist both tool_use_id and result fields to the events row.
    """
    from collections import defaultdict
    from ..parser import _extract_agent_result

    # 1. Get file_path
    async with conn.execute(
        "SELECT file_path FROM sessions WHERE session_id = ?", (session_id,)
    ) as cur:
        row = await cur.fetchone()
    if not row:
        return
    file_path: str = row["file_path"]

    # 2. Read JSONL lines (best-effort; skip on IO error)
    try:
        from pathlib import Path
        session_lines: list[str] = Path(file_path).read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
    except (OSError, IOError) as exc:
        logger.warning("_backfill_chain_results: cannot read %s — %s", file_path, exc)
        return

    # 3. Build ts → [tool_use_id, ...] from Agent tool_use lines in the file
    ts_to_ids: dict[str, list[str]] = defaultdict(list)
    for raw in session_lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = _json.loads(raw)
        except _json.JSONDecodeError:
            continue
        if data.get("type") != "assistant":
            continue
        for block in (data.get("message") or {}).get("content") or []:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") == "Agent"
                and block.get("id")
            ):
                ts = data.get("timestamp") or ""
                ts_to_ids[ts].append(block["id"])

    # Occurrence counters per ts (to handle rare duplicate-ts events in order)
    ts_occurrence: dict[str, int] = defaultdict(int)

    # 4. Process each missing event row
    for ev in event_rows:
        if ev["result_summary"] is not None:
            continue  # already filled

        event_id: int = ev["id"]
        ts: str = ev["ts"]

        # Resolve tool_use_id: prefer DB value; fall back to ts-based mapping
        tool_use_id: Optional[str] = ev["tool_use_id"]
        if not tool_use_id:
            candidates = ts_to_ids.get(ts, [])
            occ = ts_occurrence[ts]
            if occ < len(candidates):
                tool_use_id = candidates[occ]
            ts_occurrence[ts] += 1

        if not tool_use_id:
            logger.debug(
                "_backfill_chain_results: no tool_use_id for event %d (ts=%s)", event_id, ts
            )
            continue

        result = _extract_agent_result(session_lines, tool_use_id)
        r_summary = result["result_summary"] if result else None
        r_full = result["result_full"] if result else None

        # Persist — always write tool_use_id (even if result is None) so we
        # don't re-scan the same event on the next /chain call.
        await conn.execute(
            """UPDATE events
                  SET tool_use_id    = ?,
                      result_summary = ?,
                      result_full    = ?
                WHERE id = ?""",
            (tool_use_id, r_summary, r_full, event_id),
        )

    await conn.commit()
    logger.debug(
        "_backfill_chain_results: backfill done for session %s (%d Agent events)",
        session_id,
        len(event_rows),
    )


async def get_session_chain(
    conn: aiosqlite.Connection,
    session_id: str,
) -> Optional[dict[str, Any]]:
    """Return pipeline chain for a session as a **roster** (Sprint 4 / FR-001 redesign).

    Roster = one entry per unique subagent role, ordered by first appearance.
    Each entry accumulates token totals across all calls and keeps a per-call history.

    Response shape:
    {
      "session_id": "...",
      "session_state": "Running|Idle|Ended",
      "roster": [
        {
          "role": "senior-developer",
          "display_name": "Senior Developer",
          "status": "active|done",
          "call_count": N,
          "latest_description": "...",
          "latest_model": "claude-sonnet-4-6" | null,
          "first_called_at": "...",
          "last_called_at": "...",
          "total_tokens": {"input": N, "output": N, "cache_creation": N, "cache_read": N},
          "history": [
            {"call_index": 1, "started_at": "...", "description": "...",
             "model": "...", "status": "done", "tokens": {...} | null}
          ]
        }
      ]
    }

    Token data is joined from child sessions via parent_session_id / attribution_agent.
    status = "active" when the latest child session for this role is still Running;
             "done" otherwise (including when no child session found).
    Returns None if the session does not exist.
    """
    from collections import defaultdict, OrderedDict
    from ..models import get_subagent_display_name

    # Verify session exists + get its state and parent fields for Dispatcher node
    async with conn.execute(
        """SELECT state, agent_type, started_at, last_event_at, title,
                  token_input, token_output, token_cache_creation, token_cache_read
             FROM sessions WHERE session_id = ?""",
        (session_id,),
    ) as cur:
        row = await cur.fetchone()
    if not row:
        return None
    session_state: str = row["state"]
    parent_row = row  # keep reference for Dispatcher node injection below

    # ── Step 1: Fetch all Agent tool_use events ordered chronologically ──────
    async with conn.execute(
        """SELECT id, ts, payload_json, subagent_type, subagent_description,
                  tool_use_id, result_summary, result_full
             FROM events
            WHERE session_id = ? AND tool_name = 'Agent'
            ORDER BY ts ASC""",
        (session_id,),
    ) as cur:
        event_rows = await cur.fetchall()

    # ── Step 1b: Lazy backfill result fields from JSONL if any event is missing them ──
    # This handles both old events (tool_use_id=NULL, ingested before Sprint 4b)
    # and new events where the result arrived after ingest.
    need_backfill = any(
        row["result_summary"] is None for row in event_rows
    )
    if need_backfill and event_rows:
        await _backfill_chain_results(conn, session_id, event_rows)
        # Re-fetch so we have the persisted result_summary/full values
        async with conn.execute(
            """SELECT id, ts, payload_json, subagent_type, subagent_description,
                      tool_use_id, result_summary, result_full
                 FROM events
                WHERE session_id = ? AND tool_name = 'Agent'
                ORDER BY ts ASC""",
            (session_id,),
        ) as cur:
            event_rows = await cur.fetchall()

    # ── Step 2: Build per-call list (resolve subagent_type from stored col / fallback JSON) ──
    raw_calls: list[dict[str, Any]] = []
    for ev in event_rows:
        subagent_type: Optional[str] = ev["subagent_type"] if "subagent_type" in ev.keys() else None
        description: Optional[str] = ev["subagent_description"] if "subagent_description" in ev.keys() else None
        if not subagent_type:
            try:
                data = _json.loads(ev["payload_json"] or "{}")
                message = data.get("message") or {}
                content = message.get("content")
                if isinstance(content, list):
                    for block in content:
                        if (
                            isinstance(block, dict)
                            and block.get("type") == "tool_use"
                            and block.get("name") == "Agent"
                        ):
                            tool_input = block.get("input") or {}
                            subagent_type = tool_input.get("subagent_type") or None
                            description = tool_input.get("description") or None
                            break
            except (ValueError, AttributeError):
                pass
        result_summary: Optional[str] = ev["result_summary"] if "result_summary" in ev.keys() else None
        result_full: Optional[str] = ev["result_full"] if "result_full" in ev.keys() else None
        raw_calls.append({
            "subagent_type":  subagent_type,
            "description":    description,
            "started_at":     ev["ts"],
            "result_summary": result_summary,
            "result_full":    result_full,
        })

    # ── Step 3: Load child sessions grouped by attribution_agent ─────────────
    # IMPORTANT: do NOT filter by is_subagent=0 here — child sessions ARE subagents.
    async with conn.execute(
        """SELECT session_id, attribution_agent, agent_type, state, started_at,
                  token_input, token_output, token_cache_creation, token_cache_read
             FROM sessions
            WHERE parent_session_id = ?
            ORDER BY attribution_agent ASC, started_at ASC""",
        (session_id,),
    ) as cur:
        child_rows = await cur.fetchall()

    # {attribution_agent -> [child dicts sorted by started_at]}
    children_by_role: dict[str, list[dict]] = defaultdict(list)
    for r in child_rows:
        children_by_role[r["attribution_agent"]].append(dict(r))

    # ── Step 4: Match each call to its child session (Nth call of role X → Nth child of role X) ──
    occurrence_counter: dict[str, int] = defaultdict(int)
    matched_calls: list[dict[str, Any]] = []
    for call in raw_calls:
        role = call["subagent_type"]
        if role:
            idx = occurrence_counter[role]
            occurrence_counter[role] += 1
            matches = children_by_role.get(role, [])
            child = matches[idx] if idx < len(matches) else None
        else:
            child = None

        tokens_step: Optional[dict] = None
        model: Optional[str] = None
        child_state: Optional[str] = None
        if child:
            tokens_step = {
                "input":          child["token_input"] or 0,
                "output":         child["token_output"] or 0,
                "cache_creation": child["token_cache_creation"] or 0,
                "cache_read":     child["token_cache_read"] or 0,
            }
            model = child["agent_type"]
            child_state = child["state"]

        matched_calls.append({
            "subagent_type":  role,
            "description":    call["description"],
            "started_at":     call["started_at"],
            "tokens":         tokens_step,
            "model":          model,
            "child_state":    child_state,
            "result_summary": call.get("result_summary"),
            "result_full":    call.get("result_full"),
        })

    # ── Step 5: Build roster — one entry per unique role, ordered by first appearance ──
    # Use OrderedDict to preserve insertion order (Python 3.7+ guarantees it, but explicit is clearer)
    roster_map: dict[str, dict[str, Any]] = OrderedDict()
    for i, call in enumerate(matched_calls):
        role = call["subagent_type"] or "__unknown__"
        if role not in roster_map:
            roster_map[role] = {
                "role":               role if role != "__unknown__" else None,
                "display_name":       get_subagent_display_name(role) if role != "__unknown__" else None,
                "call_count":         0,
                "latest_description": None,
                "latest_model":       None,
                "first_called_at":    call["started_at"],
                "last_called_at":     call["started_at"],
                "total_tokens":       {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0},
                "history":            [],
            }
        entry = roster_map[role]
        entry["call_count"] += 1
        entry["last_called_at"] = call["started_at"]
        entry["latest_description"] = call["description"]
        if call["model"]:
            entry["latest_model"] = call["model"]

        # Accumulate tokens
        if call["tokens"]:
            for k in ("input", "output", "cache_creation", "cache_read"):
                entry["total_tokens"][k] += call["tokens"][k]

        # Per-call history item
        history_item: dict[str, Any] = {
            "call_index":     entry["call_count"],
            "started_at":     call["started_at"],
            "description":    call["description"],
            "model":          call["model"],
            "tokens":         call["tokens"],
            "result_summary": call.get("result_summary"),
            "result_full":    call.get("result_full"),
            "duration_ms":    None,
        }
        entry["history"].append(history_item)

    # ── Step 6: Compute status for each roster entry ─────────────────────────
    # PRIMARY SIGNAL — result_summary / result_full on the Agent event:
    #   If the parent session has already received a tool_result for this Agent call,
    #   both fields are populated (via backfill or real-time ingest).
    #   result_summary set → agent definitively finished, regardless of child_state.
    #   result_summary None → no result received yet → agent possibly still running.
    #
    # SECONDARY SIGNAL — child session state (only Ended is trusted):
    #   "Ended" is a reliable termination signal.
    #   "Idle" / "Running" are ambiguous (cannot distinguish "waiting for LLM" from
    #   "finished long ago but not yet timed out to Ended") — intentionally ignored.
    #
    # PARENT GATE — session_state == "Running" only:
    #   "Idle" parent = ambiguous (parent stopped writing events while child works).
    #   "Ended" parent = all roles are done.
    #   Only a "Running" parent can have an actively-executing child.
    #
    # Decision table (for the LAST call of each role):
    #   result set           → "done"  (primary, unconditional)
    #   child Ended          → "done"  (secondary, reliable)
    #   parent Ended/Idle    → "done"  (parent gate)
    #   parent Running + no result + child not Ended → "active"
    roster: list[dict[str, Any]] = []
    for role_key, entry in roster_map.items():
        # Find the last matched_call for this role
        last_matched = next(
            (c for c in reversed(matched_calls) if (c["subagent_type"] or "__unknown__") == role_key),
            None,
        )
        last_child_state = last_matched["child_state"] if last_matched else None
        last_result_summary = last_matched.get("result_summary") if last_matched else None
        last_result_full = last_matched.get("result_full") if last_matched else None

        is_active = (
            session_state == "Running"                          # parent still alive
            and last_matched is not None                        # at least one call exists
            and last_result_summary is None                     # no result received yet (primary)
            and last_result_full is None
            and last_child_state != "Ended"                    # Ended child = definitively done
        )
        entry["status"] = "active" if is_active else "done"

        # Annotate each history item's status
        for hist_item in entry["history"]:
            pass  # status per-call is implicitly "done" for all except possibly the last one
        # Last history item is "active" if role is active
        if entry["history"]:
            entry["history"][-1]["status"] = "active" if is_active else "done"
            for h in entry["history"][:-1]:
                h["status"] = "done"

        roster.append(entry)

    # ── Sprint 5 — FR-004: Prepend Dispatcher node (session gốc) ───────────────
    # The parent session IS the Dispatcher (main Claude loop). It is always the
    # first entry so the frontend can render it at the head of the pipeline view.
    # Token accounting: parent_row tokens are the Dispatcher's OWN LLM turns —
    # they do NOT include children's tokens (each session has its own DB row).
    #
    # FR-006-dispatcher (Fix vấn đề 3): Build history from USER TURNS instead
    # of every tool call. Trước đây mỗi tool (Read/Write/Bash/…) là 1 dòng —
    # gây ra danh sách quá dài, khó theo dõi. Giờ nhóm theo mỗi lần user gửi
    # tin nhắn (human turn), description = trích văn bản đầu tiên của tin đó.
    #
    # Phân biệt user turn thực với tool_result: tool_result có content=list
    # chứa block type='tool_result'; user turn thực chứa block type='text'.
    async with conn.execute(
        """SELECT ts, payload_json
             FROM events
            WHERE session_id = ? AND type = 'user'
            ORDER BY ts ASC""",
        (session_id,),
    ) as _dcur:
        _disp_event_rows = await _dcur.fetchall()

    dispatcher_history: list[dict[str, Any]] = []
    _idx = 0
    for _dev in _disp_event_rows:
        text = _extract_user_turn_text(_dev["payload_json"])
        if text is None:
            continue  # tool_result hoặc user meta message → bỏ qua
        _idx += 1
        dispatcher_history.append({
            "call_index":     _idx,
            "started_at":     _dev["ts"],
            "description":    text,
            "model":          None,
            "tokens":         None,
            "result_summary": None,
            "result_full":    None,
            "duration_ms":    None,
            "status":         "done",  # annotated below
        })

    # Fallback: nếu không có user turn nào (trường hợp hiếm — session cũ chưa
    # lưu payload_json đầy đủ), dùng title làm 1 dòng đại diện để không rỗng.
    if not dispatcher_history and parent_row["title"]:
        dispatcher_history.append({
            "call_index":     1,
            "started_at":     parent_row["started_at"],
            "description":    parent_row["title"],
            "model":          None,
            "tokens":         None,
            "result_summary": None,
            "result_full":    None,
            "duration_ms":    None,
            "status":         "done",
        })

    # Annotate last item as active when session is still Running
    if dispatcher_history:
        if session_state == "Running":
            dispatcher_history[-1]["status"] = "active"
        # All earlier items are always done
        for _h in dispatcher_history[:-1]:
            _h["status"] = "done"

    dispatcher_entry: dict[str, Any] = {
        "role":               "__dispatcher__",
        "display_name":       "Claude (Dispatcher)",
        "is_dispatcher":      True,
        "status":             "active" if session_state == "Running" else "done",
        # call_count reflects own tool events so HistoryPanel header is accurate;
        # falls back to 1 when no own tool events (unlikely but safe).
        "call_count":         len(dispatcher_history) if dispatcher_history else 1,
        "latest_description": parent_row["title"] or "Phiên chính",
        "latest_model":       parent_row["agent_type"],
        "first_called_at":    parent_row["started_at"],
        "last_called_at":     parent_row["last_event_at"],
        "total_tokens": {
            "input":          parent_row["token_input"] or 0,
            "output":         parent_row["token_output"] or 0,
            "cache_creation": parent_row["token_cache_creation"] or 0,
            "cache_read":     parent_row["token_cache_read"] or 0,
        },
        "history": dispatcher_history,
    }

    return {
        "session_id":    session_id,
        "session_state": session_state,
        "roster":        [dispatcher_entry] + roster,
    }
