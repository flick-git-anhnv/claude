---
category: dotnet-general
tags: [implicitusings, task, async, csproj, class-library]
severity: medium
created: 2026-07-15
updated: 2026-07-15
project-origin: iPGSv4 (IPGS.Object library)
---

# IPGS.Object (và các class library cũ) không có ImplicitUsings — Task<> không tìm thấy

## Tình huống gặp phải

Đang tạo interface `IInvoiceService.cs` trong project `IPGS.Object` (class library .NET 8, không phải WinForms app). File interface khai báo 3 method trả về `Task<T?>`. Build thành công tại `IPGS.Kiosk` nhưng bị lỗi tại `IPGS.Object`.

## Triệu chứng / Lỗi

```
IPGS.Object/ParkingObjects/Interfaces/IInvoiceService.cs(16,9): error CS0246:
The type or namespace name 'Task<>' could not be found
(are you missing a using directive or an assembly reference?)
```

Lỗi xuất hiện tại tất cả method signatures dùng `Task<>`.

## Nguyên nhân gốc rễ (Root Cause)

`IPGS.Object.csproj` không có `<ImplicitUsings>enable</ImplicitUsings>`. Trong khi project `IPGS.Kiosk` (WinForms app) có implicit usings (bao gồm `System.Threading.Tasks`), project library cũ thường được tạo trước .NET 6 SDK và không bật tính năng này.

```xml
<!-- IPGS.Object.csproj — KHÔNG có dòng này -->
<ImplicitUsings>enable</ImplicitUsings>

<!-- IPGS.Kiosk.csproj — CÓ hoặc WinForms SDK tự bật -->
<ImplicitUsings>enable</ImplicitUsings>
```

Kết quả: `Task`, `List<>`, `Dictionary<>`, v.v. đều cần `using` tường minh trong `IPGS.Object`.

## Giải pháp

Thêm `using System.Threading.Tasks;` vào đầu file interface (KHÔNG sửa csproj để tránh ảnh hưởng toàn bộ library):

```csharp
using System.Threading.Tasks;          // ← BẮT BUỘC nếu project không có ImplicitUsings
using IPGS.Object.ParkingObjects.Payment;

namespace IPGS.Object.ParkingObjects.Interfaces
{
    public interface IInvoiceService
    {
        Task<TaxpayerLookupResponse?> LookupTaxpayerAsync(string taxCode, int timeOut = 10000);
        // ...
    }
}
```

## Áp dụng lại (How to reuse)

- Khi tạo file mới trong project library cũ (`IPGS.Object`, `Kztek.Object`, v.v.) và dùng `Task`, `List`, `Dictionary`, `IEnumerable` → PHẢI thêm explicit `using`.
- Kiểm tra csproj: nếu không thấy `<ImplicitUsings>enable</ImplicitUsings>` → project KHÔNG có implicit usings, mọi type ngoài `System` core phải `using` rõ ràng.
- Dấu hiệu nhận biết nhanh: mở file `.cs` bất kỳ đã có sẵn trong project đó và xem có bao nhiêu `using` tường minh — nếu nhiều → project không có ImplicitUsings.

## Chú ý / Cạm bẫy (Gotchas)

- Không thêm `<ImplicitUsings>enable</ImplicitUsings>` vào csproj của library dùng chung trừ khi có lý do rõ ràng — có thể sinh conflict nếu code cũ trong cùng project đã có `using` trùng lặp (compiler cảnh báo CS0105: using directive appeared previously).
- `IPGS.Kiosk` (WinForms, .NET 8) tự có ImplicitUsings vì SDK WinForms mới bật mặc định — KHÔNG phải tất cả project trong cùng solution đều giống nhau.
- `System.Collections.Generic` (List/Dictionary) cũng cần `using` rõ trong project không có ImplicitUsings.

## Tham chiếu

- `IPGS.Object/IPGS.Object.csproj` — thiếu `<ImplicitUsings>enable</ImplicitUsings>`
- Project liên quan: iPGSv4 — `IPGS.Object/ParkingObjects/Interfaces/IInvoiceService.cs`
