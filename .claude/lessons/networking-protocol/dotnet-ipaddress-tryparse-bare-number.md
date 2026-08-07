---
category: networking-protocol
tags: [ipaddress, tryparse, ip-range-parsing, dotnet, csharp, winforms]
severity: medium
created: 2026-08-05
updated: 2026-08-05
project-origin: KztekAdbPublishTool
---

# IPAddress.TryParse("254") KHÔNG báo lỗi — phá vỡ logic phân biệt "IP đầy đủ" vs "octet đơn"

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Đang implement tính năng quét dải mạng LAN (NetworkScanForm) trong app WinForms .NET 8, cho phép user
nhập dải IP rút gọn dạng `192.168.1.1-254` (thay vì phải gõ đầy đủ `192.168.1.1-192.168.1.254`).
Logic dự định: thử `IPAddress.TryParse` vế sau dấu `-` trước; nếu fail thì coi là octet cuối (`byte.TryParse`).

## Triệu chứng / Lỗi

> Lỗi hiện ra như thế nào? Exception message? Behavior sai?

User nhập `192.168.1.1-254` và bấm Quét → hiện lỗi "Chỉ hỗ trợ quét trong cùng dải /24 (3 octet đầu phải
giống nhau)." mặc dù input hoàn toàn hợp lệ theo định dạng rút gọn đã thiết kế.

```
Dải IP không hợp lệ: Chỉ hỗ trợ quét trong cùng dải /24 (3 octet đầu phải giống nhau).
```

## Nguyên nhân gốc rễ (Root Cause)

> Tại sao xảy ra? Không ghi "chưa rõ" — phải điều tra đến cùng.

`System.Net.IPAddress.TryParse("254")` **trả về `true`** — không fail như kỳ vọng! .NET kế thừa cú pháp
IPv4 kiểu cũ (giống `inet_aton` của C): 1 số đơn được hiểu là giá trị 32-bit đầy đủ, tự động expand thành
`0.0.0.254`. Tương tự `"1.254"` → `1.0.0.254`, `"1.2.254"` → `1.2.0.254`. Vì vậy code `if (IPAddress.TryParse(parts[1], out var endIpFull))`
luôn đi vào nhánh "coi là IP đầy đủ" thay vì rơi xuống nhánh `byte.TryParse` dự định, khiến octet cuối bị
tính sai hoàn toàn (thành `0.0.0.254` thay vì giữ nguyên 3 octet đầu của IP bắt đầu).

## Giải pháp

> Làm gì để fix? Bước nào theo thứ tự nào?

Không dựa vào `IPAddress.TryParse` để phân biệt 2 định dạng — phải tự kiểm tra sự hiện diện của dấu `.`
TRƯỚC khi quyết định nhánh xử lý:

```csharp
if (parts[1].Contains('.'))
{
    // Chắc chắn là IP đầy đủ (có dấu chấm) — parse bình thường
    if (!IPAddress.TryParse(parts[1], out var endIpFull)) { /* báo lỗi */ }
    endBytes = endIpFull.GetAddressBytes();
}
else if (byte.TryParse(parts[1], out var lastOctet))
{
    // Không có dấu chấm — chắc chắn là octet cuối rút gọn
    endBytes = (byte[])startBytes.Clone();
    endBytes[3] = lastOctet;
}
else
{
    /* báo lỗi định dạng */
}
```

1. Không bao giờ dùng `IPAddress.TryParse(x)` làm điều kiện `if` đầu tiên khi `x` có thể là 1 số bare (không dấu chấm) mà ý định là "octet/phần tử đơn lẻ", không phải IP đầy đủ.
2. Luôn kiểm tra định dạng cấu trúc (có `.` hay không, số phần tách bởi `.`) trước khi gọi `TryParse`.

## Áp dụng lại (How to reuse)

> Lần sau gặp tình huống tương tự, làm gì ngay lập tức?

- Khi thấy code dùng `IPAddress.TryParse` để "thử parse rồi fallback nếu fail" cho input rút gọn (short-hand)
  → kiểm tra ngay input có phải số bare (không dấu chấm) không, vì `TryParse` sẽ KHÔNG fail cho các dạng
  rút gọn `"w"`, `"w.x"`, `"w.x.y"` — tất cả đều hợp lệ theo chuẩn IPv4 cũ.
- Viết unit test/test case thủ công với input dạng `"254"`, `"1.254"` để xác nhận hành vi trước khi tin
  tưởng `TryParse` làm bộ phân loại (discriminator) giữa 2 định dạng khác nhau.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `IPAddress.TryParse("192")` → hợp lệ, ra `0.0.0.192`. `IPAddress.TryParse("192.168")` → hợp lệ, ra `192.0.0.168`. Không có cách nào để `TryParse` tự báo "đây không phải IP đầy đủ" — phải tự kiểm tra cấu trúc chuỗi trước.
- ⚠️ Lỗi này im lặng — không throw exception, không log gì bất thường, chỉ ra kết quả tính toán sai (subnet mismatch) khiến người dùng tưởng nhầm là do nhập sai, trong khi code mới là nguyên nhân.

## Tham chiếu

- Project liên quan: KztekAdbPublishTool (`src/KztekAdbPublishTool/Forms/NetworkScanForm.cs`, hàm `OnScanAsync`)
