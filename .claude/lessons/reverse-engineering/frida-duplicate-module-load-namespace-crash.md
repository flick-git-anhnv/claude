---
category: reverse-engineering
tags: [frida, android, dlopen, native-hooking, dynamic-analysis, arm64]
severity: high
created: 2026-08-08
updated: 2026-08-08
project-origin: DecodeTools (ArcSoft model weight dynamic capture, ilocker-android/F10B thiết bị thật)
---

# Tự `Module.load()` một `.so` app đã dùng → 2 bản song song, hook sai bản, gây SIGBUS crash

## Tình huống gặp phải

Cần bắt trace load-weight của CNN (`libarcsoft_face.so`, ArcSoft SDK) trên thiết bị Android ARM64
thật (F10B/RK3568) qua Frida gadget đã nhúng sẵn trong APK. Vì app chưa tới màn hình có khuôn mặt
thật trước camera (chưa trigger native init tự nhiên), đã dùng `Module.load(path)` để tự dlopen
thư viện rồi gọi thẳng `AFInitEngine` qua `NativeFunction` với tham số đoán bừa — nhằm ép trigger
load weight mà không cần chờ luồng UI thật.

## Triệu chứng / Lỗi

- Lệnh tự gọi `AFInitEngine` với tham số đoán trả về mã lỗi (không phải 0), không thấy có
  allocation lớn nào tương ứng việc load weight thật.
- Sau khi dùng Java hook gọi đúng API thật (`com.arcsoft.face.FaceEngine.init()` qua tầng Java,
  license thật đã được cấp) và engine init THÀNH CÔNG (return true nhiều engine liên tiếp) — thì
  app crash: `Fatal signal 7 (SIGBUS), code 1 (BUS_ADRALN)` trong 1 thread pool nội bộ SDK.
- `Process.enumerateModules()` sau đó cho thấy **2 bản `libarcsoft_face.so` load ở 2 base address
  khác nhau** trong cùng 1 tiến trình (`0x73f6681000` và `0x73ec883000`), cùng kích thước.

## Nguyên nhân gốc rễ (Root Cause)

Gọi `Module.load(path)` thủ công để dlopen 1 thư viện app **đã hoặc sẽ tự load qua linker namespace
riêng của nó** (namespace mặc định app dùng khi resolve NEEDED dependency của
`libarcsoft_face_engine.so` → `libarcsoft_face.so`) không đảm bảo dùng CHUNG 1 instance. Trên
Android 10+ với app namespace isolation, dlopen từ context của Frida script (chạy trong gadget,
có thể ở namespace khác) với CÙNG đường dẫn tuyệt đối vẫn có thể tạo ra **bản ánh xạ bộ nhớ độc
lập thứ hai**, không tăng refcount của bản app tự load. Hai bản CNN 112MB cùng chạy song song
(dùng chung numeric constant/lookup table ở địa chỉ tương đối giống nhau nhưng base khác nhau,
hoặc tranh chấp buffer/pool nội bộ dùng con trỏ tuyệt đối lưu global) → truy cập lệch alignment
→ SIGBUS.

## Giải pháp

1. **KHÔNG tự `Module.load()` một thư viện mà app đã/sẽ tự dlopen qua luồng bình thường** — dù
   mục đích chỉ để "ép trigger sớm" hay "gọi hàm export trực tiếp". Rủi ro tạo bản trùng lặp âm
   thầm rất khó phát hiện cho tới khi crash.
2. Thay vào đó: chỉ **hook thụ động** (`Interceptor.attach`) chờ module load tự nhiên
   (`Process.enumerateModules()` polling bằng `setTimeout` lặp lại, không dlopen).
3. Để trigger native init THẬT mà không cần thao tác UI thủ công (camera cần mặt người thật) —
   dùng Frida **Java.use()** gọi thẳng API Java gốc app dùng (ở đây:
   `com.example.ilocker.engine_face.InitEngine.initRGBEngine(ctx)` lấy từ đúng source code thật
   của app, KHÔNG đoán tham số native). Cách này tái sử dụng đúng 1 instance thư viện app đã tự
   quản lý, không tạo bản trùng.
4. Nếu buộc phải hook 1 module có khả năng bị load nhiều lần (kể cả không phải do lỗi của mình,
   ví dụ do chính app load lại), luôn hook theo **filter TOÀN BỘ module cùng tên** (lặp qua
   `Process.enumerateModules().filter(m => m.name === soName)`), không giả định chỉ có 1 instance.
5. Sau khi app crash do lỗi tự gây ra, **force-stop + relaunch sạch** rồi mới tiếp tục — không
   cố "sửa chữa" tiến trình đang ở trạng thái crash dở dang.

## Áp dụng lại (How to reuse)

- Trước khi viết bất kỳ script Frida nào có `Module.load()`/`Module.ensureInitialized()`/`dlopen`
  thủ công nhắm vào thư viện của TARGET APP (không phải thư viện hệ thống độc lập) — luôn tự hỏi:
  "app có tự load cái này không? nếu có, đợi thụ động thay vì tự load."
- Khi cần trigger 1 luồng native mà UI/camera/thiết bị vật lý không sẵn sàng để test thủ công
  (VD: cần khuôn mặt thật trước camera nhưng camera đang chĩa hướng khác) → tìm **source code thật
  của app** (nếu có quyền truy cập repo nội bộ) để gọi đúng API tầng Java tương ứng qua
  `Java.use()`, thay vì đoán mò tham số native hoặc cố giả lập input phần cứng (camera frame) —
  nhanh hơn, an toàn hơn, và cho kết quả THẬT thay vì dữ liệu giả.
- `Process.enumerateModules()` filter theo tên PHẢI coi là có thể trả về NHIỀU kết quả trùng tên,
  không bao giờ giả định `Process.findModuleByName()` (chỉ trả 1 kết quả) là đủ khi nghi ngờ có
  khả năng load kép.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ App tự khởi động lại (respawn) sau crash không có nghĩa là an toàn tiếp tục ngay — kiểm tra
  lại toàn bộ trạng thái hook (module base address đổi hoàn toàn sau mỗi lần restart process,
  phải re-poll từ đầu).
- ⚠️ `frida -H host -p PID -l script.js` **tự động reload script khi file được sửa** (live edit) —
  hữu ích để chỉnh hook nhanh mà không cần tắt/mở lại kết nối, nhưng cũng nghĩa là sửa file trong
  lúc đang debug sẽ tự kích hoạt lại toàn bộ `install()`/`poll()` logic ngay lập tức, cần thiết kế
  hàm cài hook idempotent (dùng `Set` theo dõi base đã hook) để tránh attach trùng.
- ⚠️ Gọi lệnh Frida ngắn hạn (`session.create_script(...).load()`) qua Python trong lúc một
  Monitor/session Frida KHÁC đang đồng thời attach vào CÙNG tiến trình đôi khi bị
  `frida.TransportError: timeout was reached` dù lệnh vẫn thực thi thành công phía sau (event vẫn
  tới qua Monitor) — không vội coi đây là lỗi thật, kiểm tra Monitor trước khi kết luận thất bại.

## Tham chiếu

- Project liên quan: DecodeTools — `temp/device-f10b/hook_arm64_weights.js`,
  `hook_full_init.js`; source thật của app tại
  `E:\KZTEK\Code_Git\2.Mobile\Locker\ilocker-android`.
- Liên quan: [arcsoft-rsa-key-shared-across-cpu-arch-builds.md](arcsoft-rsa-key-shared-across-cpu-arch-builds.md)
