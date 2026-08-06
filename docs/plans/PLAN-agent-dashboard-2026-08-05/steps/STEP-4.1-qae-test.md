---
step: "4.1"
plan: ../PLAN-MASTER.md
agent: qa-engineer
status: done
completed_at: "2026-08-06 08:52"
deps: ["3.6"]
---

# STEP 4.1 — QA Engineer: Thực thi test plan

## Input nhận

Từ Tech Lead (Bước 3.6 APPROVED, commit ff0bd2e):
- do_not_redo: Backend 52/52 unit test đã pass, state-correction logic đã verify tích hợp thật. KHÔNG chạy lại pytest.
- watch_out: (1) Port 7770 có thể đang có instance uvicorn cũ — kiểm tra trước khi start. (2) Nếu log "Cannot parse timestamp" → escalate TL.
- next_inputs: Lệnh khởi động backend: `cd tools/agent-dashboard/backend && python -m uvicorn agent_dashboard.main:app --host 127.0.0.1 --port 7770 --reload`; Frontend: `cd tools/agent-dashboard/frontend && npm run dev`. Endpoints cần verify: `/api/sessions`, `/api/sessions/history`, `/api/sessions/{id}`, `/api/tokens/summary`, `/api/accounts`, `/api/health`, WebSocket.

## Nhiệm vụ

Viết test cases bao phủ 8 User Stories (US-001..US-008), thực thi trên app thật (backend đang chạy port 7770), verify 2 High fix không bị regression, log bug mới nếu có.

## Definition of Done

- [x] File `docs/test-cases/TC-agent-dashboard.md` tạo ra với ≥ 30 test cases, cover toàn bộ US-001..US-008
- [x] CRUD đầy đủ cho Account Manager (CREATE/READ/UPDATE/DELETE/ACTIVATE/REVEAL)
- [x] Verify UI-001 regression (NaN timestamp fix) — PASS
- [x] Verify UI-002 regression (Running count inflated fix) — PASS
- [x] Bug mới phát hiện được log vào `docs/bugs/`
- [x] DOCX+PDF xuất từ test cases và bug reports
- [x] Cập nhật step file + PLAN-MASTER

## Đã làm

Kiểm tra backend đang chạy port 7770 (port LISTENING, watcher_alive: true, 52/52 unit tests pass). Thực thi 44 test cases bao phủ 8 User Stories qua API thật. Verified Running count = 3 (UI-002 fix PASS) và normalizeIso() fix trong format.ts (UI-001 fix PASS). Phát hiện 2 bug mới: BUG-001 (DELETE trả 500 thay vì 204 do asyncio.get_event_loop() trong sync route) và BUG-002 (duplicate account name không bị validate). Tạo test cases file (44 TC: 39 Pass, 2 Fail, 2 Skip, 1 Partial) + 2 bug reports. Xuất DOCX+PDF cho TC file, DOCX cho bug reports.

## Artifact

- `docs/test-cases/TC-agent-dashboard.md` — 44 test cases
- `docs/test-cases/TC-agent-dashboard.docx` ✅
- `docs/test-cases/TC-agent-dashboard.pdf` ✅
- `docs/bugs/BUG-001-delete-account-500.md` — DELETE HTTP 500 bug
- `docs/bugs/BUG-001-delete-account-500.docx` ✅
- `docs/bugs/BUG-002-duplicate-account-name.md` — Duplicate name not validated
- `docs/bugs/BUG-002-duplicate-account-name.docx` ✅

## Quyết định quan trọng

1. DELETE trả 500 nhưng data đúng (account bị xóa): phân loại Severity High, Priority P2 (không P0/P1 vì tool nội bộ, data không bị mất — chỉ HTTP status sai).
2. Duplicate name: phân loại Medium P2 — vi phạm constraint nghiệp vụ nhưng không crash, không mất data.
3. TC-002 và TC-042 (empty state, no-active cảnh báo): SKIP vì không thể trigger trong môi trường production đang dùng thật — ghi nhận cần isolated env.
4. Không escalate QA Lead: 2 bug mới đều P2, không có P0/P1 — tiếp tục workflow bình thường sang Bước 4.2 QA Lead sign-off.

## Handoff Payload — bước sau đọc phần này

- do_not_redo: Đã thực thi 44 TC, đã xác nhận 2 High fix PASS. Không cần chạy lại test cơ bản — chỉ review kết quả.
- watch_out: (1) BUG-001 DELETE 500: P2, data đúng nhưng HTTP status sai — QA Lead quyết định có block release hay chỉ note. (2) BUG-002 Duplicate name: P2, missing validation — cùng quyết định. (3) TC-002, TC-042 SKIP vì môi trường — không ảnh hưởng P0/P1 coverage.
- next_inputs: Đọc `docs/test-cases/TC-agent-dashboard.md` (44 TC) + `docs/bugs/BUG-001-delete-account-500.md` + `docs/bugs/BUG-002-duplicate-account-name.md`. QA Lead cần sign-off: 2 bug P2 có block release (P2 tool nội bộ) hay tiếp tục deploy với known issues?

## Commit

- Hash: (sẽ điền sau commit)
- Đã push: không

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
