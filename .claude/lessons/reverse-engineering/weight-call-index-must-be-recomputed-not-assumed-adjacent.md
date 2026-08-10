---
name: weight-call-index-must-be-recomputed-not-assumed-adjacent
description: Khi map thứ tự capture weight-fetch (chỉ gọi 1 lần/layer Convolution) sang layer thật trong bảng đầy đủ (có xen PReLU), không được suy luận "layer liền kề" bằng mắt — phải tính lại bằng script list-comprehension lọc đúng type
metadata:
  type: reverse-engineering
---

## Bối cảnh
Đang dựng lại kiến trúc ArcSoft ncnn từ dữ liệu capture thật qua Frida (xem [[extract-real-weights-via-pool-allocator-pointer-arithmetic]]). Có 2 nguồn capture độc lập:
- `captured_layer_types.json`: 55 layer thật (45 Convolution type=2 + 10 PReLU type=17), theo đúng thứ tự xuất hiện trong bảng mô tả layer ncnn.
- `real_weight_chunks_final.npz`: mảng weight thật (entry_0..entry_44), lấy từ hook một hàm `a9b2c` được gọi ĐÚNG 1 LẦN cho mỗi layer Convolution (không gọi cho PReLU).

## Lỗi đã xảy ra
Giả định "entry_41 nằm ngay TRƯỚC entry_40, nên chắc layer#49 nằm ngay trước layer#50 trong bảng 55-layer" (suy luận theo cảm tính vì #49/#50 là 2 conv liền kề trong danh sách 55 layer). Điều này **sai** vì giữa các Convolution có thể có PReLU xen vào ở NHỮNG VỊ TRÍ KHÁC, làm lệch offset giữa "thứ tự trong danh sách 45 Convolution" và "vị trí trong danh sách đầy đủ 55 layer" tại các đoạn khác nhau không đều nhau.

Kết quả: nạp nhầm `entry_41` (thực ra ứng với layer#51, shape 64×8×3×3) vào `branch_49` — dù forward pass vẫn chạy được (không NaN, vì cùng shape 64×8×3×3 trùng hợp ở cả 2 vị trí #49 và #51), nên lỗi **không hề lộ ra qua kiểm tra NaN/Inf** — chỉ là gán sai bộ trọng số vào sai nhánh output.

## Cách tính đúng
```python
conv_positions = [i for i, s in enumerate(specs) if s['type'] == 2]  # 45 phần tử
# weight_call#N (thứ N trong 45 conv, 0-indexed) -> full-layer-index = conv_positions[N]
```
Chạy script này để lấy CHÍNH XÁC full-layer-index cho từng weight_call_index, rồi mới đối chiếu params (`out_channels`, kernel) với module đã dựng để xác nhận khớp — đừng đoán bằng cách đếm tay hoặc giả định "liền kề = đúng thứ tự".

## Cách áp dụng
Bất cứ khi nào có 2 danh sách capture riêng biệt mà một cái là SUBSET có điều kiện lọc của cái kia (vd: "chỉ gọi hook cho type X"), phải viết đúng 1 dòng list-comprehension filter + index để map, không suy luận thủ công theo vị trí tương đối — đặc biệt nguy hiểm khi các phần tử xung quanh vị trí nghi ngờ có SHAPE TRÙNG NHAU (làm sai số không lộ ra qua test forward pass).
