---
task: TASK-SLUG-ĐỔI-LẠI
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: planning
workflow: WF-ID
priority: P1
---

# PLAN: Tên Task Đầy Đủ

## Mô tả
Mô tả ngắn gọn task cần làm, vấn đề cần giải quyết.

## Nguồn yêu cầu
- Yêu cầu gốc: [copy paste yêu cầu từ user]
- Workflow: [WF-ID] — [tên workflow]
- Agent chain: [Agent A] → [Agent B] → [Agent C] → ...

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự commit+push+điền cột "Hoàn thành lúc".

### Phase 1: [Tên phase — vd: Phân tích & Thiết kế]
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 1.1 | [mô tả bước cụ thể] | [agent] | ⬜ | - | - | |
| 1.2 | [mô tả bước cụ thể] | [agent] | ⬜ | - | - | |

### Phase 2: [Tên phase — vd: Triển khai]
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | [mô tả bước cụ thể] | [agent] | ⬜ | - | - | |
| 2.2 | [mô tả bước cụ thể] | [agent] | ⬜ | - | - | |

### Phase 3: [Tên phase — vd: Kiểm thử & Deploy]
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | [mô tả bước cụ thể] | [agent] | ⬜ | - | - | |
| 3.2 | [mô tả bước cụ thể] | [agent] | ⬜ | - | - | |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp — tránh đọc lại/nghiên cứu lại.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

### Bước [N.M] — [tên bước ngắn]
- Đã làm: [tóm tắt 2-3 câu]
- File/module đã đọc hoặc đổi: [đường dẫn cụ thể]
- Quyết định quan trọng: [nếu có]
- Bước sau cần biết: [cảnh báo/gotcha — hoặc "Không có"]

## Artifacts dự kiến
- [ ] [artifact 1 — vd: docs/prd/PRD-xxx.md]
- [ ] [artifact 2 — vd: src/module/feature.ts]
- [ ] [artifact 3 — vd: docs/test-cases/TC-xxx.md]

## Blockers
Không có

## Quyết định / Ghi chú
[Các quyết định quan trọng được đưa ra trong quá trình thực hiện. Thêm vào đây khi có.]

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| YYYY-MM-DD | Plan tạo mới | task-planner |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
