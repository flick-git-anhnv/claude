---
task: harness-research
created: 2026-07-12
updated: 2026-07-12
status: planning
workflow: WF-GITHUB-RESEARCH
priority: P2
---

# PLAN: Nghiên cứu repo GitHub revfactory/harness

## Mô tả
Nghiên cứu repo GitHub https://github.com/revfactory/harness, phân tích cấu trúc và nội dung, đề xuất các cải tiến có thể áp dụng vào codebase KZTEK, sau đó áp dụng các đề xuất đã được user xác nhận và merge về main.

## Nguồn yêu cầu
- Yêu cầu gốc: Nghiên cứu repo GitHub https://github.com/revfactory/harness
- Workflow: WF-GITHUB-RESEARCH — Nghiên cứu 1 repo GitHub theo link user gửi
- Agent chain: GITHUB REPO RESEARCHER → USER (xác nhận đề xuất) → GITHUB REPO RESEARCHER → USER (xác nhận merge) → GITHUB REPO RESEARCHER

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự commit+push+điền cột "Hoàn thành lúc".

### Phase 1: Chuẩn bị & Nghiên cứu
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 1.1 | Tạo nhánh nghiên cứu mới `research/harness-2026-07-12` từ main | github-repo-researcher | ⬜ | nhánh `research/harness-2026-07-12` | - | |
| 1.2 | Clone repo https://github.com/revfactory/harness về thư mục scratchpad (ngoài working tree KZTEK), đọc & phân tích toàn bộ cấu trúc, code, tài liệu | github-repo-researcher | ⬜ | ghi chú phân tích nội bộ (scratchpad) | - | Repo clone CHỈ để đọc, không đưa .git của repo ngoài vào commit KZTEK |
| 1.3 | Viết `docs/research/RESEARCH-harness-2026-07-12.md` + bảng đề xuất cải tiến, xuất DOCX+PDF, trình user | github-repo-researcher | ⬜ | `docs/research/RESEARCH-harness-2026-07-12.md` + `.docx` + `.pdf` | - | Đề xuất đụng auth/payment/DB schema → chạy security-audit-stride trước khi merge |

### Phase 2: User xác nhận & Áp dụng
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | **[DỪNG — CHỜ USER]** User xem báo cáo và xác nhận đề xuất nào được áp dụng | USER | ⬜ | Danh sách đề xuất được chọn | - | KHÔNG tự áp dụng khi chưa có xác nhận rõ ràng |
| 2.2 | Áp dụng các đề xuất đã được user chọn vào code/tài liệu KZTEK, commit lên nhánh `research/harness-2026-07-12` | github-repo-researcher | ⬜ | Các file code/tài liệu đã sửa, commit trên nhánh nghiên cứu | - | Chỉ làm sau bước 2.1 có xác nhận |

### Phase 3: Merge về main
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | **[DỪNG — CHỜ USER]** User xác nhận merge nhánh nghiên cứu về main | USER | ⬜ | Xác nhận rõ ràng của user | - | Xác nhận ở bước 2.1 KHÔNG thay thế cho xác nhận merge này (Git Safety Protocol) |
| 3.2 | Merge nhánh `research/harness-2026-07-12` về main sau khi có xác nhận rõ ràng | github-repo-researcher | ⬜ | Merge commit trên main | - | Chỉ làm sau bước 3.1 có xác nhận |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp — tránh đọc lại/nghiên cứu lại.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

_(Chưa có entry — sẽ bổ sung sau khi từng bước hoàn thành)_

## Artifacts dự kiến
- [ ] nhánh `research/harness-2026-07-12` trên remote
- [ ] `docs/research/RESEARCH-harness-2026-07-12.md` — báo cáo nghiên cứu + bảng đề xuất
- [ ] `docs/research/RESEARCH-harness-2026-07-12.docx` — bản Word theo brand KZTEK
- [ ] `docs/research/RESEARCH-harness-2026-07-12.pdf` — bản PDF xuất từ DOCX
- [ ] Các file code/tài liệu KZTEK được cải tiến theo đề xuất đã duyệt (xác định sau bước 2.1)

## Blockers
Không có

## Quyết định / Ghi chú
- Repo clone về scratchpad CHỈ để đọc, KHÔNG đưa `.git` của repo ngoài vào commit KZTEK.
- Bước 2.1 và 3.1 là bước chờ user — workflow PHẢI dừng tại đây, không tự tiến tiếp.
- Nếu đề xuất cải tiến đụng auth/payment/DB schema/dữ liệu nhạy cảm → bắt buộc chạy `security-audit-stride` trước khi merge (CLAUDE.md §4 WF-GITHUB-RESEARCH).
- Nhánh nghiên cứu: `research/harness-2026-07-12`.

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-07-12 | Plan tạo mới | task-planner |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
