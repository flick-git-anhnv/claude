---
category: networking-protocol
tags: [namespace, port, copy-paste, dotnet, udp]
severity: medium
created: 2026-07-04
updated: 2026-07-04
project-origin: 3rdLedLib (KZtek.ControllerLib)
---

# File đã có trong project đích vẫn giữ namespace của project nguồn — build fail khi port class mới sang

## Tình huống gặp phải

Port `MT166Controller.cs` (project cũ `Kztek.Controller`, .NET Framework style) sang thư viện mới
`KZtek.ControllerLib` (.NET 8). Thư viện đích đã có sẵn `KZtek.ControllerLib/SocketHelpers/UdpTools.cs`
(dùng chung cho class `KzE02NetDevice` có sẵn), nên viết `using KZtek.ControllerLib.SocketHelpers;` cho
class mới theo đúng root namespace của project.

## Triệu chứng / Lỗi

```
error CS0234: The type or namespace name 'SocketHelpers' does not exist in the namespace 'KZtek.ControllerLib'
```

## Nguyên nhân gốc rễ (Root Cause)

File `KZtek.ControllerLib/SocketHelpers/UdpTools.cs` **đã tồn tại từ trước** trong project đích, nhưng đó
là bản copy-paste nguyên văn từ project cũ `Kztek.Controller` — kể cả dòng `namespace` cũng bị copy nguyên,
nên vẫn khai báo `namespace Kztek.Controller.SocketHelpers`, KHÔNG phải `KZtek.ControllerLib.SocketHelpers`
như vị trí file (đường dẫn thư mục) gợi ý. Class có sẵn `KzE02NetDevice.cs` trong cùng project đã âm thầm
`using Kztek.Controller.SocketHelpers;` để dùng được — bằng chứng namespace thật khác với đường dẫn file.

## Giải pháp

1. Không giả định namespace của một file dựa theo đường dẫn thư mục — luôn `Read` file đó trước khi viết
   `using` cho code mới tham chiếu tới nó.
2. Kiểm tra class có sẵn trong cùng project đã dùng namespace nào (ví dụ `KzE02NetDevice.cs` đã có
   `using Kztek.Controller.SocketHelpers;`) — đó là nguồn sự thật nhanh nhất, nhanh hơn đoán.
3. Sửa `using` cho khớp namespace thật, không sửa lại namespace của file cũ (ngoài phạm vi task, tránh phá
   vỡ code khác đang phụ thuộc namespace cũ).

```csharp
// Sai (đoán theo đường dẫn file):
using KZtek.ControllerLib.SocketHelpers;

// Đúng (namespace thật bên trong file, dù đường dẫn khác):
using Kztek.Controller.SocketHelpers;
```

## Áp dụng lại (How to reuse)

- Khi port/copy code sang project mới và cần dùng lại một helper "đã có sẵn" trong project đích →
  luôn mở file đó ra đọc `namespace` thật, đừng suy từ đường dẫn thư mục.
- Nếu nghi ngờ, tìm một file khác trong cùng project đã compile được và xem nó `using` gì cho helper đó.
- Dấu hiệu nhận biết: project được xây bằng cách "sao chép nguyên khối" từ project cũ (nhiều file cùng nội
  dung ở nhiều project) — rất dễ có namespace không khớp đường dẫn.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Không tự động đổi `namespace` trong file cũ để "cho khớp" đường dẫn — có thể có code khác (hoặc DLL
  build sẵn) đang phụ thuộc namespace cũ đó.
- ⚠️ Lỗi build CS0234 chỉ báo "namespace không tồn tại" — không tự nói namespace thật là gì; phải grep/Read
  file thực tế mới biết.

## Tham chiếu

- Project liên quan: `H:\Vitecode\Claude\3rdLedLib` (KZtek.ControllerLib, KZtek.ControllerLib.Demo)
- File gặp lỗi: `KZtek.ControllerLib/SocketHelpers/UdpTools.cs`, `KZtek.ControllerLib/CardDispenser/CardDispenserController.cs`
