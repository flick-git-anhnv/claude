---
name: recover-cnn-weights-via-im2col-lstsq-from-captured-featuremaps
description: Khi không lấy được weight thô từ pool (bị lưu ở layout transformed như Winograd/NEON-pack), phục hồi weight CHÍNH XÁC bằng cách capture input+output feature-map của từng conv rồi giải Y=conv(X,W) bằng im2col+least-squares; đọc output ở onLeave (không phải onEnter), và mask Y>0 để vượt qua ReLU
metadata:
  type: reverse-engineering
---

## Bối cảnh
Dựng lại model face-detection ncnn thật trên thiết bị (chip Qualcomm, engine CPU). Đã có kiến trúc thật (55 layer) nhưng chỉ lấy được weight thật của vài layer qua pool pointer-delta (xem [[extract-real-weights-via-pool-allocator-pointer-arithmetic]]). Cần TOÀN BỘ weight để model dùng được.

## Vấn đề với việc đọc weight trực tiếp từ pool
- Con trỏ weight KHÔNG được truyền qua argument của hàm forward `a9b2c` (đã kiểm x0–x8, chỉ 6/45 lần có pointer hợp lệ = rác thanh ghi — xem [[stale-register-arg-mimics-real-pointer-not-embedded-in-struct]]).
- Con trỏ weight KHÔNG nằm trong graph-node struct (node chỉ có input/output blob, không có weight blob).
- Weight trong pool được lưu ở **layout đã transform** (Winograd cho 3×3, NEON-pack cho 1×1): giá trị + kích thước KHÁC weight thô `(out,in,kh,kw)`, nên dù dump được pool cũng không map ngược ra weight PyTorch/ONNX dùng được. Đã verify: weight giải-ngược đúng KHÔNG hề xuất hiện verbatim trong pool dump.

## Giải pháp: giải ngược weight từ feature-map (im2col + least-squares)
Hook `a9b2c` (conv forward), với mỗi lần gọi đọc blob input (field offset 0x10, data@+0x50) và output (field 0x8), lấy `c@0x30, h@0x34, w@0x38`. Với X (input) và Y (output) thật:
```
Y = conv(X, W) + b   (Y là output TRƯỚC activation)
```
im2col(X) rồi giải W,b bằng `np.linalg.lstsq` per output-channel. Vì hệ overdetermined (H·W phương trình ≫ in·k·k ẩn), nghiệm là CHÍNH XÁC (resid ~1e-7) nếu quan hệ tuyến tính.

Kết quả: 43/45 layer phục hồi chính xác (resid < 1e-2, phần lớn ~1e-7). Model cuối validate end-to-end với output THẬT của thiết bị: tương quan corr **0.87–1.0000**, 0 NaN/Inf, chạy được trong ONNX Runtime.

## 3 gotcha quyết định thành–bại
1. **ĐỌC OUTPUT Ở `onLeave`, KHÔNG PHẢI `onEnter`.** Đọc ở onEnter thì buffer output chứa dữ liệu RÁC/CŨ (conv chưa chạy) → chỉ ~10/45 layer giải được (tình cờ). Chuyển sang onLeave (sau khi conv ghi kết quả) → nhảy vọt lên 39/45. Đây là lỗi tinh vi nhất và có tác động lớn nhất.
2. **Output thường POST-ReLU → mask Y>0.** Nếu output đã qua ReLU (min=0), phần âm mất. Nhưng tại vị trí Y>0, ReLU là hàm đồng nhất nên `Y=conv+b` chính xác → giải per-channel chỉ dùng cột Y>0 vẫn ra W đúng. (Layer output tuyến tính — project/head cuối — thì mọi điểm đều hợp lệ.)
3. **pad của 1×1 conv phải = 0.** Trường `pad` trong param struct = 1 kể cả cho 1×1 (rác/mặc định); dùng nó làm im2col ra sai kích thước (66≠64). Ép pad=0 khi k==1.

## Tái dựng đồ thị kết nối (residual/FPN)
Khớp input của layer i với output layer j bằng so khớp mảng byte-for-byte trong CÙNG 1 session (ASLR đổi base). Pattern residual quan trọng: `block_out = relu(project_out + block_INPUT)` — dùng INPUT của block (in[j]), KHÔNG phải conv output của layer trước. Với pattern này 43/45 cạnh khớp relerr=0.0000. (2 cạnh FPN lateral còn xấp xỉ — có thể có op non-conv xen giữa không hook được qua a9b2c.)

## Cách áp dụng
Bất cứ khi nào cần phục hồi weight của 1 mạng chạy trên engine đóng (weight mã hoá/transform, không đọc thô được) nhưng CÓ THỂ chạy inference và hook được input/output từng lớp: giải ngược bằng đại số tuyến tính từ (X,Y) thay vì cố đọc weight thô. Đây là cách mạnh nhất, không phụ thuộc layout lưu trữ nội bộ của engine.
