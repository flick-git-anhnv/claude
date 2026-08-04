---
step: 3.2
plan: ../PLAN-MASTER.md
agent: github-repo-researcher
status: done
completed_at: 2026-08-04 08:53
---

# STEP 3.2 — Hoàn thiện theo Mode (A: áp dụng đề xuất / B: tài liệu tổng hợp)

## Input nhận
Handoff từ STEP-3.1: [Mode A] danh sách đề xuất user đã chọn / [Mode B] xác nhận user đã nắm rõ nguyên lý.

## Nhiệm vụ
**Nếu Mode A:** Áp dụng các đề xuất đã được user chọn vào code/tài liệu KZTEK. Commit lên nhánh `research/gitnexus-2026-08-04`. Nếu đề xuất đụng auth/payment/DB schema → chạy `security-audit-stride` trước khi tiếp tục.

**Nếu Mode B:** Viết tài liệu tổng hợp cuối cùng (phân tích + nguyên lý + hướng dẫn áp dụng) vào `docs/research/RESEARCH-gitnexus-2026-08-04-guide.md`. Xuất DOCX+PDF. Xin xác nhận merge nhánh về main.

## Definition of Done
**Mode A:**
- [ ] Các đề xuất đã chọn được áp dụng vào KZTEK
- [ ] Commit + push lên nhánh research
- [ ] Báo user danh sách thay đổi đã áp dụng

**Mode B:**
- [ ] `docs/research/RESEARCH-gitnexus-2026-08-04-guide.md` được tạo
- [ ] DOCX + PDF xuất thành công
- [ ] Commit + push lên nhánh research

## Đã làm
Mode A: Áp dụng 6 đề xuất GX-1 đến GX-6 từ nghiên cứu GitNexus vào hệ thống KZTEK.
- GX-1: Thêm cột Callers/Used-by + depth-1/depth-2 taxonomy vào CODE-GRAPH-template.md và CLAUDE.md §15.3
- GX-2: Thêm `deps: []` vào PLAN-STEP-template.md + validation bước deps trong task-planner.md
- GX-3: Tạo eval detect-impact.md (EDD) + skill /detect-impact graphify-aware
- GX-4: Thêm cột Last verified + staleness rule §17.2 vào CODE-GRAPH-template.md và CLAUDE.md
- GX-5: Thêm step 3b CONTEXT-HINTS trong task-planner.md + Pre-0c trong CLAUDE.md §3.0
- GX-6: Handoff Log -> Handoff Payload 3-key trong PLAN-STEP-template.md + CLAUDE.md §16.4/§16.5 + task-planner.md
Cập nhật RESEARCH file mục 8, CLAUDE.md changelog v1.9, xuất DOCX.

## Artifact
- `.claude/templates/CODE-GRAPH-template.md` (GX-1, GX-4)
- `.claude/templates/PLAN-STEP-template.md` (GX-2, GX-6)
- `.claude/commands/detect-impact.md` (GX-3 — mới)
- `.claude/evals/detect-impact.md` (GX-3 — mới)
- `.claude/agents/task-planner.md` (GX-2, GX-5, GX-6)
- `CLAUDE.md` (GX-1 §15.3, GX-4 §17.2, GX-5 §3.0, GX-6 §16.4/§16.5, changelog v1.9)
- `docs/research/RESEARCH-gitnexus-2026-08-04.md` (mục 8 kết quả) + `.docx`

## Quyết định quan trọng
- GX-6 backward compatible: step file cũ dùng "Handoff Log" vẫn hoạt động
- GX-3 graphify-aware: skill /detect-impact ưu tiên graphify query nếu đã cài
- Edit tool bug workaround: dùng Python script + PYTHONIOENCODING=utf-8 thay vì Edit tool

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: Tất cả 6 đề xuất GX-1 đến GX-6 đã áp dụng xong, không làm lại
- watch_out: Edit tool không ghi vào disk trên branch này — dùng Python script + PYTHONIOENCODING=utf-8
- next_inputs: Bước tiếp theo (STEP-3.3) là xin user xác nhận merge nhánh research/gitnexus-2026-08-04 về main

## Commit
- Hash: [điền sau khi commit]
- Đã push: [có/không]

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
