# PRD-agent-dashboard: Agent Dashboard — Dashboard Web Local Realtime Quản Lý Claude Code Agents

**Phiên bản:** 1.0
**Ngày:** 2026-08-05
**PM:** Product Manager (KZTEK)
**Ưu tiên:** P2 — Công cụ nội bộ

---

## Tổng quan

- **Vấn đề:** Khi chạy hệ thống multi-agent Claude Code (KZTEK), người dùng không có cách nào quan sát được: agent nào đang chạy, đang làm task gì, đã dùng bao nhiêu token, và token cost tích lũy theo thời gian ra sao. Chuyển đổi giữa nhiều tài khoản/API key cũng phải thao tác thủ công, mất thời gian và dễ nhầm lẫn.
- **Đối tượng người dùng:** 1 developer/admin nội bộ KZTEK, sử dụng trên 1 máy local duy nhất. Không có multi-user, không có cloud.
- **Giá trị mang lại:** Khả năng quan sát (observability) realtime cho hệ thống agent, giúp phát hiện agent chạy lâu/hao token bất thường, phân tích xu hướng sử dụng token theo thời gian để tối ưu chi phí, và chuyển đổi tài khoản nhanh mà không cần dừng session.

---

## Mục tiêu (Goals)

- **G1 — Observability realtime:** Hiển thị danh sách agent đang chạy/đã chạy trong session hiện tại và lịch sử gần, với thông tin task đang làm — độ trễ chấp nhận được 1–2 giây.
- **G2 — Token analytics:** Theo dõi token usage (input/output/cache) theo agent và theo session; lưu lịch sử dài hạn vào SQLite để phân tích xu hướng qua biểu đồ.
- **G3 — Account switching nhanh:** Cho phép lưu danh sách tài khoản/API key, chuyển đổi tài khoản đang dùng trong vài click, không cần mở terminal thủ công.
- **G4 — Zero-setup startup:** Dashboard khởi động bằng 1 lệnh đơn, không cần cài đặt phức tạp, không phụ thuộc dịch vụ cloud.

---

## Non-goals

- **Không multi-user:** Dashboard chỉ dùng cho 1 người, 1 máy — không có login, session management, hay phân quyền.
- **Không cloud:** Mọi dữ liệu lưu local (SQLite, file config). Không gửi dữ liệu ra ngoài.
- **Không kiểm soát agent:** Dashboard chỉ quan sát (read-only trên log). Không có nút dừng/khởi động lại agent từ dashboard.
- **Không quản lý prompt/codebase:** Dashboard không đọc nội dung code hoặc prompt của agent — chỉ đọc metadata (token, status, session ID) từ file `.jsonl`.
- **Không auth phức tạp:** Không cần password login, không OAuth, không HTTPS (local only).
- **Không multi-platform deploy:** Chỉ chạy trên Windows (máy local phát triển); không container hóa, không deploy cloud.
- **Không real-time dưới 1 giây:** File-watch polling 1–2s là đủ; không cần WebSocket push sub-second.

---

## User Persona

**Persona duy nhất: KZTEK Internal Developer (vietanh / dungnn)**

| Thuộc tính | Chi tiết |
|---|---|
| Vai trò | Developer/admin vận hành hệ thống multi-agent Claude Code nội bộ |
| Môi trường | Windows 11, 1 máy local, chạy nhiều Claude Code session đồng thời |
| Mục tiêu chính | Biết ngay agent nào đang tốn token, session nào kéo dài bất thường, tổng chi phí tuần/tháng |
| Pain point | Phải mở terminal đọc log thủ công; không biết token đang chạy đến đâu; chuyển API key mất nhiều bước |
| Kỳ vọng UX | Dashboard mở trong browser, luôn mới nhất, không cần refresh thủ công |

---

## User Stories (sơ lược — BA chi tiết hóa ở bước tiếp theo)

- **US-01:** Là admin, tôi muốn xem danh sách agent đang chạy realtime để biết hệ thống đang làm gì.
- **US-02:** Là admin, tôi muốn xem token usage của từng session/agent để phát hiện hao token bất thường ngay lập tức.
- **US-03:** Là admin, tôi muốn xem biểu đồ token theo ngày/tuần/tháng để phân tích xu hướng chi phí.
- **US-04:** Là admin, tôi muốn chuyển đổi tài khoản/API key trong vài click để không phải sửa file config thủ công.
- **US-05:** Là admin, tôi muốn xem lịch sử session (agent đã làm gì, kết quả) để audit lại công việc đã thực hiện.

---

## Feature List (phân theo priority)

### P0 — Phải có khi launch (MVP)

| ID | Feature | Mô tả |
|---|---|---|
| F-01 | **Agent Status Panel** | Danh sách agent đang chạy trong các session active: tên agent, task đang làm (tóm tắt từ `.jsonl`), thời gian bắt đầu, trạng thái (running/idle/done) |
| F-02 | **Realtime File Watcher** | Backend watch `~/.claude/projects/*/*.jsonl`, parse sự kiện mới, push update qua WebSocket tới frontend — độ trễ ≤2 giây |
| F-03 | **Token Usage Per Session** | Hiển thị token input/output/cache cho mỗi session hiện tại và gần nhất |
| F-04 | **SQLite Ingestion** | Ghi mọi sự kiện token usage vào SQLite local để lưu lịch sử dài hạn |

### P1 — Quan trọng, cần có trong sprint 1

| ID | Feature | Mô tả |
|---|---|---|
| F-05 | **Token Analytics Chart** | Biểu đồ token usage theo ngày/tuần/tháng; filter theo agent/session; hiển thị tổng và breakdown input/output |
| F-06 | **Session History List** | Danh sách session đã kết thúc: agent, task, tổng token, thời gian; có thể lọc theo ngày |
| F-07 | **Account Switcher** | UI quản lý danh sách tài khoản (tên hiển thị + API key), chọn tài khoản active, lưu vào file local với mã hoá nhẹ (XOR/base64 hoặc tương đương đủ để không để lộ plaintext) |
| F-08 | **Active Account Indicator** | Header dashboard luôn hiển thị tài khoản đang dùng; cảnh báo nếu không có tài khoản active |

### P2 — Nice-to-have, có thể lùi sang sprint 2

| ID | Feature | Mô tả |
|---|---|---|
| F-09 | **Token Cost Estimate** | Tính ước tính chi phí USD từ token count (dựa trên pricing Anthropic hiện tại, config thủ công) |
| F-10 | **Alert: High Token Session** | Cảnh báo (badge/màu đỏ) khi 1 session vượt ngưỡng token cấu hình (VD: >50k tokens) |
| F-11 | **Export CSV** | Xuất lịch sử token usage ra CSV để import vào Excel/Google Sheets |
| F-12 | **Dashboard Config UI** | Màn hình cài đặt: cấu hình ngưỡng cảnh báo token, giá model, polling interval |

---

## Acceptance Criteria (mức cao — BA chi tiết hóa)

- [ ] **AC1:** Khi có Claude Code session mới bắt đầu, Agent Status Panel cập nhật trong vòng 2 giây không cần refresh tay.
- [ ] **AC2:** Token usage (input/output/cache) hiển thị đúng với giá trị trong file `.jsonl` tương ứng.
- [ ] **AC3:** Dữ liệu token của mọi session được lưu vào SQLite và tồn tại sau khi restart dashboard.
- [ ] **AC4:** Biểu đồ hiển thị đúng tổng token theo ngày trong 30 ngày gần nhất.
- [ ] **AC5:** Chuyển đổi tài khoản thành công — tài khoản active mới hiển thị ngay trên header.
- [ ] **AC6:** API key lưu trong file config không phải plaintext (tối thiểu encode/xor).
- [ ] **AC7:** Dashboard khởi động bằng 1 lệnh duy nhất từ thư mục project, không báo lỗi.

---

## Metric đo lường thành công

| Metric | Mục tiêu |
|---|---|
| Độ trễ cập nhật agent status | ≤ 2 giây sau khi `.jsonl` có entry mới |
| Thời gian khởi động dashboard | < 5 giây từ lệnh start đến UI hiển thị |
| Token usage drift (so với `.jsonl`) | 0% sai lệch — phải khớp chính xác |
| Adoption | Developer mở dashboard ≥ 1 lần/ngày trong tuần đầu sau launch |
| Không lộ API key | Kiểm tra file config: không có plaintext API key |

---

## Kiến trúc tổng quan (gợi ý — TL xác nhận ở Bước 2.1)

```
~/.claude/projects/*/*.jsonl  ──file-watch──►  Backend (Python/FastAPI)
                                                    │
                                              SQLite (lịch sử)
                                                    │
                                             WebSocket Server
                                                    │
                                         Frontend (React hoặc Vanilla JS)
                                         chạy trên localhost:PORT
```

- **Backend:** Python (FastAPI + watchfiles hoặc watchdog) — đơn giản, dễ cài, phù hợp task I/O-heavy
- **Frontend:** React + Vite (nếu cần chart phức tạp) hoặc Vanilla HTML/JS + chart.js (nếu muốn zero-build)
- **Storage:** SQLite local, file `~/.claude/agent-dashboard/history.db`
- **Account config:** File `~/.claude/agent-dashboard/accounts.enc` (mã hoá nhẹ)
- **Port:** localhost:7770 (mặc định, config được)

---

## Rủi ro / Câu hỏi mở

| # | Rủi ro / Câu hỏi | Mức độ | Gợi ý xử lý |
|---|---|---|---|
| R1 | Format `.jsonl` của Claude Code có thể thay đổi khi Anthropic update → parser bị vỡ | Medium | Defensive parsing: bỏ qua field lạ, log warning thay vì crash |
| R2 | File `.jsonl` đang được Claude Code ghi đồng thời → đọc partial line | Low | Đọc theo line-by-line với retry khi parse JSON fail |
| R3 | SQLite file lock nếu nhiều process cùng ghi | Low | WAL mode cho SQLite; chỉ 1 backend process ghi |
| Q1 | Giá token Anthropic thay đổi thường xuyên — F-09 có nên fetch API pricing hay config thủ công? | — | Config thủ công (P2 feature, không cần realtime pricing) |
| Q2 | "Account switching" chỉ lưu danh sách hay thực sự apply vào CLAUDE.md/env của Claude Code? | — | Sprint 1: chỉ lưu + hiển thị; BA xác nhận cơ chế apply ở Bước 1.2 |
| Q3 | Có cần dark mode không? | — | Nice-to-have P3, không block MVP |

---

## Out of Scope (không làm trong phạm vi này)

- Remote access từ máy khác trong mạng LAN
- Notification hệ thống (Windows toast/tray icon)
- Integration với monitoring platform bên ngoài (Datadog, Grafana Cloud...)
- Plugin cho VS Code / IDE
- Quản lý prompt / codebase agent
- Authentication / login dashboard
- Tự động stop/restart agent từ dashboard
- Multi-tenant / SaaS

---

*Tài liệu này phục vụ Business Analyst (Bước 1.2) để chi tiết hóa User Story + AC, và UI/UX Designer (Bước 1.3) để thiết kế wireframe.*
