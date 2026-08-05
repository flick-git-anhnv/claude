---
step: "1.1"
plan: ../PLAN-MASTER.md
agent: product-manager
status: done
completed_at: 2026-08-05 22:52
deps: []
---

# STEP 1.1 — PM: Viết PRD

## Input nhận
Task mới — từ PLAN-MASTER.md. Scope đã chốt:
- Tool nội bộ local, không multi-user, không production
- Realtime qua file-watch ~/.claude/projects/*/*.jsonl + WebSocket
- SQLite lưu lịch sử dài hạn
- Account/API key switching (file local, mã hoá nhẹ)

## Nhiệm vụ
Viết Product Requirements Document (PRD) cho Agent Dashboard. Tập trung vào goals, user persona (1 developer dùng cá nhân), feature list, và non-goals rõ ràng để BA có thể viết AC cụ thể.

## Definition of Done
- [ ] `docs/prd/PRD-agent-dashboard.md` được tạo với đủ các mục: Goals, User Persona, Features (prioritized), Non-goals, Metrics đo lường
- [ ] `docs/prd/PRD-agent-dashboard.docx` + `.pdf` được xuất qua `scripts/md_to_docx_kztek.py`
- [ ] Mục "Non-goals" ghi rõ: không multi-user, không cloud, không auth phức tạp
- [ ] Feature list có priority rõ (P0/P1/P2) để TL có thể estimate

## Đã làm
- Đọc plan master, scope đã chốt từ scope-check
- Đọc kztek-brand-info và PRD-template
- Tạo thư mục `docs/prd/`
- Viết `docs/prd/PRD-agent-dashboard.md` với đầy đủ: Tổng quan, Goals (G1–G4), Non-goals, User Persona, User Stories sơ lược, Feature List (P0/P1/P2 — 12 features), Acceptance Criteria mức cao, Metrics, Kiến trúc gợi ý, Rủi ro/Câu hỏi mở, Out of Scope
- Xuất DOCX (thành công) và PDF (docx2pdf báo RPC failed nhưng file PDF thực tế đã tạo — false failure theo lesson `docx2pdf-false-failure-pdf-still-created`)

## Artifact
- `docs/prd/PRD-agent-dashboard.md`
- `docs/prd/PRD-agent-dashboard.docx`
- `docs/prd/PRD-agent-dashboard.pdf`

## Quyết định quan trọng
1. Feature list chia 3 tầng P0/P1/P2: P0 là core MVP (file-watch, realtime, SQLite ingest, agent status); P1 là analytics và account switcher; P2 là cost estimate, alert, export.
2. "Account switching" — Q2 ghi rõ: Sprint 1 chỉ lưu + hiển thị danh sách tài khoản, BA cần xác nhận cơ chế apply (CLAUDE.md/.env) ở Bước 1.2.
3. Kiến trúc gợi ý: Python/FastAPI backend + React/Vanilla frontend + SQLite — TL xác nhận final ở Bước 2.1.
4. Port mặc định: localhost:7770 (tránh đụng 3000/8000 thường dùng).

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: PRD đã viết xong và xuất DOCX+PDF tại `docs/prd/PRD-agent-dashboard.md`. Không viết lại PRD, chỉ đọc để làm input.
- watch_out: Q2 trong PRD — "Account switching" chưa xác định cơ chế apply API key vào Claude Code runtime. BA cần hỏi lại user hoặc đưa ra giả định rõ ràng trong User Story tương ứng (US-04/F-07). Scope chỉ "lưu + hiển thị" là an toàn, không tự mở rộng sang "inject vào .env".
- next_inputs: `docs/prd/PRD-agent-dashboard.md` — đọc toàn bộ, đặc biệt Feature List (P0–P2) và Acceptance Criteria để viết User Stories + AC chi tiết. Feature IDs: F-01..F-12. AC cao: AC1..AC7.

## Commit
- Hash: [điền sau khi commit]
- Đã push: không

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
