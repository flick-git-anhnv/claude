# UX/UI Review Report — Agent Dashboard

**App / Module:** Agent Dashboard (tools/agent-dashboard)
**Reviewer:** UX/UI Reviewer Agent
**Ngày review:** 2026-08-06
**Môi trường:** Local | Build: commit affb0c6 (post-merge bước 3.3)
**Backend:** FastAPI uvicorn port 7770 | Frontend: Vite/React/TS build (dist/)
**Tổng số màn hình review:** 5 màn hình chính + trạng thái đặc biệt
**Kết quả tổng quan:** ⚠️ Cần cải thiện — 2 issue High cần fix trước QA

---

## Tóm tắt phát hiện

| Mức độ | Số lượng |
|--------|---------|
| 🔴 Critical (chặn release) | 0 |
| 🟠 High (ảnh hưởng UX đáng kể) | 2 |
| 🟡 Medium (khó chịu nhưng dùng được) | 2 |
| 🟢 Low (polish / nice-to-have) | 2 |

---

## Chi tiết từng màn hình

### Màn hình 1: Agent Status Panel

**Screenshot:** `screenshots/2026-08-05/agents-panel-default.png`

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | ✅ | Sidebar + main content rõ ràng; header cố định đúng design spec |
| C2 Không chồng chéo | ✅ | Các card không overlap, token row hiển thị sạch |
| C3 Hiển thị đầy đủ | ⚠️ | "NaNh trước" — relative time hiển thị NaN cho phần lớn session cards (xem UI-001) |
| C4 Typography nhất quán | ✅ | Font size, weight đúng spec; monospace token values hiển thị đúng |
| C5 Màu sắc & Brand | ✅ | Header Navy #251C53, RUNNING badge Cam #F05922, sidebar đúng màu |
| C6 Trạng thái đặc biệt | ⚠️ | RUNNING count hiển thị 62–240+ sessions từ nhiều tháng trước (xem UI-002) |
| C7 Khoảng cách & Alignment | ✅ | Padding/margin đều; left border Cam 3px trên sidebar item active đúng spec |

**Phát hiện:**
- [UI-001] 🟠 Relative time hiển thị "NaNh trước" (NaN hours ago) trên tất cả agent card có session cũ. Session hiện tại (~55s trước) hiển thị đúng, nhưng các session từ ngày trước đều bị "NaNh trước". Nguyên nhân: JavaScript `Date` parse thất bại với format timestamp trả về từ API.
- [UI-002] 🟠 Agent panel hiển thị 62–240+ sessions RUNNING bao gồm các session idle hàng trăm giờ (ví dụ: "205h 13m trước", "246h 6m trước"). Ngưỡng DONE >300s không được áp dụng khi backend khởi động lại cho các session cũ trong DB. Gây confusing — user thấy hàng trăm RUNNING agents khi thực tế chỉ có 1–2 đang chạy.

---

### Màn hình 2: Token Analytics

**Screenshot:** `screenshots/2026-08-05/token-analytics-default.png`

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | ✅ | Filter bar → Chart → Summary cards → Detail table — luồng logic tốt |
| C2 Không chồng chéo | ✅ | Không có overlap |
| C3 Hiển thị đầy đủ | ✅ | Summary cards hiển thị đủ: Tổng Input 972.467, Tổng Output 30.595.305, 219 sessions |
| C4 Typography nhất quán | ✅ | Heading H2 Navy, caption đúng |
| C5 Màu sắc & Brand | ⚠️ | Chart có 4 series (Input/Output/Cache Write/Cache Read). Output (cam) gần như vô hình do giá trị quá nhỏ so với Cache Read (hàng triệu token). Màu Input bars thiên navy-light thay vì Navy đậm #251C53 (xem UI-003) |
| C6 Trạng thái đặc biệt | ✅ | Filter buttons đổi state đúng (active: nền Navy, inactive: nền nhạt) |
| C7 Khoảng cách & Alignment | ✅ | Summary cards 3 cột đều spacing; table header Navy đúng spec |

**Phát hiện:**
- [UI-003] 🟡 Chart bar màu Output Tokens (cam) không phân biệt được do giá trị quá nhỏ (30K) so với Cache Read (hàng triệu). Với data thực tế, chart gần như chỉ hiển thị Cache Read. Đề xuất: thêm scale log hoặc chia thành 2 chart riêng (Input/Output vs Cache).
- Design spec chỉ hiển thị 2 series (Input + Output) nhưng implementation thêm Cache Write + Cache Read — đây là enhancement hữu ích nhưng gây scale problem.

---

### Màn hình 3: Session History

**Screenshot:** `screenshots/2026-08-05/session-history-default.png`

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | ✅ | Filter → Table layout rõ ràng |
| C2 Không chồng chéo | ✅ | |
| C3 Hiển thị đầy đủ | ✅ | "Hiển thị 78 session" caption đúng vị trí góc phải |
| C4 Typography nhất quán | ✅ | |
| C5 Màu sắc & Brand | ✅ | Table header Navy #251C53 white text; "Ended" badge green #22C55E đúng |
| C6 Trạng thái đặc biệt | ✅ | Filter date range hoạt động; "Lọc" button Navy đúng |
| C7 Khoảng cách & Alignment | ✅ | |

**Ghi chú:** Cột "Task Description" theo design spec không có — thay bằng "Task / Session ID" hiển thị session ID rút gọn và project path. Là deviation nhỏ nhưng chấp nhận được vì session ID là thông tin có ích hơn để debug.

---

### Màn hình 4: Account Manager — Empty State

**Screenshot:** `screenshots/2026-08-05/account-manager-empty.png`

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | ✅ | Empty state icon + text + CTA button căn giữa đúng |
| C2 Không chồng chéo | ✅ | |
| C3 Hiển thị đầy đủ | ✅ | "Chưa có tài khoản nào" + caption + button đủ |
| C4 Typography nhất quán | ✅ | H3 Navy, caption #4A3F8C đúng |
| C5 Màu sắc & Brand | ⚠️ | Empty state icon hiển thị màu navy/tím đậm thay vì #B8B3D6 (light gray) theo design spec (xem UI-004) |
| C6 Trạng thái đặc biệt | ✅ | Header banner "Chưa có tài khoản active" hiển thị đúng màu Cam #F05922 |
| C7 Khoảng cách & Alignment | ✅ | |

**Phát hiện:**
- [UI-004] 🟢 Icon user/person trong empty state hiển thị màu navy/purple đậm thay vì #B8B3D6 (navy light) theo design spec. Minor visual inconsistency.

---

### Màn hình 5: Account Manager — Có account, trạng thái Active

**Screenshot:** `screenshots/2026-08-05/account-manager-active-badge.png`
**Screenshot:** `screenshots/2026-08-05/account-manager-with-accounts.png`

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | ✅ | Account cards liệt kê rõ; action buttons đúng vị trí |
| C2 Không chồng chéo | ✅ | |
| C3 Hiển thị đầy đủ | ✅ | Tên account, key masked, action buttons đủ |
| C4 Typography nhất quán | ✅ | Account name H3 Navy, key monospace đúng |
| C5 Màu sắc & Brand | ✅ | "ACTIVE" badge cam #F05922 ✓; "Đặt active" btn Navy ✓; "Copy API key" outline ✓; "Xóa" text red ✓ |
| C6 Trạng thái đặc biệt | ⚠️ | Cảnh báo "no-active-account" banner không cập nhật reactive khi account được set active từ phiên khác qua WebSocket (xem UI-005) |
| C7 Khoảng cách & Alignment | ✅ | Spacing đồng đều; button row căn trái đúng |

**Phát hiện:**
- [UI-005] 🟡 Khi account được set active qua WebSocket (ví dụ từ API hoặc từ tab khác), header cập nhật ngay lập tức (WebSocket reactive đúng) nhưng Account Manager page vẫn hiển thị warning banner cũ và account card chưa show ACTIVE badge cho đến khi user navigate đi và quay lại. Reactive update cho Account Manager page component chưa được implement.
- [UI-006] 🟢 Không có nút "Reveal" (hiển thị full API key tạm thời) trong UI dù backend đã implement endpoint `/api/accounts/{id}/reveal`. Nếu đây là tính năng theo spec, cần bổ sung button vào account card.

---

### Màn hình 6: Header — Indicator với Active Account

**Screenshot:** `screenshots/2026-08-05/header-with-active-account.png`

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | ✅ | Logo + title trái, account indicator phải — đúng spec |
| C2 Không chồng chéo | ✅ | |
| C3 Hiển thị đầy đủ | ✅ | "KZTEK Test Account / sk-ant-api03-****7890" hiển thị đủ |
| C4 Typography nhất quán | ✅ | Account name white 14px bold, key monospace #B8B3D6 đúng spec |
| C5 Màu sắc & Brand | ✅ | Green dot #22C55E, header bg #251C53 đúng |
| C6 Trạng thái đặc biệt | ✅ | "Chưa có tài khoản active" banner cam khi không có account — đúng spec |
| C7 Khoảng cách & Alignment | ✅ | |

---

## Danh sách issue cần fix

| ID | Màn hình | Mô tả | Mức độ | Tiêu chí | Đề xuất fix |
|---|---|---|---|---|---|
| UI-001 | Agent Status Panel | "NaNh trước" — JavaScript Date parse lỗi với timestamp cũ, relative time hiển thị NaN | 🟠 High | C3 | Debug `formatRelativeTime()` trong frontend, xử lý các format ISO8601 có timezone; thêm fallback "dd/MM HH:mm" khi diff > 24h |
| UI-002 | Agent Status Panel | 62–240 sessions cũ (inactive hàng trăm giờ) hiển thị RUNNING. State machine không re-evaluate sessions cũ khi backend restart | 🟠 High | C6 | Backend: khi load sessions từ DB lúc startup, tính lại state dựa trên `last_event_at` vs current time thay vì giữ nguyên state cũ |
| UI-003 | Token Analytics | Output Tokens bar (cam) không phân biệt được do scale chênh lệch với Cache Read | 🟡 Medium | C5 | Thêm option "scale log" hoặc chia 2 chart: Input/Output riêng; Cache riêng |
| UI-004 | Account Manager | Empty state icon màu navy/purple thay vì #B8B3D6 (light gray) theo design spec | 🟢 Low | C5 | Sửa CSS color của icon SVG: `color: #B8B3D6` |
| UI-005 | Account Manager | Account Manager page không cập nhật reactive qua WebSocket khi account active thay đổi | 🟡 Medium | C6 | Subscribe WebSocket event `account_changed` trong AccountManager component, trigger re-fetch/state update khi nhận event |
| UI-006 | Account Manager | Không có "Reveal" button trong UI dù backend đã có endpoint | 🟢 Low | C3 | Bổ sung "Reveal" button ẩn sau xác nhận; self-clear sau 30s nếu muốn |

---

## Kết luận & Đề xuất

**Tổng thể:** Dashboard đạt yêu cầu về brand (Navy/Cam đúng palette KZTEK, layout sidebar + main content theo spec, typography nhất quán). Không có issue Critical.

**Cần fix trước QA (2 High):**
1. **UI-001 (NaNh trước)** — Ảnh hưởng trực tiếp readability của Agent Status Panel; mọi session cũ hơn vài giờ hiển thị thời gian sai.
2. **UI-002 (RUNNING inflated)** — Gây misleading nghiêm trọng: user thấy 200+ "đang chạy" khi thực tế chỉ có 1–2 session thật sự active. Root cause: backend startup không re-evaluate state của session cũ từ DB.

**Có thể để QA test song song (Medium):**
- UI-003, UI-005 không chặn functionality, có thể ghi nhận trong QA test plan để verify behavior.

**Backlog (Low):**
- UI-004, UI-006 là polish — không ảnh hưởng workflow chính.

---

## Phụ lục: Screenshots đã chụp

| File | Nội dung |
|------|---------|
| `screenshots/2026-08-05/agents-panel-default.png` | Agent Status Panel — 126 sessions RUNNING (dữ liệu thật) |
| `screenshots/2026-08-05/token-analytics-default.png` | Token Analytics — filter 30 ngày, chart + summary + table |
| `screenshots/2026-08-05/session-history-default.png` | Session History — 78 sessions, filter bar, table |
| `screenshots/2026-08-05/account-manager-empty.png` | Account Manager — Empty state (no accounts) |
| `screenshots/2026-08-05/account-manager-with-accounts.png` | Account Manager — 2 accounts, warning banner, no active |
| `screenshots/2026-08-05/account-manager-active-badge.png` | Account Manager — ACTIVE badge đúng sau set active |
| `screenshots/2026-08-05/account-manager-active-set.png` | Account Manager — Ngay sau set active qua API (banner stale) |
| `screenshots/2026-08-05/header-with-active-account.png` | Header indicator — có active account (WebSocket update OK) |
