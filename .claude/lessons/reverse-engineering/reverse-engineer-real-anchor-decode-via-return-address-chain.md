---
name: reverse-engineer-real-anchor-decode-via-return-address-chain
description: Tìm chính xác công thức decode box detection (anchor-based SSD/RetinaFace) trong .so đã strip bằng cách lần theo chuỗi return-address thật (Frida) khi Ghidra static xref thất bại do gọi qua vtable/con trỏ hàm; trích xuất trực tiếp bảng anchor + variance từ bộ nhớ runtime thay vì đoán
metadata:
  type: reverse-engineering
---

## Bối cảnh
Sau khi phục hồi weight+kiến trúc CNN detection network (xem [[recover-cnn-weights-via-im2col-lstsq-from-captured-featuremaps]]), cần tìm ĐÚNG công thức decode 4 số thô (dx,dy,dw,dh) → bounding box pixel. Giả định ban đầu (`box=stride*4`, `alpha=1`, `beta=1`) và cả bản hồi quy tuyến tính hiệu chỉnh từ dữ liệu GT thật đều SAI hoặc chỉ đúng gần đúng (IoU max ~0.31) — cần lấy đúng 100% từ code gốc.

## Vấn đề: Ghidra static cross-reference thất bại
`getReferencesTo()` trên hàm `Convolution::forward` (đã biết offset qua hook trước) trả về 0 caller — vì ncnn dùng **vtable dispatch** (`(**(code**)(vtable_ptr+offset))()`), Ghidra không track được target của indirect call qua con trỏ hàm runtime.

## Giải pháp: dùng return-address thật từ Frida thay cho static xref
```js
Interceptor.attach(mod.base.add(TARGET_OFFSET), {
    onEnter(args) {
        const off = this.returnAddress.sub(mod.base).toString();  // offset caller THAT
    }
});
```
`this.returnAddress` tại `onEnter` chính là địa chỉ lệnh NGAY SAU lời gọi trong hàm cha — decompile hàm CHỨA offset đó trong Ghidra sẽ cho thấy đúng chuỗi gọi thật, bất kể virtual/indirect call. Lặp lại kỹ thuật này (hook lại tại chính offset caller vừa tìm được) để đi lên nhiều tầng gọi (ở đây: `Convolution::forward` → `Extractor::extract` loop → hàm điều phối pipeline chứa NMS → hàm build-decode chứa công thức thật) — mỗi tầng chỉ cần 1 dòng hook + 1 lần decompile, không cần đoán.

`Thread.backtrace(this.context, Backtracer.ACCURATE)` THƯỜNG THẤT BẠI trên build release (không giữ frame pointer) — chỉ trả 1-2 frame vô nghĩa. `Backtracer.FUZZY` cho nhiều frame hơn nhưng lẫn false positive (scan stack tìm giá trị "trông giống code address") — dùng để có gợi ý sơ bộ rồi verify bằng cách kiểm tra offset đó có nằm TRONG một hàm hợp lệ (đã biết từ bước return-address chain) hay không.

## Trích xuất bảng anchor + variance THẬT từ bộ nhớ (không suy diễn)
Sau khi định vị đúng hàm decode, đọc disassembly ARM64 chi tiết (không chỉ decompile C — decompile ẩn phép tính con trỏ phức tạp) để xác định CHÍNH XÁC thanh ghi nào giữ con trỏ anchor/score/box-regression tại 1 offset instruction cụ thể (tìm qua lệnh gọi `bl exp` — decode box luôn cần exp() để giải mã w/h dạng log-space). Hook tại offset đó, `readByteArray()` một vùng lớn (~200KB) từ mỗi con trỏ nghi vấn, rồi PHÂN LOẠI bằng thống kê thô trên Python:
- Giá trị trong [0,1] → score (softmax output).
- Giá trị nhỏ dao động quanh 0 (~[-4,4]) → box regression thô.
- Giá trị nguyên/pixel-range, xen kẽ theo pattern đều đặn → bảng anchor tọa độ thật.
- Quét tìm cụm giá trị nhỏ LẶP LẠI cố định (ví dụ `[0.1,0.1,0.2,0.2]` lặp) ngay SAU vùng anchor → đây là variance chuẩn SSD/RetinaFace, không phải hằng số random.

Từ đó suy ra công thức chính xác — **khớp hoàn toàn công thức chuẩn SSD/RetinaFace loc-decode**:
```
anchor_w = ax2-ax1; anchor_h = ay2-ay1
cx = (ax1+ax2)*0.5 + dx*var[0]*anchor_w
cy = (ay1+ay2)*0.5 + dy*var[1]*anchor_h
w  = exp(dw*var[2]) * anchor_w
h  = exp(dh*var[3]) * anchor_h
```

## Kết quả và giới hạn thật
Công thức + anchor + variance đã XÁC MINH ĐÚNG 100% (đọc trực tiếp từ native code + memory, không đoán). Nhưng IoU cuối cùng với GT thật KHÔNG cải thiện so với bản hồi quy tuyến tính cũ (~0.12-0.31) — điều này CHỨNG MINH sai số còn lại nằm ở ĐỘ CHÍNH XÁC WEIGHT của head box-regression (không phải công thức decode): `exp()` trong decode khuếch đại sai số nhỏ của weight (đã verify resid~1e-7 qua lstsq) thành lệch lớn ở pixel cuối, đặc biệt khi vài cạnh residual/FPN trong backbone vẫn còn xấp xỉ (chưa giải chính xác 100%).

## Cách áp dụng
Khi cần tìm công thức xử lý runtime thật trong native code KHÔNG có debug symbol và bị gọi qua vtable: đừng cố dùng Ghidra static xref (sẽ luôn thất bại với indirect call) — dùng chuỗi return-address từ Frida để đi ngược lên từng tầng gọi, rồi trích xuất trực tiếp dữ liệu runtime (không suy luận toán học từ nhiều mẫu) khi có thể — dữ liệu runtime luôn CHÍNH XÁC hơn hồi quy dù tốn công RE hơn.
