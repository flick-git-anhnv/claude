# UX/UI Review Report — Sprint 5 Agent Dashboard

**App / Module:** Agent Dashboard (tools/agent-dashboard) — Sprint 5
**Reviewer:** UX/UI Reviewer Agent
**Ngay review:** 2026-08-07
**Môi trường:** Local | http://127.0.0.1:7770 | build Sprint 5 (frontend dist: 2026-08-07 09:04)
**Tổng số màn hình review:** 4 (Agents/Theo Session, Agents/Tổng hợp, Accounts, Header)
**Kết quả tổng quan:** PASS — Không có issue Critical hoặc High. QA có thể tiếp tục.

---

## Tóm tắt phát hiện

| Mức độ | Số lượng |
|--------|---------|
| Critical (chặn release) | 0 |
| High (ảnh hưởng UX đáng kể) | 0 |
| Medium (khó chịu nhưng dùng được) | 1 |
| Low (polish / nice-to-have) | 1 |

---

## Môi trường & Cách chạy

- **Backend:** `python -m agent_dashboard` tại `tools/agent-dashboard/backend/` — port 7770
- **Frontend:** Build từ `npm run build` trong `frontend/` — served qua backend tại `http://127.0.0.1:7770`
- **Accounts hoạt động:** 2 tài khoản OAuth (`Dungnn`, `anhnv` [ACTIVE])
- **Usage API:** Trả `{"error":"http_429"}` — Anthropic rate-limiting quota endpoint trong session này

---

## Chi tiết từng màn hình

---

### 1. Agents Page — Chế độ "Theo Session" (Pipeline view)

**Screenshot:** `screenshots/2026-08-07/agents-session-view.png`

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | PASS | Toggle nằm đúng góc phải, Pipeline dưới session card, Dispatcher đứng đầu chain |
| C2 Không chồng chéo | PASS | Không có element nào đè lên nhau |
| C3 Hiển thị đầy đủ | PASS | Tất cả text hiển thị đầy đủ, không bị cắt |
| C4 Typography nhất quán | PASS | Font size nhất quán: heading 16px, body 14px, token 12px mono |
| C5 Màu sắc & Brand | PASS | Dispatcher node Navy #251C53, RUNNING badge cam #F05922, không dùng đỏ tươi |
| C6 Trạng thái đặc biệt | PASS | Running session hiển thị rõ, Dispatcher node done state mờ hơn khi session kết thúc |
| C7 Khoảng cách & Alignment | PASS | Padding đều, cards cùng height, arrow connector thẳng hàng |

**Phát hiện tốt:**
- FR-004 Dispatcher Node: "Claude (Dispatcher)" luôn đứng đầu chain, nền Navy #251C53, KHÔNG có nút "Xem lịch sử" (đúng spec)
- FR-005 Toggle: "Theo Session" / "Tổng hợp" hiển thị đúng, "Theo Session" active (navy) / inactive (light)
- BUG-005 Fix: UX/UI Reviewer card (call_count=1) có nút "Xem lịch sử" — FIX HOẠT ĐỘNG ĐÚNG

---

### 2. Agents Page — Chế độ "Tổng hợp" (Aggregate view)

**Screenshot:** `screenshots/2026-08-07/agents-tonghop-view2.png`

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | PASS | Bảng aggregate rõ ràng, subtitle "355 sessions · 1038 lượt gọi" đầy đủ |
| C2 Không chồng chéo | PASS | Không có overlap |
| C3 Hiển thị đầy đủ | PASS | Tất cả 6 cột hiển thị: Vai trò, Lần gọi, Sessions, Token IN, Token OUT, Active |
| C4 Typography nhất quán | PASS | Header bảng bold white, body regular dark — phân cấp rõ |
| C5 Màu sắc & Brand | PASS | Header bảng Navy #251C53, "X đang chạy" cam #F05922, không có màu lạ |
| C6 Trạng thái đặc biệt | PASS | Active: "2 đang chạy" cam; Inactive: "—"; Search và dropdown filter hoạt động |
| C7 Khoảng cách & Alignment | PASS | Row height đều, dividers nhất quán |

**Phát hiện tốt:**
- Bảng sắp xếp đúng theo Lần gọi giảm dần (Senior Developer 389 đứng đầu)
- "Tìm vai trò..." search box và "Tất cả thời gian" dropdown hiển thị đúng vị trí
- Active indicator dùng cam #F05922 — đúng brand (không dùng đỏ tươi)
- Toggle switch giữa 2 chế độ mượt, không flash

---

### 3. Account Manager Page (/accounts)

**Screenshot:** `screenshots/2026-08-07/accounts-page.png`

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | PASS | Header + security banner + cards theo luồng từ trên xuống dưới |
| C2 Không chồng chéo | PASS | Không overlap |
| C3 Hiển thị đầy đủ | PASS | "ACTIVE" badge, OAuth badge, masked key, "Còn 28 ngày" hiển thị đủ |
| C4 Typography nhất quán | PASS | "QUOTA CLAUDE PRO" uppercase label rõ, error text nhỏ hơn |
| C5 Màu sắc & Brand | PASS | "ACTIVE" badge cam, "OAuth" badge Navy, nút "Đặt active" Navy |
| C6 Trạng thái đặc biệt | WARN | Khi quota API trả 429: hiện "Không lấy được quota" — OK nhưng text khác spec |
| C7 Khoảng cách & Alignment | PASS | Padding card đều, divider giữa section rõ |

**Phát hiện:**
- [UI-002] LOW: AccountCard hiện "Không lấy được quota" (xám nhỏ) khi quota API lỗi 429. Design spec (A3) nói bars sẽ ẩn khi null, nhưng không chỉ định text cụ thể. Text này là UX addition hợp lý, chưa gây nhầm lẫn. Cân nhắc thêm retry timestamp hoặc tooltip giải thích lý do.

---

### 4. AppHeader — UsageBar (Phần A)

**Screenshot:** `screenshots/2026-08-07/header-app-area.png` (crop từ agents-session-view.png)

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | PASS | Logo trái, account info phải — nhất quán |
| C2 Không chồng chéo | PASS | Không overlap |
| C3 Hiển thị đầy đủ | WARN | Header chỉ hiện 1 dòng (không có UsageBar) — thiếu null indicator "--" |
| C4 Typography nhất quán | PASS | "anhnv" + masked key đọc được |
| C5 Màu sắc & Brand | PASS | Navy header, white text |
| C6 Trạng thái đặc biệt | WARN | UsageBar ẩn hoàn toàn khi error — spec nói phải hiện "--" |
| C7 Khoảng cách & Alignment | PASS | Header 56px (đúng khi không có bars) |

**Phát hiện:**
- [UI-001] MEDIUM: AppHeader UsageBar ẩn hoàn toàn khi quota API trả về lỗi (http_429). Design spec (A2) nói trạng thái null/error phải hiện "──" + tooltip "Đang lấy quota...". Tuy nhiên code (`AppHeader.tsx` line 77) định nghĩa `showBars = usageLoading || (usage != null && usage.error == null)` — khi error, showBars=false và không render gì cả. `UsageBar.tsx` line 129 cũng `return null` khi có error.

  **Hệ quả:** Người dùng không biết quota đang được tải hay là account không có quota. Đặc biệt khó nhận ra sự khác biệt giữa "API key account" (không có quota) và "OAuth account với quota đang lỗi".

  **Root cause:** Code comment trong `UsageBar.tsx` ghi "usage.error = other → return null (ẩn lặng lẽ, không crash)" — quyết định thay đổi từ spec. Cần align lại với spec hoặc cập nhật spec.

  **Đề xuất:** Khi `usage.error != null` (bất kỳ lỗi nào), vẫn render UsageBar container với text "--" và tooltip. Chỉ `return null` khi account là `api_key` type.

---

### 5. Chi tiết Dispatcher Node (Close-up)

**Screenshot:** `screenshots/2026-08-07/dispatcher-node-crop.png`

Xác nhận từ crop:
- "Claude (Dispatcher)" — label đúng spec
- Navy bg — đúng spec
- Icon: emoji/icon tại góc trái — có thể là 🧠 emoji render nhỏ trên resolution cao (không phải vấn đề nghiêm trọng)
- "97.2K tokens" — hiển thị token tổng
- Pipeline label "8 vai trò" — đúng count
- Không có "Xem lịch sử" — ĐÚNG spec (Dispatcher không có history)

---

### 6. BUG-005 Fix Confirmation

**Screenshot:** `screenshots/2026-08-07/uxr-running-card.png`

Xác nhận:
- UX/UI Reviewer card: đang RUNNING, call_count = 1 (lần gọi đầu tiên)
- "Xem lịch sử •" button IS VISIBLE (dấu "•" là live indicator)
- Trước khi fix: button ẩn khi call_count=1 (`history.length > 1`)
- Sau khi fix: button hiển thị khi call_count >= 1 (`history.length >= 1`)
- **BUG-005 FIX CONFIRMED**

---

## Danh sách issue cần fix

| ID | Màn hình | Mô tả | Mức độ | Tiêu chí | Đề xuất fix |
|---|---|---|---|---|---|
| UI-001 | AppHeader | UsageBar ẩn hoàn toàn khi quota API lỗi (429). Spec nói phải hiện "--" + tooltip. | Medium | C3, C6 | Khi `usage.error != null`, vẫn render container với "--". Chỉ return null khi account là api_key. |
| UI-002 | AccountCard | Text "Không lấy được quota" không có trong spec. Thiếu retry hint. | Low | C6 | Thêm timestamp "Thử lại lúc X" hoặc icon refresh. Text hiện tại vẫn chấp nhận được. |

---

## Kết luận & Đề xuất

Sprint 5 đạt chất lượng PASS, sẵn sàng để QA tiến hành smoke test. Không có issue Critical hay High nào cản trở release.

**3 điểm nổi bật đã xác nhận hoạt động tốt:**
1. FR-004 Dispatcher Node — Navy bg, không có history button, luôn đứng đầu chain.
2. FR-005 Toggle — Chuyển đổi mượt, Tổng hợp table đầy đủ dữ liệu và đúng format.
3. BUG-005 Fix — Nút "Xem lịch sử" hiển thị khi call_count=1 (đã sửa điều kiện >= thay vì >).

**1 điểm cần theo dõi cho sprint tiếp:**
- UI-001 (Medium): AppHeader UsageBar cần cân nhắc hiện "--" indicator thay vì ẩn hoàn toàn khi error. Tuy nhiên không ảnh hưởng đến chức năng core và có thể test đầy đủ hơn khi quota API không còn bị rate-limit.

**Note cho QA (bước 8.7):** Quota API đang bị rate-limit (429). Các TC liên quan đến happy path UsageBar (bars hiển thị %) sẽ không pass trong môi trường hiện tại. Cần test lại khi rate-limit được giải phóng hoặc dùng mock data.
