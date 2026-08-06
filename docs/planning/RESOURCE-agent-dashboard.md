# RESOURCE-agent-dashboard: Phân bổ nhân sự — Agent Dashboard

**Feature:** Agent Dashboard — Dashboard Web Local Realtime Quản Lý Claude Code Agents
**Engineering Manager:** Engineering Manager (KZTEK)
**Ngày:** 2026-08-05
**Tham chiếu PRD:** `docs/prd/PRD-agent-dashboard.md`
**Tham chiếu US:** `docs/user-stories/US-agent-dashboard.md`
**Tham chiếu Design:** `docs/design/DESIGN-agent-dashboard.md`

---

## Xác nhận Priority

| Thuộc tính | Giá trị | Lý do |
|-----------|---------|-------|
| Priority | **P2** | Tool nội bộ, không phải production user-facing, không đụng auth/payment/production DB |
| CTO Review | **Skip (⏭️)** | P2, tool cá nhân 1 máy, kiến trúc không chiến lược — không đủ điều kiện WF-FEATURE Bước 5 |
| Timeline | Linh hoạt — không có hard deadline bên ngoài | Dự án nội bộ |

---

## Team được giao

| Role | Phân công | Tỉ lệ tham gia | Scope |
|------|-----------|----------------|-------|
| Tech Lead | Tech Lead | 40% (Bước 2.1 + 3.3) | Viết TDD, code review cuối, merge decision |
| Senior Developer | Senior Developer | 100% (Bước 3.1) | Backend toàn bộ |
| Junior Developer | Junior Developer | 100% (Bước 3.2) | Frontend toàn bộ (song song với SD) |
| QA Engineer | QA Engineer | 50% (Bước 4.1) | Thực thi test plan, log bug |
| QA Lead | QA Lead | 20% (Bước 4.2) | Sign-off nếu còn P0/P1 bug |
| DevOps Engineer | DevOps Engineer | 20% (Bước 4.3) | Deploy local — start script, verify |
| DevOps Lead | DevOps Lead | 10% (Bước 4.4) | Smoke test cuối, approve |

---

## Phân bổ nhiệm vụ chi tiết

### Senior Developer — Backend (Bước 3.1)

> Phần phức tạp: file-watcher, JSONL parser, SQLite ingestion, WebSocket server, account API.

| Hạng mục | Mô tả | Ước tính |
|---------|-------|---------|
| Project setup + cấu trúc | FastAPI/Python hoặc Node.js, virtual env, cấu trúc folder backend | 0.5 ngày |
| File-watcher + JSONL parser | Watch `~/.claude/projects/*/*.jsonl` (Windows), parse entry realtime, extract agent name / task / tokens / timestamp | 2 ngày |
| SQLite schema + ingestion layer | Thiết kế schema (sessions, token_events), ORM/raw SQL, batch insert, index cho query analytics | 1.5 ngày |
| WebSocket server | Endpoint `/ws`, push delta update khi file thay đổi, handle reconnect grace | 1 ngày |
| Account Management API | CRUD `/accounts` — lưu danh sách account trong `accounts.enc` (XOR + base64 hoặc tương đương mã hóa nhẹ), GET active/SET active/DELETE | 1.5 ngày |
| Unit tests + integration tests | Tests cho JSONL parser, SQLite queries, account CRUD, WebSocket message format | 0.5 ngày |
| **Tổng SD** | | **7 ngày (~56 giờ)** |

**Rủi ro kỹ thuật SD:**
- File-watcher trên Windows (`watchdog` lib) có thể có độ trễ khác Linux — cần test thực tế trên máy target.
- JSONL từ Claude Code có thể thay đổi format theo version — cần defensive parsing (bỏ qua entry không hợp lệ, không crash).
- Mã hóa `accounts.enc` chỉ mức bảo mật nhẹ (obscurity) — đã được PM/UX chấp nhận, không escalate thêm.

---

### Junior Developer — Frontend (Bước 3.2)

> Phần có spec rõ từ Design: 13 React component, 5 màn hình, design token đầy đủ.

| Hạng mục | Component | Ước tính |
|---------|-----------|---------|
| Project setup + routing | Vite + React, React Router (hoặc tab-based state), CSS variables từ design tokens | 0.5 ngày |
| Layout toàn cục | `AppHeader`, `SidebarNav`, `WebSocketStatus`, khung layout chính | 1.5 ngày |
| Màn hình Agent Status | `AgentCard` (running/idle/done states), `AgentStatusPanel` (empty/error/has-data states), auto-refresh | 1.5 ngày |
| Màn hình Token Analytics | `TokenBarChart` (dùng Chart.js hoặc Recharts), `SummaryCard` (3 card), filter bar 4 khoảng, agent dropdown | 2 ngày |
| Màn hình Session History | `SessionTable` (sort + pagination), date range filter | 1 ngày |
| Màn hình Account Manager | `AccountCard` (active/inactive), `AddAccountPanel` (slide-in), `ConfirmDialog` (xóa account), validation inline | 2 ngày |
| Global utility components | `ToastNotification`, `BannerAlert` (info/warning/error) | 0.5 ngày |
| WebSocket client integration | Connect `/ws`, nhận delta update, cập nhật state React realtime | 0.5 ngày |
| **Tổng JD** | | **9.5 ngày (~76 giờ)** |

**Ghi chú JD:**
- Spec design rõ ràng (wireframe + component list + design tokens) — ít rủi ro scope creep.
- Bar chart là component phức tạp nhất phía frontend — ưu tiên làm sớm để phát hiện blocker.
- SD và JD chạy **song song (∥)** sau khi TDD (Bước 2.1) được duyệt — JD dùng mock data API trong giai đoạn đầu.

---

## Ước lượng effort tổng thể

| Phase | Agent | Effort | Ghi chú |
|-------|-------|--------|---------|
| Phase 1: Phân tích & Design | PM + BA + UX + EM | ~6h | Đã hoàn thành |
| Phase 2: TDD | Tech Lead | 2 ngày | Viết TDD trước khi code |
| Phase 3: Code (song song) | SD + JD | 7–9.5 ngày | SD backend ∥ JD frontend |
| Phase 3 review | Tech Lead | 1.5 ngày | Review + merge |
| Phase 4: QA + Deploy | QAE + QAL + DOE + DOL | 2 ngày | Test + deploy local |
| **Tổng (wall-clock)** | | **~13 ngày sau khi TDD xong** | Tính theo calendar time, có song song |

**Tổng effort người-ngày (bao gồm cả phase 2–4):**
`TL: 4.5nd + SD: 7nd + JD: 9.5nd + QAE: 1.5nd + QAL: 0.5nd + DOE: 0.5nd + DOL: 0.5nd ≈ 24 người-ngày`

---

## Điều kiện kèm theo / Risk

| Risk | Mức độ | Mitigation |
|------|--------|-----------|
| File-watcher Windows performance | Thấp–Trung | Test sớm ở Bước 3.1; fallback polling 2s nếu watchdog không ổn định |
| JSONL format thay đổi theo Claude Code version | Thấp | Parser defensive — skip entry invalid, log cảnh báo, không crash server |
| Chart library integration phức tạp hơn dự kiến | Thấp | JD dùng Recharts (React-native, ít boilerplate); nếu blocke → escalate TL |
| Mã hóa accounts.enc không đủ cho môi trường nhạy cảm | N/A (đã chấp nhận) | Scope đã giới hạn local-only, 1 user — không escalate |
| TDD chưa chốt stack trước khi SD/JD bắt đầu | Trung | **Bắt buộc:** SD và JD chỉ bắt đầu Bước 3.1/3.2 SAU KHI TDD (2.1) được duyệt |

**Không có rủi ro nào đủ nghiêm trọng để escalate lên CTO.**

---

## Quyết định ưu tiên

- **Priority: P2** — tool nội bộ, không production user-facing.
- CTO step **skipped** vì: không đụng kiến trúc sản phẩm chính, không có auth/payment/production DB, không ảnh hưởng người dùng cuối bên ngoài.
- Bước 3.1 (SD) và 3.2 (JD) **chạy song song** sau khi Bước 2.1 (TDD) được Tech Lead hoàn thành và duyệt.
- Backend và frontend giao tiếp qua REST API + WebSocket — JD dùng **mock server** (MSW hoặc json-server) trong giai đoạn song song, tích hợp thật ở Bước 3.3 (TL review).

---

## Approve bởi

- Engineering Manager: Engineering Manager — 2026-08-05
