---
task: TASK-SLUG-ĐỔI-LẠI
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: planning
workflow: WF-ID
priority: P1
---

# PLAN MASTER: Tên Task Đầy Đủ

> File này CHỈ chứa tổng quan + trạng thái. Chi tiết từng bước (mô tả đầy đủ, Handoff Log, artifact chi tiết) nằm ở `steps/STEP-[N.M]-[tên].md` tương ứng — xem cột "Step file" bên dưới.

## Mô tả
Mô tả ngắn gọn task cần làm, vấn đề cần giải quyết.

## Nguồn yêu cầu
- Yêu cầu gốc: [copy paste yêu cầu từ user]
- Workflow: [WF-ID] — [tên workflow]
- Agent chain: [Agent A] → [Agent B] → [Agent C] → ...

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự tạo/cập nhật step file riêng, commit+push, rồi cập nhật đúng 1 dòng status ở bảng dưới đây.

### Phase 1: [Tên phase — vd: Phân tích & Thiết kế]
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 1.1 | [mô tả ngắn 1 dòng] | [agent] | ⬜ | `steps/STEP-1.1-[ten].md` | - |
| 1.2 | [mô tả ngắn 1 dòng] | [agent] | ⬜ | `steps/STEP-1.2-[ten].md` | - |

### Phase 2: [Tên phase — vd: Triển khai]
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 2.1 | [mô tả ngắn 1 dòng] | [agent] | ⬜ | `steps/STEP-2.1-[ten].md` | - |
| 2.2 | [mô tả ngắn 1 dòng] | [agent] | ⬜ | `steps/STEP-2.2-[ten].md` | - |

### Phase 3: [Tên phase — vd: Kiểm thử & Deploy]
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 3.1 | [mô tả ngắn 1 dòng] | [agent] | ⬜ | `steps/STEP-3.1-[ten].md` | - |
| 3.2 | [mô tả ngắn 1 dòng] | [agent] | ⬜ | `steps/STEP-3.2-[ten].md` | - |

## Artifacts dự kiến (tổng)
- [ ] [artifact 1 — vd: docs/prd/PRD-xxx.md]
- [ ] [artifact 2 — vd: src/module/feature.ts]
- [ ] [artifact 3 — vd: docs/test-cases/TC-xxx.md]

## Blockers
Không có

## Quyết định / Ghi chú tổng
[Quyết định ảnh hưởng nhiều bước / toàn task. Quyết định chỉ ảnh hưởng 1 bước → ghi trong step file đó.]

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| YYYY-MM-DD | Plan tạo mới | task-planner |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
**Cách đọc nhanh:** đọc MASTER trước → nếu cần chi tiết bước cụ thể mới mở step file tương ứng.
