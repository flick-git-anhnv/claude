---
step: N.M
plan: ../PLAN-MASTER.md
agent: [agent phụ trách]
status: todo
completed_at:
deps: []
---

# STEP N.M — [Tên bước ngắn]

## Input nhận
[Từ MASTER hoặc step trước — mô tả bối cảnh cần biết TRƯỚC khi bắt đầu bước này. Nếu có Handoff Log của bước liền trước, agent tạo plan PHẢI nhúng nguyên văn vào đây khi giao việc.]

## Nhiệm vụ
[Mô tả cụ thể 1-3 câu việc cần làm ở bước này.]

## Definition of Done
- [ ] [Tiêu chí 1]
- [ ] [Tiêu chí 2]

## Đã làm
[Điền SAU khi hoàn thành — tóm tắt 2-4 câu đã làm gì, không chép lại toàn bộ log/tool-call.]

## Artifact
- [đường dẫn file/module đã tạo hoặc đổi — điền sau khi xong]

## Quyết định quan trọng
[Nếu có — vd: chọn cách A vì lý do X. Không có → "Không có".]

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: [thao tác đã làm xong, bước sau KHÔNG làm lại — vd: "đã clone repo, không cần clone lại"; nếu không có → "Không có"]
- watch_out: [gotcha / điều kiện bất ngờ bước sau cần biết — vd: "branch X đang ở dirty state"; nếu không có → "Không có"]
- next_inputs: [artifact/file/quyết định bước sau cần dùng làm input — vd: "dùng commit hash abc1234, file plan ở docs/plans/..."; nếu không có → "Không có"]

## Commit
- Hash: [điền sau khi commit]
- Đã push: [có/không]

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
