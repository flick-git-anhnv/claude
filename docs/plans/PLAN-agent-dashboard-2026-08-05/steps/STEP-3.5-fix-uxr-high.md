---
step: "3.5"
plan: ../PLAN-MASTER.md
agent: Senior Developer (backend) ∥ Junior Developer (frontend)
status: in-progress
completed_at:
deps: ["3.4"]
---

# STEP 3.5 — Fix 2 issue High từ UXR (UI-001 frontend + UI-002 backend)

## Input nhận
Từ STEP-3.4 UX/UI Reviewer:
- `docs/ux-review/UX-REVIEW-agent-dashboard.md` — danh sách 6 issue; 2 High cần fix trước QA:
  - **UI-001** (frontend): "NaNh trước" — `formatRelativeTime()` parse fail với timestamp ISO cũ
  - **UI-002** (backend): 62–240+ sessions hiển thị RUNNING dù `last_event_at` hàng trăm giờ trước;
    root cause: `initialize_from_db()` restore state cũ từ DB thay vì re-evaluate từ `last_event_at`

## Nhiệm vụ
Senior Developer fix UI-002 ở backend (state_manager + main.py + tests).
Junior Developer fix UI-001 ở frontend (formatRelativeTime + fallback). Hai người chạy song song (∥), KHÔNG đụng file của nhau.

## Definition of Done
- [x] UI-002: `initialize_from_db()` re-evaluates state từ `last_event_at` thay vì dùng stored state
- [x] UI-002: `main.py` lifespan persist startup corrections ngay trước khi ticker chạy
- [x] UI-002: Unit test mới — stale Running→Ended, Running→Idle, no-change, multiple stale
- [x] UI-002: `python -m pytest tests/ -q` — 50/50 pass, 0 fail
- [ ] UI-001: `formatRelativeTime()` frontend xử lý đúng mọi ISO format (kể cả timestamp cũ)
- [ ] UI-001: Fallback "dd/MM HH:mm" khi diff > 24h để tránh "NaNh trước"
- [ ] UI-001: Frontend build (tsc + vite) không có error sau fix

## Đã làm (backend — Senior Developer)

### Root cause xác nhận
`initialize_from_db()` trong `state_manager.py` gọi `row.get("state", "Running")` rồi dùng thẳng giá trị đó làm state in-memory. Các session cũ trong SQLite có `state = 'Running'` (mặc định khi insert) và chưa bao giờ bị ticker update vì backend đã restart nhiều lần. Hệ quả: mọi client kết nối WebSocket trong 30s đầu sau startup nhận snapshot với 200+ session RUNNING.

### Fix thực hiện
1. **`state_manager.py`** — `initialize_from_db()` signature thay đổi:
   - Nhận thêm `idle_threshold: Optional[int]` và `ended_threshold: Optional[int]`
   - Tính `elapsed = (now - last_event_ts).total_seconds()` cho từng session
   - Gán `new_state = "Ended"` / `"Idle"` / `"Running"` theo thresholds — KHÔNG dùng stored state
   - Trả về `List[StateChange]` cho các session cần correction (thay vì `None`)

2. **`main.py`** — lifespan cập nhật:
   - Nhận `startup_changes = _state_mgr.initialize_from_db(active_sessions)`
   - Loop persist từng change vào DB qua `db_module.update_session_state()` ngay trước khi yield
   - Log số correction để audit

3. **`tests/test_state_manager.py`** — 4 test mới thay thế `test_initialize_from_db` cũ:
   - `test_initialize_from_db_recent_sessions_keep_correct_state`
   - `test_initialize_from_db_stale_running_becomes_ended`
   - `test_initialize_from_db_returns_no_changes_when_states_already_correct`
   - `test_initialize_from_db_multiple_stale_sessions_all_corrected`

## Đã làm (frontend — Junior Developer)
[Chờ JD điền sau khi hoàn thành UI-001]

## Artifact
- `tools/agent-dashboard/backend/agent_dashboard/state_manager.py` (sửa)
- `tools/agent-dashboard/backend/agent_dashboard/main.py` (sửa)
- `tools/agent-dashboard/backend/tests/test_state_manager.py` (sửa)

## Quyết định quan trọng
- Re-evaluate tại `initialize_from_db()` thay vì chỉ gọi `evaluate_all()` sau — để state in-memory sạch ngay khi seeded, không phụ thuộc vào caller nhớ gọi thêm.
- `initialize_from_db()` override không dùng `_idle_override`/`_ended_override` nếu là 0 (falsy) — dùng pattern `x if x is not None else (self._override or config.X)` để truyền `0` từ test không bị ignore.

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: Backend UI-002 đã fix và commit ed84b69. Test 50/50 pass. Không cần sửa thêm state_manager/main.py cho issue này.
- watch_out: `initialize_from_db()` bây giờ trả về `List[StateChange]` thay vì `None` — nếu có test mock cũ gọi method này mà không dùng return value sẽ vẫn pass nhưng cần aware về signature change.
- next_inputs: Sau khi JD xong UI-001, cả 2 fix merge vào branch → QA (bước 4.1) verify: (1) backend restart → agent panel chỉ hiện session thực sự active, (2) timestamps frontend hiển thị đúng định dạng, không "NaNh trước".

## Commit
- Hash (backend): ed84b69
- Hash (frontend UI-001): [JD điền]
- Đã push: có (branch research/skills-2026-08-05)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
