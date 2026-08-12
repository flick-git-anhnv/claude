---
step: "8.5"
plan: ../PLAN-MASTER.md
agent: tech-lead
status: done
completed_at: 2026-08-07 09:08
deps: ["8.3", "8.4"]
---

# STEP 8.5 — Code Review Sprint 5: Tất cả 4 hạng mục (Usage + BUG-004 + FR-004 + FR-005)

## Input nhận
- Backend commit `ad14bdb` (8.3) — usage_service.py, routes/pipeline.py, db.py (FR-004+FR-005), main.py (BUG-004), test_sprint5.py (22 tests), 3 test file regression fix
- Frontend commit `d9c89a5` (8.4) — UsageBar.tsx, AppHeader.tsx, AccountCard.tsx, AgentRosterItem.tsx (3 sub-components), PipelineCard.tsx, usePipelineMode.ts, AggregatePipelineView.tsx, wsReducer.ts, types/index.ts, mockData.ts, interceptor.ts
- Schema handoff từ 8.3: `UsageInfo` TypedDict fields, Dispatcher entry shape, aggregate response shape

## Nhiệm vụ
Review toàn bộ code Sprint 5 — 5 hạng mục A/B/C/D/E, verify tích hợp thật, quyết định merge.

## Kết quả review

### Build & Test
| Kiểm tra | Kết quả |
|---|---|
| `pytest --tb=short -q` (backend) | ✅ **250 passed**, 1 warning (starlette deprecation, không liên quan) |
| `tsc --noEmit` (frontend) | ✅ 0 errors |
| `vite build` (frontend) | ✅ built in 4.88s, 864 modules, 0 errors (có warning chunk >500KB — non-blocking) |

### A — Usage Display ✅ PASS
- **Schema match**: Pydantic `UsageInfo` TypedDict (`usage_service.py:22`) và TS `UsageInfo` (`types/index.ts:150`) khớp 100% — 11 field: `account_id, five_hour_pct, seven_day_pct, seven_day_opus_pct, seven_day_sonnet_pct, resets_at, seven_day_resets_at, rate_limit_type, overage_status, fetched_at, error`. **Không có regression Sprint 3 (lệch schema)**.
- **Robustness**: `httpx.AsyncClient(timeout=5.0)`, bắt `TimeoutException → error='timeout'`, `HTTPError → error='network'`, 401 → `unauthorized`, 4xx/5xx khác → `http_NNN`. Không có branch nào raise ra ngoài — app không crash khi API lỗi.
- **Cache 60s TTL** đúng thiết kế TDD §29; `invalidate_cache()` hỗ trợ cả selective + full clear.
- **Route ordering** đúng: `/usage/active` khai báo TRƯỚC `/{acc_id}/usage` (accounts.py:109-129) — nếu không FastAPI sẽ match "usage" thành `acc_id`.
- **Frontend cleanup**: AppHeader useEffect có `cancelled` flag + `clearInterval` khi unmount — không memory leak. AccountCard lazy fetch on mount, không race giữa nhiều card (mỗi card fetch với `acc_id` riêng).
- **UsageBar null-safe**: return null khi `usage==null || usage.error!=null` (UsageBar.tsx:129) — không crash.
- **Tích hợp thật (port 7772)**: `GET /api/accounts/usage/active` → 200 với `{error:'http_429'}` (Anthropic rate-limit real-time), frontend xử lý đúng (UsageBar ẩn khi error).

### B — BUG-004 Fix ✅ PASS
- **Backend fix ở đúng chỗ**: broadcast `chain_updated` trong ingest loop `_process_file` (main.py:287-292), không phải state_manager — đúng vì cần trigger ngay khi parse child event, không đợi DB write.
- **Điều kiện chính xác**: `if parsed.is_subagent and parsed.parent_session_id:` — chỉ broadcast cho child session có parent link.
- **Payload đủ**: `{session_id: parent_session_id, child_session_id, reason:'child_event'}`.
- **Frontend refetch pattern sạch**: `chainUpdateTriggers[sid]` counter trong WsReducer (wsReducer.ts:132-141), PipelineCard subscribe qua `useEffect deps` (PipelineCard.tsx:263) — không tạo vòng lặp vì HTTP refetch không phát sinh WS event.
- **Không vỡ Ended logic**: test cũ 228/228 pass sau khi thêm broadcast.

### C — FR-004 Dispatcher Node ✅ PASS
- **Luôn first entry**: `[dispatcher_entry] + roster` (db.py:1208).
- **Verified thực tế** (session `8f3eab89-...`): `roster[0].is_dispatcher=true, role='__dispatcher__', display_name='Claude (Dispatcher)'`. Kiểm tra `roster[1:]` không có entry nào `is_dispatcher=true` → **duplicate = 0**.
- **AggregatePipelineView KHÔNG lẫn Dispatcher**: SQL query `WHERE parent_session_id IN (...) AND attribution_agent IS NOT NULL` — Dispatcher chính là parent session nên `parent_session_id IS NULL` cho row đó → tự loại. Grep frontend `AggregatePipelineView.tsx` cũng không reference `is_dispatcher` → không misuse.
- **Frontend render riêng**: `AgentRosterItem.tsx:380` `if (entry.is_dispatcher) return <DispatcherNode/>` — style Navy #251C53, icon 🧠, không hiện nút "Xem lịch sử".
- **Empty history[]**: dispatcher_entry.history=[] mọi lúc — frontend không crash khi map history.

### D — FR-005 Aggregate ✅ PASS
- **SQL edge cases**:
  - `parent_ids` empty → early return `{total_sessions:0, total_calls:0, roster:[]}` (db.py:1247-1248) → tránh `IN ()` SQL syntax error.
  - `window_days=0` → skip filter, return all-time.
  - `project` filter: exact match, không có project → early return `[]`.
- **`parent_ids + parent_ids`** bind 2× đúng cho placeholder ở correlated subquery + main WHERE (db.py:1275).
- **Sort `call_count DESC`** đúng thiết kế.
- **`active_now`** tính từ `SUM(CASE state WHEN 'Running' THEN 1 ELSE 0 END)` — chính xác.
- **Tích hợp thật**: window=7 → 34 sessions/149 calls/18 roles; window=0 → 355 sessions/1035 calls. Response shape khớp 100% TS `AggregateResponse`.
- **Frontend chưa gửi `project` param** (chỉ `window`) — chấp nhận cho MVP, backend support sẵn khi cần thêm filter sau này (FYI — không block).

### E — BUG-005 ✅ PASS
- `hasHistory = !entry.is_dispatcher && entry.call_count >= 1` (AgentRosterItem.tsx:377) — đúng specification: Dispatcher không có nút "Xem lịch sử", subagent gọi ≥1 lần có nút.
- Fix từ `> 1` → `>= 1` giải quyết đúng issue (agent chỉ được gọi 1 lần trước đây không hiện nút).

## Quyết định

### ✅ **APPROVED — Merge cả 2 commit (`ad14bdb` backend + `d9c89a5` frontend)**

**Không có vấn đề chặn merge (Critical/Required):**
- 5/5 hạng mục A/B/C/D/E pass tất cả DoD
- 250/250 pytest pass, tsc/vite build 0 errors
- Tích hợp thật (uvicorn port 7772): usage endpoint OK (http_429 gracefully handled), /chain có Dispatcher đúng vị trí, /pipeline/aggregate trả data thật đúng schema
- Schema backend ↔ frontend khớp 100% (không lặp lại lỗi lệch schema Sprint 3)
- Two-Eyes Principle giữ nguyên — SD + JD code, TL review

**Optional (không chặn merge, cân nhắc cải tiến sau):**
1. **Optional (PipelineCard.tsx:263):** Counter `chainUpdateCount` mỗi lần WS `chain_updated` → trigger 1 lần refetch. Nếu child session có event rất dày (>10/s), có thể debounce (throttle 500ms) để giảm HTTP requests. Không cần fix ngay — hiện tại 1-2s độ trễ file-watch đã tự throttle.
2. **FYI (AggregatePipelineView.tsx):** Chưa expose UI cho `project` filter dù backend hỗ trợ. Nếu user cần trong tương lai, thêm dropdown tương tự window.
3. **Nit (usage_service.py:78-81):** 2 branch `r.status_code>=500` và `r.status_code!=200` cùng gán `http_NNN` — có thể gộp thành 1 điều kiện. Không quan trọng.

## Đã làm

1. Chạy `pytest --tb=short -q` backend → 250/250 pass
2. Chạy `tsc --noEmit` + `vite build` frontend → 0 errors, build 4.88s
3. Review chi tiết 5 hạng mục A/B/C/D/E theo file:
   - Backend: `usage_service.py`, `routes/accounts.py` (usage endpoints), `routes/pipeline.py`, `db.py` (get_session_chain FR-004 + get_pipeline_aggregate FR-005), `main.py` (BUG-004 broadcast)
   - Frontend: `UsageBar.tsx`, `AppHeader.tsx`, `AccountCard.tsx`, `AgentRosterItem.tsx`, `PipelineCard.tsx`, `AggregatePipelineView.tsx`, `wsReducer.ts`, `types/index.ts`
4. Khởi động uvicorn port 7772, test thật 3 endpoint:
   - `GET /api/accounts/usage/active` → 200 `{error:'http_429'}` (Anthropic rate-limit real, frontend handle đúng)
   - `GET /api/sessions/{sid}/chain` → roster[0] là Dispatcher, no duplicate
   - `GET /api/pipeline/aggregate?window=7` → 34 sessions/149 calls/18 roles đúng shape
5. Verify schema Pydantic ↔ TypeScript khớp 100% cho `UsageInfo`, `RosterEntry` (thêm is_dispatcher?), `AggregateEntry`, `AggregateResponse`, `chain_updated` delta event
6. Quyết định: **APPROVED merge**, chuyển bước 8.6 (UXR)

## Artifact
- Review report inline trong step file này
- **Merge decision: APPROVED**
- Không có code fix trực tiếp — không có commit mới từ TL

## Quyết định quan trọng

1. **APPROVED merge cả 2 commit** — không có Critical/Required issue.
2. **Không request changes cho 3 optional/nit** — để dev tự cân nhắc trong sprint sau nếu perf cần tuning.
3. **UXR (8.6) tiếp theo bắt buộc** — Sprint 5 đổi UI ở nhiều điểm (AppHeader height, AccountCard quota section, Dispatcher node style, Segmented Control, Aggregate table).

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")

- **do_not_redo**: 250/250 pytest + tsc/vite build đã verify. 3 endpoint thật đã curl OK. Schema Pydantic↔TS đã match 100%. Không cần chạy lại test suite hay verify schema.
- **watch_out**:
  - **UXR cần chụp screenshot 5 điểm**: (1) AppHeader khi có OAuth active — bars 5h/7d visible; height 80px (56→80 transition 150ms); nếu API rate-limit 429, bars ẩn hoàn toàn — không hiển thị lỗi. (2) AccountCard khi mở AccountManager — section "Quota Claude Pro" hiện cho OAuth, không hiện cho api_key. (3) PipelineCard → node đầu tiên phải là "Claude (Dispatcher)" Navy #251C53 background, icon 🧠, KHÔNG có nút "Xem lịch sử". (4) Segmented Control "Theo Session"/"Tổng hợp" — toggle chuyển view + persist localStorage. (5) AggregatePipelineView bảng: header Navy, active row viền trái 3px cam, dropdown window filter (Tất cả/7d/30d/90d).
  - **BUG-005 verify**: agent trong roster chỉ có `call_count=1` phải có nút "Xem lịch sử" (trước sprint 5 không có).
  - **AppHeader height dynamic** dùng inline `style={{height, transition}}` — không Tailwind class. Nếu UXR thấy layout jump đột ngột, tăng transition duration ≥ 300ms.
  - **AggregatePipelineView chưa expose `project` filter** — dropdown chỉ có window. UXR không cần đánh Fail vì backend hỗ trợ nhưng UI chưa expose (không phải bug).
- **next_inputs**:
  - Commit hash: `ad14bdb` (backend) + `d9c89a5` (frontend) — cả 2 chưa push, TL không tự push (đợi UXR+QA xong).
  - File UI chính thay đổi: `AppHeader.tsx`, `AccountCard.tsx`, `UsageBar.tsx` (A); `AgentRosterItem.tsx`, `PipelineCard.tsx` (B/C/E); `AggregatePipelineView.tsx`, `AgentStatusPage.tsx` (D).
  - Không có Critical/High UI issue nào TL phát hiện — UXR bắt đầu review sạch, không cần fix trước.

## Commit
- Hash: (không có — TL review only, không sửa code)
- Đã push: N/A

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
