---
step: 4.2
agent: junior-developer
status: done
created: 2026-08-10
completed_at: 2026-08-10 09:00
---

# Bước 4.2 — Junior Developer: Frontend Auto-Failover UI

## Nhiệm vụ

Implement toàn bộ frontend Sprint 7 (S7-T21..T27) cho tính năng Auto-Failover Anthropic.

## Đã làm

### File mới tạo

| File | Mô tả |
|------|-------|
| `src/components/accounts/failover/FailoverChainConfig.tsx` | Tab "Failover Chain": ordered list priority, checkbox include/exclude (block last), ▲/▼ reorder, PUT /api/failover/chain |
| `src/components/accounts/failover/FailoverLogTable.tsx` | Tab "Failover Log": table Navy header, date range filter, WS realtime (watch failoverCount24h), skeleton/empty/pagination 20/page |
| `src/components/common/WaitRetryBanner.tsx` | Banner full-width dưới AppHeader (không overlay), 5 states, countdown mono font, nút Hủy auto-retry, role="alert" |
| `src/components/common/FailoverToastBridge.tsx` | Null-rendered bridge: watch failoverToastNonce → gọi showFailoverToast |
| `src/state/wsReducer.test.ts` | 17 unit tests cho failover reducer state machine |
| `src/components/common/WaitRetryBanner.test.ts` | 8 unit tests cho formatCountdown |

### File sửa đổi

| File | Thay đổi |
|------|----------|
| `src/pages/AccountManagerPage.tsx` | Thêm tab bar 3 tab (Danh sách / Failover Chain / Failover Log), lazy-render tab content |
| `src/components/accounts/AccountCard.tsx` | Tích hợp FailoverStatusBadge: badge FAILOVER ACTIVE (30s auto-hide) + EXHAUSTED |
| `src/App.tsx` | Thêm WaitRetryBanner (dưới AppHeader) + FailoverToastBridge |
| `src/api/interceptor.ts` | Mock endpoints: GET/PUT /api/failover/chain, GET /api/failover/log, GET /api/failover/status, POST /api/failover/cancel-retry |
| `src/styles/tokens.css` | Thêm `@keyframes fadeIn` + `.animate-fade-in` |

### Đã confirm không làm lại (đã có sẵn từ agent trước)

- `FailoverStatusBadge.tsx` — đầy đủ, tái dùng nguyên vẹn
- `wsReducer.ts` — Sprint 7 failover events đã xử lý đầy đủ
- `ToastContext.tsx` — `failover` + `failover-error` variant có sẵn
- `types/index.ts` — `FailoverChainItem`, `FailoverEvent`, `FailoverLogResponse` đã định nghĩa

## Kết quả verification

```
npx tsc -b          → 0 lỗi compile
npx vitest run      → 48/48 tests pass (23 cũ + 17 wsReducer + 8 WaitRetryBanner)
npm run build       → ✓ built in 5.70s (0 lỗi, 1 warning chunk size thông thường)
```

## Quyết định kỹ thuật

- Tab content lazy-render: `{activeTab === 'chain' && <FailoverChainConfig />}` — tránh fetch /api/failover/chain khi user chưa vào tab
- WaitRetryBanner dùng `shrink-0` để không bị co lại trong flex layout
- `formatCountdown` được export riêng để unit test được trong môi trường `node`
- FailoverToastBridge: dùng `useRef` lưu prevNonce để không trigger toast khi mount lần đầu
- moveUp/moveDown trong FailoverChainConfig: swap priority values VÀ swap vị trí array để UI hiển thị đúng ngay lập tức (optimistic update)

## Handoff Payload — bước sau đọc phần này

- do_not_redo: Toàn bộ các file kể trên đã hoàn thành. Không viết lại FailoverStatusBadge, wsReducer failover events, ToastContext.
- watch_out: Tab content dùng `hidden` attribute (không unmount) ngoại trừ FailoverChainConfig và FailoverLogTable dùng conditional render (`{activeTab === 'chain' && ...}`) để tránh unnecessary API calls. Backend failover/status endpoint trả `state: "waiting"` khi đang trong trạng thái chờ retry — WaitRetryBanner sẽ hiển thị ngay.
- next_inputs: Bước 4.3 (Tech Lead review): xem `src/components/accounts/failover/`, `src/components/common/WaitRetryBanner.tsx`, `src/App.tsx`. Security audit STRIDE bắt buộc theo PLAN-MASTER do đụng credential swap tự động (backend, không phải frontend). Frontend không lưu credential, chỉ hiển thị trạng thái.
