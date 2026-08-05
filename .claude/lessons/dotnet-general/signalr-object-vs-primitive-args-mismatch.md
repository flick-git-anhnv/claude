---
category: dotnet-general
tags: [signalr, asp.net-core, javascript, contract, real-time]
severity: high
created: 2026-08-05
updated: 2026-08-05
project-origin: KztekAdbPublishTool (migrate WinForms → ASP.NET Core)
---

# SignalR `SendAsync` với anonymous object vs primitive args — JS nhận sai kiểu

## Tình huống gặp phải

Migrate WinForms sang ASP.NET Core Razor Pages + SignalR. Backend C# push nhiều sự kiện
real-time (scan progress, install progress). Dev Phase 2 viết tách biệt backend và frontend
rồi ghép lại ở Phase 3 — phát hiện tất cả SignalR events đều bị broken khi chạy thật.

## Triệu chứng / Lỗi

JS không cập nhật UI dù server push event. Console không có lỗi.
Khi debug: tham số đầu tiên nhận được là **object**, không phải string/number như expect.

Ví dụ: backend gửi `SendAsync("ScanFound", new { ipPort })` → JS nhận `ipPort = {ipPort: "192.168.1.1:5555"}` thay vì string `"192.168.1.1:5555"`. `addFoundRow` hiển thị `[object Object]`.

## Nguyên nhân gốc rễ (Root Cause)

`IHubContext.SendAsync(method, arg1)` map **từng arg riêng biệt** sang từng tham số của JS handler.

```csharp
// Gửi 1 anonymous object → JS nhận 1 param kiểu object
await hub.SendAsync("ScanFound", new { ipPort });
// JS: conn.on("ScanFound", function(ipPort) { ... })
// → ipPort = { ipPort: "..." }  ← WRONG: là object, không phải string
```

Khi backend gửi **anonymous object** (dù chỉ có 1 field), SignalR serialize thành JSON object
`{"ipPort":"..."}` và JS nhận **toàn bộ object đó** làm giá trị của tham số đầu tiên.

Ngược lại, nếu backend gửi **primitive trực tiếp**:
```csharp
await hub.SendAsync("ScanFound", ipPort);  // string
// → JS nhận string "192.168.1.1:5555" ✅
```

Và khi muốn gửi **nhiều tham số** → truyền nhiều arg vào SendAsync:
```csharp
await hub.SendAsync("ScanProgress", found, scanned, total);
// → JS: function(found, scanned, total) — 3 param riêng biệt ✅
```

## Giải pháp

Với mỗi SignalR event, **đọc kỹ JS handler trước** để xác định:
- Số lượng tham số JS expect
- Kiểu của mỗi tham số (string, int, bool, hay object)

Rồi gọi `SendAsync` với **đúng kiểu và số lượng arg**:

```csharp
// ❌ Sai — JS nhận object thay vì string
await hub.SendAsync("ScanFound", new { ipPort });

// ✅ Đúng — JS nhận string trực tiếp
await hub.SendAsync("ScanFound", ipPort);

// ❌ Sai — JS nhận 1 object, không phải 3 params riêng
await hub.SendAsync("ScanProgress", new { found, scanned, total });

// ✅ Đúng — JS nhận 3 params riêng biệt
await hub.SendAsync("ScanProgress", found, scanned, total);

// ❌ Sai khi JS expect bool — backend gửi string "Thành công"
await hub.SendAsync("DeviceInstalled", new { serial, status, version });

// ✅ Đúng — compute bool, gửi primitive
var success = status == "Thành công";
await hub.SendAsync("DeviceInstalled", serial, success, version);
```

## Áp dụng lại (How to reuse)

- Khi viết SignalR event mới → **viết JS handler trước** (define param names & types), sau đó viết C# SendAsync để khớp — không làm ngược lại.
- Khi review code SignalR → đối chiếu **1-1 từng arg** giữa `SendAsync(method, a, b, c)` và `conn.on(method, function(a, b, c))`.
- Nếu cần gửi complex object (VD: device record với nhiều field) → gửi 1 object là đúng; nhưng khi đó JS handler phải nhận 1 tham số duy nhất `function(data)` rồi đọc `data.field`.
- **Rule of thumb:** primitive/array → gửi trực tiếp; object phức tạp nhiều field → gửi object, handler nhận 1 tham số.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Anonymous object `new { ipPort }` tưởng là "wrapper tiện lợi" nhưng thực ra thay đổi hoàn toàn cách JS nhận data — JS nhận cả object, không phải field value.
- ⚠️ Khi dev backend và frontend tách nhau (multi-agent parallel), định nghĩa SignalR signature PHẢI được viết ra ở DeviceHub comment (hoặc một file contract chung) TRƯỚC — không để 2 phía tự giả định rồi ghép.
- ⚠️ Nếu dùng strongly-typed hub (`Hub<IDeviceClient>`), compiler sẽ catch mismatch. Với `IHubContext<T>` và `SendAsync` dynamic, không có compile-time check — cần test thực tế.
- ⚠️ Lỗi này **không có exception** — JS handler được gọi nhưng nhận giá trị sai kiểu; `typeof` check hoặc console.log mới phát hiện được.

## Tham chiếu

- [ASP.NET Core SignalR — Send messages from hub](https://learn.microsoft.com/en-us/aspnet/core/signalr/hubs#send-messages-from-outside-a-hub)
- Project liên quan: KztekAdbPublishTool (branch docker-deploy, commit 058aea5)
