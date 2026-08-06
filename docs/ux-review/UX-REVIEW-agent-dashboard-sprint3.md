# UX/UI Review Report — Agent Dashboard Sprint 3

**App / Module:** Agent Dashboard (`tools/agent-dashboard/`) — Sprint 3 (FR-001 Pipeline view, FR-002 %Context badge, FR-003 Session title, BUG-003 Invalid Date)
**Reviewer:** UX/UI Reviewer Agent
**Ngày review:** 2026-08-06
**Môi trường:** Local — Backend port 7770 (uvicorn), Frontend build dist/ served cùng backend
**Build / Commit:** `79f36c7` (layout fix wrap), merge Sprint 3 qua commit `e2fe5a5`
**Tổng số màn hình review:** 4 (Agents view — Theo Agent, Agents view — Theo Dự án, Pipeline 6 bước, Pipeline 36 bước + scrolled list)
**Kết quả tổng quan:** ✅ Pass (2 Medium, 0 High, 0 Critical)

---

## Tóm tắt phát hiện

| Mức độ | Số lượng |
|--------|---------|
| 🔴 Critical (chặn release) | 0 |
| 🟠 High (ảnh hưởng UX đáng kể) | 0 |
| 🟡 Medium (khó chịu nhưng dùng được) | 2 |
| 🟢 Low (polish / nice-to-have) | 1 |

---

## Chi tiết từng màn hình

### 1. Agents View — Theo Agent (toàn bộ danh sách)

**Screenshot:** `screenshots/2026-08-06-sprint3/dashboard-pipeline-main.png`

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | ✅ | Danh sách session theo thứ tự hợp lý, header "Agents đang chạy" rõ ràng, toggle Theo Agent / Theo Dự án dễ nhận biết |
| C2 Không chồng chéo | ✅ | Không phát hiện overlap giữa các SessionCard |
| C3 Hiển thị đầy đủ | ✅ | Tên session, token info, context badge, pipeline đều hiển thị không bị clip |
| C4 Typography nhất quán | ✅ | Heading navy, body text rõ, monospace cho token counts, badge caption nhỏ hơn đúng phân cấp |
| C5 Màu sắc & Brand | ✅ | Navy #251C53 header/sidebar, Cam #F05922 badge RUNNING và active pipeline station, IDLE badge dùng màu mờ hơn — đúng palette KZTEK |
| C6 Trạng thái đặc biệt | ✅ | RUNNING: orange badge đặc; IDLE: muted badge có viền; Live indicator (xanh lá) góc dưới sidebar; badge context đổi màu đúng ngưỡng |
| C7 Khoảng cách & Alignment | ✅ | Padding đều giữa các card, token row align trái nhất quán |

**Phát hiện:**
- Không có issue nghiêm trọng trên màn hình này.
- IDLE badge hiển thị với kiểu "outline" khác RUNNING "filled" — phân biệt trạng thái tốt.

---

### 2. FR-003 — Tên Session Thân Thiện

**Screenshot:** `screenshots/2026-08-06-sprint3/dashboard-pipeline-main.png` (Session "Kiểm tra KzBadge.axaml preview không hiển thị màu đúng" nhìn thấy rõ)

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | ✅ | Dòng title hiển thị ngay bên dưới header status row, đúng vị trí spec |
| C3 Hiển thị đầy đủ | ✅ | Title dài ("Kiểm tra KzBadge.axaml preview không hiển thị màu đúng") hiển thị đầy đủ, không bị truncate |
| C5 Màu sắc | ✅ | Title dùng màu navy nhạt / body text, phân biệt với subagent badge |

**Phát hiện:**
- [UI-SPR3-001] 🟡 **Fallback title hiển thị dưới dạng "last activity" thay vì dòng tiêu đề riêng biệt:** Các session không có `ai_title` (ví dụ session `agent-aaa12f5e503`) hiển thị "Hoạt động cuối: vừa xong — session agent-aaa12f5e503..." thay vì một dòng tiêu đề `session_id.slice(0,8)` như spec mô tả. Về mặt kỹ thuật là fallback đúng (tránh hiển thị chữ "null"), nhưng về UX sẽ tốt hơn nếu có dòng tiêu đề rõ ràng ngay cả khi chỉ là ID ngắn. Xem screenshot: `dashboard-pipeline-main.png` (session đầu tiên không có title riêng).

---

### 3. FR-002 — Badge %Context Window

**Bằng chứng:** Screenshot `dashboard-pipeline-main.png` + API `/api/sessions` verification

Kết quả kiểm tra theo ngưỡng màu:

| Session (context_pct) | Màu badge quan sát | Đúng spec (navy <70%, cam 70-90%, đỏ >90%) |
|---|---|---|
| 22.6% | Navy (xanh đậm) | ✅ |
| 39.9% – 48.8% | Navy | ✅ |
| 57.3% | Navy | ✅ |
| 82.3% (session 973154ca) | Cam / Orange | ✅ (xác nhận qua screenshot đầu phiên) |
| 69.2% (session agent-ac708) | Navy / approaching threshold | ✅ (dưới 70% → navy) |

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C2 Không chồng chéo | ✅ | Badge nằm đúng cuối dòng token row, không đè lên text khác |
| C3 Hiển thị đầy đủ | ✅ | Progress bar + % text hiển thị đầy đủ |
| C5 Màu sắc | ✅ | Đổi màu đúng ngưỡng 70% và 90% theo palette KZTEK |
| C6 Trạng thái đặc biệt | ✅ | Context 0% (hoặc không có data) không hiển thị badge — đúng spec "Ẩn badge khi =0" |

**Phát hiện:** Không có issue.

---

### 4. FR-001 — Pipeline View (6 bước)

**Screenshot:** `screenshots/2026-08-06-sprint3/dashboard-pipeline-main.png` (Pipeline KzBadge session — 6 steps rõ ràng)

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | ✅ | Pipeline header "Pipeline [6 bước]" rõ ràng, station flow trái → phải tự nhiên |
| C2 Không chồng chéo | ✅ | Stations không đè lên nhau |
| C3 Hiển thị đầy đủ | ✅ | Done stations hiển thị role + description truncated đủ nhận biết; Active station mở rộng full description |
| C4 Typography | ✅ | Station label rõ ràng, description text nhỏ hơn đúng hierarchy |
| C5 Màu sắc | ✅ | Done stations: xám nhạt, mờ 0.65; Active station: cam nền nhạt + viền cam `#F05922` — nổi bật đúng spec |
| C6 Trạng thái | ✅ | Checkmark ✓ trên done stations rõ ràng; dot cam ● trên active station |
| C7 Khoảng cách | ✅ | Connector `──▶` đều nhau, spacing nhất quán |

**Phát hiện:** Không có issue với pipeline ngắn (≤10 steps, single row).

---

### 5. FR-001 — Pipeline View (36 bước, wrap nhiều dòng)

**Screenshot:** Xác nhận qua API `/api/sessions/973154ca/chain` (36 steps) và screenshot phiên đầu (session 973154ca, "Xây dựng UI quản lý agents và token")

**Lưu ý thiết kế quan trọng:** Design spec (DESIGN-agent-dashboard.md §Sprint3 "Chiến lược") yêu cầu:
> "Scroll ngang — toàn bộ stations trong overflow-x: auto. Không wrap 2 dòng, không ẩn bước."

Tuy nhiên commit `79f36c7` đổi implementation sang **flex-wrap nhiều dòng** thay vì scroll ngang.

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | ⚠️ | Wrap nhiều dòng cho 36 steps tạo ra 3 rows → active station (step 35) nằm cuối row 3, user phải trace qua 2 rows mới tìm thấy active; khác với scroll ngang + auto-scroll to active trong spec |
| C2 Không chồng chéo | ✅ | Stations không đè lên nhau dù wrap |
| C3 Hiển thị đầy đủ | ✅ | Tất cả 36 stations đều hiển thị |
| C5 Màu sắc | ✅ | Active station cam nổi bật dù ở row 3 |
| C7 Khoảng cách | ⚠️ | Connector `──▶` ở **cuối mỗi dòng trước khi wrap** trở thành "dangling connector" — trỏ sang phải vào khoảng trống, không kết nối với station nào trong cùng dòng. Nhìn kỳ về mặt trực quan dù về logic vẫn đúng |

**Phát hiện:**
- [UI-SPR3-002] 🟡 **Dangling connector ở cuối mỗi row wrap:** Khi pipeline wrap sang dòng mới, connector `──▶` ở cuối row trước trỏ vào khoảng trống. Đây là kết quả tất yếu khi dùng flex-wrap thay scroll ngang. Gợi ý fix: ẩn connector của station cuối mỗi row, hoặc dùng CSS để hiển thị connector xuống dòng (↵ ) thay vì `──▶`.
- [UI-SPR3-003] 🟢 **Deviation từ design spec:** Design spec quy định scroll ngang để auto-scroll đến active station. Wrap nhiều dòng là tradeoff hợp lý cho pipeline 30+ steps (không cần scroll ngang dài) nhưng mất khả năng auto-scroll. Đề xuất: document lại quyết định này trong design spec, hoặc thêm "Jump to active" button cho pipeline dài.

---

### 6. BUG-003 — Invalid Date

**Bằng chứng:** API `/api/sessions` — started_at fields kiểm tra thực tế:
- `'2026-08-06T08:35:41.954Z'` ✅
- `'2026-08-06T08:26:01.359Z'` ✅
- `'2026-08-05T15:32:43.826Z'` ✅

**Trong UI (screenshot `dashboard-pipeline-main.png`):**
- "Bắt đầu: 15:46:16", "15:45:08", "15:44:38" — định dạng HH:mm:ss, không có "Invalid Date" ✅

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C3 Hiển thị đầy đủ | ✅ | Timestamp hiển thị đúng HH:mm:ss, không có "Invalid Date" trên bất kỳ session nào |
| C6 Trạng thái đặc biệt | ✅ | Session không có started_at rỗng ("") được xử lý đúng ở backend (`_parse_ts('')` → epoch), không lọt lên UI |

**Phát hiện:** BUG-003 đã được fix hoàn toàn. ✅

---

### 7. Agents View — Theo Dự án

**Screenshot:** `screenshots/2026-08-06-sprint3/dashboard-main-default.png` (Theo Dự án view)

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | ✅ | Grouped view rõ ràng theo project path, tổng sessions + tokens hiển thị |
| C2 Không chồng chéo | ✅ | |
| C3 Hiển thị đầy đủ | ✅ | Project path dài không bị cắt không hợp lý |
| C5 Màu sắc | ✅ | Dropdown arrow cam, project heading navy |
| C7 Khoảng cách | ✅ | Hai project rows cách đều nhau |

**Phát hiện:** Không có issue.

---

## Danh sách issue cần fix

| ID | Màn hình | Mô tả | Mức độ | Tiêu chí | Đề xuất fix |
|---|---|---|---|---|---|
| UI-SPR3-001 | Agents / Session Card | Session không có `ai_title` không có dòng tiêu đề riêng biệt — fallback lẫn vào "last activity" text | 🟡 Medium | C1, C3 | Thêm dòng tiêu đề `session_id.slice(0,8)` rõ ràng ngay cả khi không có `ai_title`, phân biệt về style với "last activity" text |
| UI-SPR3-002 | Pipeline / SessionCard | Connector `──▶` ở cuối mỗi row trước khi wrap → "dangling connector" trông kỳ thị giác | 🟡 Medium | C7 | Ẩn connector của station cuối mỗi row (CSS: `last-child-in-row:after { display: none }`) hoặc đổi connector sang ký hiệu thích hợp cho wrap |
| UI-SPR3-003 | Pipeline / SessionCard | Design spec quy định scroll ngang; implementation dùng flex-wrap. Mất auto-scroll đến active station | 🟢 Low | C1 | Cân nhắc thêm "Jump to active" indicator / button cho pipeline dài, và cập nhật design spec để phản ánh quyết định wrap |

---

## Kết luận & Đề xuất

Sprint 3 đã thực hiện đủ 4 mục tiêu (FR-001 Pipeline view, FR-002 %Context badge, FR-003 Session title, BUG-003 Invalid Date fix). Không có issue Critical hoặc High. Hai issue Medium (UI-SPR3-001 fallback title không rõ ràng, UI-SPR3-002 dangling connector khi wrap) không chặn sử dụng nhưng nên được fix trong sprint tiếp để polish UX. Issue Low (UI-SPR3-003 deviation từ design spec về scroll vs wrap) cần được document lại trong DESIGN doc để giữ consistency.

**Kết luận: Sprint 3 sẵn sàng đưa vào sử dụng.** Chức năng cốt lõi hoạt động đúng, brand KZTEK được áp dụng nhất quán, không có lỗi chặn release.
