---
step: "1.4"
plan: ../PLAN-MASTER.md
agent: engineering-manager
status: done
completed_at: 2026-08-05 23:50
deps: ["1.1", "1.2", "1.3"]
---

# STEP 1.4 — EM: Estimate Resource + Confirm Priority

## Input nhận
Output từ Bước 1.1–1.3: PRD, User Stories, Design Spec.

## Nhiệm vụ
Đánh giá resource cần thiết, confirm priority P2, phân bổ team (SD phụ trách backend, JD phụ trách frontend), estimate thời gian tổng thể.

## Definition of Done
- [ ] `docs/planning/RESOURCE-agent-dashboard.md` được tạo: estimate effort (người-ngày), team assignment, priority confirmation
- [ ] Ghi rõ: SD → backend (file-watcher, WebSocket, SQLite), JD → frontend (UI, WebSocket client)
- [ ] Confirm priority P2 và không cần CTO review (tool nội bộ, không đụng production)
- [ ] `docs/planning/RESOURCE-agent-dashboard.docx` + `.pdf` được xuất

## Đã làm
Đọc PRD, User Stories, và Design Spec (5 màn hình, 13 component). Xác nhận Priority P2, skip CTO review. Phân bổ SD cho toàn bộ backend (file-watcher, JSONL parser, SQLite, WebSocket, account API — 7 ngày) và JD cho toàn bộ frontend (13 React component theo design spec — 9.5 ngày). Ước lượng tổng ~24 người-ngày. Không có rủi ro nghiêm trọng cần escalate. Tạo `docs/planning/RESOURCE-agent-dashboard.md`, xuất DOCX (PDF thất bại do lỗi COM docx2pdf — không block).

## Artifact
- `docs/planning/RESOURCE-agent-dashboard.md`
- `docs/planning/RESOURCE-agent-dashboard.docx` (✓ DOCX hoàn thành)
- `docs/planning/RESOURCE-agent-dashboard.pdf` (⚠️ thất bại — lỗi COM docx2pdf, không block)

## Quyết định quan trọng
1. Priority P2 xác nhận — CTO review skipped, tool nội bộ 1 máy, không đụng production.
2. SD backend ∥ JD frontend sau khi TDD (Bước 2.1) được duyệt — JD dùng mock server trong giai đoạn song song.
3. Mã hóa accounts.enc dùng mức bảo mật nhẹ (đã chấp nhận từ bước UX) — không escalate.
4. File-watcher trên Windows cần test sớm ở Bước 3.1 (`watchdog` lib) — risk thấp, có fallback polling 2s.

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: Estimate resource, priority confirmation, team assignment — đã hoàn thành, KHÔNG làm lại.
- watch_out: SD và JD chỉ bắt đầu Bước 3.1/3.2 SAU KHI TDD (2.1) được duyệt — không chạy song song trước đó. JD dùng mock server trong giai đoạn song song với SD.
- next_inputs: `docs/planning/RESOURCE-agent-dashboard.md` — team assignment + effort estimate cho sprint planning. SD: 7 ngày backend. JD: 9.5 ngày frontend. TL: 4.5 ngày (TDD + review). QAE: 1.5 ngày. DOE+DOL: 1 ngày.

## Commit
- Hash: [điền sau khi commit]
- Đã push: không

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
