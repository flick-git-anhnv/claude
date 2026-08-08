---
category: reverse-engineering
tags: [pytorch, onnx, model-recovery, arcsoft, architecture-search, batchnorm]
severity: high
created: 2026-08-08
updated: 2026-08-08
project-origin: DecodeTools (model_4_detection.bin architecture recovery, ArcSoft ilocker-android)
---

# Dựng lại kiến trúc CNN từ blob weight thô: khớp TỔNG SỐ THAM SỐ THẬT quan trọng hơn đoán tên kiến trúc

## Tình huống gặp phải

`model_4_detection.bin` (29,846,144 byte, trích xuất tĩnh từ `libarcsoft_face.so` bản
armeabi-v7a, xác nhận PLAINTEXT qua entropy-scan) cần dựng lại đúng kiến trúc PyTorch để
export ONNX không bị NaN. Đã thử nhiều họ kiến trúc đoán mò (YOLOv5-C3...) từ trước, đều
sai. Không có `.param` hay bất kỳ metadata kiến trúc nào đi kèm — chỉ có blob nhị phân thô.

## Triệu chứng / Lỗi

Export ONNX ra NaN toàn bộ output khi build kiến trúc theo phỏng đoán và nạp weight thật
vào — do kiến trúc SAI (số layer/kích thước kênh không khớp cách blob thật được ghi), khiến
việc `reshape`/`slice` weight thật vào layer sai vị trí, tạo ra giá trị điên rồ (BatchNorm
running_var âm hoặc quá lớn) → NaN khi forward.

## Nguyên nhân gốc rễ (Root Cause)

1. Toàn bộ file KHÔNG phải chỉ có weight — có 1 vùng "đuôi" (ở đây: 750KB cuối, byte
   offset 29,078,304 → 29,846,144) là **bảng metadata/anchor** chứa giá trị nguyên
   `0xFFFFFFFF` (sentinel "hết danh sách", đọc nhầm thành float sẽ ra `NaN` thật trong
   chính plaintext gốc — không phải lỗi giải mã, mà là do đọc sai kiểu dữ liệu tại vùng đó).
2. Việc quét thống kê "tìm mảng BatchNorm running_var" (toàn số dương liên tiếp) chỉ đáng
   tin khi độ dài dãy ≥16 (xác suất ngẫu nhiên toàn dương của dãy N phần tử = 0.5^N; N=16
   → 1.5e-5, đủ thấp để loại nhiễu). Dùng ngưỡng ngắn hơn (4-14) tạo ra hàng trăm nghìn
   false positive từ nhiễu conv-weight thông thường — vô dụng để định biên layer.
3. **Insight quyết định**: không cần đoán ĐÚNG TÊN kiến trúc (MobileNet/RetinaFace/YOLO...)
   — chỉ cần dựng 1 kiến trúc THAM SỐ HOÁ (width factor `w`, `head_ch`) thuộc đúng HỌ dạng
   (backbone nhẹ + N head lặp giống hệt nhau — suy từ bằng chứng dynamic capture thật: 5
   khối byte-size giống hệt nhau lặp 5 lần), rồi **grid-search độ rộng kênh sao cho TỔNG SỐ
   THAM SỐ khớp CHÍNH XÁC với số float thật trong vùng weight** (ở đây 7,269,576). Đây là
   ràng buộc CỨNG và có thể verify được — khác hẳn việc đoán shape từng layer riêng lẻ.

## Giải pháp

1. Xác định ranh giới weight/metadata thật bằng cách quét NaN/giá trị cực đoan khi đọc
   toàn file dạng `float32` — vị trí NaN đầu tiên = ranh giới an toàn để cắt vùng weight.
2. Dựng kiến trúc tham số hoá theo HỌ dạng suy từ bằng chứng thật (không phải đoán tên cụ
   thể) — ở đây: `Backbone(w)` + `N_heads x SSHHead(w*16, head_ch)`.
3. Grid-search 2 tham số width (`w`, `head_ch`) để `sum(p.numel() for p in model.parameters())`
   khớp gần đúng nhất với `real_weight_bytes / 4` (giả định float32). Bắt đầu range rộng
   (bậc 10x quanh giá trị đoán ban đầu) vì tổng tham số tăng theo bậc 2 với độ rộng kênh —
   sai lệch nhỏ trong ước lượng ban đầu có thể lệch xa mục tiêu.
4. Nạp toàn bộ float thật TUẦN TỰ vào `model.named_parameters()` theo đúng thứ tự khai báo
   (không xáo trộn) — đây chính là cách ncnn/hầu hết framework serialize weight tuần tự.
5. Verify bằng 2 lớp độc lập: (a) forward pass PyTorch không NaN/Inf, (b) export ONNX rồi
   chạy lại bằng `onnxruntime` (framework khác, engine khác) — không NaN/Inf ở CẢ HAI xác
   nhận kiến trúc + weight thật tương thích, không phải trùng hợp do bug riêng của 1 framework.

## Áp dụng lại (How to reuse)

- Khi có blob weight thô KHÔNG rõ kiến trúc: đừng cố đoán tên kiến trúc gốc trước — dựng
  kiến trúc THAM SỐ HOÁ theo family dạng (số stage, có head lặp hay không, dựa vào bằng
  chứng cấu trúc thật nếu có) rồi search độ rộng kênh khớp TỔNG THAM SỐ. Tổng tham số là
  con số DỄ LẤY và KHÓ SAI (chỉ cần biết đúng ranh giới weight/non-weight), trong khi đoán
  shape từng layer dễ sai từng bước nhỏ nhưng cộng dồn thành sai hoàn toàn.
- Trước khi coi 1 file blob là "toàn bộ đều là weight", LUÔN quét NaN/giá trị cực đoan khi
  ép kiểu `float32` toàn file — nếu có, đó là dấu hiệu có vùng dữ liệu khác kiểu (int32,
  bảng anchor, header, sentinel) trộn lẫn, phải cắt bỏ trước khi phân tích tiếp.
- Quét "mảng toàn dương" (kiểu BatchNorm variance) CHỈ đáng tin với độ dài ≥16; luôn tính
  ngưỡng xác suất ngẫu nhiên (0.5^N) trước khi tin vào kết quả quét thống kê dạng nhị phân
  (dương/âm, chẵn/lẻ...).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Chuỗi byte size lặp lại giống hệt nhau quan sát được qua **dynamic capture trên thiết
  bị thật** (arm64, dù bản đó có mã hoá không đọc được giá trị) vẫn RẤT hữu ích — nó cho biết
  SỐ LƯỢNG và QUAN HỆ CẤU TRÚC giữa các khối (vd "5 khối kích thước giống hệt nhau" → 5 head
  cùng shape) dù không cho biết giá trị thật. Đừng bỏ phí dữ liệu structural chỉ vì không
  giải mã được nội dung.
- ⚠️ Khớp 99.97% tổng tham số (không phải 100% tuyệt đối) là đủ tốt để coi là "khớp" trong
  bài toán này — phần dư nhỏ (ở đây ~2500/7.27M float, <0.04%) hợp lý là do làm tròn kênh
  hoặc 1 lớp phụ nhỏ (bias cuối, hoặc phần nào đó của bảng metadata lấn sang) không mô hình
  hết — không cần ép bằng tuyệt đối 100% nếu điều đó buộc kiến trúc trở nên vô lý (VD số kênh
  lẻ gây lỗi runtime khi split concat).
- ⚠️ head_ch lẻ (không chia hết cho 4) gây lỗi runtime ngay (`RuntimeError: expected N
  channels but got M`) nếu kiến trúc concat nhiều nhánh có công thức chia kênh
  (`out_ch//2 + out_ch//4 + out_ch//4`) — luôn ràng buộc search space theo đúng chia hết
  của công thức kiến trúc, đừng chỉ ràng buộc theo "tổng tham số gần đúng".

## Tham chiếu

- Project liên quan: DecodeTools — `temp/device-f10b/reconstruction/build_model.py`,
  output: `reconstructed_model_4/model_4_reconstructed.{pt,onnx}`.
- Liên quan: [frida-duplicate-module-load-namespace-crash.md](frida-duplicate-module-load-namespace-crash.md),
  [ghidra-portable-setup-and-entropy-model-detection.md](ghidra-portable-setup-and-entropy-model-detection.md)
