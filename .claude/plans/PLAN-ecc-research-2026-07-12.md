---
task: ecc-research
created: 2026-07-12
updated: 2026-07-12
status: planning
workflow: WF-GITHUB-RESEARCH
priority: P2
---

# PLAN: Nghiên cứu repo GitHub — affaan-m/ecc

## Mô tả
Nghiên cứu repo GitHub https://github.com/affaan-m/ecc theo workflow WF-GITHUB-RESEARCH: phân tích cấu trúc, mục đích, điểm nổi bật kỹ thuật, sau đó đề xuất cải tiến có thể áp dụng vào codebase KZTEK.

## Nguồn yêu cầu
- Yêu cầu gốc: Nghiên cứu repo GitHub https://github.com/affaan-m/ecc
- Workflow: WF-GITHUB-RESEARCH — Nghiên cứu 1 repo GitHub theo link user gửi
- Agent chain: GITHUB-REPO-RESEARCHER (Phase 0 Audit) → GITHUB-REPO-RESEARCHER (tạo nhánh + clone + phân tích + đề xuất) → USER (duyệt) → GITHUB-REPO-RESEARCHER (áp dụng) → USER (xác nhận merge) → GITHUB-REPO-RESEARCHER (merge main)

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự commit+push+điền cột "Hoàn thành lúc".

### Phase 0: Audit & Khởi tạo
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 0.1 | Phase 0 Audit — kiểm tra đã có nhánh/plan/artifact chưa; phát hiện drift; xác định bước nào cần chạy vs bỏ qua | GITHUB-REPO-RESEARCHER | ⬜ | Ma trận bước cần chạy/bỏ qua | - | |
| 0.2 | Tạo nhánh nghiên cứu mới `research/ecc-2026-07-12` từ main | GITHUB-REPO-RESEARCHER | ⬜ | Nhánh `research/ecc-2026-07-12` | - | |

### Phase 1: Clone & Phân tích repo
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 1.1 | Clone repo https://github.com/affaan-m/ecc về thư mục scratchpad (ngoài working tree KZTEK), đọc & phân tích toàn bộ cấu trúc | GITHUB-REPO-RESEARCHER | ⬜ | Repo đã clone trong scratchpad | - | Clone CHỈ để đọc, KHÔNG đưa `.git` ngoài vào commit KZTEK |
| 1.2 | Viết phần phân tích repo vào `docs/research/RESEARCH-ecc-2026-07-12.md` — mục đích, cấu trúc, điểm nổi bật kỹ thuật. KHÔNG kèm đề xuất cải tiến ở bước này | GITHUB-REPO-RESEARCHER | ⬜ | `docs/research/RESEARCH-ecc-2026-07-12.md` (phần phân tích), `.docx`, `.pdf` | - | |
| 1.3 | Dựa trên phân tích Bước 1.2, viết bảng đề xuất cải tiến (học từ đâu, áp dụng vào đâu trong KZTEK, lợi ích, rủi ro/effort) và trình user | GITHUB-REPO-RESEARCHER | ⬜ | Bảng đề xuất cải tiến (nhúng vào `RESEARCH-ecc-2026-07-12.md` hoặc file riêng) | - | |

### Phase 2: User duyệt & Áp dụng
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | User xác nhận đề xuất nào được áp dụng | USER | ⬜ | Danh sách đề xuất được chọn | - | Bước chờ input user — KHÔNG tự áp dụng khi chưa có xác nhận |
| 2.2 | Áp dụng đề xuất đã được user chọn vào code/tài liệu KZTEK, commit lên nhánh `research/ecc-2026-07-12` | GITHUB-REPO-RESEARCHER | ⬜ | Các file đã sửa/thêm; commit trên nhánh nghiên cứu | - | Đề xuất đụng auth/payment/DB schema → chạy `security-audit-stride` trước khi merge |

### Phase 3: Merge về main
| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | User xác nhận merge nhánh nghiên cứu về main | USER | ⬜ | Xác nhận merge rõ ràng | - | Cần xác nhận riêng biệt tại đúng thời điểm này — không suy ra từ lần xác nhận trước |
| 3.2 | Merge nhánh `research/ecc-2026-07-12` về main sau khi có xác nhận rõ ràng | GITHUB-REPO-RESEARCHER | ⬜ | Nhánh đã merge vào main | - | KHÔNG tự merge khi chưa có xác nhận tại Bước 3.1 |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp — tránh đọc lại/nghiên cứu lại.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

_(Chưa có entry — sẽ được điền sau khi từng bước hoàn thành)_

## Artifacts dự kiến
- [ ] Nhánh `research/ecc-2026-07-12` (tạo từ main)
- [ ] `docs/research/RESEARCH-ecc-2026-07-12.md` — phân tích repo + bảng đề xuất cải tiến
- [ ] `docs/research/RESEARCH-ecc-2026-07-12.docx` — xuất bởi `md_to_docx_kztek.py`
- [ ] `docs/research/RESEARCH-ecc-2026-07-12.pdf` — xuất bởi `md_to_docx_kztek.py`
- [ ] Các file áp dụng đề xuất (tuỳ theo đề xuất user chọn ở Bước 2.1)

## Blockers
Không có

## Quyết định / Ghi chú
- Repo nguồn: https://github.com/affaan-m/ecc
- Scratchpad clone: `/tmp/claude-0/-home-user-claude/9f35383a-4fe9-500e-a681-19d6d717f447/scratchpad/ecc-clone/` (ngoài working tree KZTEK)
- Nguyên tắc cứng: repo ngoài clone CHỈ để đọc; không đưa `.git` ngoài vào commit KZTEK
- Nếu đề xuất đụng auth/payment/DB schema/dữ liệu nhạy cảm → bắt buộc chạy `security-audit-stride` trước khi merge

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-07-12 | Plan tạo mới | task-planner |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
