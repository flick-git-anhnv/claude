---
step: 6.2
plan: ../PLAN-MASTER.md
agent: UI/UX Designer
status: done
completed_at: 2026-08-06 11:45
deps: ["6.1"]
---

# STEP 6.2 — Wireframe Pipeline View (FR-001, FR-002, FR-003)

## Input nhận
- TDD §24–26 (FR-003 session title, FR-002 % context, FR-001 chain endpoint schema).
- TDD §28.1 Handoff Payload từ Tech Lead (chain = 1 session cha, max 15+ steps, Cam #F05922 active).
- `docs/design/DESIGN-agent-dashboard.md` v1.0 (brand KZTEK, component library hiện có).

## Nhiệm vụ
Thiết kế wireframe cho PipelineCard (FR-001) + cập nhật SessionCard v2 với title (FR-003) và %context badge (FR-002). Lưu vào cuối `docs/design/DESIGN-agent-dashboard.md`.

## Đã làm

**Thiết kế chính:**

1. **SessionCard v2** — giữ nguyên layout v1, bổ sung:
   - Dòng tiêu đề session (FR-003): `ai_title` → user text → session_id.slice(0,8). Style 13px `#4A3F8C`.
   - ContextBadge (FR-002): progress bar 48×8px ở cuối hàng token. Màu theo ngưỡng: 0–70% navy #4A3F8C, 70–90% cam nhạt #FFAA80, >90% đỏ #EF4444. Ẩn khi context_pct=0.

2. **PipelineCard** (FR-001) — block mới bên dưới token row, chỉ render khi `steps.length > 0`:
   - Background `#FAFAFA`, border-top 1px `#CBCBCB`.
   - Header row: icon chain + "Pipeline [N bước]" caption.
   - Stations hàng ngang: `overflow-x: auto`, `white-space: nowrap`, scrollbar 4px.
   - **Done station:** 96×80px, bg `#F5F5F5`, opacity 0.65, ✓ icon, role name 11px, description 10px truncate 2 dòng. Hover: opacity 1, box-shadow nhẹ, tooltip description đầy đủ.
   - **Active station:** 164×80px (wider), bg `rgba(#FFAA80, 0.12)`, border-left 4px `#F05922`, animated pulse dot, role name 13px bold `#251C53`, description 12px max 3 dòng.
   - Connector: `──▶` 20px, màu `#CBCBCB`.

3. **Xử lý chain dài (10–20+ bước):**
   - Auto-scroll to active station khi component mount/update (`scrollIntoView inline: 'end'`).
   - Fade gradient phải (pseudo `::after`, 32px, transparent→#FAFAFA) gợi ý scroll.
   - Header luôn hiển thị count "[N bước]" để user biết không cần scroll hết.
   - Done station compact 96px (hover expand +16px với transition 150ms).

4. **Session đơn (không có chain):** render SessionCard v1 bình thường — không có PipelineCard block.

5. **PipelineCard DONE:** opacity 0.6 toàn container, header "🔗 Pipeline [N bước — kết thúc]", tất cả stations = done.

**Quyết định UX quan trọng:**
- Scroll ngang thay vì ẩn/collapse bước — transparency toàn bộ workflow đã qua.
- PipelineCard KHÔNG replace SessionCard header — pipeline là thông tin phụ trợ.
- Active station LUÔN là bước cuối (TDD §26.4) — không cần logic "jump" giữa chain.
- ContextBadge ẩn khi pct=0 — tránh "0%" gây nhầm lẫn khi session mới bắt đầu.

## Artifact
- `docs/design/DESIGN-agent-dashboard.md` — Section "Sprint 3" appended (FR-001, FR-002, FR-003 specs).
- `docs/design/DESIGN-agent-dashboard.docx` + `.pdf` — xuất lại bằng md_to_docx_kztek.py.

## Quyết định quan trọng
1. Station height đồng nhất 80px cho cả done và active — tránh layout shift khi active thay đổi.
2. Done station opacity 0.65 (không phải 0.5) — vẫn đọc được role name không cần hover.
3. Auto-scroll là UX pattern quan trọng nhất cho chain dài — implement ngay từ đầu, không phải cải tiến sau.

## Handoff Payload — bước sau đọc phần này

- **do_not_redo:** Quyết định scroll ngang (không ẩn bước), active luôn ở cuối, station height 80px đồng nhất, pipeline nằm TRONG SessionCard (không phải trang riêng).
- **watch_out:**
  1. Active station width 164px (rộng hơn done 96px) — container cần `display: flex`, `align-items: center` (không `align-items: stretch`). Vertical alignment là center.
  2. Fade gradient `::after` cần `pointer-events: none` để không chặn click vào station cuối.
  3. Auto-scroll: gọi `scrollIntoView` SAU khi DOM đã render xong (`useEffect` với deps `[steps]`).
  4. ContextBadge ẩn khi `context_pct === 0` (không phải `context_pct == null`): check `context_pct > 0`.
  5. Session title fallback: KHÔNG render dòng tiêu đề nếu title===null; KHÔNG hiển thị chữ "null".
  6. PipelineCard chỉ render khi `steps.length > 0` — check trước khi fetch endpoint.
  7. Skeleton loading: 3 pill placeholder pulse — chỉ show khi đang fetch, không khi empty.
- **next_inputs:**
  - `docs/design/DESIGN-agent-dashboard.md` §Sprint 3 — spec đầy đủ component + tokens + states.
  - TDD §25.4 (context_pct field schema), TDD §26.3 (steps array schema).
  - Modules frontend cần sửa/tạo: `SessionCard.tsx` (add title + ContextBadge), `PipelineCard.tsx` (new), `StepStation.tsx` (new), `ContextBadge.tsx` (new).
  - JD (Bước 6.4) có thể prep `useChain(sessionId)` hook trước khi implement UI; UI chờ file này.

## Commit
- Hash: [điền sau commit]
- Đã push: [điền sau commit]

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
