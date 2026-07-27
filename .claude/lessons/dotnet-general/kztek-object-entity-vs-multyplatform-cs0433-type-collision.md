---
category: dotnet-general
tags: [CS0433, type-collision, kztek-object, multyplatform, kztek-cameras-avalonia, migration, logging]
severity: high
created: 2026-07-26
updated: 2026-07-26
project-origin: DoorAlarmv3.Avalonia (migrate WinForms → Avalonia, Bước 3.5)
---

# `Kztek.Object.Entity` và `Kztek.Object.MultyPlatform` trùng tên kiểu → CS0433 khi thêm `Kztek.Cameras.Avalonia`

## Tình huống gặp phải

Project `DoorAlarmv3.Avalonia` đang build sạch, tham chiếu `Kztek.Object.Entity` (qua `Kztek.Tool`
/ `Kztek.Database`). Đến bước port camera, thêm `ProjectReference` tới `Kztek.Cameras.Avalonia` —
thư viện này kéo theo `Kztek.Object.MultyPlatform` (của `parking-v8-app-avalonia`).

Lập tức **5 lỗi biên dịch ở những file không hề đụng tới camera**.

## Triệu chứng / Lỗi

```
error CS0433: The type 'EmSystemActionType' exists in both
  'Kztek.Object.Entity, Version=1.0.1.0, ...' and
  'Kztek.Object.MultyPlatform, Version=1.0.0.0, ...'
error CS0433: The type 'EmLogServiceType' exists in both ...
```

Lỗi rơi vào `Program.cs`, `LoginViewModel.cs`, `MainWindowViewModel.cs` — tức là **các file ghi log**,
không phải file camera. Dễ hiểu nhầm là do mình viết sai `using`.

## Nguyên nhân gốc rễ

`Kztek.Object.MultyPlatform` là bản port cross-platform của `Kztek.Object.Entity` nhưng **giữ nguyên
namespace và tên kiểu**: `Kztek.Object.SystemUtils`, `Kztek.Object.SystemLog`,
`Kztek.Object.EmSystemActionType`, `Kztek.Object.EmLogServiceType`…

Khi một project tham chiếu **cả hai** assembly, compiler không biết chọn kiểu nào → CS0433.
Không phải lỗi `using`, và **không sửa được bằng cách đổi thứ tự `using`**.

## Giải pháp (ĐÃ KIỂM CHỨNG)

Không dùng `extern alias` (phải sửa mọi call site, rất lan man). Thay vào đó **gom toàn bộ điểm chạm
với cặp kiểu bị trùng vào đúng một project** — ở đây là project lõi chỉ tham chiếu
`Kztek.Object.Entity`:

```csharp
// DoorAlarm.Core/CoreLog.cs  — chỉ project này "biết" SystemUtils/SystemLog/EmSystemActionType
public static class CoreLog
{
    public static void Initialize(string basePath)
        => SystemUtils.logger = LoggerFactory.CreateLoggerService(EmLogServiceType.OFFLINE_DB, basePath);

    public static void Info(string action)  => Write(action, null, EmSystemActionType.INFO);
    public static void Warn(string action, Exception? ex = null) => Write(action, ex, EmSystemActionType.WARNING);
    public static void Error(string action, Exception? ex)       => Write(action, ex, EmSystemActionType.ERROR);
    ...
}
```

Rồi thay mọi lời gọi trực tiếp ở project UI:

```csharp
// TRƯỚC (vỡ khi thêm thư viện camera)
SystemUtils.logger?.SaveSystemLog(SystemLog.CreateApplicationProccess(action, ex, EmSystemActionType.ERROR));

// SAU
CoreLog.Error(action, ex);
```

Sau đó build sạch trên **cả win-x64 lẫn linux-x64**, self-test chạy thật cũng PASS.

## Áp dụng lại

- Trước khi thêm một thư viện KZTEK lớn (`Kztek.Cameras.Avalonia`, `parking-v8` …) vào project đang
  chạy tốt: kiểm nó kéo theo assembly nào — `dotnet list package --include-transitive`, hoặc mở
  `.csproj` xem `ProjectReference` bắc cầu. Thấy `Kztek.Object.MultyPlatform` → **chuẩn bị sẵn** lớp
  bọc log/tiện ích trước, đừng để vỡ rồi mới sửa rải rác.
- Quy tắc chung khi migrate: **đừng gọi thẳng API của thư viện nền ở lớp UI**. Một lớp bọc mỏng
  (`CoreLog`) biến 5 lỗi rải rác thành 1 chỗ sửa.
- Lỗi CS0433 luôn kèm tên **hai assembly** trong thông báo — đọc tên assembly, đừng đọc tên kiểu, thì
  ra nguyên nhân ngay.

## Chú ý / Cạm bẫy

- ⚠️ Lỗi hiện ở file **không liên quan** tới thư viện vừa thêm → dễ đi sai hướng (tưởng lỗi `using`).
- ⚠️ Namespace project trùng tiền tố cũng gây lỗi tương tự nhưng **khác mã lỗi**: `CS0118`
  (`'Camera' is a namespace but is used like a type`) khi đặt namespace `DoorAlarm.Core.Camera` cạnh
  kiểu `Kztek.Cameras.Camera` — phải đổi thành `DoorAlarm.Core.Cameras` (số nhiều).
- ⚠️ `extern alias` chạy được nhưng phải khai báo ở **mọi** file dùng kiểu đó, và IDE hay mất alias
  khi sinh code — không đáng cho trường hợp này.

## Tham chiếu

- Project: `DoorAlarmv3.Avalonia` / `DoorAlarm.Core` / `DoorAlarm.Core.Camera`
- File: `DoorAlarm.Core/CoreLog.cs`
- Plan: `docs/plans/PLAN-migrate-dooralarmv3-avalonia-2026-07-26/steps/STEP-3.5-camera-views.md`
- Liên quan: `avalonia-namespace-collision-ipgs-kiosk.md`
