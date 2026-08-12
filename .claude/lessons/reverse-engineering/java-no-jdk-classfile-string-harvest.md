---
category: reverse-engineering
tags: [java, jvm, classfile, jni, jar, so, reverse-engineering, license-check, no-jdk]
severity: medium
created: 2026-08-07
updated: 2026-08-07
project-origin: DecodeTools
---

# Audit license/key hardcode trong .jar/.so mà không cần cài JDK

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Đã có sẵn quy trình audit bảo vệ .NET DLL (`DecodeTools\dll_check`, ILSpy +
NETReactorSlayer + bulk string-harvest). User muốn làm tương tự cho các SDK
Java/Android bên thứ 3 (ArcSoft face, Posutil, Telpo, RKNN) nằm trong
`DecodeTools\libs\*.jar` và `DecodeTools\jniLibs\*\*.so` — để xem SDK check
license/activation theo cơ chế nào. Máy KHÔNG có JDK/JRE cài sẵn (`java -version`
→ command not found), nên không dùng được decompiler chuẩn (CFR/procyon/JD-GUI)
ngay lập tức.

## Triệu chứng / Lỗi

```
$ java -version
bash: line 1: java: command not found
```

Không có JDK, không có `pyelftools` trong Python env sẵn có → tưởng phải dừng
lại xin cài thêm phần mềm mới audit được.

## Nguyên nhân gốc rễ (Root Cause)

Không cần JVM để đọc **constant pool** của file `.class` — đây chỉ là format
nhị phân tài liệu công khai (magic `CAFEBABE`, rồi bảng constant pool với tag
byte quyết định kích thước mỗi entry, tag=1 là UTF8 string). Việc "bulk
string-harvest" (đã áp dụng cho .NET DLL) hoàn toàn làm được bằng cách tự viết
1 parser Python đọc thẳng byte, không cần chạy JVM/decompile ra source thật.

Tương tự, JNI exported function trong `.so` (`Java_com_...`) luôn là literal
ASCII trong `.dynstr` — nên chỉ cần quét chuỗi in-được (regex ASCII run) là đủ
liệt kê toàn bộ JNI bridge, không cần `objdump`/`readelf` (vốn không có sẵn
trên Windows và không cài pyelftools).

## Giải pháp

```python
# classfile_parser.py — đọc constant pool .class, không cần JVM
# Loop qua constant_pool_count entries theo tag:
#   tag=1 Utf8: u2 length + bytes  -> đây là toàn bộ string literal/tên class/method
#   tag=5,6 Long/Double: 8 bytes, chiếm 2 slot index (phải i += 1 thêm)
#   tag khác: kích thước cố định theo bảng CONSTANT_TAG_SIZE
```

1. Viết `classfile_parser.py` tự parse constant pool, trả về mọi UTF8 string.
2. `scan_jar.py`: mở `.jar` bằng `zipfile` (built-in), lấy từng `.class`, gọi
   parser trên, lọc string nghi ngờ bằng regex (`key|license|token|aes|activ|
   expire|fingerprint|decrypt|...`).
3. `scan_so.py`: regex ASCII run (`[\x20-\x7e]{5,}`) trên raw bytes của `.so`,
   lọc thêm pattern `^Java_[A-Za-z0-9_]+$` để liệt kê JNI export mà không cần
   đọc symbol table ELF thật.
4. Kết quả thật: phát hiện `libarcsoft_face_engine.so` có `JNI_OnLoad` nhưng
   **0 export theo tên `Java_...`** → SDK đăng ký native method động qua
   `RegisterNatives` lúc runtime thay vì export tên cố định — 1 kỹ thuật ẩn
   ánh xạ Java↔native phổ biến của SDK thương mại.

## Áp dụng lại (How to reuse)

- Khi cần audit `.jar`/`.class` mà máy không có JDK → viết constant-pool parser
  thuần Python (không cần Krakatau/CFR) để harvest string, đủ dùng cho audit
  license/key hardcode, không cần decompile ra source đầy đủ.
- Khi cần audit `.so` không có objdump/readelf/pyelftools → chỉ cần regex ASCII
  run là đủ liệt kê JNI export (`Java_...`) và string nghi ngờ, không cần parse
  ELF symbol table thật.
- Nếu 1 file `.so` có `JNI_OnLoad` nhưng 0 export `Java_...` → nghi ngờ ngay
  cơ chế `RegisterNatives` động, ghi chú lại trong report thay vì kết luận nhầm
  "không có JNI bridge".
- Regex lọc "sign" dễ dính từ `Signature` (tên attribute chuẩn trong mọi file
  `.class` chứa generic type) → luôn thêm negative lookahead `sign(?!al|ature)`
  để tránh noise gần như 100% class nào cũng có.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Cách này CHỈ đọc được string hằng số (constant pool / ASCII thô), KHÔNG
  đọc được logic bên trong method (bytecode thật). Muốn xem thuật toán validate
  đầy đủ vẫn cần JDK + CFR/procyon thật hoặc Ghidra/IDA cho native.
- ⚠️ Đoán tên class bằng heuristic "chuỗi dài nhất chứa `/`" có thể sai với
  class ẩn danh/lambda — không ảnh hưởng việc harvest string nhưng đừng tin
  tuyệt đối tên class hiển thị trong report.
- ⚠️ `long`/`double` constant chiếm 2 slot trong constant pool (JVM spec) —
  quên `i += 1` sẽ làm lệch toàn bộ offset parse phía sau, dễ crash hoặc đọc
  sai dữ liệu ở các entry còn lại.

## Tham chiếu

- JVM ClassFile format spec: https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-4.html
- Project liên quan: DecodeTools (`java_check/` — `classfile_parser.py`,
  `scan_jar.py`, `scan_so.py`, `run_all.py`)
- Tương tự kỹ thuật đã dùng cho .NET: `dll_check/dumpstrings_tool` (bulk
  string-harvest qua reflection), khác biệt là Java làm được tĩnh hoàn toàn
  không cần chạy runtime.
