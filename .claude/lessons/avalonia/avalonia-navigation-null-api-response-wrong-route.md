---
category: avalonia
tags: [navigation, mvvm, api, null-guard, kiosk]
severity: high
created: 2026-07-21
updated: 2026-07-21
project-origin: IPGS.Kiosk.Avalonia (iPGSv4)
---

# NavigateTo sai route khi API trả về null — remain=0 bị hiểu nhầm là "đã thanh toán"

## Tình huống gặp phải

> Đang debug luồng tìm xe máy: `LocateVehicle → MotorVehicleResult → MotorInforDetail`.
> Sau khi click item trong `MotorVehicleResultView`, app không chuyển sang `MotorInforDetailView`.
> Project: `IPGS.Kiosk.Avalonia` (Avalonia MVVM kiosk, .NET 8 / Windows).

## Triệu chứng / Lỗi

```
App vẫn đứng ở màn MotorVehicleResult sau khi click item.
Không có exception, không crash, không log lỗi rõ ràng.
```

Nếu bật log sẽ thấy:
```
[MotorVehicleResultVM] plate=... total=0 remain=0
```
→ điều hướng sang `BikePaymentResult` (xe đã trả đủ) thay vì `MotorInforDetail`.

## Nguyên nhân gốc rễ (Root Cause)

Trong `MotorVehicleResultViewModel.ItemClicked`, logic tính `remain`:

```csharp
var vehicle = new PaymentVehicleDto
{
    TotalAmount    = detail?.Charge ?? 0,  // 0 khi detail null
    PaidAmount     = detail?.Amount ?? 0,  // 0 khi detail null
};
long remain = vehicle.GetRemain(); // Max(0, 0-0) = 0

if (remain <= 0)
    _nav.NavigateTo(AppRoutes.BikePaymentResult, vehicle);  // ← SAI
else
    _nav.NavigateTo(AppRoutes.MotorInforDetail, vehicle);
```

Khi `GetEntryByIdAsync` trả `null` (API lỗi, timeout, stub mode):
- `TotalAmount = 0`, `PaidAmount = 0` → `remain = 0`
- `remain <= 0` → navigate sang **BikePaymentResult** (xe đã trả đủ)
- THỰC TẾ: không biết trạng thái thanh toán, nên phải hiển thị **MotorInforDetail**

Đây là silent misdirection — không có exception, không log lỗi, app vẫn chạy nhưng sai luồng.

## Giải pháp

Dùng `detail.IsPaid` thay vì tính `remain` từ `PaymentVehicleDto`:

```csharp
// SAI: remain = 0 khi TotalAmount=0 → nhầm là "đã trả đủ"
long remain = vehicle.GetRemain();
if (remain <= 0) _nav.NavigateTo(AppRoutes.BikePaymentResult, vehicle);

// ĐÚNG: kiểm tra IsPaid từ API, null → mặc định về MotorInforDetail
if (detail != null && detail.IsPaid)
    _nav.NavigateTo(AppRoutes.BikePaymentResult, vehicle);
else
    _nav.NavigateTo(AppRoutes.MotorInforDetail, vehicle);
```

Đồng thời fix `DateTimeIn` fallback:

```csharp
// SAI:
DateTimeIn = DateTime.Now,  // luôn dùng "bây giờ"

// ĐÚNG:
var dateTimeIn = (detail?.DateTimeIn != default)
    ? detail!.DateTimeIn
    : (entry.DateTimeIn != default ? entry.DateTimeIn : DateTime.Now);
```

## Áp dụng lại (How to reuse)

- Khi mapping DTO có nullable field (API có thể null) → KHÔNG dùng `?? 0` cho field tài chính (Amount/Charge) rồi tính lại `remain` — tính `remain=0` từ null-coalesced zero là sai ngữ nghĩa.
- Luôn kiểm tra `source != null` TRƯỚC khi dùng trường tính toán từ source đó.
- Nguyên tắc: `null` = "chưa biết", không phải "=0" hay "đã xong".

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `NavigateTo` nằm trong `try` block — nếu nó throw (VD: ViewModel constructor lỗi), exception bị catch và log, navigation thất bại âm thầm, user vẫn thấy màn hình cũ.
- ⚠️ Stub (`KioskApiServiceStub.GetEntryByIdAsync`) trả `null` → luồng test offline luôn bị ảnh hưởng.
- ⚠️ Route `AppRoutes.MotorInforDetail` và `case AppRoutes.MotorInforDetail:` đúng, alias `MotoPaymentVehicleDto = IPGS.Kiosk.Avalonia.Models.PaymentVehicleDto` đúng — KHÔNG phải namespace confusion như lo ngại ban đầu.

## Tham chiếu

- File sửa: `IPGS.Kiosk.Avalonia/ViewModels/Moto/MotorVehicleResultViewModel.cs`
- `EntryDetailDto.IsPaid` — computed property trong `IKioskApiService.cs` (namespace `Services.Abstractions`)
- Project: iPGSv4 (`IPGS.Kiosk.Avalonia`)
