---
step: "4.3"
plan: ../PLAN-MASTER.md
agent: devops-engineer
status: todo
completed_at:
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
[Điền sau khi hoàn thành]

## Artifact
[Điền sau khi hoàn thành]

## Quyết định quan trọng
[Điền sau khi hoàn thành]

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: Không có
- watch_out: Không có
- next_inputs: Không có

## Commit
- Hash: [điền sau khi commit]
- Đã push: [có/không]

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
