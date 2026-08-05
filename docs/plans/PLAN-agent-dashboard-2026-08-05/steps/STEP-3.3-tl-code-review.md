---
step: "3.3"
plan: ../PLAN-MASTER.md
agent: tech-lead
status: todo
completed_at:
deps: ["3.1", "3.2"]
---

# STEP 3.3 — TL: Code Review + Merge Decision

## Input nhận
Output từ Bước 3.1 (SD): PR backend với VERIFICATION REPORT từ `/verify-pr`.
Output từ Bước 3.2 (JD): PR frontend với VERIFICATION REPORT từ `/verify-pr`.

## Nhiệm vụ
Review toàn bộ code backend + frontend, kiểm tra correctness, security (account store encryption đủ không?), performance (file-watcher có leak không?), và adherence to TDD. Merge decision sau khi approve.

## Definition of Done
- [ ] VERIFICATION REPORT của cả 2 PR toàn PASS trước khi bắt đầu review
- [ ] Review backend: file-watcher không leak fd/memory, JSONL parser robust, SQLite query có index, WebSocket broadcast không block
- [ ] Review frontend: WebSocket reconnect logic đúng, token chart hiển thị đúng scale, account switcher không lộ API key trong DOM/console
- [ ] Security check nhẹ: API key trong account store không log ra console/file, mã hoá đủ cho mục đích "cá nhân local"
- [ ] Merge cả 2 PR (hoặc 1 combined PR nếu TDD gộp) sau khi review sạch
- [ ] Không cần chạy `security-audit-stride` (P2, không đụng production auth/payment) — ghi nhận trong review note

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
