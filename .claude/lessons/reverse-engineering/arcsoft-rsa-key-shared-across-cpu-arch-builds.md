---
category: reverse-engineering
tags: [ghidra, android, arm64, rsa, license, arcsoft, obfuscation]
severity: high
created: 2026-08-08
updated: 2026-08-08
project-origin: DecodeTools (ArcSoft license patch/model recovery)
---

# ArcSoft dùng CHUNG 1 cặp khoá RSA cho mọi kiến trúc CPU — chỉ đổi offset/hàm loader theo build

## Tình huống gặp phải

Đã reverse-engineer thành công vị trí + giá trị 2 khoá public RSA (F8/ArcFace và F10/ArcFace3568)
nhúng obfuscate (base26/XOR seed 0x522) trong `libarcsoft_face_engine.so` / `_main.so` bản
**armeabi-v7a** (offset file `0x000ac2cc`, hàm loader `FUN_0005e6fc`). Khi có thiết bị thật
(F10B/RK3568, arm64 thật) để tiếp tục patch key, phát hiện app cài trên thiết bị đó dùng bản
**arm64-v8a** của cùng 2 file `.so` — kích thước khác hẳn (1321608 byte so với 772248 byte của
bản v7), nên lo ngại toàn bộ offset/hàm đã tìm trước đó vô giá trị với build mới.

## Triệu chứng / Lỗi

Không phải lỗi — là nghi vấn hợp lý cần kiểm chứng: "build khác kiến trúc CPU thì địa chỉ hàm,
offset file, thậm chí cặp khoá RSA có còn giống bản cũ không?"

## Nguyên nhân gốc rễ (Root Cause)

ArcSoft build cùng 1 mã nguồn cho nhiều kiến trúc CPU (armeabi-v7a, arm64-v8a) từ cùng
`libarcsoft_face_engine.so`. Compiler tạo layout offset khác nhau theo target (dĩ nhiên), NHƯNG
**dữ liệu khoá RSA nhúng cứng (embedded constant) không đổi theo kiến trúc** — nó là data, không
phải code, nên ArcSoft dùng lại y hệt giữa các build. Hàm loader-khoá tuy đổi tên/địa chỉu Ghidra
(`FUN_0005e6fc` ở v7 → `FUN_0016f620` ở arm64) nhưng **logic + cipher (base26/XOR seed 0x522,
540 ký tự) giữ nguyên**.

## Giải pháp

1. Re-run pipeline dò khoá TỪ ĐẦU trên build mới, đừng giả định offset cũ áp dụng được:
   - Import `.so` bản arm64 vào Ghidra project riêng, chạy full auto-analysis.
   - Tìm string `"activeKey"`, `"importantInfo"`, `"deviceFingerPrint"`... → xref tới các hàm
     JSON parser (đổi tên `FUN_xxx` theo build nhưng logic giống).
   - Tìm hàm ENCODE/DECODE base26-xor (dò theo pattern seed `0x522` truyền literal) → liệt kê
     TẤT CẢ caller của nó bằng `getReferencesTo()`.
   - Trong danh sách caller, tìm hàm có **paramCount = 0** — đó chính là "hardcoded key loader"
     (không cần tham số bên ngoài vì string key là literal cứng trong hàm).
   - Decompile hàm đó — Ghidra sẽ inline luôn chuỗi 540 ký tự A-Z trực tiếp trong code C giả lập
     (không cần dò thêm địa chỉ tham chiếu chuỗi thủ công như cách cũ).
2. Giải mã chuỗi bằng `decrypt_from_base26_xor(key_str, 0x522)` đã có sẵn trong
   `generate_license_tool.py` → so khớp với khoá cũ.
3. Nếu khớp 100% (như trường hợp F8 + F10 ở đây) → xác nhận ArcSoft dùng chung khoá xuyên kiến
   trúc, chỉ cần lưu thêm offset file mới của build đang patch (tìm bằng
   `data.find(key_string_bytes)` trên file thật), không cần nghi ngờ toàn bộ phát hiện cũ.

## Áp dụng lại (How to reuse)

- Khi native lib có nhiều bản ABI (armeabi-v7a, arm64-v8a, x86...), **KHÔNG giả định** một phát
  hiện offset/địa chỉ hàm ở ABI này áp dụng được cho ABI khác — luôn re-run Ghidra trên đúng file
  binary sẽ chạy thật.
- NHƯNG cũng đừng vứt bỏ phát hiện cũ về mặt LOGIC (cipher, seed, format, tên trường JSON) — chỉ
  địa chỉ/offset đổi, thuật toán và hằng số nghiệp vụ (RSA keypair, seed XOR) thường được tái sử
  dụng nguyên xi giữa các build cùng hãng.
- Kỹ thuật "tìm hàm 0-tham-số gọi vào hàm decode/encode dùng chung" là cách nhanh nhất để định vị
  hardcoded-secret-loader trong native lib, nhanh hơn nhiều so với dò ngược địa chỉ chuỗi thủ công.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Ghidra headless cần `JAVA_HOME` trỏ đúng JDK đầy đủ (không phải JRE) set TRƯỚC khi gọi
  `analyzeHeadless` — nếu không sẽ báo "Java runtime not found" dù máy có sẵn nhiều bản JDK khác
  trong PATH.
- ⚠️ Ghidra API `getReferencesTo(addr)` trả về `Reference[]` (mảng), KHÔNG PHẢI
  `ReferenceIterator` như một số API cũ hơn — code mẫu cũ dùng `while(it.hasNext())` sẽ lỗi
  compile "incompatible types" khi chạy trên Ghidra 11.2.1. Dùng `for (Reference r : refs)`.
- ⚠️ Khi rerun script đã sửa lỗi compile trên project đã `-import` xong, dùng
  `-process <filename>` + `-noanalysis` thay vì `-import` lại — tiết kiệm rất nhiều thời gian
  (khỏi phân tích lại từ đầu), đặc biệt quan trọng với file lớn (thử nghiệm thực tế: file 112MB
  mất hàng chục phút để full-analyze, trong khi rerun script trên project có sẵn chỉ mất giây).
- ⚠️ File `.so` lớn bất thường (112MB so với ~1-4MB thông thường) có thể là dấu hiệu build mới
  tích hợp thêm runtime khác (ở đây là RKNN/Rockchip NPU, thấy qua external symbol link tới
  `librknnrt.so`) — nhưng đừng vội kết luận toàn bộ format thay đổi; kiểm tra bằng cách search
  magic bytes của format nghi ngờ (vd `RKNN`, `ncnn`, `.param`) trong toàn bộ file trước, nếu
  KHÔNG thấy thì nhiều khả năng đó vẫn là raw weight blob cũ, chỉ là code lớn hơn do link thêm
  thư viện không dùng tới cho phần đang phân tích.

## Tham chiếu

- Project liên quan: DecodeTools — `generate_license_tool.py`, offset v7 cũ `0x000ac2cc`,
  offset arm64 mới `0x108310` (cả `libarcsoft_face_engine.so` và `_main.so`).
- Liên quan: [java-no-jdk-classfile-string-harvest.md](java-no-jdk-classfile-string-harvest.md),
  [ghidra-portable-setup-and-entropy-model-detection.md](ghidra-portable-setup-and-entropy-model-detection.md)
