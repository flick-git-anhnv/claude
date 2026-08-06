---
step: 5.5
title: Code review cuối Sprint 2 (Track A + Track B) + merge decision
agent: Tech Lead
status: done
completed_at: 2026-08-06 10:30
depends_on: [5.2, 5.3, 5.4]
---

# Bước 5.5 — TL review cuối Sprint 2 (Track A OAuth + Track B Agent View)

## Nhiệm vụ
Review cuối trước khi đóng Sprint 2: xác nhận Track A (OAuth, `7dcae48` + hotfix H-1 `b1866cc`) và Track B (Agent name/2-view, `5c23e75`) không xung đột logic, chạy full test + build, tích hợp thật, quyết định merge.

## Đã làm
1. **Diff cross-track:** `models.py` chỉ Track B sửa (thêm `SUBAGENT_DISPLAY`, `decode_project_slug`, 2 field optional `subagent_type`/`subagent_activity` vào `ParsedLine`). Track A KHÔNG đụng `models.py` — đúng như JD báo cáo. Không xung đột.
2. **Backend tests:** `pytest tests/ -q` → **119/119 PASS** (0.50s). Không hồi quy.
3. **Frontend build ban đầu FAIL:** `tsc -b` báo 6 lỗi TS2741 — Track A thêm `kind: AccountKind` làm required trong `Account`/`ActiveAccount` nhưng `wsReducer.ts:101` (production) và 5 file mock (`interceptor.ts`, `mockData.ts` ×3, `mockWebSocket.ts`) chưa được cập nhật. Đây là regression của Track A chưa được phát hiện ở 5.2 (SD chỉ test backend + chạy `claude -p`, không chạy `npm run build`).
4. **Hotfix inline (TL authority, type-only, không đổi runtime):** Nới `kind: AccountKind` → `kind?: AccountKind` trong cả `Account` và `ActiveAccount` (`src/types/index.ts`). Lý do: WS delta `account_changed` (`routes/accounts.py:300-308`) chưa gửi `kind`, và các mock legacy vẫn hợp lệ. Sprint 3 sẽ chuẩn hóa backend gửi `kind` rồi thắt lại required.
5. **Re-build:** `tsc -b` 0 lỗi, `vite build` PASS (580 kB gzip 169 kB, warning size only).
6. **Tích hợp thật:** server đang chạy port 7770.
   - `/api/health` → `{"status":"ok","watcher_alive":true,"ws_clients":1}` ✅
   - `/api/accounts` → trả 2 account, có field `kind:"api_key"` ✅ (Track A schema OK)
   - `/api/sessions/by-project` → endpoint Track B trả về, có `project_slug`, `session_count`, `token_total` ✅

## Bug mới phát hiện (user report qua UI thật)

### BUG-003: "Bắt đầu: Invalid Date" trên session mới / legacy
- **Reproduce:** ✅ TÁI HIỆN được. `curl /api/sessions/by-project` trả về sessions có `started_at: ""` (chuỗi rỗng). Frontend `new Date("")` → `Invalid Date`.
- **Root cause:** `parser.py:55` fallback `timestamp: str = data.get("timestamp") or data.get("ts") or ""`; và `state_manager` snapshot sessions cũ (khi chưa từng parse dòng nào có timestamp hợp lệ) cũng để `""`.
- **Chênh với UI-002 cũ:** UI-002 fix cho `last_event_at=''` (state machine), lần này là `started_at=''` (snapshot API + WS `agent_started` khi JSONL đầu tiên không có timestamp).
- **Severity/Priority đề xuất:** P2 (UI display only, không ảnh hưởng chức năng). Fix pattern giống UI-001: `fmtDateTime`/`fmtTime` trả về "—" khi input rỗng hoặc `isNaN(date.getTime())`. Ghi vào Blockers → Sprint 3.

### FR-001 (feature request): Pipeline view cho Agent Status Panel
- **Nội dung:** User muốn thay list card rời rạc bằng 1 flow/pipeline duy nhất — các vai trò trong chain (PM→BA→…→SD/JD→TL→QA→Deploy) xếp thành hàng, agent đang hoạt động highlight sáng (tên + việc đang làm + token), agent khác trong chain mờ đi.
- **Impact:** UI thay đổi lớn — cần UX/UI Designer thiết kế lại `AgentStatusPanel` + xác định vòng đời "chain đang chạy" (định danh 1 workflow như thế nào từ JSONL log?).
- **Action:** Ghi vào Backlog Sprint 3 (không làm ngay). Kèm câu hỏi cho PM/UX: nhận diện "chain" bằng gì (session_id gốc? parent-task marker?).

## Quyết định merge
✅ **APPROVED merge Sprint 2** (Track A + Track B + H-1 + hotfix TS type nới `kind` optional).
- 119/119 backend tests PASS
- Frontend `tsc -b` + `vite build` PASS
- Tích hợp thật: 3/3 endpoint chính PASS
- 2 vấn đề mới ghi nhận vào Backlog Sprint 3 (BUG-003 P2 + FR-001)
- Không có vấn đề chặn merge

## Artifact
- `tools/agent-dashboard/frontend/src/types/index.ts` — hotfix TS `kind?: AccountKind` (2 chỗ)
- `tools/agent-dashboard/frontend/dist/` — bundle prod build OK
- STEP file này + PLAN-MASTER cập nhật

## Handoff Payload — bước sau đọc phần này
- Đã làm: Review cross-track, chạy đủ test + build + tích hợp thật, hotfix type strictness của Track A (nới `kind` optional), xác nhận không xung đột. Bug Invalid Date + feature request pipeline view đã ghi Backlog Sprint 3.
- do_not_redo: Không cần chạy lại pytest/tsc/vite build cho Sprint 2. Không cần reproduce lại bug Invalid Date — đã có curl output chứng minh.
- watch_out: Sprint 3 cần: (1) backend gửi `kind` trong WS delta `account_changed` + `activeAccount` snapshot → sau đó thắt lại `kind: AccountKind` required trong TS types; (2) fix `fmtDateTime`/`fmtTime` an toàn với input rỗng hoặc chuẩn hóa `started_at` ở backend (không dùng `""` fallback ở `parser.py:55` + `state_manager` snapshot); (3) Pipeline view cần cả UX design mới + backend cách nhận diện "chain".
- next_inputs: Không có — WF-FEATURE Sprint 2 khép lại; Sprint 3 kick-off cần Phase mới trong PLAN-MASTER (task-planner).
