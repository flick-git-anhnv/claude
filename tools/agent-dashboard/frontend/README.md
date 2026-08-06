# Agent Dashboard — Frontend

Dashboard web local theo dõi Claude Code agents (Vite + React 18 + TypeScript + Tailwind + Recharts).

## Cài đặt

```bash
cd tools/agent-dashboard/frontend
npm install
```

## Chạy dev (mock mode — không cần backend)

```bash
npm run dev
# Mở http://localhost:5173
# VITE_MOCK=true được set trong .env.development → dùng mock data tự động
```

## Build production (backend serve)

```bash
npm run build
# Output: tools/agent-dashboard/dist/
# Backend FastAPI mount StaticFiles(directory="../dist", html=True)
```

## Tech stack

| Thư viện | Version | Mục đích |
|----------|---------|----------|
| React | 18.3+ | UI framework |
| Vite | 5.3+ | Build tool + HMR |
| TypeScript | 5.5+ | Type safety |
| Tailwind CSS | 3.4+ | Styling với brand KZTEK tokens |
| Recharts | 2.12+ | Bar chart Token Analytics |
| React Router | 6.24+ | Client-side routing (HashRouter) |

## Cấu trúc

```
src/
├── types/index.ts          — TypeScript types toàn bộ domain
├── state/wsReducer.ts      — WS state machine (snapshot + delta)
├── styles/tokens.css       — CSS variables + Tailwind base
├── api/
│   ├── mockData.ts         — Mock data (sessions, accounts, tokens)
│   └── interceptor.ts      — Fetch interceptor cho VITE_MOCK mode
├── mocks/
│   └── mockWebSocket.ts    — MockWebSocket (snapshot khi connect, delta mỗi 4s)
├── contexts/
│   ├── WsContext.tsx       — WS connection + state provider
│   └── ToastContext.tsx    — Global toast notifications
├── hooks/
│   └── useApi.ts           — REST API calls (fetch wrapper)
├── utils/format.ts         — Formatting helpers
├── components/
│   ├── layout/             — AppHeader, SidebarNav, WebSocketStatus
│   ├── agents/             — AgentCard, AgentStatusPanel
│   ├── tokens/             — TokenBarChart, SummaryCard, FilterBar
│   ├── sessions/           — SessionTable
│   ├── accounts/           — AccountCard, AddAccountPanel, ConfirmDialog
│   └── common/             — BannerAlert, ToastNotification
└── pages/                  — AgentStatusPage, TokenAnalyticsPage,
                              SessionHistoryPage, AccountManagerPage
```

## Routes (HashRouter)

| Route | Trang |
|-------|-------|
| `/#/agents` | Agent Status Panel (mặc định) |
| `/#/tokens` | Token Analytics |
| `/#/sessions` | Session History |
| `/#/accounts` | Account Manager |

## Mock mode

- `VITE_MOCK=true` (set trong `.env.development`) → interceptor thay thế mọi `/api/*` fetch bằng mock data
- `MockWebSocket` gửi `snapshot` ngay khi kết nối, sau đó `delta` mỗi 4 giây
- Mock accounts state: có 3 tài khoản (1 active), có thể thêm/xóa/đổi active tạm thời trong session

## Kết nối backend thật

Khi backend FastAPI đang chạy tại `localhost:7770`:
1. Đổi hoặc xóa `.env.development` (hoặc set `VITE_MOCK=false`)
2. `npm run dev` — Vite proxy `/api/*` và `/ws` về `:7770` tự động

## Brand KZTEK

Tailwind custom colors: `kz-navy` (#251C53), `kz-orange` (#F05922), `kz-navy-mid` (#4A3F8C), `kz-navy-light` (#B8B3D6), `kz-orange-light` (#FFAA80), `kz-green` (#22C55E), `kz-red` (#EF4444).
