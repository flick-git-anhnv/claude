---
task: research-gitnexus
created: 2026-08-04
updated: 2026-08-04 15:30
status: in-progress
workflow: WF-GITHUB-RESEARCH
priority: P2
---

# PLAN MASTER: Nghiên cứu repo GitHub — abhigyanpatwari/GitNexus

> File này CHỈ chứa tổng quan + trạng thái. Chi tiết từng bước (mô tả đầy đủ, Handoff Log, artifact chi tiết) nằm ở `steps/STEP-[N.M]-[tên].md` tương ứng — xem cột "Step file" bên dưới.

## Mô tả
Nghiên cứu repo GitHub https://github.com/abhigyanpatwari/GitNexus theo workflow WF-GITHUB-RESEARCH. Bao gồm: audit xem đã có artifact chưa, tạo nhánh research, clone repo, phân tích kỹ thuật, hỏi user chọn Mode A (áp dụng KZTEK) hoặc Mode B (học tập/tham khảo), rồi thực hiện theo nhánh tương ứng.

## Nguồn yêu cầu
- Yêu cầu gốc: Nghiên cứu repo GitHub https://github.com/abhigyanpatwari/GitNexus theo WF-GITHUB-RESEARCH
- Workflow: WF-GITHUB-RESEARCH — Nghiên cứu 1 repo GitHub theo link user gửi
- Agent chain: github-repo-researcher (Phase 0 Audit → tạo nhánh → clone → phân tích → hỏi Mode → nhánh A hoặc B)

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự tạo/cập nhật step file riêng, commit+push, rồi cập nhật đúng 1 dòng status ở bảng dưới đây.

### Phase 1: Audit & Setup
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 1.1 | Phase 0 Audit — kiểm tra artifact/nhánh đã có chưa | github-repo-researcher | ✅ | `steps/STEP-1.1-phase0-audit.md` | 2026-08-04 10:00 |
| 1.2 | Tạo nhánh `research/gitnexus-2026-08-04` | github-repo-researcher | ✅ | `steps/STEP-1.2-tao-nhanh.md` | 2026-08-04 10:05 |

### Phase 2: Clone & Phân tích
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 2.1 | Clone repo về scratchpad, đọc & phân tích cấu trúc | github-repo-researcher | ✅ | `steps/STEP-2.1-clone-phan-tich.md` | 2026-08-04 10:30 |
| 2.2 | Viết phân tích repo vào `docs/research/RESEARCH-gitnexus-2026-08-04.md` | github-repo-researcher | ✅ | `steps/STEP-2.2-viet-phan-tich.md` | 2026-08-04 11:00 |
| 2.3 | Hỏi user chọn Mode A (áp dụng KZTEK) hay Mode B (học tập/tham khảo) | github-repo-researcher | ✅ | `steps/STEP-2.3-hoi-mode.md` | 2026-08-04 |

### Phase 3: Theo mode được chọn (điền sau khi biết Mode)
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 3.1 | [Mode A] Bảng đề xuất cải tiến KZTEK — hoặc — [Mode B] Giải thích tương tác nguyên lý/cách vận hành | github-repo-researcher | ✅ | `steps/STEP-3.1-mode-action.md` | 2026-08-04 15:30 |
| 3.2 | [Mode A] User duyệt + áp dụng đề xuất — hoặc — [Mode B] Tài liệu tổng hợp cuối cùng + xuất DOCX/PDF | github-repo-researcher | ⬜ | `steps/STEP-3.2-mode-finalize.md` | - |
| 3.3 | [Mode A only] Xác nhận merge nhánh research → main | github-repo-researcher | ⬜ | `steps/STEP-3.3-merge.md` | - |

> Bước 3.3 chỉ chạy nếu Mode A. Nếu Mode B → đánh dấu ⏭️ Skipped sau khi biết mode.

## Artifacts dự kiến (tổng)
- [ ] Nhánh git `research/gitnexus-2026-08-04`
- [ ] `docs/research/RESEARCH-gitnexus-2026-08-04.md` — phân tích repo
- [ ] `docs/research/RESEARCH-gitnexus-2026-08-04.docx` + `.pdf`
- [ ] [Mode A] Đề xuất cải tiến KZTEK được áp dụng (nếu có)
- [ ] [Mode B] Tài liệu tổng hợp nguyên lý/hướng dẫn (nếu chọn Mode B)

## Blockers
Không có

## Quyết định / Ghi chú tổng
- Bước 1.1–2.3 (Phase 0 đến hỏi Mode) là bước đọc/nghiên cứu — không thay đổi code, có thể tiến hành ngay mà không cần user duyệt thêm.
- Từ bước 3.1 Mode A trở đi (áp dụng đề xuất, merge) cần user xác nhận rõ ràng từng bước theo WF-GITHUB-RESEARCH.
- Repo nguồn clone về CHỈ để đọc, không đưa `.git` của repo ngoài vào commit KZTEK.

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-08-04 | Plan tạo mới | task-planner |
| 2026-08-04 | Phase 1 hoàn thành (1.1 audit, 1.2 tạo nhánh), Phase 2 bước 2.1+2.2 hoàn thành (clone, viết RESEARCH-gitnexus.md+docx+pdf) | github-repo-researcher |
| 2026-08-04 15:30 | Bước 2.3 ✅ (user chọn Mode A), Bước 3.1 ✅ (6 đề xuất GX-1..GX-6 viết vào RESEARCH file + xuất DOCX+PDF) — chờ user chọn đề xuất áp dụng (Bước 4) | github-repo-researcher |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
**Cách đọc nhanh:** đọc MASTER trước → nếu cần chi tiết bước cụ thể mới mở step file tương ứng.
