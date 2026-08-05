---
step: "3.3"
plan: ../PLAN-MASTER.md
agent: tech-lead
status: done
completed_at: 2026-08-06 00:45
deps: ["3.1", "3.2"]
---

# STEP 3.3 — TL: Code Review + Merge Decision

## Input nhận
Output từ Bước 3.1 (SD): backend 27 files, 47/47 unit test pass.
Output từ Bước 3.2 (JD): frontend 44 files, `tsc -b` 0 lỗi, `vite build` OK.

## Nhiệm vụ
Review backend + frontend, phát hiện lệch schema giữa mock frontend và backend thật (2 dev code song song), tích hợp thực tế trên port 7770.

## Đã làm
1. Đọc code backend (accounts, routes, main, db, models) và frontend (types, wsReducer, mockData, TokenAnalyticsPage) — đối chiếu contract từng field.
2. Phát hiện 4 lệch schema:
   - `Session.token_total`: backend trả `int`, frontend cần `TokenCounts` object → fix backend `db.py` (thêm `_row_to_session` helper, đổi query, thêm `get_session_totals`).
   - `TokenSummaryResponse.totals`: thiếu field `sessions` → thêm COUNT(DISTINCT session_id) trong `get_token_summary`.
   - WS `token_update`: thiếu `cumulative` → `main.py` gọi `get_session_totals` sau upsert.
   - WS `account_changed`: thiếu `key_masked` → `routes/accounts.py` thêm vào payload.
3. Refactor `__import__("agent_dashboard.accounts", fromlist=["mask_key"])` hack → `from ..accounts import mask_key` sạch.
4. Sửa `vite.config.ts` `outDir: '../dist'` → `'dist'` (frontend build ra `tools/agent-dashboard/dist` trong khi backend mount tại `frontend/dist` → 404 khi truy cập `/`).
5. Chạy tích hợp thật: `uvicorn agent_dashboard.main:app --port 7770`
   - `/api/health` → `{"status":"ok","watcher_alive":true}` ✅
   - `/api/sessions` → mảng session, `token_total` là object đúng shape ✅
   - `/api/tokens/summary?range=7d` → có field `sessions: 7` ✅
   - `/` → serve `index.html` production ✅
   - WebSocket `/ws` → snapshot 93 sessions, `token_total` type=dict với 4 key đúng ✅
6. Chạy lại `pytest tests/ -q` → 47/47 pass, không hồi quy.

## Artifact
- Commit b1c148f: 4 files changed (db.py, main.py, routes/accounts.py, vite.config.ts)
- Frontend build: `tools/agent-dashboard/frontend/dist/` (index.html + assets/)

## Quyết định quan trọng
- MERGE PASS — cả backend và frontend đã đồng bộ contract, integration verify trên môi trường thật.
- Không chạy `security-audit-stride` (P2, tool nội bộ, không đụng production auth/payment — nhất quán ghi chú Bước 1.5).
- Rate-limit reveal (5/min sliding window) đúng theo TDD §7, mask_key trả `sk-ant-api03-****XXXX` với 4 char cuối.

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: Không cần build lại frontend hay sửa contract; backend đã chạy được cả REST + WS + static mount.
- watch_out:
  (1) Port 7770 có thể ở TIME_WAIT sau shutdown — chờ ~30s hoặc kill process trước khi start lại.
  (2) Frontend `dist/` build vào `tools/agent-dashboard/frontend/dist/` (KHÔNG phải `tools/agent-dashboard/dist` như trước fix); nếu thấy `/` 404, kiểm tra thư mục này tồn tại.
  (3) `data/dashboard.db` được tự tạo khi start, đã có sẵn 93 session thực từ máy dev — UXR sẽ thấy dữ liệu thật, không cần seed.
  (4) `active_account` = null (chưa add account nào) — UXR nên test luồng add account trong màn Accounts để chụp cả trạng thái active.
- next_inputs:
  - Backend + frontend đã sẵn. Cách khởi động app thật cho UXR:
    ```bash
    # Terminal 1 — start backend (đồng thời serve frontend production)
    cd tools/agent-dashboard/backend
    python -m uvicorn agent_dashboard.main:app --host 127.0.0.1 --port 7770

    # Frontend đã build sẵn. Nếu cần rebuild:
    cd tools/agent-dashboard/frontend && npm run build

    # Mở trình duyệt: http://127.0.0.1:7770
    ```
  - Design spec: `docs/design/DESIGN-agent-dashboard.md`
  - Screenshot cần chụp: Dashboard (session list + KPI), Token Analytics (7d/30d/12w/6m), Session History, Session Detail, Accounts (rỗng + có 1 account + reveal modal).

## Commit
- Hash: b1c148f
- Đã push: chưa (nhánh `research/skills-2026-08-05`, chờ user quyết định merge/push)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
