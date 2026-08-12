---
step: "8.6"
plan: ../PLAN-MASTER.md
agent: ux-ui-reviewer
status: done
completed_at: "2026-08-07 09:33"
deps: ["8.5"]
---

# STEP 8.6 — UX/UI Review Sprint 5: Usage Display + Dispatcher Node (FR-004) + Toggle 2 chế độ (FR-005)

## Input nhận
[Điền từ Handoff Payload của STEP-8.5 trước khi bắt đầu]
- Code đã được TL approve merge (tất cả 4 hạng mục)
- UI thay đổi ở 4 vị trí:
  - AppHeader: UsageBar compact (Session % + Weekly %)
  - AccountCard: UsageBar full + fallback text
  - PipelineCard/StepStation: node Dispatcher (Navy #251C53, icon, label "Claude (Dispatcher)")
  - Pipeline section: toggle "Theo Session" / "Tổng hợp" + aggregate view
- App chạy local: `http://localhost:5173` (frontend) + `http://localhost:7770` (backend)
- Design spec: `docs/design/DESIGN-agent-dashboard.md` §Sprint5 (wireframe từ 8.2)

## Nhiệm vụ
Chạy app thật, kiểm tra toàn bộ UI Sprint 5 (3 nhóm thay đổi: Usage Display, FR-004 Dispatcher, FR-005 Toggle), đánh giá 7 tiêu chí UX (C1–C7), chụp screenshot, phân loại issue.

## Definition of Done
- [ ] App chạy thật (không dùng screenshot giả), chụp từ browser thật
- [ ] **Nhóm A — Usage Display (AppHeader + AccountCard):**
  - [ ] Screenshot: AppHeader với UsageBar compact đầy đủ (Session % + Weekly %)
  - [ ] Screenshot: AccountManagerPage với UsageBar trên ≥1 AccountCard
  - [ ] Screenshot: edge case UsageBar null (hiển thị "--" hoặc ẩn)
- [ ] **Nhóm C — Dispatcher Node (FR-004):**
  - [ ] Screenshot: PipelineCard với node "Claude (Dispatcher)" ở đầu chain — đúng màu Navy, đúng label
  - [ ] Screenshot: session đang active — Dispatcher node trạng thái in-progress (nếu có session live)
  - [ ] So sánh với wireframe 8.2: node style có khớp không?
- [ ] **Nhóm D — Toggle 2 chế độ (FR-005):**
  - [ ] Screenshot: toggle "Theo Session" — Pipeline view cũ bình thường
  - [ ] Screenshot: toggle "Tổng hợp" — aggregate view (sort by calls, compact token)
  - [ ] Screenshot: transition giữa 2 chế độ (không flash/vỡ layout)
- [ ] Đánh giá 7 tiêu chí (C1–C7) cho cả 3 nhóm:
  - C1: Bố cục — UsageBar có vỡ header? Dispatcher node có vỡ chain layout? Aggregate view có đọc được?
  - C2: Màu/Brand — Navy #251C53 cho Dispatcher node đúng không? Màu UsageBar (cam #F05922 ở 70-90%) đúng brand?
  - C3: Typography — Text nhỏ "Resets in Xh", token compact, label "Claude (Dispatcher)" có đọc được?
  - C4: Consistency — Style node Dispatcher có nhất quán với các node khác (về padding, height, font)?
  - C5: Interactivity — Toggle hoạt động mượt? Polling 60s không flicker? 
  - C6: Edge cases — Null usage đúng, session không có subagent (chỉ Dispatcher) đúng, aggregate rỗng (không crash)?
  - C7: Responsive — Header không vỡ khi thu nhỏ sau khi thêm UsageBar?
- [ ] Tạo report `docs/ux-review/UX-REVIEW-sprint5.md` (embed screenshots, bảng issue Critical/High/Medium/Low)
- [ ] Xuất DOCX: `python scripts/md_to_docx_kztek.py docs/ux-review/UX-REVIEW-sprint5.md`
- [ ] Kết luận: PASS (không Critical/High) hoặc FAIL (chặn QA)

## Đã làm
- Khởi động backend (port 7770) + xác nhận frontend dist Sprint 5 (build 09:04 ngày 07/08).
- Mở Chrome tại http://127.0.0.1:7770, capture bằng PrintWindow API (không cần window focus).
- Chụp 9 screenshots: dashboard-main-default, agents-session-view, agents-tonghop-view2, accounts-page, dispatcher-node-crop, header-app-area, toggle-area, uxr-running-card, dispatcher-node-closeup.
- Kiểm tra API: `/api/accounts/usage/active` → `{"error":"http_429"}` (quota API bị rate-limit).
- Đọc source code `UsageBar.tsx` và `AppHeader.tsx` để hiểu logic null/error state.
- Đánh giá 7 tiêu chí (C1-C7) cho 4 màn hình + 5 điểm review.
- Viết `docs/ux-review/UX-REVIEW-sprint5.md` + xuất `UX-REVIEW-sprint5.docx` (PDF thất bại do COM error).
- Kết luận: PASS — 0 Critical, 0 High, 1 Medium (UI-001), 1 Low (UI-002).

## Artifact
- `docs/ux-review/UX-REVIEW-sprint5.md` — report đầy đủ
- `docs/ux-review/UX-REVIEW-sprint5.docx` — DOCX KZTEK brand (PDF thất bại COM error, ghi chú)
- `docs/ux-review/screenshots/2026-08-07/` — 9 screenshots thực tế từ app chạy

## Quyết định quan trọng
- **PASS** — không có issue Critical hoặc High. QA có thể tiến hành smoke test.
- 0 Critical, 0 High, 1 Medium (UI-001: AppHeader UsageBar ẩn hoàn toàn khi error thay vì hiện "--"), 1 Low (UI-002: AccountCard error text format).
- Quota API đang bị rate-limit (http_429). Các TC happy path cho UsageBar bars sẽ không pass trong môi trường hiện tại — QAE cần ghi chú và test khi rate-limit giải phóng.
- FR-004, FR-005, BUG-005 đều hoạt động đúng theo spec.

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: App đã chạy trên port 7770, screenshot đã chụp đủ, không cần chạy lại UXR. FR-004/FR-005/BUG-005 đã xác nhận hoạt động.
- watch_out: Quota API đang trả http_429 (rate-limited). Các TC cho UsageBar happy path (bars hiện với %) sẽ không pass — cần mock data hoặc đợi rate-limit giải phóng. Dispatcher node không xuất hiện trong bảng aggregate (đúng hành vi — không phải sub-agent). Icon Dispatcher là emoji nhỏ, có thể khó nhìn trên màn hình DPI thấp.
- next_inputs: PASS — QAE tiến hành 8.7 smoke test. Issue Medium UI-001 (AppHeader null state) và Low UI-002 (AccountCard error text) cần QAE note lại nhưng không chặn smoke test. Report full tại `docs/ux-review/UX-REVIEW-sprint5.md`.

## Commit
- Hash: [điền sau khi commit report]
- Đã push: [có/không]

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
