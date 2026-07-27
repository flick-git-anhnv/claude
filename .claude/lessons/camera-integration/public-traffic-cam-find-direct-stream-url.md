---
category: camera-integration
tags: [traffic-camera, m3u8, hls, opencctv, caltrans, cv2, public-data]
severity: low
created: 2026-07-02
updated: 2026-07-02
project-origin: KZTEK Image Tools (d:\Tool)
---

# Tìm URL stream trực tiếp từ trang web aggregator camera công cộng (opencctv.org, v.v.)

## Tình huống gặp phải

> Người dùng muốn detect YOLO liên tục từ 1 camera giao thông công khai họ tìm thấy trên
> `opencctv.org` (aggregator hiển thị 160,000+ camera công cộng toàn cầu qua bản đồ). Họ đưa
> link dạng `https://opencctv.org/cam/<id>` — là trang web hiển thị player, không phải file
> media. Tab YOLO Detect (`tool/features/detection/tab_yolo.py`) đã có ô "RTSP/HTTP" nhận
> URL stream trực tiếp qua `cv2.VideoCapture`, nhưng cần lấy đúng URL gốc trước.

## Triệu chứng / Lỗi

`cv2.VideoCapture("https://opencctv.org/cam/300482")` → `isOpened()` = `False`. Giống hệt vấn
đề với link YouTube dạng `watch?v=` ([[yt-dlp-youtube-stream-cv2]]) — URL trang web luôn
không mở được trực tiếp bằng cv2, dù trình duyệt phát video bình thường.

## Nguyên nhân gốc rễ (Root Cause)

Trang aggregator là SPA (React) — video thật được load qua JS runtime, không xuất hiện trong
HTML tĩnh (`curl` trang chỉ trả về shell rỗng `<div id="root"></div>`). Một số camera trong hệ
thống được **proxy qua backend riêng** của aggregator (`/api/hls/...` kèm token ký sẵn,
VD `?s=1m6ojdt`) — không nên dùng URL proxy này (vi phạm ToS, có thể hết hạn/đổi token liên
tục). Cần tìm URL **gốc** của cơ quan chủ quản camera (DOT, Freeway Bureau...).

## Giải pháp

1. **Kiểm tra UI của trang trước khi mở DevTools** — nhiều aggregator (opencctv.org) tự hiển
   thị sẵn metadata + link **"Feed URL"** ngay trong sidebar (kèm "Feed type: m3u8", tọa độ,
   trạng thái Active/Inactive). Chuột phải vào link đó → **Copy link address** — nhanh hơn hẳn
   dò Network tab.
2. Nếu không có sẵn "Feed URL": mở DevTools (`F12`) → tab **Network** → filter `hls` hoặc
   `Media` → F5 reload → tìm request lặp lại dạng `.m3u8`/`.ts` → chuột phải → **Copy as cURL**
   để lấy đủ headers (Referer/Origin) phòng khi server chặn hotlink.
3. **Ưu tiên link URL gốc từ cơ quan chủ quản** (vd `wzmedia.dot.ca.gov` — domain chính thức
   của Caltrans) hơn là URL proxy riêng của aggregator (`opencctv.org/api/hls/...`) — ổn định
   lâu dài, không phụ thuộc session/token của bên thứ ba, và không vướng ToS.
4. Verify nhanh bằng Python trước khi cắm vào UI:
   ```python
   import cv2
   cap = cv2.VideoCapture("https://wzmedia.dot.ca.gov/D11/C009_NB_5_JNO_Old_Town.stream/playlist.m3u8")
   print(cap.isOpened(), cap.get(cv2.CAP_PROP_FPS))   # True, fps > 0 → dùng được
   ```
5. Dán thẳng URL `.m3u8` đã verify vào ô **RTSP / HTTP** sẵn có trong dialog Video Detect —
   **không cần sửa code gì thêm**, pipeline `cv2.VideoCapture(source)` đã tổng quát đủ để nhận
   HLS/RTSP/HTTP mp4/webcam.

## Áp dụng lại (How to reuse)

- Gặp link dạng trang web hiển thị 1 camera (aggregator, dashboard giao thông...) → luôn hỏi
  "có link Feed URL / Direct stream URL không" trước khi tự đi dò Network tab
- `cap.get(cv2.CAP_PROP_FRAME_COUNT)` với live HLS trả về số âm khổng lồ (garbage, không phải
  lỗi) — code seek bar hiện tại đã tự loại bằng check `if total_f > 0`, không cần xử lý thêm
- Domain gốc là dấu hiệu tốt để đánh giá độ tin cậy: `*.dot.ca.gov`, `*.freeway.gov.tw` là domain
  chính phủ — ổn định, công khai hợp pháp; domain proxy của aggregator có thể đổi cấu trúc bất
  kỳ lúc nào

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đừng cố dò/brute-force API nội bộ của aggregator site (kiểu `/api/cameras/<id>`,
  `/api/camera/<id>`) khi không public — dễ dính rate-limit/chặn IP và không đúng mục đích sử
  dụng công khai của họ
- ⚠️ URL proxy có token (`?s=xxxxx`) thường **hết hạn theo phiên trình duyệt** — không lưu lại
  dùng lâu dài, phải lấy lại URL gốc (domain chính chủ) nếu muốn ổn định
- ⚠️ Camera "Status: Active" trên trang aggregator không đảm bảo nguồn gốc đang sống — có thể
  timeout ở origin dù aggregator vẫn hiển thị UI bình thường (đã gặp: 1 cam Colorado + 1 cam
  Đài Loan trả `503`/`ERR_CONNECTION_TIMED_OUT` ở request gốc dù trang vẫn load)

## Tham chiếu

- Lesson liên quan: [[yt-dlp-youtube-stream-cv2]] — cùng nguyên tắc "resolve URL trang web →
  URL media trực tiếp" nhưng dùng yt-dlp cho YouTube; lesson này dùng thao tác thủ công/DevTools
  cho các aggregator không có API resolve công khai
- Project liên quan: KZTEK Image Tools (`d:\Tool`) — `tool/features/detection/tab_yolo.py`,
  ô "RTSP / HTTP" trong dialog `_open_video_detect`
- Ví dụ URL đã verify hoạt động: `https://wzmedia.dot.ca.gov/D11/C009_NB_5_JNO_Old_Town.stream/playlist.m3u8`
