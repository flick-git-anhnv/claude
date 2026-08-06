---
step: 3.6
plan: ../PLAN-MASTER.md
agent: Tech Lead
status: blocked
completed_at:
deps: ["3.5"]
---

# STEP 3.6 — TL verify 2 fix UXR High + quyết định merge cuối

## Input nhận
- SD commit `ed84b69` fix UI-002 (`state_manager.initialize_from_db` re-evaluate + main.py persist trước ticker).
- JD commit `52bf96b` fix UI-001 (`format.ts` normalizeIso + fmtDateShort fallback).
- Handoff Payload STEP-3.5: chờ TL xác nhận trước khi chuyển QAE.

## Nhiệm vụ
Verify nhanh 2 fix qua đọc code, chạy full test, chạy tích hợp thật port 7770 để xác nhận dashboard không còn hiển thị "NaNh trước" và số session RUNNING đã hợp lý trước khi chuyển QA.

## Definition of Done
- [x] Code review `state_manager.py` + `main.py` (UI-002)
- [x] Code review `format.ts` (UI-001)
- [x] Backend `pytest -q` → 50/50 pass
- [x] Frontend `vitest run` → 20/20 pass + `npm run build` OK
- [x] Chạy uvicorn port 7770 + kiểm tra `/api/sessions?state=Running`
- [ ] **Số Running hợp lý (≤ vài session active)** → **FAIL: 244 Running sau restart**
- [ ] Quyết định merge cuối

## Đã làm
1. Đọc `state_manager.py`, `main.py`, `format.ts`: logic đúng theo mô tả commit.
2. Chạy test: backend 50/50 pass, frontend 20/20 pass, vite build 573KB OK.
3. Start uvicorn port 7770 với `logging.basicConfig(level=INFO)` → log rõ ràng:
   `agent_dashboard.main INFO State machine seeded with 245 sessions; 0 stale-state corrections`
4. `/api/sessions?state=Running` trả về **244 sessions** (kỳ vọng ≤ vài).
5. Truy vấn DB trực tiếp: `SELECT state, COUNT(*) FROM sessions GROUP BY state` → Running=245, Ended=105.
6. Truy vấn top Running: 3 sessions có `last_event_at` hợp lệ (~40s trước, đang thực sự active), **242 sessions có `last_event_at = ''` (empty string)**.
7. Test `_parse_ts('')` → trả về `datetime.now(timezone.utc)` → elapsed = 0 → luôn coi là Running → không có state correction cho 242 rows.

## Quyết định merge
**REQUEST CHANGES — chưa được merge sang QA.**

### Lý do
Fix UI-002 chưa xử lý edge case `last_event_at = ''` (data legacy, chiếm 242/245 = 99% sessions). Kết quả thực tế trên môi trường thật: dashboard vẫn hiển thị **244 sessions RUNNING** sau restart — chính hiện tượng mà UI-002 muốn khắc phục.

Root cause phụ:
- `_parse_ts('')` trong `state_manager.py` trả về `datetime.now(timezone.utc)` → mọi row có timestamp rỗng bị tính là "vừa mới active" → luôn giữ nguyên state Running.
- Test suite của SD (4 tests) không cover case `last_event_at = ''`.

### Yêu cầu Senior Developer sửa lại (P1)
1. **Ưu tiên A (chỉ định):** Trong `state_manager._parse_ts`, khi input rỗng/None → return `datetime.min.replace(tzinfo=timezone.utc)` (hoặc epoch UTC) thay vì `now()`. Kết hợp `initialize_from_db` sẽ tính elapsed rất lớn → chuyển sang Ended đúng.
2. **Thêm test:** ít nhất 1 test case `initialize_from_db` với `last_event_at = ''` kỳ vọng chuyển sang Ended + có StateChange trong return list.
3. (Optional) Thêm data-cleanup migration: `UPDATE sessions SET state='Ended', ended_at=COALESCE(ended_at,started_at) WHERE state='Running' AND (last_event_at IS NULL OR last_event_at = '')` để chuyển sạch legacy state trong DB hiện có.
4. Re-verify sau fix: `/api/sessions?state=Running` phải trả về ≤ 5 sessions (chỉ 3 subagent active gần đây).

### UI-001 (frontend)
- Code `normalizeIso()` xử lý đúng 4 case: microseconds 6-digit, đã 3-digit, không có fractional, `+00:00`/`Z`. Test 20 pass. **APPROVED.**

## Artifact
- Không tạo file mới; chỉ verify + báo cáo.
- Log tích hợp thật: `<scratchpad>/uvicorn2.log`

## Handoff Payload — bước sau đọc phần này
- do_not_redo: Backend test 50/50 pass và frontend 20/20 pass — không cần chạy lại; port 7770 uvicorn đã tắt.
- watch_out: DB thực tế có 242 sessions `last_event_at=''` — cả cleanup và fix `_parse_ts` cần thiết. Không được chuyển sang QA (Bước 4.1) trước khi SD fix xong và TL re-verify.
- next_inputs: SD sửa `state_manager.py._parse_ts` (empty→epoch) + thêm test + optional cleanup migration; sau đó chạy lại Bước 3.6.

## Commit
- Hash: (sẽ điền sau khi commit step file)
- Đã push: (sẽ push)
