---
task: memmachine-research
created: 2026-07-19
updated: 2026-07-19 14:30
status: in-progress
workflow: WF-GITHUB-RESEARCH
priority: P2
---

# PLAN: Nghiên cứu repo GitHub — MemMachine/MemMachine

## Mô tả
Nghiên cứu repo https://github.com/MemMachine/MemMachine: phân tích mục đích, cấu trúc, điểm nổi bật kỹ thuật, sau đó đề xuất cải tiến có thể áp dụng vào codebase KZTEK. Áp dụng đề xuất được user chọn, commit lên nhánh nghiên cứu và merge về main sau khi xác nhận.

## Nguồn yêu cầu
- Yêu cầu gốc: "nghiên cứu https://github.com/MemMachine/MemMachine"
- Workflow: WF-GITHUB-RESEARCH — Nghiên cứu 1 repo GitHub theo link user gửi
- Agent chain: GITHUB-REPO-RESEARCHER (Phase 0 Audit) → GITHUB-REPO-RESEARCHER (tạo nhánh) → GITHUB-REPO-RESEARCHER (clone + phân tích) → GITHUB-REPO-RESEARCHER (viết báo cáo) → GITHUB-REPO-RESEARCHER (đề xuất cải tiến) → USER (xác nhận đề xuất) → GITHUB-REPO-RESEARCHER (áp dụng) → USER (xác nhận merge) → GITHUB-REPO-RESEARCHER (merge main)

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự commit+push+điền cột "Hoàn thành lúc".

### Phase 0: Audit & Chuẩn bị
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 0.1 | Phase 0 Audit: Kiểm tra đã có nhánh/plan/artifact liên quan đến MemMachine chưa; phát hiện drift; xác định task mới hay nối tiếp; đưa ra ma trận bước cần chạy vs bỏ qua | github-repo-researcher | ✅ | Task mới — không có nhánh/artifact trước, chạy tất cả bước | 2026-07-19 14:00 | |
| 0.2 | Tạo nhánh nghiên cứu mới `research/memmachine-2026-07-19` từ main | github-repo-researcher | ✅ | Nhánh `research/memmachine-2026-07-19` đã tạo và push | 2026-07-19 14:05 | |

### Phase 1: Thu thập & Phân tích
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 1.1 | Clone repo https://github.com/MemMachine/MemMachine về thư mục scratchpad (ngoài working tree KZTEK); đọc & phân tích cấu trúc, source code, README, dependencies | github-repo-researcher | ✅ | Clone tại `/tmp/claude-0/.../scratchpad/research/memmachine/` — 845 files | 2026-07-19 14:10 | Repo ngoài CHỈ đọc, không đưa `.git` của repo ngoài vào commit KZTEK |
| 1.2 | Viết phần phân tích repo trong `docs/research/RESEARCH-memmachine-2026-07-19.md`: mục đích dự án, cấu trúc thư mục, kiến trúc kỹ thuật, điểm nổi bật — KHÔNG kèm đề xuất cải tiến ở bước này | github-repo-researcher | ✅ | `docs/research/RESEARCH-memmachine-2026-07-19.md` + `.docx` (commit 5fbb425) | 2026-07-19 14:30 | PDF thất bại do thiếu LibreOffice — DOCX OK |

### Phase 2: Đề xuất cải tiến
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | Dựa trên phân tích Phase 1, viết bảng đề xuất cải tiến vào `docs/research/RESEARCH-memmachine-2026-07-19.md` (mục đề xuất riêng biệt): mỗi đề xuất nêu rõ học từ đâu, áp dụng vào đâu trong KZTEK, lợi ích, rủi ro/effort; trình user xem xét | github-repo-researcher | ⬜ | `docs/research/RESEARCH-memmachine-2026-07-19.md` (mục đề xuất), `.docx`, `.pdf` cập nhật | - | |
| 2.2 | USER xác nhận đề xuất nào được áp dụng | user | ⬜ | Danh sách đề xuất được chọn | - | Dừng chờ user phản hồi |

### Phase 3: Áp dụng & Merge
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | Áp dụng các đề xuất được user chọn vào code/tài liệu KZTEK; commit lên nhánh `research/memmachine-2026-07-19` | github-repo-researcher | ⬜ | Commit(s) trên nhánh nghiên cứu | - | Nếu đề xuất đụng auth/payment/DB schema → chạy `security-audit-stride` trước khi merge |
| 3.2 | USER xác nhận merge nhánh nghiên cứu về main | user | ⬜ | Xác nhận merge | - | Dừng chờ user phản hồi — KHÔNG tự suy ra từ lần xác nhận trước |
| 3.3 | Merge nhánh `research/memmachine-2026-07-19` về main sau khi có xác nhận rõ ràng tại đúng thời điểm này | github-repo-researcher | ⬜ | Merge commit vào main | - | |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp — tránh đọc lại/nghiên cứu lại.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

### Phase 0 + Phase 1 — Clone, Đọc & Phân tích repo MemMachine

- **Đã làm:** Clone `--depth 1` về scratchpad (845 files). Đọc README, USAGE.md, AGENTS.md, docs/core_concepts/, packages/server/src/memmachine_server/semantic_memory/ (semantic_memory.py, semantic_ingestion.py, semantic_model.py), packages/server/src/memmachine_server/server/api_v2/ (service.py, mcp.py). Đọc cấu trúc packages, integrations, pyproject.toml.
- **File/module đã đọc:** `README.md`, `USAGE.md`, `AGENTS.md`, `docs/core_concepts/agentic_memory.mdx`, `packages/server/src/memmachine_server/semantic_memory/semantic_memory.py`, `semantic_ingestion.py`, `semantic_model.py`, `server/api_v2/service.py`, `server/api_v2/mcp.py`, `packages/server/src/memmachine_server/__init__.py`.
- **Hiện trạng KZTEK đã đọc:** `.claude/agents/task-planner.md`, `.claude/agents/github-repo-researcher.md`, `.claude/agents/code-migrator.md` (phần Handoff Log + Progress Ledger). Không có AI memory layer nào trong KZTEK.
- **Quyết định quan trọng:** Phân tích chỉ tập trung vào architecture/pattern kỹ thuật và so sánh với cơ chế memory thực tế của KZTEK (plan file + Handoff Log + GOTCHAS.md). Không đề xuất ở Phase 1.
- **Bước sau cần biết:** Phase 2 viết bảng đề xuất cải tiến vào cùng file `RESEARCH-memmachine-2026-07-19.md` (mục riêng, bổ sung vào phần 8). Bảng đề xuất CẦN đối chiếu cụ thể: MemMachine dùng pattern gì (file cụ thể) ↔ KZTEK đang làm gì ↔ lý do nên thay đổi ↔ đạt được gì cụ thể. KHÔNG đề xuất deploy Neo4j/PostgreSQL vì KZTEK là workspace agent, không phải production app — hãy tìm pattern có thể áp dụng nhẹ nhàng hơn (VD: cơ chế ingestion, category system, backoff pattern).

## Artifacts dự kiến
- [ ] Nhánh `research/memmachine-2026-07-19`
- [ ] `docs/research/RESEARCH-memmachine-2026-07-19.md` — Báo cáo phân tích + bảng đề xuất
- [ ] `docs/research/RESEARCH-memmachine-2026-07-19.docx`
- [ ] `docs/research/RESEARCH-memmachine-2026-07-19.pdf`
- [ ] Commit(s) áp dụng đề xuất trên nhánh nghiên cứu (nếu user chọn)
- [ ] Merge về main (nếu user xác nhận)

## Blockers
Không có

## Quyết định / Ghi chú
- Repo nguồn clone về CHỈ để đọc, không đưa `.git` của repo ngoài vào commit KZTEK.
- Không tự áp dụng đề xuất khi chưa được user chọn ở Bước 2.2.
- Không tự merge về main khi chưa có xác nhận rõ ràng tại đúng thời điểm Bước 3.2.
- Đề xuất đụng auth/payment/DB schema/dữ liệu nhạy cảm → chạy `security-audit-stride` trước khi merge.

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-07-19 | Plan tạo mới | task-planner |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
