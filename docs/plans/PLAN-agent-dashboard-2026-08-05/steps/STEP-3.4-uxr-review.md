---
step: "3.4"
plan: ../PLAN-MASTER.md
agent: ux-ui-reviewer
status: todo
completed_at:
deps: ["3.3"]
---

# STEP 3.4 — UXR: UX/UI Review

## Input nhận
Output từ Bước 3.3 (TL): code đã merge, app có thể chạy được local.
Output từ Bước 1.3 (UX): `docs/design/DESIGN-agent-dashboard.md` — design spec gốc để đối chiếu.

## Nhiệm vụ
Chạy app thật local, chụp screenshot từng màn hình chính, đánh giá 7 tiêu chí C1–C7, so sánh với design spec. Ghi nhận issues nếu có.

## Definition of Done
- [ ] App được khởi động thật (backend + frontend) trước khi review — KHÔNG review trên mockup
- [ ] Screenshots chụp đủ: Agent Live View, Session History, Token Chart, Account Switcher, empty states, WebSocket disconnect state
- [ ] Đánh giá C1–C7:
  - [ ] C1: Visual hierarchy rõ ràng (agent đang chạy vs đã chạy phân biệt được)
  - [ ] C2: Màu sắc đúng brand KZTEK (Navy/Cam dominant)
  - [ ] C3: Typography nhất quán
  - [ ] C4: Spacing/padding nhất quán
  - [ ] C5: Interactive states (hover, active, loading) hiển thị đúng
  - [ ] C6: Empty states có thông báo rõ ràng (không blank trắng)
  - [ ] C7: Error/disconnect states dễ hiểu với non-technical user
- [ ] `docs/ux-review/UX-REVIEW-agent-dashboard.md` được tạo với screenshots + đánh giá
- [ ] `docs/ux-review/UX-REVIEW-agent-dashboard.docx` + `.pdf` được xuất
- [ ] Nếu có issue: liệt kê rõ mức độ (blocker/minor) — blocker phải fix trước QA, minor có thể ghi nợ

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
