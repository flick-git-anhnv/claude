---
step: "8.2"
plan: ../PLAN-MASTER.md
agent: ui-ux-designer
status: done
completed_at: "2026-08-07 08:24"
deps: ["8.1"]
---

# STEP 8.2 — UX/UI Design Sprint 5: Wireframe FR-004 (Dispatcher Node) + FR-005 (Toggle 2 chế độ Pipeline)

## Input nhận
- TDD §29–35 (Sprint 5 ADDENDUM): schema `is_dispatcher`, endpoint `/api/accounts/{id}/usage`, toggle localStorage `pipelineMode`, endpoint `/api/pipeline/aggregate`
- TDD §35.1 Handoff Payload → UX Designer: do_not_redo + watch_out (màu, size, usage bar 2 dòng, aggregate có thể > 50 entry)
- Design spec hiện tại: `docs/design/DESIGN-agent-dashboard.md` (Sprint 3 wireframe đã append)
- Component hiện tại: `AgentRosterItem.tsx` (196×100px grid, ACTIVE/DONE styles), `AppHeader.tsx` (height 56px), `AccountCard.tsx`
- Brand KZTEK: Navy #251C53, Cam #F05922, không dùng đỏ tươi

## Nhiệm vụ
Thiết kế wireframe + design spec cho Sprint 5:
- **Phần A:** UsageBar (Session 5hr + Weekly 7day) tại AppHeader và AccountCard
- **Phần C:** Node "Claude (Dispatcher)" — style Navy đặc biệt, luôn đầu roster
- **Phần D:** Toggle 2 chế độ Pipeline + AggregatePipelineView (table)
- **BUG-005:** Rule nút "Xem lịch sử"

## Đã làm

1. **Đọc TDD §29–35** — nắm đầy đủ API contract: `UsageInfo` (five_hour_pct/seven_day_pct/resets_at), Dispatcher entry (`is_dispatcher`, `history=[]`, `call_count=1`), aggregate roster schema, toggle localStorage.

2. **Đọc AppHeader.tsx + AccountCard.tsx + AgentRosterItem.tsx** — xác định điểm chèn UsageBar, kích thước card 196×100px, logic `hasHistory = call_count > 1` (BUG-005 root).

3. **Thiết kế Phần A (Usage Bars):**
   - AppHeader: height 56→80px, 2 UsageBar mỗi dòng 1 bar (5h + 7d), màu theo ngưỡng (<80% xanh, ≥80% cam)
   - AccountCard: section Quota sau OAuth badges, lazy fetch IntersectionObserver, ẩn với API key account
   - Component `UsageBar` spec với props (`label`, `pct`, `resetsAt`, `onHeader`, `loading`)

4. **Thiết kế Phần C (Dispatcher Node):**
   - Style: bg #251C53, text white, border 4px #251C53 — phân biệt rõ với subagent cam
   - Icon 🧠 tĩnh (không pulse) — Dispatcher là phiên gốc, không phải agent được gọi
   - Không có nút "Xem lịch sử" (`is_dispatcher` check)
   - Edge cases: session đơn độc, tokens=0 ẩn dòng (khác BUG-004 subagent)

5. **Thiết kế Phần D (Toggle + Aggregate View):**
   - Toggle: Segmented Control 2 button, inline với page title, height 32px, Navy active
   - AggregatePipelineView: table layout (không phải card grid), sort call_count DESC
   - Filter: search text + dropdown thời gian (7/30/90 ngày / all-time)
   - Active row: viền trái 3px cam + text "N đang chạy" (không pulse — thống nhất UX)
   - Không phân trang (estimate ≤ 30 role unique)

6. **Thiết kế BUG-005 rule:**
   - Điều kiện mới: `!entry.is_dispatcher && entry.call_count >= 1`
   - Fix BUG-005 (>= 1) đồng thời loại Dispatcher (is_dispatcher check)

7. **Append DESIGN file** — section "Sprint 5" vào `docs/design/DESIGN-agent-dashboard.md` (bảng tổng quan + ASCII wireframe + design tokens + accessibility + quyết định UX)

8. **Xuất DOCX** — `python -X utf8 scripts/md_to_docx_kztek.py docs/design/DESIGN-agent-dashboard.md` → DOCX OK, PDF fail RPC (non-blocking)

## Artifact
- `docs/design/DESIGN-agent-dashboard.md` — section Sprint 5 appended (~250 dòng: Phần A/B/C/D + BUG-005 + tokens + accessibility + quyết định UX)
- `docs/design/DESIGN-agent-dashboard.docx` — xuất OK

## Quyết định quan trọng

| Câu hỏi | Quyết định |
|---------|-----------|
| Header height sau thêm usage bars | 56px → 80px (2 bars + reset text cần chỗ) |
| Màu cảnh báo usage cao | Cam #F05922 (≥80%), không dùng đỏ tươi |
| Dispatcher icon | 🧠 tĩnh (không pulse cam) — tránh nhầm với subagent active |
| Aggregate: table hay grid? | Table — dễ so sánh số liệu |
| Aggregate: phân trang? | Không — scroll tự nhiên (≤ 30 role) |
| BUG-005 condition | `!is_dispatcher && call_count >= 1` (gộp cả 2 fix) |
| Dispatcher tokens=0 | Ẩn dòng (khác BUG-004 subagent — không hiện "— tokens") |

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")

- **do_not_redo:** Header height 56→80px đã chốt; toggle vị trí đầu AgentStatusPage inline với title đã chốt; Dispatcher style Navy bg #251C53 (không phải cam) đã chốt; BUG-005 condition `!is_dispatcher && call_count >= 1` đã chốt.
- **watch_out:**
  1. UsageBar trên header: track bg là `rgba(255,255,255,0.2)` (nền navy tối) — khác trong card là `rgba(203,203,203,0.4)` (nền trắng).
  2. Dispatcher node: `history=[]` theo backend — không expect key thiếu, phải là empty array; `call_count=1` — không gọi API lấy history.
  3. BUG-005: điều kiện `!entry.is_dispatcher && entry.call_count >= 1` — áp dụng CẢ 2 branch (ACTIVE lẫn DONE) trong AgentRosterItem.
  4. `active_now > 0` trong aggregate: viền trái 3px cam + text "N đang chạy" — KHÔNG pulse animation.
  5. API key account (not OAuth): ẩn toàn bộ Usage section — không render skeleton hay "—".
  6. Aggregate polling: 30s (không phải 60s như usage bars AppHeader).
- **next_inputs:**
  - `docs/design/DESIGN-agent-dashboard.md` — section Sprint 5 (Phần A/C/D + BUG-005)
  - Design tokens mới: `--header-height: 80px`, màu dispatcher, màu usage bars
  - File cần edit: `AppHeader.tsx`, `AccountCard.tsx`, `AgentRosterItem.tsx` (3 file edit)
  - File cần tạo mới: `UsageBar.tsx`, `AggregatePipelineView.tsx`, `hooks/usePipelineMode.ts`
  - Artifact từ SD (Bước 8.3): cần schema thực tế của `UsageInfo` + endpoint `/api/accounts/{id}/usage` trước khi JD code UsageBar (xem TDD §30.3)

## Commit
- Hash: c069b5c
- Đã push: không

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
