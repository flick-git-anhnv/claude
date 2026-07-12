---
task: superpowers-research
created: 2026-07-12
updated: 2026-07-12 04:27
status: active
workflow: WF-GITHUB-RESEARCH
priority: P2
---

# PLAN: Nghiên cứu repo GitHub obra/superpowers

## Mô tả
Nghiên cứu repo GitHub https://github.com/obra/superpowers, phân tích cấu trúc, mục đích và điểm nổi bật kỹ thuật, đề xuất các cải tiến có thể áp dụng vào codebase KZTEK, sau đó áp dụng các đề xuất đã được user xác nhận và merge về main.

## Nguồn yêu cầu
- Yêu cầu gốc: "nghiên cứu https://github.com/obra/superpowers"
- Workflow: WF-GITHUB-RESEARCH — Nghiên cứu 1 repo GitHub theo link user gửi
- Agent chain: GITHUB REPO RESEARCHER → USER (xác nhận đề xuất) → GITHUB REPO RESEARCHER → USER (xác nhận merge) → GITHUB REPO RESEARCHER

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự commit+push+điền cột "Hoàn thành lúc".

### Phase 0: Audit — Kiểm tra trạng thái hiện tại
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 0.1 | Phase 0 Audit: kiểm tra đã có nhánh/plan/artifact nghiên cứu repo obra/superpowers chưa; xác định đây là task mới hay nối tiếp | GITHUB REPO RESEARCHER | ✅ | - | 2026-07-12 | Đã xác nhận: CHƯA CÓ nhánh, artifact hay plan nào — đây là task hoàn toàn mới |

### Phase 1: Phân tích repo & Viết báo cáo
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 1.1 | Tạo nhánh nghiên cứu mới `research/superpowers-2026-07-12` | GITHUB REPO RESEARCHER | ✅ | nhánh `research/superpowers-2026-07-12` | 2026-07-12 04:09 | |
| 1.2 | Clone repo https://github.com/obra/superpowers về scratchpad (ngoài working tree KZTEK), đọc & phân tích toàn bộ cấu trúc | GITHUB REPO RESEARCHER | ✅ | `/tmp/.../scratchpad/research/superpowers/` (không commit vào KZTEK) | 2026-07-12 04:09 | Đọc README, CLAUDE.md, 8/14 SKILL.md tiêu biểu, hooks.json, plugin.json, RELEASE-NOTES.md |
| 1.3 | Viết phần phân tích repo vào `docs/research/RESEARCH-superpowers-2026-07-12.md` — mục đích, cấu trúc, điểm nổi bật kỹ thuật; KHÔNG kèm đề xuất ở bước này; xuất DOCX+PDF | GITHUB REPO RESEARCHER | ✅ | `docs/research/RESEARCH-superpowers-2026-07-12.md` + `.docx` (PDF thất bại do chưa có LibreOffice) | 2026-07-12 04:09 | |
| 1.3b | Dựa trên phân tích Bước 1.3, viết bảng đề xuất cải tiến riêng biệt (mỗi đề xuất: học từ đâu, áp dụng vào đâu trong KZTEK, lợi ích, rủi ro/effort); cập nhật vào file `.md` đã tạo; xuất lại DOCX+PDF; trình user | GITHUB REPO RESEARCHER | ✅ | Bảng 7 đề xuất (P1-P7) trong `docs/research/RESEARCH-superpowers-2026-07-12.md` | 2026-07-12 04:09 | |

### Phase 2: User xác nhận & Áp dụng đề xuất
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | [DỪNG — CHỜ USER] User xác nhận đề xuất nào được áp dụng vào codebase KZTEK | USER | ✅ | Xác nhận áp dụng TẤT CẢ 7 đề xuất (P1–P7) | 2026-07-12 | User xác nhận qua dispatch message — áp dụng toàn bộ P1–P7 |
| 2.2 | Áp dụng các đề xuất đã được user chọn vào code/tài liệu KZTEK; commit lên nhánh `research/superpowers-2026-07-12`; nếu đề xuất đụng auth/payment/DB schema → chạy `security-audit-stride` trước khi tiếp tục | GITHUB REPO RESEARCHER | ✅ | 14 files đã cập nhật (xem Handoff Log), commit + push lên nhánh | 2026-07-12 04:27 | Không có đề xuất nào đụng auth/payment/DB — không cần security-audit-stride |

### Phase 3: User xác nhận merge & Merge về main
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | [DỪNG — CHỜ USER] User xác nhận merge nhánh `research/superpowers-2026-07-12` về main | USER | ⬜ | Xác nhận rõ ràng từ user tại đúng thời điểm này | - | KHÔNG tự suy ra từ lần xác nhận trước (Git Safety Protocol) |
| 3.2 | Merge nhánh `research/superpowers-2026-07-12` về main sau khi có xác nhận rõ ràng | GITHUB REPO RESEARCHER | ⬜ | Nhánh đã được merge vào main | - | |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp — tránh đọc lại/nghiên cứu lại.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

### Bước 0.1 — Phase 0 Audit
- Đã làm: Kiểm tra toàn bộ `.claude/plans/`, `docs/research/`, git branches — không tìm thấy artifact hay nhánh nào liên quan đến obra/superpowers. Đây là task mới hoàn toàn.
- File/module đã đọc hoặc đổi: `.claude/plans/` (Glob), không có file nào liên quan
- Quyết định quan trọng: Xác nhận task mới — bắt đầu từ Bước 1.1
- Bước sau cần biết: Không có artifact nào cần kế thừa; bắt đầu từ đầu hoàn toàn

### Bước 1.1 — Tạo nhánh nghiên cứu
- Đã làm: Tạo nhánh `research/superpowers-2026-07-12` từ `claude/superpowers-research-otxyms` bằng `git checkout -b`.
- File/module đã đọc hoặc đổi: Plan file (đọc), không có file code nào thay đổi.
- Quyết định quan trọng: Không cần push ngay — sẽ push khi commit đầu tiên.
- Bước sau cần biết: Nhánh đã tồn tại cục bộ, chưa push lên remote.

### Bước 1.2 — Clone & phân tích repo
- Đã làm: Clone `--depth 1` vào scratchpad. Đọc: README.md, CLAUDE.md, plugin.json, hooks.json, RELEASE-NOTES.md, và 8 SKILL.md (using-superpowers, subagent-driven-development, writing-plans, brainstorming, verification-before-completion, systematic-debugging, dispatching-parallel-agents, writing-skills).
- File/module đã đọc hoặc đổi: Scratchpad tại `/tmp/claude-0/-home-user-claude/ddb05ad1-365a-5f35-9174-56323bfb3e6f/scratchpad/research/superpowers/` — KHÔNG commit vào KZTEK.
- Quyết định quan trọng: Tập trung đọc các skill core liên quan đến agent orchestration và workflow; bỏ qua skill git-worktrees, finishing-branch, requesting/receiving-code-review vì ít liên quan nhất với KZTEK multi-agent system.
- Bước sau cần biết: Repo v6.1.1 (MIT). 14 skills. Key patterns: Red Flags tables, file handoffs, durable ledger, model tier selection, two-stage review, writing-skills TDD methodology.

### Bước 1.3 — Viết phân tích repo
- Đã làm: Viết `docs/research/RESEARCH-superpowers-2026-07-12.md` (Phần 1: phân tích repo). Xuất DOCX thành công. PDF thất bại do thiếu LibreOffice (ghi chú, không block).
- File/module đã đọc hoặc đổi: `docs/research/RESEARCH-superpowers-2026-07-12.md` (tạo mới), `docs/research/RESEARCH-superpowers-2026-07-12.docx` (tạo mới).
- Quyết định quan trọng: Tách Phần 1 (phân tích) và Phần 2 (đề xuất) thành 2 section riêng trong cùng 1 file theo đúng CLAUDE.md §4 WF-GITHUB-RESEARCH.
- Bước sau cần biết: Không cần đọc lại toàn bộ repo — đã tóm tắt đủ trong RESEARCH-*.md Phần 1.

### Bước 1.3b — Viết bảng đề xuất
- Đã làm: Viết 7 đề xuất (P1-P7) vào Phần 2 của cùng file. Cập nhật DOCX. Tất cả đề xuất không đụng auth/payment/DB — không cần security-audit-stride.
- File/module đã đọc hoặc đổi: `docs/research/RESEARCH-superpowers-2026-07-12.md` (cập nhật), `docs/research/RESEARCH-superpowers-2026-07-12.docx` (cập nhật).
- Quyết định quan trọng: 7 đề xuất tập trung vào cải thiện compliance agent (P1-P2), tooling workflow (P3), resilience (P4), consistency (P5), skill creation process (P6), cost optimization (P7). Không có đề xuất nào thay đổi cấu trúc agent hierarchy.
- Bước sau cần biết: Bước 2.1 là DỪNG bắt buộc chờ user. KHÔNG tự áp dụng bất kỳ đề xuất nào trước khi user chọn.

### Bước 2.2 — Áp dụng đề xuất P1–P7
- Đã làm: Áp dụng tất cả 7 đề xuất đã được user xác nhận. Cập nhật 14 file (12 sửa, 2 tạo mới). Xuất DOCX+PDF cho tất cả file `.md` bị thay đổi (11 DOCX thành công; PDF thất bại do thiếu LibreOffice — không block). Cập nhật bảng trạng thái áp dụng trong RESEARCH file (tất cả ✅).
- File/module đã đọc hoặc đổi:
  - `.claude/commands/scope-check.md` (P1 — thêm Red Flags table)
  - `.claude/commands/ship.md` (P1 — thêm Red Flags table)
  - `.claude/agents/tech-lead.md` (P1 — chuyển Red Flags sang table; P3 — thêm tip review-package.sh)
  - `.claude/agents/qa-lead.md` (P1 — thêm Red Flags table)
  - `.claude/agents/senior-developer.md` (P2 — thêm Verification Gate; P3 — thêm tip review-package.sh)
  - `.claude/agents/junior-developer.md` (P2 — thêm Verification Gate; P5 — chuẩn hóa description)
  - `.claude/agents/qa-engineer.md` (P2 — thêm Verification Gate)
  - `.claude/agents/code-migrator.md` (P4 — thêm Progress Ledger)
  - `.claude/agents/github-repo-researcher.md` (P4 — thêm Progress Ledger)
  - `.gitignore` (P4 — thêm `_workspace/` và `_workspace_*/`)
  - `scripts/review-package.sh` (P3 — tạo mới)
  - `.claude/commands/writing-agent-skill.md` (P6 — tạo mới)
  - `CLAUDE.md` (P7 — thêm turn count caution vào §13.1b và §13.2)
  - `docs/research/RESEARCH-superpowers-2026-07-12.md` (cập nhật bảng trạng thái → tất cả ✅)
- Quyết định quan trọng: P5 chỉ sửa `junior-developer.md` (file duy nhất dùng "Dùng agent này khi:" thay vì "PHẢI dùng agent này khi:"); tất cả agent khác đã chuẩn. P1 cho tech-lead.md: chuyển đổi bullet format cũ sang Thought|Reality table, không xóa nội dung.
- Bước sau cần biết: Bước 3.1 là DỪNG CHỜ USER xác nhận merge. TUYỆT ĐỐI KHÔNG tự merge nhánh `research/superpowers-2026-07-12` về main — phải có xác nhận rõ ràng từ user tại đúng thời điểm này (Git Safety Protocol).

## Artifacts dự kiến
- [ ] nhánh `research/superpowers-2026-07-12`
- [ ] `docs/research/RESEARCH-superpowers-2026-07-12.md` — phân tích repo + bảng đề xuất
- [ ] `docs/research/RESEARCH-superpowers-2026-07-12.docx`
- [ ] `docs/research/RESEARCH-superpowers-2026-07-12.pdf`
- [ ] Các file code/tài liệu KZTEK được cập nhật theo đề xuất đã chọn (xác định sau Bước 2.1)

## Blockers
Không có

## Quyết định / Ghi chú
- Repo nguồn: https://github.com/obra/superpowers
- Scratchpad clone: `/tmp/claude-0/-home-user-claude/ddb05ad1-365a-5f35-9174-56323bfb3e6f/scratchpad/superpowers-clone/` (KHÔNG commit vào KZTEK)
- Bước 2.1 và 3.1 là điểm DỪNG bắt buộc chờ user — không được tự tiếp tục

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-07-12 | Plan tạo mới, Phase 0 Audit hoàn thành (task mới xác nhận) | task-planner |
| 2026-07-12 04:09 | Bước 1.1-1.3b Done: nhánh tạo, repo clone+phân tích, RESEARCH-*.md + .docx viết xong (7 đề xuất P1-P7) | GitHub Repo Researcher |
| 2026-07-12 04:27 | Bước 2.1 Done (user xác nhận áp dụng P1-P7); Bước 2.2 Done: 14 files cập nhật (12 sửa, 2 tạo mới), commit+push lên nhánh | GitHub Repo Researcher |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
