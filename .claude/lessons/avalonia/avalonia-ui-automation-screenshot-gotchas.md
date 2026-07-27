---
category: avalonia
tags: [ui-automation, screenshot, win32, keybd_event, postmessage, documentation]
severity: medium
created: 2026-07-26
updated: 2026-07-26
project-origin: iPGSv4 (CCU Avalonia)
---

# Automation chụp màn hình app Avalonia bằng Win32: 4 gotcha phải biết

## Tình huống gặp phải

Documentation Writer cần chụp toàn bộ màn hình app Avalonia (iPGSv4 CCU) bằng PowerShell + Win32 API (SetForegroundWindow, mouse_event, keybd_event, PostMessage) để làm user manual — không có framework automation chuyên dụng.

## Triệu chứng / Lỗi

1. Nhấn **Enter** khi focus đang ở một Button thường (đã Tab tới) → form ĐÓNG NGAY thay vì bấm nút đó.
2. **mouse_event wheel** (0x0800) gửi vào giữa cửa sổ dialog → ScrollViewer KHÔNG cuộn.
3. **Alt+F4 qua keybd_event** đôi khi không đóng được cửa sổ (nhất là khi gọi liên tiếp nhiều cửa sổ) — trước đó cùng kỹ thuật này lại hoạt động.
4. Click chuột mô phỏng rơi vào cửa sổ khác khi cửa sổ đích không ở foreground.

## Nguyên nhân gốc rễ (Root Cause)

1. Avalonia: **Enter kích hoạt nút `IsDefault`** (thường là "Lưu") của Window, KHÔNG phải nút đang giữ keyboard focus. Space mới là phím "bấm nút đang focus" — nhưng nếu đếm Tab sai 1 bước sẽ bấm nhầm nút bên cạnh (Hủy).
2. Wheel event tổng hợp không được Avalonia định tuyến tới ScrollViewer nếu con trỏ/hit-test không đúng — không tin cậy.
3. `SetForegroundWindow` bị Windows chặn (foreground lock) khi process gọi không sở hữu foreground → Alt+F4 rơi vào cửa sổ khác.
4. Như (3) — click theo tọa độ tuyệt đối cần cửa sổ đích thực sự foreground/topmost.

## Giải pháp

1. **Không dùng Enter/Space để bấm nút** — Tab để cuộn control vào khung nhìn, rồi **click chuột theo tọa độ** của nút (đã biết từ ảnh chụp trước đó).
2. **Cuộn form dài bằng phím Tab**: mỗi lần Tab, Avalonia tự scroll control được focus vào view — đếm số Tab rồi chụp. Tin cậy hơn wheel event.
3. **Đóng cửa sổ Avalonia tin cậy nhất: `PostMessage(hwnd, WM_CLOSE=0x0010, 0, 0)`** — không cần foreground, đóng được cả chuỗi dialog chồng nhau (đóng từ dialog trong cùng ra ngoài). Alt+F4 chỉ là phương án phụ.
4. Trước mọi click: `SetWindowPos(TOPMOST)` + `SetForegroundWindow` + sleep 400ms, click xong trả `NOTOPMOST` (pattern trong `temp/manual-ipgsv4/click-win.ps1`).

## Cách phòng tránh sau này

- Khi automation form Avalonia: xác định nút `IsDefault`/`IsCancel` từ AXAML trước — Enter/Esc sẽ kích hoạt chúng bất kể focus.
- Chuỗi đóng nhiều cửa sổ: dùng vòng lặp PostMessage WM_CLOSE theo danh sách HWND (EnumWindows lọc theo PID), delay ~800ms giữa các lần.
- Chụp cửa sổ con (dialog): luôn chụp theo HWND/tiêu đề của chính nó, KHÔNG bám `MainWindowHandle` (Avalonia đổi MainWindowHandle khi cửa sổ con foreground).
