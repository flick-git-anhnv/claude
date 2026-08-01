---
category: linux-desktop
tags: [dotnet, runtime, deploy-detection, systemd, offline-install]
severity: medium
created: 2026-07-30
updated: 2026-07-30
project-origin: 6.RemoteControlTool (IPGS.RemoteControl.ZcuAgent / CcuUI offline deploy)
---

# `dotnet --version` báo lỗi/NOT_FOUND dù .NET Runtime đã cài đủ (chỉ hoạt động khi có SDK)

## Tình huống gặp phải

Đang cài đặt offline `IPGS.RemoteControl.ZcuAgent` (.NET 8, framework-dependent) lên máy
ZCU (Ubuntu 22.04) qua `ZcuRemoteInstallerService` (SSH.NET). Máy đích chỉ cần **Runtime**
(không cần SDK) vì app publish kiểu `--self-contained false`. Bước kiểm tra "đã cài .NET
chưa" dùng lệnh:

```bash
dotnet --version 2>/dev/null || $HOME/.dotnet/dotnet --version 2>/dev/null || echo 'NOT_FOUND'
```

## Triệu chứng / Lỗi

Sau khi cài `.dotnet` bằng cách giải nén tarball Runtime offline (`dotnet-runtime-8.0.20-linux-x64.tar.gz`)
vào `$HOME/.dotnet`, chạy `$HOME/.dotnet/dotnet --version` vẫn báo lỗi:

```
The command could not be loaded, possibly because:
  * You intended to execute a .NET application:
      The application '--version' does not exist.
  * You intended to execute a .NET SDK command:
      No .NET SDKs were found.
```

Trong khi `$HOME/.dotnet/dotnet --list-runtimes` lại in đúng:
```
Microsoft.NETCore.App 8.0.20 [/home/kztek/.dotnet/shared/Microsoft.NETCore.App]
```

## Nguyên nhân gốc rễ (Root Cause)

`dotnet --version` là lệnh **cấp SDK** — muxer `dotnet` cần tìm 1 SDK cài sẵn để thực thi
lệnh này, dù chỉ để in version. Máy chỉ cài **Runtime** (không có SDK, đúng theo thiết kế
"chỉ cần Runtime trên production") thì `dotnet --version` LUÔN fail/timeout dù runtime đã
cài đủ và app chạy bình thường qua systemd (`ExecStart=.../IPGS.RemoteControl.ZcuAgent`
+ `DOTNET_ROOT` — không đi qua muxer `dotnet --version` nên không bị ảnh hưởng).

Hệ quả: nếu dùng `dotnet --version` để "check đã cài chưa" trước khi cài, installer sẽ
LUÔN nghĩ là NOT_FOUND (dù đã cài từ lần chạy trước) → tải lại/giải nén lại runtime mỗi
lần chạy installer — lãng phí, không phải lỗi chặn hoạt động nhưng gây hiểu nhầm.

## Giải pháp

Dùng `dotnet --list-runtimes` (hoạt động đúng với CẢ SDK lẫn Runtime-only install) thay
`dotnet --version`, và check output có chứa `"Microsoft.NETCore.App"` thay vì kiểm tra
"NOT_FOUND":

```csharp
var dotnetCheck = ExecuteCommand(ssh,
    "dotnet --list-runtimes 2>/dev/null || $HOME/.dotnet/dotnet --list-runtimes 2>/dev/null || echo 'NOT_FOUND'");
if (!dotnetCheck.Contains("Microsoft.NETCore.App"))
{
    // cài .NET Runtime
}
```

## Áp dụng lại (How to reuse)

- Khi viết script/code kiểm tra ".NET đã cài chưa" trên máy **chỉ cài Runtime** (không SDK)
  → LUÔN dùng `dotnet --list-runtimes` hoặc `dotnet --list-sdks`, KHÔNG dùng `dotnet --version`.
- `dotnet --version`/`dotnet --info` yêu cầu SDK — chỉ dùng detection kiểu này trên máy dev
  có cài SDK đầy đủ, không dùng trên máy production framework-dependent runtime-only.
- Khi verify 1 lệnh CLI "có hoạt động không" trên máy production, luôn test bằng SSH thật
  (như đã làm ở đây) thay vì tin vào tài liệu/thói quen — hành vi `dotnet` muxer thay đổi
  tùy có SDK hay không, dễ gây bug âm thầm nếu chỉ test trên máy dev (luôn có SDK).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Không phải bug chặn hoạt động — app vẫn chạy đúng qua systemd dù `dotnet --version` fail,
  vì systemd ExecStart gọi thẳng apphost + `DOTNET_ROOT`, không qua lệnh `dotnet --version`.
- ⚠️ Dễ nhầm là "cài thất bại" nếu debug bằng cách gõ tay `dotnet --version` trên máy production
  chỉ có Runtime — phải dùng `--list-runtimes` để kiểm tra đúng.

## Tham chiếu

- Project liên quan: `6.RemoteControlTool` — `IPGS.RemoteControl.CcuClient/ZcuRemoteInstallerService.cs` (F20)
- `docs/devops/DEPLOY-remote-control.md` mục 2.3 (GOTCHA cài đặt .NET Runtime)
