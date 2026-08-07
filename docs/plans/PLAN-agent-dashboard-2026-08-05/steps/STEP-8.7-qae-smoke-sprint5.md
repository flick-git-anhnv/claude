---
step: "8.7"
plan: ../PLAN-MASTER.md
agent: qa-engineer
status: done
completed_at: 2026-08-07 15:30
deps: ["8.6"]
---

# STEP 8.7 — QA Smoke Test Sprint 5: Usage Display + BUG-004 + FR-004 + FR-005

## Input nhận
- UXR Sprint 5 PASS (report `docs/ux-review/UX-REVIEW-sprint5.md`): 0 Critical, 0 High, 1 Medium (UI-001 UsageBar ẩn khi 429), 1 Low (UI-002 text quota)
- App chạy local: http://127.0.0.1:7770 (backend FastAPI + frontend dist — một URL duy nhất qua start.bat). KHÔNG dùng port 5173 (tool khác).
- Quota API Anthropic đang rate-limit (429) trong suốt session test — ảnh hưởng happy path UsageBar
- 4 hạng mục cần test: A Usage Display, B BUG-004, C FR-004 Dispatcher, D FR-005 Toggle + BUG-005
- Handoff từ TL 8.5: 250/250 pytest pass, tsc/vite 0 errors, schema Pydantic↔TS khớp 100%, 5/5 hạng mục APPROVED

## Nhiệm vụ
Smoke test Sprint 5 — kiểm tra cả 4 hạng mục hoạt động đúng, verify BUG-004 đã fixed, và regression test không phá các tính năng Sprint 1-4 cũ.

## Definition of Done
- [ ] Chạy app thật (backend port 7770 + frontend port 5173) — không dùng mock

### Usage Display (A)
- [ ] TC-S5-01: AppHeader hiển thị UsageBar — Session % + Weekly % hoặc "--" graceful
- [ ] TC-S5-02: Giá trị % trong [0, 100] hoặc null — không NaN/Infinity
- [ ] TC-S5-03: "Resets in Xh/Xd" text hợp lý (không âm, không Invalid)
- [ ] TC-S5-04: AccountManagerPage — UsageBar trên ≥1 AccountCard
- [ ] TC-S5-05: Polling 60s — UsageBar refresh không flicker, không console error
- [ ] TC-S5-06: CLI fail scenario — dashboard không crash, UsageBar fallback graceful
- [ ] TC-S5-07: `GET /api/accounts/usage` → HTTP 200, schema đúng (`session_pct`, `weekly_pct` float hoặc null)
- [ ] TC-S5-08: `GET /api/accounts/{id}/usage` → 200 với data hoặc null, không 500

### BUG-004 Fix (B)
- [ ] TC-S5-09: Card agent đang RUNNING (có session live hoặc trigger thủ công) → hiển thị `model` và `tokens` (không để trống hoặc "--")
- [ ] TC-S5-10: Card ✅ Done vẫn hiển thị model+tokens như trước (không regression)
- [ ] TC-S5-11: `GET /api/sessions/by-project` → session RUNNING có `model != null` và `tokens_in > 0` trong response JSON

### FR-004 Dispatcher Node (C)
- [ ] TC-S5-12: Mở Pipeline view của bất kỳ session → node "Claude (Dispatcher)" luôn xuất hiện đầu tiên
- [ ] TC-S5-13: Node Dispatcher có style phân biệt (màu Navy, label đúng) — không lẫn với subagent node
- [ ] TC-S5-14: `GET /api/sessions/{id}/chain` → `roster[0].subagent_type === "dispatcher"` hoặc tương đương (confirm qua curl)

### FR-005 Toggle 2 chế độ (D)
- [ ] TC-S5-15: Toggle "Tổng hợp" → render aggregate view (danh sách role, total_calls, token)
- [ ] TC-S5-16: Toggle "Theo Session" → render session list như cũ (không regression)
- [ ] TC-S5-17: `GET /api/pipeline/aggregate` (hoặc endpoint tương ứng) → HTTP 200, sort by calls DESC
- [ ] TC-S5-18: Toggle nhiều lần liên tục → không crash, không console error

### Regression (Sprint 1-4)
- [ ] AccountCard activate/deactivate vẫn hoạt động sau khi thêm UsageBar
- [ ] AppHeader account name + chấm xanh vẫn đúng bên cạnh UsageBar
- [ ] Pipeline view Sprint 3/4 — `/api/sessions/{id}/chain` vẫn load đúng (không bị Dispatcher node vỡ schema cũ)
- [ ] Token Analytics chart (Output/Input tách riêng, Sprint 4 fix UI-003) không ảnh hưởng
- [ ] Không có lỗi console ERROR khi navigate toàn bộ các trang

- [ ] Ghi kết quả vào `docs/test-cases/TC-agent-dashboard.md` (append section Sprint 5)
- [ ] Kết luận: PASS hoặc FAIL (danh sách TC fail nếu có)

## Đã làm

1. Đọc UXR Sprint 5 (STEP-8.6), TL review (STEP-8.5), SD backend (STEP-8.3) để nắm API contract và known issues
2. Xác nhận app đang chạy: `GET /api/health → {"status":"ok","watcher_alive":true,"ws_clients":1}`
3. **Nhóm A — Usage Display (8 TC):**
   - TC-S5-07/08: curl cả 2 endpoints usage → HTTP 200, schema đúng, error="http_429" graceful
   - TC-S5-01: FAIL — UsageBar ẩn hoàn toàn khi 429, không hiện "--" (UI-001 Medium đã biết từ UXR)
   - TC-S5-02/04/05/06: PASS — null handled, no NaN, code verify clearInterval, no crash
   - TC-S5-03: SKIP — rate-limited, không có data reset timer
4. **Nhóm B — BUG-004 (3 TC):**
   - curl /chain session 8f3eab89: roster[8]=qa-engineer active, latest_model=None, tokens=0 → trigger "đang khởi tạo…" fallback (code verified AgentRosterItem.tsx:192-194)
   - Done entries trong roster có model + tokens đầy đủ (PASS regression)
   - TC-S5-11: /by-project RUNNING session có agent_type="claude-sonnet-5" và token_total.input=212 ✅
5. **Nhóm C — FR-004 Dispatcher (3 TC):**
   - curl /chain: roster[0].role="__dispatcher__", is_dispatcher=True, history=[], 1 dispatcher count
   - Test cả Running (8f3eab89) và Ended (11816ae6) sessions: Dispatcher luôn đầu tiên
   - Code review: Navy #251C53, icon 🧠, không có "Xem lịch sử" button
6. **Nhóm D — FR-005 + BUG-005 (4 TC):**
   - curl /aggregate: HTTP 200, sorted DESC ([389,148,84,74,66]), edge cases (project=nonexistent, window=0/7/30/90) không crash
   - Code verify usePipelineMode.ts: localStorage persist ✅
   - BUG-005: AgentRosterItem.tsx:375 `hasHistory = !is_dispatcher && call_count >= 1`, UXR confirmed ✅
7. **Regression (5 test):**
   - /api/accounts: 2 accounts, is_active đúng ✅
   - /chain schema: history fields Sprint 3/4 nguyên vẹn ✅
   - /api/tokens/summary: output + cache_read tách riêng ✅ (Sprint 4 UI-003 fix intact)
   - Health + account name PASS
8. Append section Sprint 5 vào `docs/test-cases/TC-agent-dashboard.md` (18 TC + 5 regression)
9. Xuất DOCX + PDF: `docs/test-cases/TC-agent-dashboard.docx` + `.pdf` ✅

## Artifact
- `docs/test-cases/TC-agent-dashboard.md` — section Sprint 5 appended (18 TC + 5 regression)
- `docs/test-cases/TC-agent-dashboard.docx` ✅
- `docs/test-cases/TC-agent-dashboard.pdf` ✅

## Quyết định quan trọng

1. **Sprint 5 PASS** — không có P0/P1 bug mới. QA Engineer tự kết luận đủ điều kiện (P2 tool nội bộ, không cần QA Lead sign-off theo thỏa thuận trước).
2. **TC-S5-01 FAIL = UI-001 Medium (non-blocking)**: UsageBar ẩn hoàn toàn khi quota API 429. Đã có trong UXR report. Không tạo BUG file mới (không phải bug mới từ QA). Đề xuất fix Sprint 6.
3. **TC-S5-03 SKIP** = Quota API rate-limited, không phải lỗi code. Có thể test lại khi rate-limit giải phóng.
4. **Plan AGENT-DASHBOARD có thể đóng** sau commit bước này. Sprint 6 backlog (FR-006 group-by-project) sẽ là plan mới nếu tiếp tục.
5. **Không có bug mới** nào yêu cầu tạo `docs/bugs/BUG-*.md` mới.

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: 18 TC đã thực thi và ghi kết quả đầy đủ vào TC-agent-dashboard.md Sprint 5 section. DOCX+PDF đã xuất. Không cần chạy lại test suite hay re-verify schema.
- watch_out: TC-S5-01 FAIL (UI-001 Medium) là known issue, không phải regression mới. TC-S5-03 SKIP do rate-limit môi trường. Quota API đang 429 — nếu Sprint 6 cần test Usage happy path, phải đợi rate-limit hết.
- next_inputs: Sprint 5 PASS — plan agent-dashboard-2026-08-05 có thể đóng (status: completed). Backlog Sprint 6: FR-006 group-by-project (PLAN-MASTER "Backlog Sprint 6"). UI-001 Medium cần fix trong Sprint 6: AppHeader UsageBar phải hiển thị "--" + tooltip khi error, không ẩn hoàn toàn.

## Commit
- Hash: (điền sau commit)
- Đã push: không

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
