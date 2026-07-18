---
task: graphify-research
created: 2026-07-18
updated: 2026-07-18 15:10
status: in-progress
workflow: WF-GITHUB-RESEARCH
priority: P2
---

# PLAN: Nghiên cứu GitHub Repo — Graphify Labs / graphify

## Mô tả
Nghiên cứu repo GitHub https://github.com/Graphify-Labs/graphify theo workflow WF-GITHUB-RESEARCH: phân tích cấu trúc, mục đích, điểm nổi bật kỹ thuật, và đề xuất cải tiến có thể áp dụng cho codebase KZTEK.

## Nguồn yêu cầu
- Yêu cầu gốc: Nghiên cứu repo GitHub https://github.com/Graphify-Labs/graphify
- Workflow: WF-GITHUB-RESEARCH — Nghiên cứu 1 repo GitHub theo link user gửi
- Agent chain: GitHub Repo Researcher → User → GitHub Repo Researcher → User → GitHub Repo Researcher

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự commit+push+điền cột "Hoàn thành lúc".

### Phase 0: Audit & Chuẩn bị
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 0.1 | Phase 0 Audit — kiểm tra đã có nhánh/plan/artifact liên quan đến graphify chưa; phát hiện drift; xác định các bước cần chạy vs bỏ qua | GitHub Repo Researcher | ✅ | Ma trận bước cần chạy (không có drift, task hoàn toàn mới) | 2026-07-18 15:04 | |

### Phase 1: Clone & Phân tích
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 1.1 | Tạo nhánh nghiên cứu mới `research/graphify-2026-07-18` từ main | GitHub Repo Researcher | ✅ | Nhánh `research/graphify-2026-07-18` | 2026-07-18 15:04 | |
| 1.2 | Clone repo https://github.com/Graphify-Labs/graphify về scratchpad (ngoài working tree KZTEK), đọc & phân tích toàn bộ cấu trúc | GitHub Repo Researcher | ✅ | Repo tại scratchpad/research/graphify/ | 2026-07-18 15:05 | |

### Phase 2: Viết báo cáo & Đề xuất
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | Viết phần phân tích repo vào `docs/research/RESEARCH-graphify-2026-07-18.md` — mục đích, cấu trúc, điểm nổi bật kỹ thuật (KHÔNG kèm đề xuất cải tiến) | GitHub Repo Researcher | ✅ | `docs/research/RESEARCH-graphify-2026-07-18.md` + `.docx` | 2026-07-18 15:08 | |
| 2.2 | Dựa trên phân tích Bước 2.1, viết bảng đề xuất cải tiến (từng đề xuất: học từ đâu, áp dụng vào đâu trong KZTEK, lợi ích, rủi ro/effort), trình user | GitHub Repo Researcher | ✅ | §6 Bảng đề xuất G1-G5 (nhúng trong RESEARCH-*.md) | 2026-07-18 15:10 | |

### Phase 3: User duyệt & Áp dụng
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | USER xác nhận đề xuất nào được áp dụng | User | ⬜ | Danh sách đề xuất được chọn | - | Chờ phản hồi từ user |
| 3.2 | Áp dụng đề xuất đã chọn vào code/tài liệu KZTEK, commit lên nhánh `research/graphify-2026-07-18` | GitHub Repo Researcher | ⬜ | Commit trên nhánh nghiên cứu | - | Chỉ chạy nếu user chọn ít nhất 1 đề xuất |

### Phase 4: Merge về main
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 4.1 | USER xác nhận merge nhánh `research/graphify-2026-07-18` về main | User | ⬜ | Xác nhận merge | - | Chờ phản hồi từ user |
| 4.2 | Merge nhánh nghiên cứu về main sau khi có xác nhận rõ ràng | GitHub Repo Researcher | ⬜ | Nhánh merged vào main | - | Không tự suy ra từ lần xác nhận trước |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp — tránh đọc lại/nghiên cứu lại.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

### Bước 0.1 — Phase 0 Audit
- Đã làm: Kiểm tra git branch, docs/research/, .claude/plans/ — không có artifact graphify nào trước đó. Task hoàn toàn mới, chạy toàn bộ bước.
- File/module đã đọc: `git branch -a`, `ls docs/research/`, `ls .claude/plans/`
- Quyết định quan trọng: Tạo nhánh từ `claude/graphify-research-c6fb1j` (nhánh task hiện tại), không từ main (không cần tạo thêm nhánh trung gian).
- Bước sau cần biết: Nhánh hiện tại khi bắt đầu là `claude/graphify-research-c6fb1j`; nhánh research mới là `research/graphify-2026-07-18`.

### Bước 1.1 + 1.2 — Tạo nhánh + Clone
- Đã làm: Tạo nhánh `research/graphify-2026-07-18`, clone `--depth 1` repo vào scratchpad `/tmp/claude-0/.../scratchpad/research/graphify/`.
- File/module đã đọc: README.md, ARCHITECTURE.md, pyproject.toml, graphify/extractors/csharp.py, graphify/validate.py, graphify/security.py (80 dòng đầu), graphify/hooks.py (80 dòng đầu), graphify/affected.py (100 dòng đầu), graphify/global_graph.py (50 dòng đầu), graphify/always_on/*.md, AGENTS.md.
- Quyết định quan trọng: Không clone `.git` của repo ngoài vào workspace KZTEK.
- Bước sau cần biết: Repo đã clone tại path trên; .git của graphify hoàn toàn tách biệt khỏi KZTEK.

### Bước 2.1 + 2.2 — Viết phân tích + Đề xuất
- Đã làm: Tạo `docs/research/RESEARCH-graphify-2026-07-18.md` (§1-§8 đầy đủ, bao gồm 5 đề xuất G1-G5). Xuất DOCX thành công (`docs/research/RESEARCH-graphify-2026-07-18.docx`). PDF thất bại do thiếu LibreOffice (chấp nhận được theo §19.4).
- File/module đã đọc: code-graph/CODE-GRAPH.md (để mô tả hiện trạng KZTEK), .claude/agents/ và .claude/commands/ (liệt kê).
- Quyết định quan trọng: Gộp Bước 2.1 và 2.2 vào cùng 1 file (§1-§5 là phân tích, §6 là bảng đề xuất) theo đặc tả WF-GITHUB-RESEARCH.
- Bước sau cần biết: Chờ user chọn đề xuất nào trong G1-G5 tại Bước 3.1. KHÔNG áp dụng bất kỳ đề xuất nào trước khi có xác nhận.

## Artifacts dự kiến
- [x] Nhánh `research/graphify-2026-07-18` (git branch)
- [x] `docs/research/RESEARCH-graphify-2026-07-18.md` — Báo cáo phân tích repo
- [x] `docs/research/RESEARCH-graphify-2026-07-18.docx` — Xuất DOCX theo brand KZTEK
- [ ] `docs/research/RESEARCH-graphify-2026-07-18.pdf` — Xuất PDF từ DOCX (thiếu LibreOffice)
- [x] Bảng đề xuất cải tiến G1-G5 (nhúng trong file RESEARCH §6)
- [ ] Commit áp dụng đề xuất trên nhánh nghiên cứu (chờ user chọn Bước 3.1)

## Blockers
Không có

## Quyết định / Ghi chú
- Repo nguồn: https://github.com/Graphify-Labs/graphify
- Nhánh nghiên cứu: `research/graphify-2026-07-18`
- Repo ngoài clone về CHỈ để đọc — không đưa `.git` của repo ngoài vào commit KZTEK
- Bước 3.2 (áp dụng đề xuất) chỉ thực hiện nếu user chọn ít nhất 1 đề xuất tại Bước 3.1
- Bước 4.2 (merge) chỉ thực hiện khi có xác nhận rõ ràng tại đúng thời điểm Bước 4.1 — không tự suy ra
- Đề xuất đụng auth/payment/DB schema/dữ liệu nhạy cảm → phải chạy `security-audit-stride` trước khi merge

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-07-18 | Plan tạo mới | task-planner |
| 2026-07-18 15:10 | Hoàn thành Bước 0.1, 1.1, 1.2, 2.1, 2.2 — RESEARCH-graphify-2026-07-18.md + .docx tạo xong, đề xuất G1-G5 sẵn sàng trình user | github-repo-researcher |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
