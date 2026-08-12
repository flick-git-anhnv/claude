---
name: stale-register-arg-mimics-real-pointer-not-embedded-in-struct
description: Hook Interceptor.attach đọc args[3] (x3) của hàm chỉ nhận 3 tham số thật vẫn trả về giá trị "giống pointer hợp lệ" ở một số lần gọi — đó là rác thanh ghi sống sót từ lệnh gọi trước, KHÔNG phải tham số thật, và giá trị đó cũng không nằm cố định trong bất kỳ struct nào có thể đọc lại được
metadata:
  type: reverse-engineering
---

## Bối cảnh
Tiếp tục [[weight-call-index-must-be-recomputed-not-assumed-adjacent]] và [[extract-real-weights-via-pool-allocator-pointer-arithmetic]]: đang cố trích thêm weight thật ngoài 6 tensor đã có, bằng cách hook hàm `a9b2c` trong `libarcsoft_face.so` và đọc `args[3]` (x3) làm "con trỏ dữ liệu weight".

## Phát hiện
Decompile đầy đủ hàm (Ghidra, không cắt dòng — script mặc định `ForceDecompileCallList.java` cắt ở 50 dòng nên chỉ thấy phần khai báo biến, phải viết script riêng với limit cao hơn để thấy được logic thật) cho thấy chữ ký thật là:
```c
ulong FUN_001a9b2c(long param_1, ulong param_2, ulong param_3)
```
**Chỉ 3 tham số** (x0, x1, x2) — không có tham số thứ 4. `Interceptor.attach` của Frida vẫn cho đọc `args[3]` (x3) vì nó chỉ đọc thanh ghi thô theo ABI slot, không biết/không kiểm tra chữ ký thật của hàm.

Với 39/45 lần gọi, `args[3]` là số nguyên nhỏ vô nghĩa (0x1, 0x8, 0x20, 0x200...). Với 6/45 lần gọi, nó lại là một con trỏ pool hợp lệ, TRÙNG với giá trị weight thật đã xác nhận trước đó qua kỹ thuật junk-run/pointer-delta.

Giả thuyết ban đầu: giá trị đó có thể đang NẰM SẴN trong struct mô tả layer (đọc được qua `param_1 + a1`, đã dump 800 byte struct này ở nơi khác) — nếu đúng thì có thể tìm offset cố định để đọc TRỰC TIẾP weight pointer cho cả 45 layer mà không cần dựa vào x3 may rủi.

**Đã kiểm chứng và BÁC BỎ giả thuyết này**: chạy capture kết hợp (struct 800-byte + giá trị x3) trong CÙNG một process/session (bắt buộc vì ASLR đổi base mỗi lần app khởi động lại — không thể đối chiếu giá trị con trỏ giữa 2 lần chạy khác nhau), rồi quét toàn bộ struct tìm giá trị 64-bit khớp với x3 — **không tìm thấy ở bất kỳ offset nào trong cả 6 trường hợp**. Kết luận: x3 hợp lệ hoàn toàn là NGẪU NHIÊN — thanh ghi x3 được nạp giá trị con trỏ weight thật ở MỘT bước tính toán trước đó tại call site (có thể một sub-call khác dùng x3 làm tham số), rồi KHÔNG bị ghi đè trước khi gọi `a9b2c` — chỉ xảy ra ở call site có pattern biên dịch cụ thể (rất có thể do trùng hợp giữa 1x1-conv non-depthwise với channel lớn), không phải cơ chế API ổn định.

## Cách áp dụng
- Khi hook một hàm bằng `Interceptor.attach` + đọc `args[N]`, LUÔN decompile đầy đủ (không cắt dòng) để xác nhận hàm thật sự CÓ N+1 tham số theo ABI — nếu không, `args[N]` là rác thanh ghi, và tính "hợp lệ tình cờ" của nó ở một số lần gọi KHÔNG chứng minh nó là dữ liệu thật ổn định.
- Khi nghi ngờ 1 giá trị "tình cờ đúng" có thể lấy được ổn định hơn từ 1 struct đã biết, phải verify bằng cách capture CẢ HAI nguồn trong CÙNG 1 session (không phải 2 lần chạy khác nhau) rồi so khớp giá trị byte-for-byte — nếu không khớp ở bất kỳ offset nào, từ bỏ giả thuyết thay vì tiếp tục đoán offset khác.
- Điểm dừng hợp lý: sau khi bác bỏ giả thuyết "offset cố định trong struct", không còn nguồn dữ liệu tĩnh nào khác để thử với kỹ thuật hiện có (đã kiểm tra a0/a1/a2/a3 tại 1 điểm hook, và toàn bộ 800 byte struct lân cận) — muốn tiến xa hơn cần disassemble từng call-site RIÊNG BIỆT (45 vị trí gọi khác nhau trong code) để tìm ra hàm/lệnh nào thực sự nạp weight pointer vào thanh ghi trước lệnh `bl a9b2c`, việc này tốn công sức không tương xứng với lợi ích cho 39 tensor còn thiếu.
