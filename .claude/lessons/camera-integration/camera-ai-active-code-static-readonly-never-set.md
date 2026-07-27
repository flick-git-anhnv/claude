---
category: camera-integration
tags: [readpl, license-activation, static-readonly, kztek-cameras, silent-failure]
severity: high
created: 2026-07-20
updated: 2026-07-20
project-origin: parking-v8-app-avalonia
---

# `Camera.AI_ACTIVE_CODE` static field không bao giờ được gán — ReadPL/AI luôn chạy degraded mode im lặng

## Tình huống gặp phải

Đang hoàn thiện fix loại bỏ SkiaSharp + tích hợp ReadPL 1.1.2 (tensor API) cho pipeline camera
(`Kztek.Cameras.Avalonia`). User hỏi: "Camera.AI_ACTIVE_CODE chưa có set giá trị khi loading" — nghi
ngờ activation code cho SDK nhận dạng chưa từng được gán ở đâu trong app thật (ParkingV8), chỉ có trong
tool test nội bộ (`MotionGateTest`, nhập tay qua TextBox UI).

## Triệu chứng / Lỗi

`grep -r "AI_ACTIVE_CODE" src/` trên toàn bộ repo `parking-v8-app-avalonia` → **0 kết quả** (không nơi
nào gán field này). `LprConfig.AIActiveCode` (property cấu hình sẵn có, đọc từ config/DB) tồn tại nhưng
KHÔNG BAO GIỜ được copy sang `Kztek.Cameras.Camera.AI_ACTIVE_CODE` (static field của thư viện camera).
Hệ quả: `AnvPlayerService.plateReader` (`public static readonly NhanDangBienSo? plateReader = new
NhanDangBienSo("GPU", "NORMAL", Camera.AI_ACTIVE_CODE);`) luôn khởi tạo với activation code RỖNG.
SDK ReadPL chạy ở "degraded mode" — im lặng không detect biển số/AI đúng, KHÔNG throw exception, không
log lỗi rõ ràng (đã xác nhận trong log điều tra trước đó của library repo: "aiEvents=0... AI_ACTIVE_CODE
rỗng → không detect", "Known-limitation" ghi nhận nhiều lần trong plan cũ nhưng chưa từng fix ở app thật).

## Nguyên nhân gốc rễ (Root Cause)

1. `Camera.AI_ACTIVE_CODE` (`Kztek.Cameras.Avalonia/Camera.cs`) là `public static string AI_ACTIVE_CODE = ""`
   — field static thường (không readonly ở đây, nhưng field TIÊU THỤ nó — `plateReader` — LÀ readonly).
2. `AnvPlayerService.plateReader` là `static readonly` — C# chỉ chạy static field initializer **DUY NHẤT
   1 LẦN**, tại lần đầu tiên bất kỳ member static/instance nào của class `AnvPlayerService` được chạm
   (JIT type initialization). Nếu `Camera.AI_ACTIVE_CODE` chưa được gán giá trị thật TRƯỚC thời điểm đó,
   `plateReader` sẽ "đóng băng" activation code rỗng vĩnh viễn cho toàn bộ vòng đời process — gán lại
   `Camera.AI_ACTIVE_CODE` SAU đó KHÔNG có tác dụng gì (đã late-bound vào `plateReader` rồi).
3. Không ai từng viết code copy `LprConfig.AIActiveCode` (đã có sẵn trong model config) sang
   `Camera.AI_ACTIVE_CODE` trong ParkingV8 — chỉ tool test nội bộ (`MotionGateTest.MainForm.cs`) gán từ
   TextBox UI, không áp dụng cho app thật.

## Giải pháp

Gán `Kztek.Cameras.Camera.AI_ACTIVE_CODE` **CÀNG SỚM CÀNG TỐT** trong bootstrap — ngay sau khi load
config, chắc chắn TRƯỚC khi bất kỳ camera nào `Start()` (tức trước khi `AnvPlayerService` bị chạm lần
đầu). Đặt trong `AppStartupLoader.PrepareBootstrapStateAsync()`, ngay sau `configurationService.Load()`:

```csharp
var configuration = configurationService.Load();
Kztek.Cameras.Camera.AI_ACTIVE_CODE = configuration.Lpr.AIActiveCode;
```

Lưu ý: fully-qualify `Kztek.Cameras.Camera` (không `using Kztek.Cameras;`) nếu file đã có type `Camera`
khác cùng tên (VD: DTO camera từ backend, `Kztek.Object`) — tránh xung đột namespace.

## Áp dụng lại (How to reuse)

- Khi thấy pattern `public static readonly X field = new X(..., SomeStaticConfigField, ...)` — LUÔN hỏi
  "`SomeStaticConfigField` được gán ở đâu, và có CHẮC CHẮN chạy TRƯỚC lần đầu class này bị chạm không?"
  Đừng tin rằng gán field static ở bất kỳ đâu trong app là "đủ" — thứ tự thực thi quan trọng tuyệt đối
  với `static readonly`.
- Khi 1 SDK/thư viện có "degraded mode" khi thiếu license/activation key mà KHÔNG throw exception rõ
  ràng — luôn `grep` toàn repo tên field/key để xác nhận nó THỰC SỰ được gán ở app thật, không chỉ ở tool
  test nội bộ hay tài liệu hướng dẫn.
- Sau khi thêm activation code thật, PHẢI test lại bằng camera/video có biển số thật để xác nhận detect
  hoạt động — trước đó mọi "PASS" trong test đều chỉ xác nhận "không crash", không xác nhận nhận dạng
  đúng (xem `PLAN-fix-camera-livestream-box-delay-2026-07-07.md` — nhiều vòng test bị chặn ở đúng vấn đề
  này mà không ai truy đến gốc).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đừng đặt việc gán `AI_ACTIVE_CODE` SAU bước "InitLprEngine" trong loading nếu bước đó (hoặc bất kỳ
  code nào trước nó) đã lỡ chạm `AnvPlayerService`/`Camera` (Kztek.Cameras) — dù chỉ 1 dòng code gọi
  method static của class đó cũng đủ trigger static initializer sớm. An toàn nhất: gán ngay khi vừa đọc
  xong config, TRƯỚC MỌI thứ khác liên quan tới namespace `Kztek.Cameras`.
- ⚠️ `Camera.AI_ACTIVE_CODE` (Kztek.Cameras) và một class `Camera` KHÁC (DTO camera từ backend, dùng phổ
  biến trong `AppStartupLoader.cs`) dễ gây nhầm — luôn fully-qualify khi cả 2 cùng xuất hiện trong 1 file.
- ⚠️ Không log activation code ra console/log file (dù để debug) — đây là secret, tương tự bài học
  `PRD-motiongatetest-rebuild.md` (đã từng leak activation key thật vào `launchSettings.json`/source).

## Tham chiếu

- `Kztek.Cameras.Avalonia/Camera.cs` — `public static string AI_ACTIVE_CODE`.
- `Kztek.Cameras.Avalonia/Players/FFMPEG/UserControls/AnvPlayerService.cs` — `plateReader` (static readonly).
- `Kztek.Object.MultyPlatform/ConfigObjects/LprConfig.cs` — `AIActiveCode` property (đã có sẵn, chưa từng dùng).
- `parking-v8-app-avalonia/src/ParkingV8.App/Bootstrap/AppStartupLoader.cs` — nơi fix (gán ngay sau load config).
- Lịch sử known-limitation: `Kztek.Camera/.claude/plans/PLAN-fix-camera-livestream-box-delay-2026-07-07.md`
  (nhiều lần ghi nhận "AI_ACTIVE_CODE rỗng → không detect" nhưng chưa ai fix ở app thật).
