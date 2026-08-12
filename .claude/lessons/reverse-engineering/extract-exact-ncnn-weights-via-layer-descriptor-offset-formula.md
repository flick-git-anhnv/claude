---
name: extract-exact-ncnn-weights-via-layer-descriptor-offset-formula
description: Trích xuất weight CHÍNH XÁC TUYỆT ĐỐI (bit-exact) của mọi conv layer từ ncnn engine bằng cách đọc công thức tính offset weight trong pool ngay từ code Conv::forward đã decompile, thay vì đoán/hồi quy — chìa khoá là công thức 2-lần-dereference và verify layout bằng corr=1.0 với lstsq
metadata:
  type: reverse-engineering
---

## Bối cảnh
Đã dựng lại kiến trúc + weight face-detection ncnn qua nhiều phương pháp xấp xỉ (im2col+lstsq resid~1e-7, xem [[recover-cnn-weights-via-im2col-lstsq-from-captured-featuremaps]]) nhưng vẫn không đủ chính xác cho box regression (IoU~0.3) vì `exp()` trong decode khuếch đại sai số nhỏ. Cần weight CHÍNH XÁC TUYỆT ĐỐI, không xấp xỉ.

## Chìa khoá: đọc công thức offset weight từ code Conv::forward
Decompile ĐẦY ĐỦ hàm `Conv::forward` (`a9b2c`, 2390 dòng — phải decompile hết, không cắt 300 dòng) tìm đoạn tính con trỏ weight. Tên hàm nội bộ lộ qua chuỗi error: `mf_ArcN_Conv_Full_Neon_FL`, `mf_ArcN_Conv_FLOAT_OpEnv_KnlSlide` → xác nhận GEMM/sliding-window CHUẨN, KHÔNG phải Winograd (nên weight lưu thô, đọc trực tiếp được).

Công thức offset THẬT (đọc từ decompile):
```
lVar1 = param_1 + layer_offset          // layer descriptor (param_1 = graph context)
flag  = *(int32*)(lVar1 + 0x1c)
puVar45 = lVar1 + 0x18
if flag != 1:  puVar45 = param_1 + *(uint32*)(lVar1 + 0x18)   // DEREF 1
inner = *(uint32*)(puVar45)                                    // DEREF 2  <-- DỄ BỎ SÓT
weight_offset = *(uint32*)(param_1 + inner + 8)
weight_ptr = *(void**)(param_1 + 0x38) + weight_offset          // pool_base + offset
```

**Gotcha quyết định:** công thức có **HAI lần dereference** liên tiếp (`param_1 + *(param_1 + val)`). Lần đầu tôi chỉ làm 1 lần deref → mọi layer flag=2 trả offset=0 (rác). Thêm deref thứ 2 → tất cả 45 layer ra weight thật hợp lý, offset tăng đơn điệu (đúng thứ tự lưu tuần tự trong pool).

## Verify layout đúng (không cần đoán)
So weight đọc trực tiếp với weight giải bằng lstsq (đã có, resid~1e-7) cho vài head layer: **corr = 1.00000, maxdiff ~1e-3**. Điều này xác nhận: (1) công thức offset đúng, (2) layout ncnn = `(out, in/groups, kh, kw)` GIỐNG HỆT PyTorch, (3) bias nằm ngay sau weight (`out` phần tử). Depthwise: `(out, 1, kh, kw)`.

## Kết quả
Trích xuất bit-exact 100% weight+bias cho cả 45 conv. Build model → 4/8 head (không phụ thuộc cạnh FPN chưa giải) đạt **corr=1.00000, rel_err=0.0000** so với thiết bị thật = KHỚP TUYỆT ĐỐI. Kết hợp decode anchor+variance thật (xem [[reverse-engineer-real-anchor-decode-via-return-address-chain]]): tensor thiết bị + decode → IoU 0.71 với GT của chính SDK.

## Cách áp dụng
Khi cần weight CHÍNH XÁC từ 1 engine inference đóng (không chỉ "gần đúng"): đừng dừng ở hồi quy/xấp xỉ từ activation — decompile ĐẦY ĐỦ hàm forward của layer, tìm công thức tính địa chỉ weight trong bộ nhớ (thường là `pool_base + offset` với offset lưu trong layer descriptor), replicate CHÍNH XÁC bằng Frida (chú ý số lần dereference), rồi verify layout bằng cách so với 1 nguồn độc lập (lstsq/param-count) — corr=1.0 là bằng chứng đọc đúng. Weight đọc trực tiếp từ bộ nhớ luôn chính xác tuyệt đối, không có sai số tích luỹ như hồi quy.
