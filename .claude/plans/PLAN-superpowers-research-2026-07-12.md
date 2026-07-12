---
task: superpowers-research
created: 2026-07-12
updated: 2026-07-12
status: planning
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
| 1.1 | Tạo nhánh nghiên cứu mới `research/superpowers-2026-07-12` | GITHUB REPO RESEARCHER | ⬜ | nhánh `research/superpowers-2026-07-12` | - | |
| 1.2 | Clone repo https://github.com/obra/superpowers về scratchpad (ngoài working tree KZTEK), đọc & phân tích toàn bộ cấu trúc | GITHUB REPO RESEARCHER | ⬜ | thư mục clone tạm trong scratchpad | - | KHÔNG đưa `.git` của repo ngoài vào commit KZTEK |
| 1.3 | Viết phần phân tích repo vào `docs/research/RESEARCH-superpowers-2026-07-12.md` — mục đích, cấu trúc, điểm nổi bật kỹ thuật; KHÔNG kèm đề xuất ở bước này; xuất DOCX+PDF | GITHUB REPO RESEARCHER | ⬜ | `docs/research/RESEARCH-superpowers-2026-07-12.md` + `.docx` + `.pdf` | - | |
| 1.3b | Dựa trên phân tích Bước 1.3, viết bảng đề xuất cải tiến riêng biệt (mỗi đề xuất: học từ đâu, áp dụng vào đâu trong KZTEK, lợi ích, rủi ro/effort); cập nhật vào file `.md` đã tạo; xuất lại DOCX+PDF; trình user | GITHUB REPO RESEARCHER | ⬜ | Bảng đề xuất trong `docs/research/RESEARCH-superpowers-2026-07-12.md` | - | |

### Phase 2: User xác nhận & Áp dụng đề xuất
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | [DỪNG — CHỜ USER] User xác nhận đề xuất nào được áp dụng vào codebase KZTEK | USER | ⬜ | Danh sách đề xuất được chọn | - | KHÔNG tự áp dụng khi chưa có xác nhận rõ ràng (CLAUDE.md §4 WF-GITHUB-RESEARCH) |
| 2.2 | Áp dụng các đề xuất đã được user chọn vào code/tài liệu KZTEK; commit lên nhánh `research/superpowers-2026-07-12`; nếu đề xuất đụng auth/payment/DB schema → chạy `security-audit-stride` trước khi tiếp tục | GITHUB REPO RESEARCHER | ⬜ | Các file code/tài liệu KZTEK đã cập nhật, commit lên nhánh | - | |

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

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
