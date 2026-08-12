# RESOURCE: Phân bổ nhân sự — Auto-Failover Anthropic (Agent Dashboard v2)

**Feature:** Auto-Failover Account Anthropic — Mở rộng Account Manager (Sprint 6)
**Engineering Manager:** Engineering Manager (KZTEK)
**Ngày:** 2026-08-09
**Tham chiếu PRD:** `docs/prd/PRD-agent-dashboard-autofailover.md` v2.3
**Tham chiếu US:** `docs/user-stories/US-agent-dashboard-autofailover.md` (7 US, 11 EC)
**Tham chiếu Design:** `docs/design/DESIGN-agent-dashboard-autofailover.md` (4 component)
**Plan:** `docs/plans/PLAN-agent-dashboard-autofailover-2026-08-09/PLAN-MASTER.md`

---

## Xác nhận Priority

| Thuộc tính | Giá trị | Lý do |
|-----------|---------|-------|
| Priority | **P2** | Tool nội bộ 1 người, không phải production user-facing, không ảnh hưởng người dùng cuối bên ngoài. Nhất quán với toàn bộ project agent-dashboard từ Sprint 1. (*PRD v2.3 ghi P1 — EM điều chỉnh xuống P2 theo đúng tiêu chí phân loại thực tế*) |
| CTO Review | **Skip (⏭️)** | Không cần — đây là MỞ RỘNG cơ chế OAuth Sprint 2 đã có (không phải cơ chế credential mới), không đụng auth thật (không login screen/token riêng), không đa người dùng, không production DB khách hàng. **Nhất quán với Sprint 2:** Sprint 2 đã xử lý credential Anthropic (activate_oauth_account, refresh_lock, XOR obfuscation) mà không cần CTO review riêng — tính năng này tái dùng đúng các building block đó. |
| Security Audit STRIDE | **BẮT BUỘC tại Bước 4.3 (TL review)** | Tính năng đụng credential swap tự động (hot-swap `.credentials.json`) — Tech Lead PHẢI chạy `security-audit-stride` tại bước review code cuối trước merge, giống Sprint 2 Bước 5.4. Đây là điều kiện cứng trước khi approve merge. |
| Timeline | Linh hoạt — không có hard deadline bên ngoài | Dự án nội bộ |

---

## Quyết định: Bỏ qua CTO Review — Lý do chi tiết

Tính năng Auto-Failover Anthropic đụng đến credential Anthropic (đọc/ghi `.credentials.json`, swap giữa các account). Tuy nhiên, EM quyết định KHÔNG cần CTO review riêng vì:

1. **Không phải cơ chế mới:** Sprint 2 đã implement `activate_oauth_account()` + `refresh_lock` + XOR obfuscation cho `.credentials.json`. Auto-Failover chỉ gọi các hàm đó theo một trigger khác (429/quota thay vì click thủ công).
2. **Sprint 2 đã làm tương tự không cần CTO:** Sprint 2 đụng credential Anthropic trực tiếp, Sprint 2 không có CTO review riêng — chỉ Tech Lead chạy `security-audit-stride` ở bước review cuối. Giữ nhất quán là đúng.
3. **Không phải kiến trúc chiến lược:** Đây là automation logic trong tool nội bộ — không ảnh hưởng đến kiến trúc sản phẩm KZTEK hay bảo mật khách hàng.
4. **Bù đắp bằng security audit bắt buộc:** Tech Lead chạy `security-audit-stride` tại Bước 4.3 (code review) — không pass audit thì BLOCK merge. Đủ bảo vệ cho mức rủi ro thực tế của tool nội bộ.

---

## Team được giao

| Role | Phân công | Tỉ lệ tham gia | Scope |
|------|-----------|----------------|-------|
| Tech Lead | Tech Lead | 40% (Bước 1.2 + 4.3) | Viết TDD, code review + security audit STRIDE, merge decision |
| Senior Developer | Senior Developer | 100% (Bước 4.1) | Backend toàn bộ: failover engine, API, WebSocket, migration |
| Junior Developer | Junior Developer | 100% (Bước 4.2) | Frontend: 3 tab mới Account Manager, badge/toast, countdown banner |
| QA Engineer | QA Engineer | 50% (Bước 4.5) | Test simulate 429, quota 100%, wait-and-retry, regression |
| QA Lead | QA Lead | 20% (Bước 4.6) | Sign-off — tính năng P2, đủ điều kiện bỏ qua nếu không có P0/P1 |
| DevOps Engineer | DevOps Engineer | 20% (Bước 5.1) | Migration script SQLite, env var mới, backward compat check Sprint 6 |
| DevOps Lead | DevOps Lead | 10% (Bước 5.2) | Approve deploy, smoke test |

---

## Phân bổ nhiệm vụ chi tiết

### Senior Developer — Backend Failover Engine (Bước 4.1)

> Mở rộng backend đã có: tái dùng `refresh_lock`, `activate_oauth_account`, WebSocket broadcast, UsageBar quota data từ Sprint 2–5.

| Hạng mục | Mô tả | Ước tính |
|---------|-------|---------|
| Failover Engine service | State machine: detect 429 (log parsing từ Claude Code CLI) + proactive detection (UsageBar callback quota 100%), chain traversal logic (BR1–BR7), phân biệt "account hết quota" vs "Anthropic API down toàn cầu" (EC3, BR2) | 2 ngày |
| Hot-swap logic | Mở rộng `activate_oauth_account()` + `refresh_lock`: thêm latency measurement (`swap_latency_ms`), atomic write guard, rollback in-memory backup khi write error (EC6, US-002 Scenario 5). Phần lớn là reuse | 0.5 ngày |
| Failover chain config persistence | Thêm `priority` field + `include_in_chain` boolean vào AccountStore schema; persist qua restart (BR13, BR14); UI API GET/PUT `/api/failover/chain` | 0.5 ngày |
| Wait-and-retry scheduler | asyncio background task: tính T_reset từ UsageBar 5h/7d window, T_retry = T_reset + 30s buffer (BR19), retry tối đa 3 lần cách nhau 5 phút (BR18), cancel ngay khi manual activation (BR16) | 1.5 ngày |
| DB migration: `failover_events` table | SQLite schema mới: 9 field (failover_id UUID, occurred_at ISO8601, from/to account, trigger_reason, result, swap_latency_ms, next_retry_at). Migration script cho DevOps. Auto-purge sau 30 ngày. Fallback log file khi DB write fail (BR8) | 0.5 ngày |
| 5 API endpoints mới | `GET /api/failover/status`, `GET /api/failover/log` (có filter ngày), `GET /api/failover/chain`, `PUT /api/failover/chain`, `GET /api/failover/stats` (số failover 24h) | 1 ngày |
| WebSocket broadcast: 5 event types mới | `failover_started`, `failover_completed`, `failover_failed`, `all_accounts_exhausted`, `retry_scheduled` — push đến tất cả client trong < 2 giây (BR11) | 0.5 ngày |
| Unit tests + integration tests | Tests cho failover state machine, hot-swap với mock, wait-and-retry timing, DB log completeness, API endpoints | 1 ngày |
| **Tổng SD** | | **7.5 ngày (~60 giờ)** |

**Rủi ro kỹ thuật SD:**
- Phát hiện 429 từ Claude Code CLI: cơ chế cụ thể (proxy / log parsing / poll) cần TL xác nhận trong TDD (Q-TL-1). Ảnh hưởng đến latency 5 giây trong US-001 — có thể thực tế khó hơn dự kiến.
- Tính T_reset chính xác: UsageBar Sprint 5 có sẵn thông tin quota window không, hay cần call thêm Anthropic endpoint? TL xác nhận trong TDD (Q-TL-4). Ảnh hưởng đến Scenario 1 US-006.
- Phân biệt "API down toàn cầu" vs "1 account hết quota" (EC3, BR2): ngưỡng cụ thể do TL quyết định (Q-TL-2) — cần rõ ràng trước khi SD code.

---

### Junior Developer — Frontend Auto-Failover UI (Bước 4.2)

> Mở rộng Account Manager (Sprint 6): thêm tab bar 3 tab + 4 component mới theo spec DESIGN-agent-dashboard-autofailover.md.

| Hạng mục | Component | Ước tính |
|---------|-----------|---------|
| Tab bar cho Account Manager | Component mới hoàn toàn — Account Manager hiện tại chưa có tab. 3 tab: "Danh sách Account" (nội dung Sprint 6 hiện tại), "Failover Chain", "Failover Log". Dùng Tailwind thuần, không thêm UI library | 1 ngày |
| `FailoverStatusBadge` trên AccountCard | Badge nhỏ trong AccountCard header: `bg-kz-orange text-white`, text "FAILOVER ACTIVE", tự ẩn sau 30 giây. Trigger từ WebSocket event `failover_completed` | 0.5 ngày |
| Extend `ToastContext` | Thêm 2 variant mới: `'failover'` (màu cam, auto-dismiss 15s) và `'failover-error'` (màu đỏ, không auto-dismiss). Tái dùng `ToastNotification.tsx` | 0.5 ngày |
| `FailoverChainConfig` tab | Ordered list account theo priority, nút ▲/▼ HTML thuần (không drag-and-drop — quyết định design cuối), checkbox "Bao gồm trong chain", nút "Lưu thứ tự", confirmation toast. API: GET/PUT `/api/failover/chain` | 1.5 ngày |
| `FailoverLogTable` tab | Table 6 cột (thời gian, from → to, lý do, kết quả, latency_ms), filter ngày, sort ngược (mới nhất lên đầu), realtime WebSocket update (animate-fade-in khi record mới xuất hiện). API: GET `/api/failover/log` | 2 ngày |
| `WaitRetryBanner` (global) | Full-width dưới AppHeader (không overlay/fixed — đẩy content xuống), visible từ mọi tab (BR12). State machine: `counting` (countdown HH:MM:SS) → `retrying` → `retry_failed` → `exhausted_all_retries`. Màu `kz-warning-bg` / `kz-error-bg`. Biến mất khi retry thành công | 1.5 ngày |
| WebSocket client: 5 event types mới | Subscribe và xử lý `failover_started`, `failover_completed`, `failover_failed`, `all_accounts_exhausted`, `retry_scheduled` — update React state đúng component | 0.5 ngày |
| **Tổng JD** | | **7.5 ngày (~60 giờ)** |

**Ghi chú JD:**
- Spec design đầy đủ (`DESIGN-agent-dashboard-autofailover.md` mục "Hand-off cho Junior Developer") — props/states cho từng component đã được định nghĩa.
- `WaitRetryBanner` là component phức tạp nhất phía frontend (state machine + countdown timer) — ưu tiên làm sớm.
- SD và JD chạy **song song (∥)** sau khi TDD (Bước 1.2) được TL duyệt — JD dùng mock WebSocket + mock API trong giai đoạn đầu.
- KHÔNG dùng drag-and-drop library (quyết định Design đã chốt) — nút ▲/▼ HTML thuần là final.

---

## Ước lượng effort tổng thể

| Phase | Agent | Effort | Ghi chú |
|-------|-------|--------|---------|
| Phase 0: Discovery (Done) | PM + BA + UX + EM | ~8h | ✅ Hoàn thành |
| Phase 1: TDD | Tech Lead | 1.5 ngày | Viết TDD, trả lời 4 câu Q-TL, chốt cơ chế detection |
| Phase 4.1 + 4.2 (song song) | SD + JD | 7.5 ngày | SD backend ∥ JD frontend — bắt đầu sau khi TDD được duyệt |
| Phase 4.3: TL review + security audit | Tech Lead | 1.5 ngày | Code review + STRIDE bắt buộc — gate trước merge |
| Phase 4.4: UX/UI Reviewer | UX/UI Reviewer | 0.5 ngày | Kiểm tra 4 component trực quan |
| Phase 4.5 + 4.6: QA | QAE + QAL | 1.5 ngày | Simulate 429, quota 100%, wait-and-retry |
| Phase 5: Deploy | DOE + DOL | 0.5 ngày | Migration script, smoke test, go-live |
| **Tổng (wall-clock sau TDD)** | | **~11 ngày lịch** | Tính theo calendar time, có song song SD+JD |

**Tổng effort người-ngày (Phase 1–5):**
`TL: 3nd + SD: 7.5nd + JD: 7.5nd + QAE: 1nd + QAL: 0.5nd + DOE: 0.5nd + DOL: 0.5nd ≈ 20.5 người-ngày`

---

## Điều kiện kèm theo / Risk

| Risk | Mức độ | Mitigation |
|------|--------|-----------|
| Cơ chế detect 429 từ Claude Code CLI (Q-TL-1) | Trung | TL xác nhận trong TDD trước khi SD bắt đầu; nếu log parsing không đủ nhanh (> 5s threshold US-001) → fallback UsageBar proactive detection |
| Tính T_reset từ UsageBar (Q-TL-4) | Thấp–Trung | UsageBar Sprint 5 có dữ liệu quota window — TL verify trong TDD; nếu không đủ → cần call thêm Anthropic billing endpoint (tăng ~0.5 ngày) |
| State machine `WaitRetryBanner` phức tạp hơn dự kiến | Thấp | JD làm sớm nhất; nếu blocker → SD hỗ trợ thêm state logic |
| Security audit STRIDE tìm vấn đề nghiêm trọng | Thấp | Cơ chế credential (XOR, refresh_lock) đã được audit Sprint 2; nếu STRIDE fail → BLOCK merge, EM quyết định escalate hay sửa trước |
| Regression với Sprint 6 | Thấp | Account Manager UI Sprint 6 vẫn là "Danh sách Account" tab — không xóa UI cũ, chỉ wrap vào tab bar mới |

**Không có rủi ro nào đủ nghiêm trọng để escalate lên CTO.**

---

## Quyết định ưu tiên

- **Priority: P2** — tool nội bộ, 1 người dùng, không production user-facing.
- **CTO review: SKIP** — mở rộng cơ chế OAuth Sprint 2 đã có; Tech Lead chạy `security-audit-stride` tại Bước 4.3 thay thế.
- **Bước 4.1 (SD) và 4.2 (JD) chạy song song** sau khi Bước 1.2 (TDD) được Tech Lead hoàn thành và duyệt.
- Backend và frontend giao tiếp qua REST API + WebSocket — JD dùng mock WebSocket + json-server trong giai đoạn song song.
- **Bước tiếp theo ngay:** Tech Lead viết TDD (Bước 1.2) — bắt đầu ngay sau khi EM step này hoàn thành, KHÔNG qua CTO.

---

## Approve bởi

- Engineering Manager: Engineering Manager (KZTEK) — 2026-08-09
