---
step: "2.1"
plan: ../PLAN-MASTER.md
agent: tech-lead
status: todo
completed_at:
deps: ["1.3", "1.6"]
---

# STEP 2.1 — TL: Technical Design Document

## Input nhận
Output từ Bước 1.3 (UX): `docs/design/DESIGN-agent-dashboard.md` — wireframe, component list.
Output từ Bước 1.6 (PJM): `docs/planning/SPRINT-agent-dashboard-01-PLAN.md` — task breakdown.
Output từ Bước 1.1 (PM): `docs/prd/PRD-agent-dashboard.md` — feature list + scope.
Output từ Bước 1.2 (BA): `docs/user-stories/US-agent-dashboard.md` — AC chi tiết.

## Nhiệm vụ
Viết Technical Design Document: chọn tech stack, thiết kế kiến trúc tổng thể (backend + frontend + storage), định nghĩa API contract (WebSocket events + REST endpoints), DB schema SQLite, file-watcher mechanism, account store design, và chia task cụ thể cho SD (backend) và JD (frontend).

## Definition of Done
- [ ] `docs/tech-design/TDD-agent-dashboard.md` được tạo đầy đủ các mục:
  - [ ] Tech stack quyết định (VD: Python/FastAPI + SQLite + vanilla HTML/JS hoặc React)
  - [ ] Kiến trúc tổng thể (sơ đồ text: file-watcher → parser → SQLite → WebSocket server → browser UI)
  - [ ] File-watcher design: watch `~/.claude/projects/*/*.jsonl`, parse JSONL, detect new lines, push events
  - [ ] API contract: WebSocket events (agent_started, agent_update, agent_ended, token_update), REST endpoints (GET /sessions, GET /sessions/history, GET /accounts, POST /accounts/switch)
  - [ ] SQLite schema: tables sessions, token_events, accounts
  - [ ] Account store design: format file lưu accounts/API keys (mã hoá nhẹ — VD: base64 + local salt, không cần AES đầy đủ với tool cá nhân)
  - [ ] Task breakdown chi tiết cho SD và JD (input/output rõ từng task)
- [ ] `docs/tech-design/TDD-agent-dashboard.docx` + `.pdf` được xuất

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
