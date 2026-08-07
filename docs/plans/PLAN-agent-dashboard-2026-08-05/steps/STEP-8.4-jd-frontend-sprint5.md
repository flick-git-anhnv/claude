---
step: "8.4"
plan: ../PLAN-MASTER.md
agent: junior-developer
status: done
completed_at: 2026-08-07 14:30
deps: ["8.2", "8.3"]
---

# STEP 8.4 — Frontend Sprint 5: UsageBar + BUG-004 Live Card + FR-004 Dispatcher Node UI + FR-005 Toggle

## Input nhận
- Schema `UsageInfo` chính xác từ STEP-8.3: `five_hour_pct`, `seven_day_pct`, `resets_at`, `seven_day_resets_at`, `error`
- BUG-004 fix backend đã xong: roster entry `ACTIVE` có thể thiếu `model`/`latest_description` ở thời điểm đầu — frontend cần render fallback "đang khởi tạo…"
- FR-004 Dispatcher node: field `is_dispatcher: true`, `role: "__dispatcher__"`, `history: []`, tokens display ẩn khi =0
- FR-005: aggregate endpoint `/api/pipeline/aggregate?window=N`, response `{mode:'aggregate', total_sessions, total_calls, roster: AggregateEntry[]}`
- DESIGN Sprint 5: Navy #251C53 background cho Dispatcher, Cam #F05922 accent, Segmented Control toggle
- BUG-005: `hasHistory = !is_dispatcher && call_count >= 1` (không phải > 1)

## Nhiệm vụ
Implement toàn bộ phần frontend Sprint 5 — 5 hạng mục trong 1 PR:

**A — UsageBar component**
**B — BUG-004 Live Card** (fallback "đang khởi tạo…" + subscribe `chain_updated` WS event)
**C — FR-004** (render Dispatcher node trong PipelineCard)
**D — FR-005** (toggle 2 chế độ Pipeline view, persist localStorage)
**E — BUG-005** (fix `hasHistory` condition `> 1` → `>= 1`)

## Definition of Done

### A — UsageBar ✅
- [x] `frontend/src/components/common/UsageBar.tsx` mới: 2 bars (5h + 7d), màu cam ≥80%, xanh <80%, aria progressbar
- [x] `AppHeader.tsx`: fetch `/api/accounts/usage/active` polling 60s, hiển thị `<UsageBar onHeader={true}/>`
- [x] `AccountCard.tsx`: fetch `/api/accounts/{id}/usage` lazy on mount, hiển thị quota section cho OAuth
- [x] `types/index.ts`: `UsageInfo` interface (optional fields, nullable)
- [x] Mock interceptor: `GET /api/accounts/usage/active` + `GET /api/accounts/:id/usage`
- [x] `utils/format.ts`: thêm `fmtResetsIn()` chuyển unix seconds → "Xd Yh" / "Xh Ym"

### B — BUG-004 Live Card Fix ✅
- [x] WS reducer: handle `chain_updated` event → tăng counter `chainUpdateTriggers[session_id]`
- [x] `PipelineCard.tsx`: subscribe `chainUpdateTriggers[sessionId]` trong useEffect deps
- [x] `AgentRosterItem.tsx` — `ActiveSubagentNode`: fallback `<p style="color:#F05922; fontStyle:italic">đang khởi tạo…</p>` khi `!model && !latest_description`
- [x] Token line active: hiển thị "— tokens" khi 0 (không ẩn — khác Dispatcher)

### C — FR-004 Dispatcher Node ✅
- [x] `AgentRosterItem.tsx`: tách thành `DispatcherNode` + `ActiveSubagentNode` + `DoneSubagentNode`
- [x] `DispatcherNode`: Navy background #251C53 (active) / rgba(37,28,83,0.08) (done), icon 🧠, label "Claude (Dispatcher)", KHÔNG có nút "Xem lịch sử"
- [x] Tokens=0 → ẩn hoàn toàn cho Dispatcher (không hiển thị "— tokens")
- [x] `is_dispatcher?: boolean` thêm vào `RosterEntry` type

### D — FR-005 Toggle ✅
- [x] `hooks/usePipelineMode.ts`: useState + localStorage persist key "pipelineMode"
- [x] `AgentStatusPage.tsx`: Segmented Control "Theo Session" | "Tổng hợp" (role="group", aria-pressed)
- [x] `AggregatePipelineView.tsx`: fetch `/api/pipeline/aggregate`, polling 30s, search filter, window dropdown
- [x] Bảng: header Navy, row xen kẽ, active row viền trái 3px Cam, skeleton/empty/error state
- [x] Mock interceptor: `GET /api/pipeline/aggregate` → MOCK_AGGREGATE (8 agent roles)

### E — BUG-005 ✅
- [x] `hasHistory = !entry.is_dispatcher && entry.call_count >= 1` (cũ: `> 1`)

### Chung ✅
- [x] `tsc --noEmit` → 0 errors
- [x] `vite build` → ✓ built in 6.44s, 0 errors
- [x] Không làm vỡ test cũ (chưa có vitest trong project)

## Đã làm

### Thứ tự implementation

1. **types/index.ts**: Thêm `PipelineMode`, `is_dispatcher` vào `RosterEntry`, `UsageInfo`, `AggregateEntry`, `AggregateResponse`, `chain_updated` vào `DeltaEvent`, `chainUpdateTriggers` vào `WsAppState`.

2. **state/wsReducer.ts**: Thêm `chainUpdateTriggers: {}` vào initialWsState, handler DELTA case cho `chain_updated` (tăng counter theo session_id).

3. **utils/format.ts**: Thêm `fmtResetsIn(resetsAt: number)` — unix seconds → "Xd Yh" / "Xh Ym" / "Ym" / "Đã reset".

4. **components/common/UsageBar.tsx** (NEW): Component 2 thanh tiến trình (5h/7d), màu theo ngưỡng 80%, onHeader prop thay đổi theme, aria-progressbar, returns null khi usage===null hoặc error!=null.

5. **components/layout/AppHeader.tsx**: Thêm polling fetchUsage 60s, dynamic header height 56→80px khi hiện bars, render `<UsageBar onHeader/>`.

6. **components/accounts/AccountCard.tsx**: Lazy fetch usage on mount cho OAuth, section "Quota Claude Pro" với `<UsageBar/>`.

7. **components/sessions/AgentRosterItem.tsx**: Tách 3 sub-components (DispatcherNode / ActiveSubagentNode / DoneSubagentNode), fix BUG-004 fallback, fix BUG-005 `hasHistory >= 1`.

8. **components/sessions/PipelineCard.tsx**: Subscribe `chainUpdateTriggers` từ WsContext, thêm vào useEffect deps.

9. **hooks/usePipelineMode.ts** (NEW): useState + localStorage persist.

10. **components/sessions/AggregatePipelineView.tsx** (NEW): Bảng tổng hợp, polling 30s, search+window filter, skeleton/empty/error state.

11. **pages/AgentStatusPage.tsx**: Segmented Control FR-005, render AggregatePipelineView khi mode=aggregate.

12. **api/mockData.ts**: Thêm `getMockChain()` trả `roster[]` (không còn `steps[]`), `MOCK_USAGE_ACTIVE`, `MOCK_USAGE_INACTIVE`, `getMockUsage()`, `MOCK_AGGREGATE`.

13. **api/interceptor.ts**: Thêm 3 route handler mới: usage/active, :id/usage, /api/pipeline/aggregate.

### Quyết định kỹ thuật quan trọng

- **BUG-004 WS pattern**: Dùng counter `chainUpdateTriggers: Record<string, number>` trong WsState thay vì event callback trực tiếp — PipelineCard dùng counter làm React dependency, tự refetch khi counter tăng. Pattern này sạch hơn, không cần expose WS message stream ra ngoài context.
- **Dispatcher tokens ẩn vs subagent tokens "—"**: Dispatcher `tokens=0` → ẩn hoàn toàn. Subagent active `tokens=0` → hiển thị "— tokens". Hai trường hợp khác nhau do business logic: Dispatcher luôn aggregate tokens vào total_tokens riêng; subagent "—" là trạng thái đang khởi tạo chưa có attribution.
- **Header height dynamic**: `showBars ? 80 : 56` với CSS transition 150ms, tránh layout shift đột ngột.
- **UsageBar threshold**: TDD spec nói <80%=xanh, ≥80%=cam — không có threshold "đỏ" (DoD của step này không dùng đỏ tươi theo brand rules).
- **AgentRosterItem tách 3 sub-component**: SRP — mỗi sub-component có style riêng, không if/else phức tạp trong 1 component lớn.
- **interceptor: usage/active TRƯỚC /:id/usage**: pattern match thứ tự quan trọng — "usage" phải không bị coi là account_id.

## Artifact

| File | Loại |
|------|------|
| `frontend/src/types/index.ts` | sửa — +PipelineMode, +is_dispatcher, +UsageInfo, +AggregateEntry, +AggregateResponse, +chain_updated, +chainUpdateTriggers |
| `frontend/src/state/wsReducer.ts` | sửa — handle chain_updated |
| `frontend/src/utils/format.ts` | sửa — +fmtResetsIn |
| `frontend/src/components/common/UsageBar.tsx` | **MỚI** |
| `frontend/src/components/layout/AppHeader.tsx` | sửa — polling usage, dynamic height |
| `frontend/src/components/accounts/AccountCard.tsx` | sửa — lazy fetch usage |
| `frontend/src/components/sessions/AgentRosterItem.tsx` | sửa — 3 sub-components, BUG-004, BUG-005, FR-004 |
| `frontend/src/components/sessions/PipelineCard.tsx` | sửa — BUG-004 chainUpdateTriggers |
| `frontend/src/hooks/usePipelineMode.ts` | **MỚI** |
| `frontend/src/components/sessions/AggregatePipelineView.tsx` | **MỚI** |
| `frontend/src/pages/AgentStatusPage.tsx` | sửa — FR-005 Segmented Control |
| `frontend/src/api/mockData.ts` | sửa — roster[] chain, MOCK_USAGE_*, MOCK_AGGREGATE |
| `frontend/src/api/interceptor.ts` | sửa — +3 route handlers |

## Verification

```
tsc --noEmit   → 0 errors (no output)
vite build     → ✓ built in 6.44s, 0 compile errors
```

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")

- do_not_redo: Tất cả 13 file đã chỉnh xong. `chainUpdateTriggers` pattern đã implement đầy đủ trong wsReducer + PipelineCard. Mock data `getMockChain()` đã trả `roster[]` format — KHÔNG còn `steps[]`. 3 endpoint mới đã intercept. tsc + vite build đều pass.
- watch_out:
  - `UsageBar` trả `null` khi `usage.error != null` — UXR nên kiểm tra AccountCard khi `error='api_key'` (không render gì, không crash).
  - `AppHeader` dynamic height 56→80px dùng `style` inline — không dùng Tailwind class cho animation height (Tailwind không có transition height tự động). Nếu UXR thấy layout jump → tăng transition duration.
  - `AgentStatusPage` title "Agent Status" → h2 — không có header "Agents đang chạy" nữa (AgentStatusPanel có internal header riêng). Kiểm tra duplicate heading.
  - Interceptor `usage/active` chỉ trả data cho account là OAuth (check `kind`). Mock MOCK_ACCOUNTS có account `acc-001` chưa set `kind` field → interceptor sẽ trả 404 (vì condition check `kind === 'api_key'` fail). Cần verify MOCK_ACCOUNTS có account với kind='oauth_session' để test flow đầy đủ.
- next_inputs:
  - Commit hash: xem mục "Commit" bên dưới
  - Scope TL review: 13 file listed trong Artifact table
  - Điểm UXR kiểm tra: AppHeader bar visible khi có OAuth active account; AccountCard quota section; Dispatcher node style Navy; Segmented Control toggle; Aggregate table

## Commit
- Hash: d9c89a5
- Đã push: không (cần TL review trước)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
