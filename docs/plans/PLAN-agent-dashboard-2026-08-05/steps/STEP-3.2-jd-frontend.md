---
step: "3.2"
plan: ../PLAN-MASTER.md
agent: junior-developer
status: done
completed_at: 2026-08-05 23:59
deps: ["2.1"]
---

# STEP 3.2 — JD: Code Frontend

## Input nhận
Output từ Bước 2.1 (TL): `docs/tech-design/TDD-agent-dashboard.md` — tech stack, API contract, WebSocket events, task breakdown JD.
Output từ Bước 1.3 (UX): `docs/design/DESIGN-agent-dashboard.md` — wireframe, component list, brand colors.

## Nhiệm vụ
Implement frontend dashboard theo design spec và TDD: Agent Live View (hiển thị agent đang chạy realtime qua WebSocket), Session History (danh sách session đã kết thúc), Token Usage Chart (biểu đồ xu hướng từ SQLite), và Account Switcher.

## Definition of Done
- [ ] `src/agent-dashboard/frontend/` tạo đủ:
  - [ ] Agent Live View: connect WebSocket, hiển thị AgentCard realtime (agent name, status, current task, token count live update)
  - [ ] Session History: fetch REST GET /sessions/history, hiển thị danh sách session theo ngày, có lọc theo date range
  - [ ] Token Usage Chart: hiển thị biểu đồ đường/cột token usage theo ngày/tuần/tháng (dùng Chart.js hoặc lightweight lib)
  - [ ] Account Switcher: dropdown/modal để xem danh sách account, chọn account active, thêm/xóa account
  - [ ] WebSocket reconnect tự động khi mất kết nối + hiển thị trạng thái connection
  - [ ] Empty state rõ ràng khi không có session/data
  - [ ] Màu sắc/style theo brand KZTEK (Navy #251C53, Cam #F05922)
- [ ] Responsive cơ bản (hoạt động tốt trên màn hình desktop 1080p+)
- [ ] Chạy pre-coding-check trước khi code
- [ ] Chạy `/verify-pr` và đính kèm VERIFICATION REPORT vào PR description trước khi chuyển TL review

## Đã làm
- Scaffold `tools/agent-dashboard/frontend/` hoàn toàn mới: Vite 5 + React 18 + TypeScript 5.5 + Tailwind 3.4 + Recharts 2.12 + React Router 6.24 (HashRouter)
- Tạo 44 file source (xem danh sách Artifact bên dưới)
- Mock mode tự động qua `VITE_MOCK=true` trong `.env.development`: fetch interceptor thay thế mọi `/api/*` call, MockWebSocket gửi snapshot khi connect + delta mỗi 4s
- Fix lỗi TypeScript `import.meta.env` bằng cách tạo `src/vite-env.d.ts` với `/// <reference types="vite/client" />`
- Fix lỗi type inference complex trong WsContext.tsx bằng explicit casts (`msg.payload as WsSnapshot`, `msg.payload as DeltaEvent`)
- Verify build: `tsc -b` → 0 errors, `vite build` → 858 modules, 573KB JS, built in 6.31s ✅

## Artifact
- `tools/agent-dashboard/frontend/` — toàn bộ project frontend (44 file, commit `b868513`)
  - `package.json`, `vite.config.ts`, `tailwind.config.js`, `tsconfig*.json`
  - `.env.development` — `VITE_MOCK=true`
  - `src/types/index.ts` — TypeScript types toàn bộ domain (Session, Account, WsMessage, WsAction...)
  - `src/state/wsReducer.ts` — WS state machine (initialWsState, applyDelta, wsReducer)
  - `src/api/mockData.ts` — 6 mock sessions, 35 mock history, 3 mock accounts, getMockTokenSummary
  - `src/api/interceptor.ts` — fetch interceptor mock cho /api/* (8 endpoints)
  - `src/mocks/mockWebSocket.ts` — MockWebSocket: snapshot khi open, delta mỗi 4s, pong handler
  - `src/contexts/WsContext.tsx` — WS lifecycle + reconnect backoff + dispatch API
  - `src/contexts/ToastContext.tsx` — global toast notifications
  - `src/hooks/useApi.ts` — 8 REST API functions (apiFetch wrapper)
  - `src/utils/format.ts` — fmtNum, fmtDate, fmtMs helpers
  - `src/styles/tokens.css` — CSS variables + Tailwind @layer base
  - 13 components (layout/agents/tokens/sessions/accounts/common)
  - 4 pages (AgentStatusPage, TokenAnalyticsPage, SessionHistoryPage, AccountManagerPage)
  - `src/App.tsx`, `src/main.tsx`, `src/vite-env.d.ts`

## Quyết định quan trọng
1. **Fetch interceptor thay vì MSW**: MSW yêu cầu chạy `npx msw init public/` để generate service worker. Dùng `window.fetch = mockFetch` đơn giản hơn, không cần setup.
2. **MockWebSocket extends EventTarget**: Cho phép browser gắn event listener như WebSocket thật, không cần thư viện.
3. **HashRouter (không dùng BrowserRouter)**: Local-only tool, không có server-side routing. Hash URL (`/#/agents`) tin cậy hơn khi serve static files.
4. **Account change dispatch vào WsContext**: Khi activate account mới ở AccountManagerPage, dispatch DELTA `account_changed` để AppHeader cập nhật ngay mà không cần reload.
5. **`VITE_MOCK=true` mặc định dev**: Khi backend thật sẵn sàng, chỉ cần set `VITE_MOCK=false` hoặc xóa `.env.development`, Vite proxy `/api/*` và `/ws` tự chuyển về `:7770`.

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: Toàn bộ 44 file frontend đã tạo xong và build verified (commit `b868513`). Không tạo lại project từ đầu.
- watch_out: (1) `src/vite-env.d.ts` bắt buộc có để TypeScript nhận `import.meta.env` — nếu thiếu sẽ lỗi TS2339. (2) Mock interceptor dùng in-memory state nên reset mỗi lần F5. (3) `VITE_MOCK=true` trong `.env.development` — khi kết nối backend thật phải đổi sang `false`. (4) ChunkWarning (>500KB) là bình thường với recharts+react-router bundled, không phải lỗi — chỉ fix nếu performance thực sự vấn đề. (5) Clipboard API cần HTTPS hoặc localhost — không hoạt động nếu serve qua IP LAN (đã có lesson `vite-dev-server-localhost-only-lan-unreachable.md`).
- next_inputs: (a) `tools/agent-dashboard/frontend/` — source frontend để review, (b) Build output tại `tools/agent-dashboard/dist/` (chạy `npm run build` trong frontend/ để tạo), (c) Backend code tại `tools/agent-dashboard/` từ Bước 3.1 (commit `fecd37d`), (d) TDD tại `docs/tech-design/TDD-agent-dashboard.md` để đối chiếu API contract.

## Commit
- Hash: b868513
- Đã push: không (chờ TL review)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
