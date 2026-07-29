---
step: "3A.3"
plan: ../PLAN-MASTER.md
agent: github-repo-researcher
status: done
completed_at: 2026-07-29 14:08
---

# STEP 3A.3 — [Mode A / Bước 4b] Áp dụng đề xuất đã được user chọn

## Input nhận
Từ Bước 3A.2 — danh sách đề xuất được user duyệt. Handoff Log sẽ được nhúng vào đây khi giao việc (danh sách cụ thể đề xuất nào được chọn, module KZTEK liên quan).

## Nhiệm vụ
Áp dụng các đề xuất đã được user chọn vào code/tài liệu KZTEK. Commit toàn bộ thay đổi lên nhánh `research/graphify-2026-07-29`. Nếu đề xuất đụng auth/payment/DB schema/dữ liệu nhạy cảm → chạy `security-audit-stride` trước khi coi là hoàn thành.

## Definition of Done
- [ ] Từng đề xuất được chọn đã được áp dụng vào đúng module/file KZTEK
- [ ] [Nếu áp dụng] Đề xuất đụng auth/payment/DB schema → đã chạy `security-audit-stride`, không có Fail nhóm rủi ro cao
- [ ] Tài liệu liên quan cập nhật theo §15 CLAUDE.md (PRD/TDD/DESIGN nếu thay đổi code/schema/UI)
- [ ] `git add` + `git commit` + `git push` trên nhánh `research/graphify-2026-07-29`
- [ ] Cập nhật step file này + PLAN-MASTER.md

## Đã làm
Áp dụng 5 đề xuất P1–P5 vào tài liệu KZTEK:

**P4 — CODE-GRAPH impact trong §15.3 (CLAUDE.md):**
- Thêm dòng `- [ ] CODE-GRAPH impact: [liệt kê module/node bị ảnh hưởng...]` vào checklist tài liệu đồng bộ trong PR description.

**P5 — LESSONS.md + §3.0 Pre-0b + §3.3 ghi chú (CLAUDE.md + docs/LESSONS.md):**
- Thêm Pre-0b vào §3.0: nhắc đọc docs/LESSONS.md khi bắt đầu session mới.
- Thêm ghi chú sau template §3.3: hướng dẫn ghi lesson sau mỗi workflow.
- Tạo file `docs/LESSONS.md` với template, mục đích, và 2 entry đầu tiên từ WF này.

**P2 — Query-first checklist §17.1 (CLAUDE.md):**
- Mở rộng Bước 3 trong §17.1: thêm danh sách 5 câu hỏi cụ thể agents PHẢI trả lời từ CODE-GRAPH (module ở đâu, phụ thuộc gì, ai gọi, API ở đâu, thay đổi gần đây).
- Gắn tiêu chí "≥ 3/5 câu trả lời được → bắt đầu coding".
- Bước 5 (tạo CODE-GRAPH mới): thêm ghi chú tùy chọn dùng `graphify` cho project > 50 file.

**P3 — Confidence labels §17.2 + CODE-GRAPH-template.md:**
- Thêm bảng 3 labels (CONFIRMED / INFERRED / UNCERTAIN) và quy tắc sử dụng vào CLAUDE.md §17.2.
- Thêm cột `Confidence` + ghi chú giải thích vào bảng "Dependencies quan trọng" trong `.claude/templates/CODE-GRAPH-template.md`.

**P1 — §17.6 graphify optional tool (CLAUDE.md):**
- Thêm mục §17.6 mới vào CLAUDE.md: giới thiệu graphify CLI như công cụ tùy chọn, cách cài, 3 lệnh cơ bản, khi nào nên dùng, và lưu ý quan trọng.

**RESEARCH update:**
- Cập nhật bảng tổng quan P1–P5 trong RESEARCH-graphify-2026-07-29.md: thêm cột "Trạng thái" ✅ cho cả 5.

**Xuất DOCX (§19):**
- Chạy `md_to_docx_kztek.py` cho 4 file: CLAUDE.md, docs/LESSONS.md, docs/research/RESEARCH-graphify-2026-07-29.md, .claude/templates/CODE-GRAPH-template.md — cả 4 DOCX thành công; PDF thất bại (thiếu converter, không block).

## Artifact
- `CLAUDE.md` — sửa §3.0, §3.3, §15.3, §17.1, §17.2, thêm §17.6
- `CLAUDE.docx` — xuất lại
- `docs/LESSONS.md` — tạo mới
- `docs/LESSONS.docx` — xuất mới
- `docs/research/RESEARCH-graphify-2026-07-29.md` — cập nhật trạng thái P1–P5 ✅
- `docs/research/RESEARCH-graphify-2026-07-29.docx` — xuất lại
- `.claude/templates/CODE-GRAPH-template.md` — thêm cột Confidence + ghi chú
- `.claude/templates/CODE-GRAPH-template.docx` — xuất lại

## Quyết định quan trọng
- P1 được áp dụng ở mức "wiring/documentation" (§17.6 optional tool) — không cài pip package, không chạy graphify thật, phù hợp vì chưa có C# product codebase để test thực tế.
- Không cần security-audit-stride: toàn bộ 5 đề xuất chỉ thay đổi tài liệu nội bộ (CLAUDE.md, templates, docs/), không đụng auth/payment/DB schema.
- docs/LESSONS.md được seeded với 2 lessons từ WF này (L001, L002) để file có nội dung meaningful ngay từ đầu.

## Handoff Log — bước sau cần biết
- Đã làm: 5 đề xuất P1–P5 áp dụng xong, commit sẽ được thực hiện ngay sau bước này.
- File/module đã đọc hoặc đổi: CLAUDE.md (§3.0, §3.3, §15.3, §17.1, §17.2, +§17.6), docs/LESSONS.md (tạo mới), docs/research/RESEARCH-graphify-2026-07-29.md (cập nhật bảng), .claude/templates/CODE-GRAPH-template.md (thêm cột Confidence).
- Quyết định quan trọng: Tất cả thay đổi chỉ là tài liệu — không cần security-audit.
- Bước sau cần biết: Bước 3A.4 là USER xác nhận merge nhánh `research/graphify-2026-07-29` về main. TUYỆT ĐỐI KHÔNG tự merge trước khi user confirm tại Bước 3A.4.

## Commit
- Hash: f7e1b51
- Đã push: có (research/graphify-2026-07-29)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
