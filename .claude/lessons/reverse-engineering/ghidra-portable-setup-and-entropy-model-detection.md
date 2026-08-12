---
category: reverse-engineering
tags: [ghidra, headless, jdk, entropy, float32, model-weights, arm64, no-install]
severity: medium
created: 2026-08-07
updated: 2026-08-07
project-origin: DecodeTools / ilocker-android (KZTEK)
---

# Ghidra headless portable trên Windows (không cài JDK/Ghidra vào máy) + kỹ thuật entropy phát hiện model chưa mã hoá

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Cần disassemble native `.so` ARM64 (`libarcsoft_face_engine.so`, `libarcsoft_face.so` — SDK
ArcSoft trong app KZTEK) để: (1) đọc cấu trúc/schema thật của license file, (2) đánh giá model AI
86.7MB nhúng trong `.so` có bị mã hoá hay không (mục đích: rút kinh nghiệm để tự mã hoá model của
KZTEK cho đúng cách). Máy không có Ghidra/JDK cài sẵn.

## Triệu chứng / Lỗi

Chuỗi lỗi gặp liên tiếp khi setup Ghidra portable:

```
Java runtime not found. Please refer to the Ghidra Installation Guide's Troubleshooting section.
```
→ (sau khi set `JAVA_HOME_OVERRIDE` trong `support/launch.properties`) vẫn lỗi y hệt.

```
JDK 21+ (64-bit) could not be found and must be manually chosen!
```
→ (sau khi thêm JRE 17 vào PATH)

## Nguyên nhân gốc rễ (Root Cause)

3 lớp vấn đề chồng lên nhau:

1. **`JAVA_HOME_OVERRIDE` không đủ** — script `analyzeHeadless.bat`/`launch.sh` cần gọi lệnh
   `java` (từ PATH) TRƯỚC để bootstrap class `LaunchSupport` (chính class này mới đọc
   `JAVA_HOME_OVERRIDE`) — nếu hoàn toàn không có `java` nào trong PATH, bước bootstrap này chết
   ngay từ đầu, không bao giờ chạm tới logic đọc override.
2. **Git Bash `export PATH="C:/..."` (dùng dạng Windows path) không hoạt động** — phải dùng dạng
   Unix `/c/Users/...` thì `which`/exec mới resolve được, dù đường dẫn đó dùng để gọi `.exe` Windows
   bình thường.
3. **Ghidra 11.2.1 yêu cầu JDK 21+, JRE (không phải JDK) KHÔNG đủ** — dù chỉ cần headless
   analyze (không compile gì), Ghidra vẫn tự check "JDK 21+ 64-bit" cụ thể qua class
   `LaunchSupport`, từ chối cả JDK 17 lẫn JRE-only.

## Giải pháp

```bash
# 1. Tai portable JDK 21 (KHONG phai JRE) tu Adoptium — khong can cai vao he thong
curl -sL -o jdk21.zip "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse"
python3 -c "import zipfile; zipfile.ZipFile('jdk21.zip').extractall('.')"

# 2. Set JAVA_HOME_OVERRIDE trong support/launch.properties TRO TOI DUNG JDK 21 nay
#    (sua dong: JAVA_HOME_OVERRIDE=C:\path\to\jdk-21.0.12+8)

# 3. QUAN TRONG: van phai them JDK vao PATH (dang Unix /c/...) truoc khi goi analyzeHeadless
#    vi buoc bootstrap LaunchSupport can `java` co san trong PATH
export PATH="/c/Users/.../jdk-21.0.12+8/bin:$PATH"   # KHONG dung "C:/..." — Git Bash khong resolve duoc

# 4. Chay headless import + auto-analyze
./support/analyzeHeadless.bat "<project_dir>" <project_name> \
  -import "<file.so>" -overwrite

# 5. Lan sau muon chay THEM script tren project da co san (khong import lai) — dung -process + -noanalysis
./support/analyzeHeadless.bat "<project_dir>" <project_name> \
  -process "<ten_file_da_import>.so" -noanalysis \
  -scriptPath "<thu_muc_chua_script.java>" -postScript MyScript.java
```

### Kỹ thuật viết Ghidra script tìm nhanh hàm xử lý theo từ khoá (không cần đọc hết assembly)

`GhidraScript.getDefinedData()` + `Data.hasStringValue()` **không đáng tin** để tìm string theo
keyword (có thể miss string tồn tại thật trong binary nếu Ghidra chưa đánh dấu đúng kiểu). Cách
chắc chắn hơn: dùng `findBytes(startAddr, "keyword", matchLimit, alignment)` (trả về `Address[]`,
không phải `Address` đơn — dễ nhầm) tìm trực tiếp trên bộ nhớ, rồi `getReferencesTo(addr)` +
`getFunctionContaining(fromAddr)` để nhảy thẳng tới hàm dùng string đó, decompile bằng
`DecompInterface`. Cách này tìm ra được hàm `nativeGetActiveFile` xử lý license chỉ trong ~1 phút
thay vì đọc hàng trăm hàm không tên (`FUN_xxxxx`).

### Kỹ thuật entropy + byte-histogram phát hiện model AI có mã hoá hay không (không cần Ghidra)

```python
# Buoc 1: entropy tho theo window 1MB tren toan file — encrypted that: ~7.99-8.0 bit/byte on dinh
#         Float32 weight CHUA ma hoa: dao dong 7.3-7.5 bit/byte (thap hon han encrypted that)
# Buoc 2: xac nhan bang byte-histogram O VI TRI byte cao nhat moi group 4 byte (offset % 4 == 3,
#         little-endian) — neu la weight that, phan bo se TAP TRUNG manh o vai gia tri
#         (0x3D/0xBD, 0x3C/0xBC...) tuong ung exponent byte cua so float nho quanh 0.
#         Encrypted that: phan bo GAN NHU DEU tren ca 256 gia tri (~0.39% moi gia tri).
```

Đã dùng để xác nhận `libarcsoft_face.so` (86.7MB) chứa model AI **plaintext hoàn toàn** — top giá
trị byte cao chiếm 18.8% (thay vì ~0.39% nếu mã hoá thật) → kết luận chắc chắn chỉ trong vài giây,
không cần disassemble gì cả.

## Áp dụng lại (How to reuse)

- Setup Ghidra portable trên máy mới → luôn cần **JDK đầy đủ (không phải JRE)** đúng version tối
  thiểu ghi trong `support/launch.properties` (đọc comment đầu file để biết version yêu cầu của
  bản Ghidra đang dùng, KHÔNG giả định theo kinh nghiệm cũ vì mỗi major version Ghidra có thể đổi
  yêu cầu JDK version).
- Muốn biết nhanh 1 file binary (model AI, license, blob bất kỳ) có thực sự được mã hoá hay chỉ là
  "trông có vẻ ngẫu nhiên" → luôn làm entropy scan theo window trước (rẻ, không cần tool gì ngoài
  Python thuần), rồi mới quyết định có đáng đầu tư Ghidra/IDA để đọc thuật toán hay không.
- Khi cần tìm 1 hàm cụ thể trong file `.so` không có ký hiệu (symbol) → tìm qua string liên quan
  (tên field JNI, error message, tên API) rồi trace cross-reference, nhanh hơn nhiều so với đọc từ
  entry point hoặc lướt danh sách hàng trăm `FUN_xxxxx`.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `findBytes()` trong Ghidra script trả về `Address[]`, KHÔNG phải `Address` — nhầm kiểu trả về
  gây lỗi compile khó hiểu (`incompatible types`) vì Ghidra script được compile on-the-fly, lỗi chỉ
  hiện ra lúc chạy (`analyzeHeadless`), không có gợi ý IDE trước.
- ⚠️ `getReferencesTo()` trả về `Reference[]` (không phải `ReferenceIterator` như class name gợi ý
  nhầm) trong API bản Ghidra 11.x.
- ⚠️ Entropy 7.3-7.5 bit/byte KHÔNG có nghĩa "hơi mã hoá yếu" — nó có nghĩa **hoàn toàn plaintext**
  (đây là entropy tự nhiên của float32 ngẫu nhiên đã train, không phải do mã hoá kém). Đừng nhầm
  "entropy cao nhưng chưa tới 8.0" với "có mã hoá nhưng thuật toán yếu" — phải làm byte-histogram
  (bước 2) mới phân biệt được 2 trường hợp này.

## Tham chiếu

- Ghidra: https://github.com/NationalSecurityAgency/ghidra/releases
- Project liên quan: `DecodeTools\java_check\REPORT-native-reverse-engineering-final.md` (báo cáo
  đầy đủ, có code decompile thật)
- Liên quan: [[java-no-jdk-classfile-string-harvest]],
  [[android-native-sdk-self-validates-despite-app-level-check-missing]]
