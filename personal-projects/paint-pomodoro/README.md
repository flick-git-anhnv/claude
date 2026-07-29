# Paint Pomodoro

Chrome extension (Manifest V3) cá nhân — timer Pomodoro chiếm màn hình khi bạn
nghỉ, dần hé lộ một bức tranh thật từ The Met Museum (hoặc ảnh bạn tự chọn).

## Tính năng

- Timer Work/Rest cấu hình được (mặc định 25/5 phút), chạy nền qua `chrome.alarms`
  nên vẫn đúng giờ dù popup đóng.
- Khi vào Rest: overlay toàn màn hình phủ lên tab đang xem, tranh dần hiện ra
  qua hiệu ứng "circle reveal" tăng dần theo thời gian còn lại.
- Quản lý task: thêm/hoàn thành/xóa task, chọn task đang làm cho phiên hiện tại.
- Lịch sử: đếm số phiên hoàn thành mỗi ngày + tổng phút tập trung + danh sách
  phiên gần nhất kèm task.
- Nguồn tranh tùy chỉnh: The Met Museum (ngẫu nhiên qua Open Access API),
  danh sách URL ảnh tự nhập, hoặc ảnh tải lên từ máy (lưu cục bộ, tối đa 10 ảnh).

## Cài đặt (chế độ Developer — chưa publish lên Chrome Web Store)

1. Mở Chrome → `chrome://extensions`.
2. Bật **Developer mode** (góc trên bên phải).
3. Bấm **Load unpacked** → chọn thư mục `paint-pomodoro/` này.
4. Ghim icon 🍅 lên thanh công cụ để dùng nhanh.

## Cấu trúc

```
paint-pomodoro/
├── manifest.json     Khai báo extension (MV3)
├── background.js     Service worker: state machine timer + fetch tranh Met
├── content.js        Inject vào tab đang xem: vẽ overlay reveal tranh
├── content.css        Style overlay
├── popup.html/js/css  UI: Timer / Tasks / History / Settings
└── icons/              Icon 16/32/48/128px
```

## Ghi chú kỹ thuật

- State lưu ở `chrome.storage.local` (`state`, `tasks`, `history`, `settings`,
  `metCache`) — popup và content script đọc trực tiếp, không cần message liên tục.
- `chrome.alarms` đảm bảo chuyển pha Work↔Rest đúng giờ kể cả khi service worker
  bị Chrome tạm ngưng.
- Ảnh Met lấy qua Open Access API (`collectionapi.metmuseum.org`), cache danh
  sách `objectID` 7 ngày để giảm số lần gọi `search`.
- Đây là dự án cá nhân/thử nghiệm — không theo quy trình multi-agent PRD/TDD
  đầy đủ của KZTEK.

## Việc có thể làm tiếp (chưa làm trong bản này)

- Đóng gói `.crx`/publish lên Chrome Web Store.
- Thông báo desktop khi chuyển pha (cần thêm permission `notifications`).
- Đồng bộ task/history qua `chrome.storage.sync` giữa nhiều máy.
