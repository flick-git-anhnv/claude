---
step: "3.5"
plan: ../PLAN-MASTER.md
agent: Senior Developer (UI-002 backend) || Junior Developer (UI-001 frontend)
status: done
completed_at: 2026-08-06 10:30
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

## Đã làm (SD phần UI-002 — fix lần 2, commit 2c0196d)

Root cause thật sự (TL xác nhận qua log tích hợp): 242/245 DB rows có `last_event_at=''`.
`_parse_ts('')` trả `now()` → elapsed ≈ 0 → tất cả giữ Running, không emit StateChange.

Fix:
1. `state_manager.py` — `_parse_ts(empty/None)` giờ trả `datetime.min.replace(tzinfo=UTC)` (`_EPOCH`) thay vì `now()`. Elapsed = hàng chục năm → `> ended_sec` → Ended.
2. Không cần migration SQL riêng: `initialize_from_db` + persistence logic trong `main.py` (lines 69-77) tự động emit 242 StateChange corrections và persist ngay vào DB khi restart.
3. Tests (52/52 pass):
   - Cập nhật `test_parse_ts_empty_returns_epoch` (thay `test_parse_ts_empty_returns_now`)
   - Thêm `test_parse_ts_none_equivalent_returns_epoch`
   - Thêm `test_initialize_from_db_empty_last_event_at_becomes_ended` (regression test chính)

Integration verify port 7770: `/api/sessions?state=Running` → **3 sessions** (trước: 244).

## Artifact (SD — fix lần 2)

- `tools/agent-dashboard/backend/agent_dashboard/state_manager.py` — `_EPOCH` constant + `_parse_ts` fix
- `tools/agent-dashboard/backend/tests/test_state_manager.py` — 3 tests cập nhật/thêm mới (52 total)
- Commit: `2c0196d`

## Quyết định quan trọng

1. Trả `datetime.min` (epoch) thay vì `epoch = datetime(1970,1,1,tzinfo=UTC)` — `datetime.min` đảm bảo elapsed luôn lớn hơn bất kỳ `ended_threshold` hợp lý nào.
2. KHÔNG thêm migration SQL riêng — `main.py` đã có logic persist `startup_changes` (commit từ bước 3.5 lần 1). Khi restart, 242 rows tự động được emit StateChange Running→Ended và persist. Clean, không cần thêm code.
3. Giữ fallback cuối hàm (parse hoàn toàn fail) vẫn trả `now()` — trường hợp khác với empty: có string nhưng sai format, hành vi cũ vẫn hợp lý.

## Handoff Payload — bước sau (TL re-verify Bước 3.6) đọc phần này

- **do_not_redo:** Backend 52 test pass, frontend 20 test pass. Không chạy lại vitest/pytest. Server đã tắt.
- **watch_out:** Verify lại port 7770 — kỳ vọng `/api/sessions?state=Running` ≤ 5. DB sẽ tự được clean khi uvicorn start (242 corrections persisted on startup). Nếu vẫn thấy nhiều Running → check xem `get_active_sessions` có còn trả rows `state='Running'` với `last_event_at=''` không (có thể DB chưa được update từ lần chạy trước).
- **next_inputs:** commit `2c0196d` (state_manager + tests). UI-001 commit `52bf96b` vẫn còn nguyên. Sau TL approve → chuyển QA Bước 4.1.
