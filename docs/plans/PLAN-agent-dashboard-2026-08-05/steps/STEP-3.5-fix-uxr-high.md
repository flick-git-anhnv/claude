---
step: "3.5"
plan: ../PLAN-MASTER.md
agent: Senior Developer (UI-002 backend) || Junior Developer (UI-001 frontend)
status: in-progress
completed_at:
deps: ["3.4"]
---

# STEP 3.5 — Fix 2 issue High từ UXR trước khi QA

## Input nhận

Từ STEP-3.4 (UXR Review), Handoff Payload:
- **do_not_redo:** Không cần chạy lại UXR — issues đã được document rõ trong `docs/ux-review/UX-REVIEW-agent-dashboard.md`
- **watch_out:** Bước này chạy SONG SONG — JD fix UI-001 (frontend only), SD fix UI-002 (backend only). Không được đụng file của nhau.
- **next_inputs:**
  - UI-001: `tools/agent-dashboard/frontend/src/utils/format.ts` → hàm `fmtRelative()` trả "NaNh trước"
  - UI-002: `tools/agent-dashboard/backend/agent_dashboard/state_manager.py` → `initialize_from_db()` không re-evaluate state cũ

## Nhiệm vụ

### JD (Junior Developer) — UI-001 FRONTEND (file này)

Fix hàm `fmtRelative()` trong `tools/agent-dashboard/frontend/src/utils/format.ts` trả "NaNh trước" cho session cũ vì JavaScript `new Date()` không parse được timestamp Python (6 chữ số microseconds + `+00:00` suffix). Thêm fallback "dd/MM HH:mm" khi diff > 24h. Viết test vitest.

### SD (Senior Developer) — UI-002 BACKEND (file riêng)

Fix `initialize_from_db()` trong `state_manager.py` để re-evaluate state của session cũ dựa trên `last_event_at` vs current time thay vì giữ nguyên state từ DB.

## Definition of Done (JD — UI-001)

- [x] `fmtRelative()` không trả "NaNh trước" cho timestamp Python isoformat (6 microseconds + +00:00)
- [x] Fallback "dd/MM HH:mm" khi diff > 24h
- [x] `normalizeIso()` helper export — áp dụng cho toàn bộ `fmtTime`, `fmtDateTime`, `fmtDate`, `fmtRelative`
- [x] NaN graceful fallback khi timestamp hoàn toàn invalid
- [x] Vitest setup + 20 test cases pass (fmtRelative + normalizeIso + fmtDateShort)
- [x] `tsc -b` 0 lỗi
- [x] `vite build` 0 lỗi

## Đã làm (JD phần UI-001)

Root cause xác nhận: Python `datetime.now(timezone.utc).isoformat()` sinh `"2026-08-06T08:30:00.123456+00:00"` — 6 chữ số microseconds không được ECMAScript Date.parse hỗ trợ (chỉ hỗ trợ tối đa 3 chữ số milliseconds) → `new Date().getTime()` = NaN. Session rất mới (~55s) không bị ảnh hưởng vì microseconds tình cờ bằng 0 hoặc backend trả timestamp khác.

Đã làm:
1. Thêm `normalizeIso()` helper: truncate 6-digit microseconds → 3-digit, đổi `+00:00` → `Z`
2. Cập nhật toàn bộ hàm format (`fmtTime`, `fmtDateTime`, `fmtDate`) dùng `normalizeIso()` trước khi `new Date()`
3. Thêm `fmtDateShort()` (dd/MM HH:mm — không có năm) làm fallback cho diff > 24h và timestamp NaN
4. Cập nhật `fmtRelative()`: sử dụng `normalizeIso`, kiểm tra `isNaN(ts)`, fallback > 24h sang `fmtDateShort()`
5. Cài đặt `vitest@^4.1` + `@vitest/coverage-v8` làm devDependency
6. Cập nhật `vite.config.ts`: import `defineConfig` từ `vitest/config`, thêm `test` block
7. Thêm `"test": "vitest run"` vào `package.json` scripts
8. Tạo `src/utils/format.test.ts` với 20 test cases: normalizeIso (5), fmtRelative JS-native (6), fmtRelative Python-style (5), fmtRelative edge cases (2), fmtDateShort (2)

Verification:
- `npm test` → 20 passed (20), 0 failed
- `npm run build` → tsc 0 errors, vite built in 5.13s (858 modules)

## Artifact (JD)

- `tools/agent-dashboard/frontend/src/utils/format.ts` — sửa `fmtRelative`, thêm `normalizeIso`, `fmtDateShort`
- `tools/agent-dashboard/frontend/src/utils/format.test.ts` — 20 vitest tests (mới)
- `tools/agent-dashboard/frontend/vite.config.ts` — thêm vitest config
- `tools/agent-dashboard/frontend/package.json` — thêm vitest devDeps + test scripts
- `C:\Users\nguye\.claude\lessons\react-web\js-date-parse-python-microseconds-nan.md` — lesson mới
- `C:\Users\nguye\.claude\lessons\react-web\js-date-parse-python-microseconds-nan.docx` — DOCX
- `code-graph/CODE-GRAPH.md` — cập nhật: thêm tools/agent-dashboard, normalizeIso/fmtDateShort, vitest

## Quyết định quan trọng

1. Dùng `normalizeIso()` thay vì chỉ patch `fmtRelative` — áp dụng cho toàn bộ format functions vì cùng nguồn dữ liệu (backend Python), tránh lỗi tương tự ở `fmtTime`/`fmtDateTime`.
2. Chọn `vitest` (không phải Jest) vì project đã dùng Vite — `vitest` tích hợp native, không cần cấu hình thêm, nhanh hơn (~1.1s cho 20 tests).
3. Fallback > 24h → `fmtDateShort` (dd/MM HH:mm) thay vì tiếp tục "240h trước" — UX tốt hơn cho session cũ.

## Handoff Payload — bước sau đọc phần này

- **Đã làm:** JD fix UI-001 frontend xong — fmtRelative không còn NaN, 20 test pass, build sạch.
- **do_not_redo:** Không install lại vitest, không sửa lại normalizeIso — đã hoàn thành và test pass.
- **watch_out:** Bước 3.5 chưa hoàn toàn Done — SD còn phần UI-002 backend. Chỉ coi bước này Done khi CẢ HAI phần JD + SD xong. Bước 4.1 (QA) phải đợi cả 2.
- **next_inputs:** Sau khi SD merge UI-002 fix, bước 4.1 QA sẽ test trên cả frontend + backend đã fix; lưu ý test case: mở lại app sau restart backend, verify session cũ không còn hiện RUNNING, và verify fmtRelative không còn NaN.
