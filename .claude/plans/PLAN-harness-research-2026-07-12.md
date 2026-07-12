---
task: harness-research
created: 2026-07-12
updated: 2026-07-12 14:30
status: in-progress
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
| 1.1 | Tạo nhánh nghiên cứu mới `research/harness-2026-07-12` từ main | github-repo-researcher | ✅ | nhánh `research/harness-2026-07-12` | 2026-07-12 14:00 | Tạo từ nhánh `claude/harness-research-tlfzbf` |
| 1.2 | Clone repo https://github.com/revfactory/harness về thư mục scratchpad (ngoài working tree KZTEK), đọc & phân tích toàn bộ cấu trúc, code, tài liệu | github-repo-researcher | ✅ | scratchpad: `/tmp/.../scratchpad/research/harness/` | 2026-07-12 14:15 | Đọc SKILL.md, 6 reference files, README — repo CHỈ đọc, không commit .git |
| 1.3 | Viết `docs/research/RESEARCH-harness-2026-07-12.md` + bảng đề xuất cải tiến, xuất DOCX+PDF, trình user | github-repo-researcher | ✅ | `docs/research/RESEARCH-harness-2026-07-12.md` + `.docx` (PDF thất bại — thiếu LibreOffice/docx2pdf) | 2026-07-12 14:30 | 8 đề xuất, không có đề xuất nào đụng auth/payment/DB — không cần security-audit-stride |

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

### Bước 1.1 — Tạo nhánh nghiên cứu
- Đã làm: checkout nhánh `research/harness-2026-07-12` từ `claude/harness-research-tlfzbf` thành công.
- File/module đã đọc hoặc đổi: git branch (local only, chưa push)
- Quyết định quan trọng: Tạo từ nhánh hiện tại (không phải main) theo đúng hướng dẫn task.
- Bước sau cần biết: Nhánh chưa có remote tracking — cần `git push -u origin research/harness-2026-07-12` khi commit.

### Bước 1.2 — Clone & phân tích repo
- Đã làm: Clone `--depth 1` vào scratchpad. Đọc README, SKILL.md (458 dòng), 6 reference files, _workspace/ examples. Repo là meta-skill sinh agent team từ domain description, dùng 6 kiến trúc mẫu.
- File/module đã đọc hoặc đổi: Đọc tất cả file trong scratchpad (chỉ đọc, không sửa, không commit .git của repo ngoài).
- Quyết định quan trọng: Repo hoàn toàn là Markdown (không có code runtime) → không có rủi ro bảo mật khi nghiên cứu.
- Bước sau cần biết: Các điểm nổi bật: _workspace/ convention, Progressive Disclosure 3 tầng, pushy description, Phase 0 audit, with/without-skill A/B testing.

### Bước 1.3 — Viết báo cáo và đề xuất
- Đã làm: Tạo `docs/research/RESEARCH-harness-2026-07-12.md` với 8 đề xuất (P1–P8), chạy `md_to_docx_kztek.py` → DOCX thành công, PDF thất bại (thiếu LibreOffice/docx2pdf — không block workflow).
- File/module đã đọc hoặc đổi: Tạo mới `docs/research/RESEARCH-harness-2026-07-12.md` và `docs/research/RESEARCH-harness-2026-07-12.docx`.
- Quyết định quan trọng: Không có đề xuất nào đụng auth/payment/DB schema → xác nhận không cần chạy security-audit-stride trước khi merge. Ưu tiên áp dụng: P3, P4, P7, P8 (low effort) trước; P1, P5 tiếp theo; P2, P6 sau cùng.
- Bước sau cần biết: Bước 2.1 là DỪNG CHỜ USER — không tự áp dụng bất kỳ đề xuất nào. User cần chọn đề xuất nào muốn áp dụng (có thể chọn 0, một số, hoặc tất cả P1–P8). Sau khi user chọn, bước 2.2 áp dụng từng đề xuất vào CLAUDE.md/.claude/ files.

## Artifacts dự kiến
- [x] nhánh `research/harness-2026-07-12` (local — push sau khi commit)
- [x] `docs/research/RESEARCH-harness-2026-07-12.md` — báo cáo nghiên cứu + bảng đề xuất ✅
- [x] `docs/research/RESEARCH-harness-2026-07-12.docx` — bản Word theo brand KZTEK ✅
- [ ] `docs/research/RESEARCH-harness-2026-07-12.pdf` — thất bại (thiếu LibreOffice/docx2pdf, ghi chú)
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
| 2026-07-12 14:30 | Phase 1 hoàn thành: Bước 1.1 (nhánh), 1.2 (clone+phân tích), 1.3 (báo cáo+DOCX). PDF thất bại do thiếu converter. | github-repo-researcher |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
