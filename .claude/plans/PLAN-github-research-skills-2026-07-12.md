---
task: github-research-skills
created: 2026-07-12
updated: 2026-07-12
status: planning
workflow: WF-GITHUB-RESEARCH
priority: P2
---

# PLAN: Nghiên cứu repo GitHub anthropics/skills

## Mô tả
Nghiên cứu repo https://github.com/anthropics/skills để phân tích mục đích, cấu trúc, điểm nổi bật kỹ thuật, và đề xuất cải tiến áp dụng vào hệ thống agent KZTEK.

## Nguồn yêu cầu
- Yêu cầu gốc: Nghiên cứu repo GitHub https://github.com/anthropics/skills theo workflow WF-GITHUB-RESEARCH
- Workflow: WF-GITHUB-RESEARCH — Nghiên cứu 1 repo GitHub theo link user gửi
- Agent chain: GITHUB-REPO-RESEARCHER (Phase 0 Audit) → GITHUB-REPO-RESEARCHER (tạo nhánh) → GITHUB-REPO-RESEARCHER (clone + phân tích) → GITHUB-REPO-RESEARCHER (viết báo cáo) → GITHUB-REPO-RESEARCHER (đề xuất cải tiến) → USER (xác nhận) → GITHUB-REPO-RESEARCHER (áp dụng) → USER (xác nhận merge) → GITHUB-REPO-RESEARCHER (merge main)

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự commit+push+điền cột "Hoàn thành lúc".

### Phase 0: Audit & Khởi động
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 0.1 | Phase 0 Audit — kiểm tra đã có nhánh/plan/artifact chưa; phát hiện drift; xác định đây là task mới hay nối tiếp; đưa ra ma trận các bước cần chạy vs bỏ qua | github-repo-researcher | ⬜ | - | - | Task mới, plan vừa tạo |

### Phase 1: Tạo nhánh & Clone repo
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 1.1 | Tạo nhánh nghiên cứu mới `research/skills-2026-07-12` từ main | github-repo-researcher | ⬜ | nhánh `research/skills-2026-07-12` | - | |
| 1.2 | Clone repo anthropics/skills về scratchpad (ngoài working tree KZTEK), đọc & phân tích cấu trúc, README, source code chính | github-repo-researcher | ⬜ | scratchpad clone | - | Clone vào scratchpad, KHÔNG đưa .git repo ngoài vào commit KZTEK |

### Phase 2: Phân tích & Báo cáo
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | Viết phần phân tích repo trong `docs/research/RESEARCH-skills-2026-07-12.md` — mục đích, cấu trúc, điểm nổi bật kỹ thuật; KHÔNG kèm đề xuất cải tiến | github-repo-researcher | ⬜ | `docs/research/RESEARCH-skills-2026-07-12.md` | - | Tương đương Bước 3 WF-GITHUB-RESEARCH |
| 2.2 | Dựa trên phân tích Bước 2.1, viết bảng đề xuất cải tiến riêng biệt — từng đề xuất nêu rõ học từ đâu, áp dụng vào đâu trong KZTEK, lợi ích, rủi ro/effort — trình user | github-repo-researcher | ⬜ | Bảng đề xuất cải tiến (nhúng vào RESEARCH-*.md hoặc file riêng) | - | Tương đương Bước 3b WF-GITHUB-RESEARCH |

### Phase 3: User xác nhận & Áp dụng
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | USER xác nhận đề xuất nào được áp dụng | USER | ⬜ | Danh sách đề xuất đã chọn | - | BLOCK cho đến khi user xác nhận |
| 3.2 | Áp dụng đề xuất đã chọn vào code/tài liệu KZTEK, commit lên nhánh `research/skills-2026-07-12` | github-repo-researcher | ⬜ | Commits trên nhánh nghiên cứu | - | Tương đương Bước 4b WF-GITHUB-RESEARCH |

### Phase 4: Merge về main
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 4.1 | USER xác nhận merge nhánh nghiên cứu về main | USER | ⬜ | Xác nhận rõ ràng từ user | - | KHÔNG tự suy ra từ lần xác nhận trước |
| 4.2 | Merge nhánh `research/skills-2026-07-12` về main sau khi có xác nhận rõ ràng | github-repo-researcher | ⬜ | Merge commit trên main | - | Tương đương Bước 5b WF-GITHUB-RESEARCH |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp — tránh đọc lại/nghiên cứu lại.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

_(Chưa có entry — plan mới tạo, chưa thực hiện bước nào)_

## Artifacts dự kiến
- [ ] Nhánh git `research/skills-2026-07-12`
- [ ] `docs/research/RESEARCH-skills-2026-07-12.md` — Báo cáo phân tích repo
- [ ] `docs/research/RESEARCH-skills-2026-07-12.docx` — Xuất bởi md_to_docx_kztek.py
- [ ] `docs/research/RESEARCH-skills-2026-07-12.pdf` — Xuất bởi md_to_docx_kztek.py
- [ ] Commits áp dụng đề xuất trên nhánh nghiên cứu (tùy theo user chọn ở Bước 3.1)

## Blockers
Không có

## Quyết định / Ghi chú
- Repo nguồn: https://github.com/anthropics/skills
- Clone về scratchpad: `/tmp/claude-0/-home-user-claude/3d8f1af7-b4b6-558a-9589-2a78e2b640e0/scratchpad/anthropics-skills/`
- Nguyên tắc cứng: repo ngoài clone chỉ để đọc, không đưa `.git` của repo ngoài vào commit KZTEK
- Đề xuất đụng auth/payment/DB schema → chạy `security-audit-stride` trước khi áp dụng

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-07-12 | Plan tạo mới | task-planner |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
