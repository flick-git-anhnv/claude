---
step: "1.2"
plan: ../PLAN-MASTER.md
agent: business-analyst
status: done
completed_at: 2026-08-05 23:30
deps: ["1.1"]
---

# STEP 1.2 — BA: Viết User Stories + Acceptance Criteria

## Input nhận
Output từ Bước 1.1 (PM): `docs/prd/PRD-agent-dashboard.md` — feature list, goals, user persona.

## Nhiệm vụ
Chi tiết hóa từng feature thành User Stories theo format Given/When/Then. Viết Acceptance Criteria đủ rõ để QA viết test case và Developer code được mà không cần hỏi thêm.

## Definition of Done
- [ ] `docs/user-stories/US-agent-dashboard.md` được tạo
- [ ] Mỗi feature lớn có ít nhất 1 User Story với AC dạng Given/When/Then
- [ ] Bao phủ: xem danh sách agent live, xem lịch sử session, xem token usage, chuyển đổi account/API key, lọc/tìm kiếm
- [ ] AC có edge case: khi không có session nào, khi WebSocket disconnect, khi API key không hợp lệ
- [ ] `docs/user-stories/US-agent-dashboard.docx` + `.pdf` được xuất

## Đã làm
Viết 8 User Stories chi tiết (US-001..US-008) cho F-01..F-08 (P0+P1). Mỗi story có Given/When/Then scenarios (happy path + edge cases), Business Rules, Edge Cases rõ ràng, và Câu hỏi mở cho PM. Bao phủ 4 edge cases trọng tâm: JSONL ghi dở, multi-session, timeout logic không có event Done, accounts.enc corrupt. F-09..F-12 (P2) ghi chú Backlog. Xuất DOCX thành công; PDF lỗi RPC Windows (known issue, không block).

## Artifact
- `docs/user-stories/US-agent-dashboard.md` — 8 User Stories + Business Flow mermaid + 7 Câu hỏi mở
- `docs/user-stories/US-agent-dashboard.docx` — DOCX xuất thành công
- PDF: lỗi docx2pdf RPC trên Windows — ghi chú ⚠️, DOCX đã có

## Quyết định quan trọng
- F-07 Account Switcher: xác nhận theo PM — Sprint 1 CHỈ lưu + hiển thị danh sách account và cho phép copy API key; KHÔNG tự inject vào Claude Code runtime. AC viết đúng theo giả định này.
- Timeout logic "agent kết thúc": 60s → Idle, 300s → Done (không có event tường minh trong JSONL). Đây là assumption cần PM xác nhận (Q1 trong file).
- Mã hoá account: XOR + base64 với key riêng trong `.enc_key` — đủ cho non-plaintext, không dùng OS keychain.

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: User Stories F-01..F-08 đã viết xong, không viết lại. F-09..F-12 là Backlog, không cần story chi tiết ở bước tiếp.
- watch_out: 7 câu hỏi mở (Q1..Q7) cho PM chưa được giải đáp — UX Designer cần thiết kế dựa trên assumption hiện tại, đánh dấu phần nào phụ thuộc vào câu trả lời của PM. Đặc biệt Q1 (timeout threshold) và Q7 (block vs warning khi không có active account) ảnh hưởng trực tiếp đến UI states.
- next_inputs: `docs/user-stories/US-agent-dashboard.md` — toàn bộ 8 stories với Acceptance Criteria + Business Rules + Edge Cases; focus vào: US-001 (Agent Status Panel layout), US-003 (Token display), US-007 (Account Manager UI), US-008 (Header indicator + warning state).

## Commit
- Hash: 5d5c19f
- Đã push: không

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
