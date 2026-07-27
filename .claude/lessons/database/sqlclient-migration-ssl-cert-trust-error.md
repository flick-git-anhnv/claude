---
category: database
tags: [sqlclient, migration, ssl-tls, connection-string, linux-compat]
severity: high
created: 2026-07-20
updated: 2026-07-20
project-origin: iPGSv4 ZCU Avalonia migration
---

# Đổi System.Data.SqlClient → Microsoft.Data.SqlClient gây lỗi SSL certificate chain not trusted

## Tình huống gặp phải

Đổi package `System.Data.SqlClient` (deprecated, chỉ chạy tốt trên .NET Core với hạn chế) sang `Microsoft.Data.SqlClient` 5.2.2 để hỗ trợ chạy trên Ubuntu/Linux (project target `net8.0` với `RuntimeIdentifiers` gồm `linux-x64`). Chỉ đổi `PackageReference` + `using` namespace, không đổi connection string. Build pass, nhưng khi connect tới SQL Server on-prem (self-signed cert) thì lỗi ngay khi mở connection.

## Triệu chứng / Lỗi

IntelliTrace / exception log:
```
Exception thrown: 'Microsoft.Data.SqlClient.SqlException' in Microsoft.Data.SqlClient.dll
("A connection was successfully established with the server, but then an error occurred
during the login process. (provider: SSL Provider, error: 0 - The certificate chain was
issued by an authority that is not trusted.)")
```
Kết nối cùng server, cùng connection string y hệt lúc trước hoạt động bình thường với `System.Data.SqlClient`.

## Nguyên nhân gốc rễ (Root Cause)

`Microsoft.Data.SqlClient` (từ v3.0+) mặc định `Encrypt=Mandatory/True` và **validate SSL certificate chain nghiêm ngặt** khi mở connection — khác với `System.Data.SqlClient` legacy vốn không encrypt/không validate cert theo default. SQL Server on-prem (VD: `DCTHANH\SQLEXPRESS`) thường dùng self-signed certificate → certificate chain không được CA tin cậy ký → `Microsoft.Data.SqlClient` từ chối kết nối ngay ở bước login, dù TCP connect thành công.

## Giải pháp

Thêm `TrustServerCertificate=True` vào MỌI connection string SQL Server (cả Windows Authentication và SQL Authentication):

```csharp
// Windows Authentication
$"data source={serverName};initial Catalog=master;Integrated Security=True;TrustServerCertificate=True"

// SQL Authentication
$"data source={serverName};initial Catalog=master;user id={username};password={password};TrustServerCertificate=True"
```

1. Grep toàn bộ codebase tìm nơi build connection string (`SqlConnection(`, `GetConnectStr`, `strConn =`, `connStr =`).
2. Thêm `TrustServerCertificate=True` vào cuối mỗi chuỗi.
3. Build + test connect thật tới SQL Server on-prem để xác nhận hết lỗi (không chỉ build pass).

## Áp dụng lại (How to reuse)

- Bất kỳ khi nào migrate `System.Data.SqlClient` → `Microsoft.Data.SqlClient` (hoặc nâng version `Microsoft.Data.SqlClient` lên ≥3.0) → **PHẢI** rà soát connection string, không chỉ đổi package + using.
- Dấu hiệu nhận biết ngay: exception message chứa `"certificate chain was issued by an authority that is not trusted"` sau khi login thành công ở TCP layer → luôn là thiếu `TrustServerCertificate=True` (hoặc `Encrypt=False` nếu môi trường dev không cần mã hóa).
- Nếu server có cert hợp lệ (CA-signed) thì không cần `TrustServerCertificate=True` — nhưng với SQL Server on-prem/dev/test hầu như luôn self-signed, nên mặc định thêm option này khi target Linux/cross-platform.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Chỉ đổi `PackageReference` + `using System.Data.SqlClient` → `using Microsoft.Data.SqlClient` là **build pass nhưng runtime fail** — lỗi này không xuất hiện lúc compile, chỉ lộ ra khi connect thật (rất dễ báo "xong" nhầm nếu chỉ verify bằng build).
- ⚠️ `TrustServerCertificate=True` làm giảm bảo mật (bỏ qua xác thực cert) — chỉ chấp nhận được với SQL Server nội bộ đáng tin cậy (LAN/VPN), KHÔNG dùng cho kết nối qua Internet công khai mà không có kiểm soát khác.
- ⚠️ API namespace `Microsoft.Data.SqlClient` gần tương thích 100% với `System.Data.SqlClient` (class names giống nhau: `SqlConnection`, `SqlCommand`, `SqlException`...) nên rất dễ nghĩ "đổi xong rồi" chỉ sau khi build sạch.

## Tham chiếu

- Files đã fix: `IPGS.Object/Databases/MDB.cs`, `ApplicationConfig/Views/SqlConfigView.axaml.cs`, `ApplicationConfig/UserControls/ucSQLConfig.cs`, `IPGSUseCam/Forms/SystemForm/frmLoading.cs`
- Project: iPGSv4, branch zcu-avalonia
- Microsoft Docs: [Connection string TrustServerCertificate](https://learn.microsoft.com/sql/connect/ado-net/sql-server-native-client-support)
