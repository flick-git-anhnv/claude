---
step: "0.3"
title: "UI/UX Designer — Wireframe/Mockup: 4 component Auto-Failover UI"
agent: ui-ux-designer
status: done
completed_at: "2026-08-09 22:32"
deps: ["0.2"]
---

# STEP 0.3 — UI/UX Designer: Thiết kế 4 Component Auto-Failover UI

## Nhiệm vụ

Thiết kế (text spec + mermaid, không cần ảnh mockup) 4 component UI bổ sung vào Account Manager đã có (Sprint 6), bám sát US-004, US-005, US-007. Không thiết kế lại màn hình.

## Đã làm

- Đọc US-001..007 đầy đủ (`docs/user-stories/US-agent-dashboard-autofailover.md`).
- Đọc Handoff Payload từ STEP-0.2 (BA) — xác nhận 4 component cần design.
- Đọc code frontend hiện tại:
  - `AccountCard.tsx` — badge pattern (ACTIVE: `bg-kz-orange`, OAuth: `bg-kz-navy`), layout flex, UsageBar integration.
  - `ToastNotification.tsx` — fixed bottom-right, dùng ToastContext.
  - `BannerAlert.tsx` — warning/error banner đã có, có type `'warning'` với `bg-kz-warning-bg`.
  - `tailwind.config.js` — xác nhận token: `kz-navy`, `kz-orange`, `kz-navy-mid`, `kz-navy-light`, `kz-orange-light`, `kz-gray`, `kz-warning-bg`, `kz-error-bg`.
- Đọc `.claude/commands/kztek-brand-info.md` — xác nhận Navy #251C53 (text/heading), Cam #F05922 (CTA/accent).
- Thiết kế 4 component:
  1. Badge "FAILOVER ACTIVE" trên AccountCard + Toast notification header-level (US-004, US-007)
  2. Failover Chain Config — tab mới với ordered list + nút ▲/▼ + checkbox (US-005)
  3. Failover Log View — tab mới với table + filter ngày + realtime WebSocket update (US-003, US-007)
  4. Wait-and-Retry Countdown Banner — global, dưới AppHeader, visible từ mọi tab (US-006, US-004)
- Thiết kế tab bar 3 tab mới cho Account Manager: "Danh sách Account" | "Failover Chain" | "Failover Log"
- Viết Hand-off spec cho Senior Developer (backend API + WebSocket events) và Junior Developer (4 React component props/states).
- Viết mermaid: (1) luồng UI tổng thể failover → badge → toast → log, (2) sơ đồ thay đổi Account Manager trước/sau.
- Kiểm tra checklist brand KZTEK: Navy/Cam đúng vị trí, không dùng màu đỏ tươi làm accent chính.
- Xuất DOCX: thành công. PDF: thất bại RPC Windows (lỗi đã biết, không block).

## Artifact

- `docs/design/DESIGN-agent-dashboard-autofailover.md` — Design spec source Markdown ✅
- `docs/design/DESIGN-agent-dashboard-autofailover.docx` — Word document (KZTEK brand) ✅
- `docs/design/DESIGN-agent-dashboard-autofailover.pdf` — ⚠️ thất bại RPC Windows (DOCX đã có, không block)

## Quyết định thiết kế quan trọng

1. **Không dùng drag-and-drop (react-dnd/dnd-kit):** Failover chain config chỉ cần nút ▲/▼ đơn giản — tránh thêm dependency nặng cho chức năng nhỏ (chỉ ~2-3 account).
2. **Tab bar mới cho Account Manager:** Thêm tab "Failover Chain" và "Failover Log" vào Account Manager section thay vì tạo trang riêng — giữ ngữ cảnh quản lý account gần nhau.
3. **Wait-and-Retry Banner đặt dưới AppHeader (không phải trong Account Manager):** Do BR12 yêu cầu indicator visible từ mọi tab. Banner full-width, đẩy nội dung xuống (không overlay/fixed) để không che content.
4. **Badge FAILOVER ACTIVE tự ẩn sau 30s:** Đúng per US-004 Scenario 1. Tái dùng màu `bg-kz-orange text-white` từ ACTIVE badge — người dùng đã quen màu cam = trạng thái active/quan trọng.
5. **Toast variant `'failover'` màu cam:** Phân biệt với success toast (navy) hiện tại — người dùng nhận ra ngay khi failover xảy ra. Min 15s hiển thị (per BR21 tối thiểu 10s).
6. **Reuse `BannerAlert` pattern:** Nội dung warning được mở rộng từ `BannerAlert` hiện tại thay vì tạo component mới — giảm code mới cần viết.
7. **Realtime WebSocket cho log table:** New event từ backend push thẳng vào đầu bảng với `animate-fade-in` — không cần user refresh tab.

## Handoff Payload — bước sau đọc phần này

- **do_not_redo:**
  - KHÔNG thiết kế thêm màn hình mới — chỉ 4 component bổ sung vào Account Manager đã có.
  - KHÔNG dùng drag-and-drop library — nút ▲/▼ HTML thuần là quyết định cuối.
  - KHÔNG dùng màu đỏ tươi làm accent — Cam #F05922 là màu cảnh báo/attention của KZTEK.
  - KHÔNG cross-provider UI (Gemini/OpenAI) — đã chốt ở scope v2.3.

- **watch_out:**
  - **Bước tiếp theo là Engineering Manager (0.4):** Cần estimate effort cho 4 component frontend + API backend + WebSocket events mới. Backend phức tạp hơn UI: failover engine, DB schema mới (failover_events), 5 API endpoints mới, 5 WebSocket event types mới.
  - **Junior Developer (Phase 4.2) sẽ code frontend:** Design spec có Hand-off section chi tiết với props/states cho 4 React component — đọc mục "Hand-off cho Junior Developer" trong DESIGN file.
  - **Senior Developer (Phase 4.1) sẽ code backend:** Design spec có Hand-off section với API mới + WebSocket events mới — đọc mục "Hand-off cho Senior Developer".
  - **Tab bar là component mới hoàn toàn:** Account Manager hiện tại không có tab — Junior Dev cần tạo tab bar từ đầu theo spec (3 tab: Danh sách Account, Failover Chain, Failover Log).
  - **`ToastContext` cần mở rộng:** Cần thêm variant `'failover'` (màu cam) và `'failover-error'` (màu đỏ, không auto-dismiss) vào ToastContext/ToastNotification hiện tại.
  - **`BannerAlert` cần mở rộng:** Thêm hỗ trợ countdown timer (HH:MM:SS) và state machine (counting/retrying/retry_failed/exhausted_all_retries) — hoặc tạo `WaitRetryBanner` component riêng.

- **next_inputs:**
  - Design spec đầy đủ: `docs/design/DESIGN-agent-dashboard-autofailover.md`
  - Key items Engineering Manager cần estimate:
    - **Backend:** Failover engine service, 5 API endpoints mới (`/api/failover/status|log|chain`), 5 WebSocket event types, DB migration (bảng `failover_events`), hot-swap logic < 100ms, wait-and-retry scheduler.
    - **Frontend:** Tab bar (mới), `FailoverStatusBadge`, `FailoverChainConfig`, `FailoverLogTable`, `WaitRetryBanner`, mở rộng `ToastContext` (1 variant mới).
    - **QA:** Cần simulate 429, simulate quota 100%, test realtime WebSocket, test countdown timer accuracy.
  - US file: `docs/user-stories/US-agent-dashboard-autofailover.md` — đặc biệt US-004, US-005, US-006, US-007 cho estimate UI effort.
