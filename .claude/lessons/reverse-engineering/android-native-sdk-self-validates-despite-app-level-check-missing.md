---
category: reverse-engineering
tags: [android, adb, arcsoft, jni, license-check, dynamic-verification, false-positive]
severity: high
created: 2026-08-07
updated: 2026-08-07
project-origin: ilocker-android (KZTEK)
---

# Static code review kết luận "bypass license hoàn toàn" — SAI, native SDK tự validate độc lập

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Audit license-check của app Android KZTEK (`ilocker-android`, dùng ArcSoft Face SDK). Đọc code
`InitEngine.initEngineOffline()` thấy hàm này **không hề gọi** `FaceEngine.activeOffline(...)` của
ArcSoft — chỉ check file `ArcFacePro32.dat` tồn tại và kích thước > 100 byte. `grep` toàn repo xác
nhận `activeOffline(` không được gọi ở bất kỳ đâu.

## Triệu chứng / Lỗi

Dựa 100% vào static analysis, kết luận ban đầu (đã viết thành báo cáo "CRITICAL"): **license có
thể bypass hoàn toàn** chỉ bằng cách tạo 1 file rác > 100 byte tên đúng `ArcFacePro32.dat` — không
cần hiểu thuật toán ArcSoft, ai cũng làm được.

Kết luận này **SAI** sau khi kiểm chứng động thật trên thiết bị Android qua ADB.

## Nguyên nhân gốc rễ (Root Cause)

Code Java thiếu gọi `activeOffline()` là có thật, nhưng đó **không phải là điểm gate bảo mật duy
nhất**. `FaceEngine.init(...)` (được gọi ngay sau đó để khởi tạo engine detect/recognition) **tự
nó** validate cấu trúc/tính toàn vẹn của activation data ở tầng native — độc lập hoàn toàn với việc
app có gọi `activeOffline()` tường minh hay không. Khi test bằng file rác ngẫu nhiên (đúng kích
thước, sai cấu trúc), `nativeInitFaceEngine` trả lỗi `MERR_ASF_ACTIVATION_DATA_DESTROYED (90129)`
cho cả 4 engine (rgb/ir/extract/rabbit) → toàn bộ tính năng nhận diện khuôn mặt **không hoạt động**,
app tự hiện toast lỗi. Biến `license` trong code KZTEK là dead/misleading code (tên gợi ý sai chức
năng) nhưng không phải là lỗ hổng bypass thật.

Bài học tổng quát: 1 method có tên gợi ý "kiểm tra X" nhưng code bên trong không làm đúng như tên
gọi **không đồng nghĩa** với "X không được kiểm tra ở đâu cả trong hệ thống" — SDK/thư viện bên
dưới có thể tự bảo vệ ở lớp khác mà code review tĩnh không nhìn thấy được (logic nằm trong
`.so`/native, không đọc được bằng decompiler Java).

## Giải pháp — quy trình kiểm chứng động đã dùng (ADB, không cần Android Studio)

```bash
ADB=".../platform-tools/adb.exe"
S="192.168.21.77:5555"           # thiết bị bật Wireless debugging (Settings > Developer options)
$ADB connect $S

# 1. Tìm đúng applicationId (khác package Java trong source!) — check app/build.gradle
grep applicationId app/build.gradle

# 2. Backup file nhạy cảm trong app-private storage TRƯỚC khi động vào (run-as, không cần root)
$ADB -s $S exec-out run-as <applicationId> cat files/ArcFacePro32.dat > backup.dat

# 3. Ghi đè bằng dữ liệu test qua stdin pipe (run-as không hỗ trợ nhận file qua `adb push` thẳng
#    vì file push bằng shell user, sai owner trong thư mục app-private)
cat fake.dat | $ADB -s $S shell "run-as <applicationId> sh -c 'cat > files/ArcFacePro32.dat'"

# 4. Force-stop + relaunch qua monkey (không cần biết rõ Activity, chỉ cần applicationId)
$ADB -s $S shell am force-stop <applicationId>
$ADB -s $S logcat -c
$ADB -s $S shell monkey -p <applicationId> -c android.intent.category.LAUNCHER 1
$ADB -s $S logcat -d -s <TAG1>:* <TAG2>:*        # đọc log để biết pass/fail thật

# 5. LUÔN khôi phục lại file gốc ngay sau khi test xong (dùng chính backup ở bước 2)
cat backup.dat | $ADB -s $S shell "run-as <applicationId> sh -c 'cat > files/ArcFacePro32.dat'"
```

## Áp dụng lại (How to reuse)

- Khi static analysis phát hiện "code không gọi hàm validate X" → **đừng vội kết luận "bypass được
  X"**. Phải test động thật để xác nhận có tầng validate khác (native, server-side, framework-level)
  đang âm thầm bảo vệ hay không, trước khi báo cáo mức độ nghiêm trọng.
- Khi cần test trên app Android thật mà không có source build sẵn (không dùng Android Studio) →
  dùng `adb + run-as` là đủ (không cần root) để đọc/ghi file trong thư mục app-private
  (`/data/data/<pkg>/files/`), miễn app không debuggable=false + có allowBackup hạn chế (một số
  ROM chặn `run-as` với release build — kiểm tra bằng thử `run-as <pkg> id` trước).
- Luôn `adb exec-out ... cat <file> > backup` **trước** khi ghi đè bất kỳ file nào trên thiết bị
  thật đang chạy production/demo — không dùng device thật để test phá hoại mà không có đường lui.
- `applicationId` trong `build.gradle` có thể khác hẳn tên package Java trong source code
  (`com.example.ilocker_manager` vs source `com.example.ilocker`) — luôn check `build.gradle`
  trước khi tìm package qua `adb shell pm list packages`, đừng đoán theo tên source.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Git Bash (MSYS) tự động convert đường dẫn Unix-style (`/sdcard/...`) thành đường dẫn Windows
  khi truyền vào `adb shell` — gây lỗi `No such file or directory` khó hiểu. Dùng đường dẫn tương
  đối trong `run-as` (`files/...`, không có `/` đầu) để tránh, hoặc set `MSYS_NO_PATHCONV=1`.
- ⚠️ Đừng chỉ tin số đếm/kết luận từ 1 lượt test — bài học này chính là ví dụ: lượt đọc code tĩnh
  đầu tiên tưởng đã đủ bằng chứng "CRITICAL", phải sửa lại báo cáo sau khi có bằng chứng động.
- ⚠️ Test 1 lần với dữ liệu RÁC (random bytes) chỉ chứng minh native chặn được dữ liệu **hỏng cấu
  trúc** — KHÔNG chứng minh được native có chặn được license **hợp lệ nhưng sai thiết bị** (tấn
  công clone license thật giữa 2 máy) hay không. Đây vẫn là câu hỏi mở, cần license thật thứ 2 từ
  thiết bị khác mới trả lời dứt điểm — đừng kết luận "an toàn tuyệt đối" chỉ từ 1 test.

## Tham chiếu

- Project liên quan: `E:\KZTEK\Code_Git\2.Mobile\Locker\ilocker-android`,
  `DecodeTools\java_check\REPORT-ilocker-license-bypass-CRITICAL.md` (báo cáo đầy đủ, có log thật)
- Liên quan: [[java-no-jdk-classfile-string-harvest]] (audit tĩnh ArcSoft SDK trước khi có kết quả
  động này)
