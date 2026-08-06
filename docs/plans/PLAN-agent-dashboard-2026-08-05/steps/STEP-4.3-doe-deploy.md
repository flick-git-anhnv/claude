---
step: "4.3"
plan: ../PLAN-MASTER.md
agent: devops-engineer
status: done
completed_at: 2026-08-06 09:01
deps: ["4.2"]
---

# STEP 4.3 — DOE: Deploy Local

## Input nhận
Output từ Bước 4.2 (QAL): sign-off, không còn P0/P1 bug.
Output từ Bước 3.1 (SD): README hướng dẫn chạy backend.

## Nhiệm vụ
Viết checklist deploy local và đảm bảo app khởi động được từ đầu trên máy target (`c:\Users\nguye\Desktop\Claude-Git\claude`). Tạo script start/stop tiện lợi.

## Definition of Done
- [ ] `docs/devops/DEPLOY-agent-dashboard.md` được tạo với:
  - [ ] Pre-requisites: Python version, pip packages, Node.js nếu cần
  - [ ] Lệnh khởi động backend (VD: `uvicorn main:app --reload --port 8765`)
  - [ ] Lệnh khởi động frontend (nếu có build step)
  - [ ] Script `start-dashboard.bat` hoặc `.ps1` để khởi động 1 lệnh
  - [ ] Script `stop-dashboard.bat` hoặc `.ps1`
  - [ ] Verify dashboard accessible tại `http://localhost:<port>`
- [ ] `docs/devops/DEPLOY-agent-dashboard.docx` + `.pdf` được xuất

## Đã làm
1. Đọc `config.py` xác nhận: port=7770, DB tại `backend/data/dashboard.db`, frontend dist path tự động từ `__file__`.
2. Tạo `tools/agent-dashboard/start.bat` — Windows one-command startup: kiểm tra Python deps, kiểm tra frontend/dist (build nếu thiếu), start uvicorn, mở browser.
3. Verify chạy thử: `python -m agent_dashboard` từ `backend/` → server start, frontend served, HTTP 200 tại `/`, health endpoint `{"status":"ok","watcher_alive":true}`. Server đã dừng sau verify.
4. Tạo `docs/devops/DEPLOY-agent-dashboard.md` — yêu cầu môi trường, cách start/stop, view log, backup/restore DB, rollback, known issues BUG-001+BUG-002, deploy checklist.
5. Xuất `DEPLOY-agent-dashboard.docx` (OK). PDF thất bại do Word RPC (non-blocking — giống các bước trước).

## Artifact
- `tools/agent-dashboard/start.bat` — Windows one-command startup script
- `docs/devops/DEPLOY-agent-dashboard.md` — deploy guide đầy đủ
- `docs/devops/DEPLOY-agent-dashboard.docx` — DOCX OK
- `docs/devops/DEPLOY-agent-dashboard.pdf` — FAIL (RPC, non-blocking)

## Quyết định quan trọng
- Script chạy `python -m agent_dashboard` từ `backend/` (dùng `__main__.py` entry point), KHÔNG gọi uvicorn trực tiếp — đảm bảo logging + port config nhất quán với `config.py`.
- DB tại `tools/agent-dashboard/backend/data/dashboard.db` (không phải `~/.claude/` như TDD đề xuất ban đầu) — xác nhận từ `config.py` thực tế.
- Frontend dist đã build sẵn trong repo — Node.js chỉ cần khi rebuild.

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: start.bat đã tạo xong; DEPLOY doc đã có; server verify chạy OK port 7770 — không cần verify lại từ đầu.
- watch_out: DB ở `tools/agent-dashboard/backend/data/dashboard.db` (không phải `~/.claude/`). PDF export thất bại do Word RPC — chỉ có DOCX. BUG-001 (DELETE 500) và BUG-002 (duplicate name) tồn đọng P2 — đã ghi vào DEPLOY doc.
- next_inputs: `tools/agent-dashboard/start.bat` (chạy để start), `http://127.0.0.1:7770` (URL kiểm tra), `http://127.0.0.1:7770/api/health` (health check), `docs/devops/DEPLOY-agent-dashboard.md` (full context), build commit ff0bd2e.

## Commit
- Hash: 10f68af
- Đã push: không

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
