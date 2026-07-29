---
step: "2.3"
plan: ../PLAN-MASTER.md
agent: user
status: todo
completed_at:
---

# STEP 2.3 — [USER] Chọn Mode A hay Mode B

## Input nhận
Từ Bước 2.2 — Handoff Log sẽ được nhúng vào đây khi giao việc (link file báo cáo phân tích, tóm tắt ngắn về repo để user đọc qua trước khi quyết định).

## Nhiệm vụ
User đọc báo cáo phân tích repo (`docs/research/RESEARCH-graphify-2026-07-29.md`) và chọn hướng tiếp theo:

- **Mode A — Áp dụng cải tiến KZTEK:** Agent sẽ đề xuất những cải tiến có thể học từ repo này để áp dụng vào hệ thống KZTEK, user duyệt từng đề xuất rồi agent thực hiện.
- **Mode B — Học tập/Tham khảo cá nhân:** Agent sẽ giải thích nguyên lý hoạt động và/hoặc hướng dẫn áp dụng repo này theo cách tương tác, đến khi user nắm rõ.

Nếu user không nói rõ mục đích từ đầu → mặc định đề xuất Mode A.

## Definition of Done
- [ ] User xác nhận lựa chọn Mode A hoặc Mode B (hoặc cả hai nếu muốn)
- [ ] Người thực thi plan ghi nhận lựa chọn vào mục "Đã làm" của step file này
- [ ] Cập nhật PLAN-MASTER.md: đánh dấu Phase không được chọn là ⏭️ Skipped với lý do ghi rõ
- [ ] Cập nhật đúng 1 dòng status trong PLAN-MASTER.md (⬜ → ✅)

## Đã làm
[Điền SAU khi user xác nhận — ghi rõ: Mode được chọn + Phase nào bị skip]

## Artifact
Không có artifact kỹ thuật — đây là bước xác nhận của user.

## Quyết định quan trọng
[Điền SAU khi user chọn — ghi Mode A/B + lý do nếu user có giải thích]

## Handoff Log — bước sau cần biết
[Điền SAU khi user chọn — ghi rõ: Mode đã chọn, bước tiếp theo là bước nào (3A.1 hoặc 3B.1)]

## Commit
- Hash: N/A (bước xác nhận user, không có code change)
- Đã push: N/A

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
