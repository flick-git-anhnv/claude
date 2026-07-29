---
task: github-research-graphify
created: 2026-07-29
updated: 2026-07-29 13:43
status: active
workflow: WF-GITHUB-RESEARCH
priority: P2
---

# PLAN MASTER: Nghiên cứu repo GitHub — Graphify-Labs/graphify

> File này CHỈ chứa tổng quan + trạng thái. Chi tiết từng bước (mô tả đầy đủ, Handoff Log, artifact chi tiết) nằm ở `steps/STEP-[N.M]-[tên].md` tương ứng — xem cột "Step file" bên dưới.

## Mô tả
Nghiên cứu repo GitHub `https://github.com/Graphify-Labs/graphify` theo workflow WF-GITHUB-RESEARCH. Phân tích cấu trúc, công nghệ, điểm nổi bật kỹ thuật; sau đó tùy theo mục đích user chọn (Mode A: đề xuất cải tiến KZTEK / Mode B: học tập, tham khảo cá nhân) để tiến hành phần tiếp theo phù hợp.

## Nguồn yêu cầu
- Yêu cầu gốc: User gửi link https://github.com/Graphify-Labs/graphify và yêu cầu nghiên cứu (workflow WF-GITHUB-RESEARCH)
- Workflow: WF-GITHUB-RESEARCH — Nghiên cứu 1 repo GitHub theo link user gửi
- Agent chain: GitHub Repo Researcher → User (xác nhận mode) → GitHub Repo Researcher (nhánh Mode A hoặc Mode B)

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự tạo/cập nhật step file riêng, commit+push, rồi cập nhật đúng 1 dòng status ở bảng dưới đây.

### Phase 0: Audit — Kiểm tra trạng thái ban đầu
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 0.1 | Phase 0 Audit — kiểm tra artifact/plan/nhánh đã có, xác định task mới hay nối tiếp | GitHub Repo Researcher | ✅ | `steps/STEP-0.1-phase0-audit.md` | 2026-07-29 13:43 |

### Phase 1: Khởi tạo — Tạo nhánh nghiên cứu
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 1.1 | Tạo nhánh `research/graphify-2026-07-29`; xác định Mode A/B nếu user đã nói rõ mục đích | GitHub Repo Researcher | ⬜ | `steps/STEP-1.1-tao-nhanh.md` | - |

### Phase 2: Nghiên cứu repo & Xác định mode
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 2.1 | Clone repo về scratchpad, đọc & phân tích cấu trúc/công nghệ/điểm nổi bật | GitHub Repo Researcher | ⬜ | `steps/STEP-2.1-clone-phan-tich.md` | - |
| 2.2 | Viết phần phân tích repo vào `docs/research/RESEARCH-graphify-2026-07-29.md` (KHÔNG kèm đề xuất cải tiến ở bước này) | GitHub Repo Researcher | ⬜ | `steps/STEP-2.2-viet-phan-tich.md` | - |
| 2.3 | [USER] Chọn Mode A (đề xuất cải tiến KZTEK) hay Mode B (học tập/tham khảo cá nhân) | User | ⬜ | `steps/STEP-2.3-user-chon-mode.md` | - |

### Phase 3A: Mode A — Đề xuất & Áp dụng cải tiến KZTEK [chờ 2.3]
> Chỉ thực hiện nếu user chọn Mode A tại Bước 2.3. Nếu chọn Mode B → bỏ qua toàn bộ Phase 3A, chuyển sang Phase 3B.

| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 3A.1 | [Bước 3b] Viết bảng đề xuất cải tiến — từng đề xuất nêu rõ học từ đâu, áp dụng vào đâu, lợi ích, rủi ro/effort | GitHub Repo Researcher | ⬜ | `steps/STEP-3A.1-de-xuat-cai-tien.md` | - |
| 3A.2 | [Bước 4] [USER] Xác nhận đề xuất nào được áp dụng | User | ⬜ | `steps/STEP-3A.2-user-confirm-de-xuat.md` | - |
| 3A.3 | [Bước 4b] Áp dụng đề xuất đã được user chọn vào code/tài liệu KZTEK, commit lên nhánh nghiên cứu | GitHub Repo Researcher | ⬜ | `steps/STEP-3A.3-ap-dung-de-xuat.md` | - |
| 3A.4 | [Bước 5] [USER] Xác nhận merge nhánh nghiên cứu về main | User | ⬜ | `steps/STEP-3A.4-user-confirm-merge.md` | - |
| 3A.5 | [Bước 5b] Merge nhánh `research/graphify-2026-07-29` về main sau khi có xác nhận rõ ràng | GitHub Repo Researcher | ⬜ | `steps/STEP-3A.5-merge-main.md` | - |

### Phase 3B: Mode B — Học tập / Tham khảo cá nhân [chờ 2.3]
> Chỉ thực hiện nếu user chọn Mode B tại Bước 2.3. Nếu chọn Mode A → bỏ qua toàn bộ Phase 3B, chuyển sang Phase 3A.

| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 3B.1 | [Bước 3c] Hỏi user muốn tìm hiểu tiếp phần nào — nguyên lý hoạt động / hướng dẫn áp dụng-sử dụng / cả hai | GitHub Repo Researcher | ⬜ | `steps/STEP-3B.1-hoi-huong-tim-hieu.md` | - |
| 3B.2 | [Bước 3d] Giải thích tương tác (ví dụ cụ thể từ repo nguồn) — lặp hỏi-đáp đến khi user xác nhận đã nắm rõ | GitHub Repo Researcher | ⬜ | `steps/STEP-3B.2-giai-thich-tuong-tac.md` | - |
| 3B.3 | [Bước 3e] Viết tài liệu tổng hợp cuối (phân tích + nguyên lý + hướng dẫn áp dụng) → xuất DOCX/PDF → xin xác nhận merge | GitHub Repo Researcher | ⬜ | `steps/STEP-3B.3-tai-lieu-tong-hop.md` | - |

## Artifacts dự kiến (tổng)
- [ ] `docs/research/RESEARCH-graphify-2026-07-29.md` — Báo cáo phân tích repo chính thức
- [ ] `docs/research/RESEARCH-graphify-2026-07-29.docx` — Xuất DOCX theo brand KZTEK
- [ ] `docs/research/RESEARCH-graphify-2026-07-29.pdf` — Xuất PDF
- [ ] Nhánh `research/graphify-2026-07-29` trên git
- [ ] [Mode A] Các thay đổi code/tài liệu KZTEK từ đề xuất được duyệt
- [ ] [Mode B] Tài liệu tổng hợp học tập (nằm trong file báo cáo hoặc file riêng)

## Blockers
Không có

## Quyết định / Ghi chú tổng
- Mode A/B sẽ được xác định tại Bước 2.3 — Phase 3A và Phase 3B là nhánh song song; chỉ 1 nhánh được thực thi.
- Repo ngoài clone về CHỈ để đọc, không đưa `.git` của repo ngoài vào commit KZTEK (CLAUDE.md §4 WF-GITHUB-RESEARCH).
- Đề xuất đụng auth/payment/DB schema → chạy `security-audit-stride` trước khi merge (áp dụng Mode A).
- KHÔNG tự merge về main khi chưa có xác nhận rõ ràng tại đúng Bước 3A.4 hoặc Bước 3B.3.

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-07-29 | Plan tạo mới | task-planner |
| 2026-07-29 13:43 | Bước 0.1 ✅ — Phase 0 Audit hoàn thành: task mới hoàn toàn, không có artifact/nhánh/clone trước đó, Mode A đã xác nhận | GitHub Repo Researcher |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
**Cách đọc nhanh:** đọc MASTER trước → nếu cần chi tiết bước cụ thể mới mở step file tương ứng.
