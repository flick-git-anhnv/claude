---
task: harness-research
created: 2026-07-12
updated: 2026-07-12 16:30
status: completed
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
| 2.1 | **[DỪNG — CHỜ USER]** User xem báo cáo và xác nhận đề xuất nào được áp dụng | USER | ✅ | User xác nhận áp dụng tất cả P1–P8 | 2026-07-12 15:00 | User xác nhận áp dụng toàn bộ 8 đề xuất |
| 2.2 | Áp dụng các đề xuất đã được user chọn vào code/tài liệu KZTEK, commit lên nhánh `research/harness-2026-07-12` | github-repo-researcher | ✅ | CLAUDE.md, 5 agent files, skill-trigger-test.md, references/documentation-writer-screenshot-guide.md, RESEARCH update | 2026-07-12 16:00 | P1-P8 áp dụng xong, DOCX xuất thành công |

### Phase 3: Merge về main
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | **[DỪNG — CHỜ USER]** User xác nhận merge nhánh nghiên cứu về main | USER | ✅ | User xác nhận "ok merge" | 2026-07-12 16:25 | Xác nhận rõ ràng, riêng biệt với bước 2.1 |
| 3.2 | Merge nhánh `research/harness-2026-07-12` về main sau khi có xác nhận rõ ràng | Dispatcher | ✅ | Merge commit `610f16a` trên `main`, đã push | 2026-07-12 16:30 | Merge no-ff, không conflict (research branch based sạch trên main) |

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

### Bước 2.2 — Áp dụng P1–P8
- Đã làm: Áp dụng toàn bộ 8 đề xuất vào CLAUDE.md và .claude/ files. Chạy DOCX script cho 9 file → DOCX thành công, PDF thất bại cho 2 file mới (không có LibreOffice — acceptable).
- File/module đã đọc hoặc đổi:
  - `CLAUDE.md`: +§11.0 (_workspace/), +Phase 0 audit vào WF-GITHUB-RESEARCH + WF-MIGRATE, +kỹ thuật run_in_background vào ∥ note, +why-first cho 3 quy tắc, +§21 Changelog
  - `.claude/agents/github-repo-researcher.md`: pushy description
  - `.claude/agents/documentation-writer.md`: pushy description + Progressive Disclosure (761→578 dòng)
  - `.claude/agents/senior-developer.md`: pushy description
  - `.claude/agents/junior-developer.md`: pushy description
  - `.claude/agents/task-planner.md`: pushy description
  - `.claude/agents/references/documentation-writer-screenshot-guide.md`: tạo mới (Progressive Disclosure reference)
  - `.claude/commands/skill-trigger-test.md`: tạo mới (skill P5)
  - `docs/research/RESEARCH-harness-2026-07-12.md`: cập nhật trạng thái ✅ P1–P8
- Quyết định quan trọng: P2 (Progressive Disclosure) áp dụng cho documentation-writer.md (761 dòng, vượt 500-dòng threshold); code-migrator.md (398) và ux-ui-reviewer.md (349) chưa tới ngưỡng — không tách.
- Bước sau cần biết: Bước 3.1 là DỪNG CHỜ USER xác nhận merge về main. Xác nhận ở bước 2.1 KHÔNG được dùng thay thế — phải hỏi lại rõ ràng tại đúng thời điểm này. Nhánh hiện tại: `research/harness-2026-07-12`.

### Bổ sung sau P1–P8 — Tách Bước 3 WF-GITHUB-RESEARCH
- Đã làm: Theo yêu cầu bổ sung của user, tách WF-GITHUB-RESEARCH Bước 3 cũ thành Bước 3 (phân tích repo, không kèm đề xuất) và Bước 3b (bảng đề xuất riêng biệt). Cập nhật đồng bộ 5 file theo §10 CLAUDE.md.
- File/module đã đọc hoặc đổi: CLAUDE.md §4 + §2, RULES.md, WORKFLOW.md (mermaid + bài học), .claude/shared/CORE.md, .claude/agents/github-repo-researcher.md (Bước 3 + 3b tách bạch).
- Quyết định quan trọng: Giữ nguyên số thứ tự Bước 4, 4b, 5, 5b — chỉ thêm Bước 3b mới sau Bước 3.
- Bước sau cần biết: Không có thêm thay đổi nào trước bước 3.1. Sẵn sàng commit + push + chờ user xác nhận merge.

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
| 2026-07-12 16:00 | Phase 2 hoàn thành: Bước 2.1 (user xác nhận P1–P8), 2.2 (áp dụng xong). 10 file thay đổi, DOCX/PDF xuất xong. Chờ bước 3.1 — user xác nhận merge. | github-repo-researcher |
| 2026-07-12 16:15 | Bổ sung từ yêu cầu mới của user: tách WF-GITHUB-RESEARCH Bước 3 thành Bước 3 (phân tích) + Bước 3b (đề xuất). Cập nhật CLAUDE.md §4, RULES.md, WORKFLOW.md, CORE.md, github-repo-researcher.md. | github-repo-researcher |
| 2026-07-12 16:30 | Phase 3 hoàn thành: user xác nhận merge → merge no-ff `research/harness-2026-07-12` vào `main` (commit `610f16a`), push thành công. Workflow WF-GITHUB-RESEARCH hoàn tất. | Dispatcher |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
