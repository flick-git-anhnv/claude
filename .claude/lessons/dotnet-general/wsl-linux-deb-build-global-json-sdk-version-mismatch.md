---
category: dotnet-general
tags: [wsl, linux, dotnet-install, global.json, sdk-version, dpkg-deb, publish]
severity: medium
created: 2026-07-18
updated: 2026-07-18
project-origin: parking-v8-app-avalonia
---

# Build .deb qua WSL báo "A compatible .NET SDK was not found" dù đã cài dotnet

## Tình huống gặp phải

> Đang dựng quy trình build file cài đặt `.deb` cho app Avalonia (target `net8.0`) thông qua WSL Ubuntu, dùng script gọi `dotnet publish -r linux-x64`.

Dev cài .NET SDK trong WSL bằng `dotnet-install.sh --channel 8.0` (nghĩ rằng vì project target `net8.0` thì cần SDK 8.0), cài thành công, `dotnet --version` ra `8.0.423` — nhưng khi chạy script build vẫn báo lỗi.

## Triệu chứng / Lỗi

```
The command could not be loaded, possibly because:
  * You intended to execute a .NET SDK command:
      A compatible .NET SDK was not found.

Requested SDK version: 9.0.313
global.json file: .../global.json

Installed SDKs:
8.0.407 [/home/flick/.dotnet/sdk]
8.0.423 [/home/flick/.dotnet/sdk]

Install the [9.0.313] .NET SDK or update [.../global.json] to match an installed SDK.
```

## Nguyên nhân gốc rễ (Root Cause)

Repo có file `global.json` ở root pin **SDK version dùng để build** (`"sdk": {"version": "9.0.313", "rollForward": "latestFeature"}`), **độc lập** với `TargetFramework` khai báo trong `.csproj` (`net8.0`). Đây là 2 khái niệm khác nhau trong .NET:

- **TargetFramework** (`net8.0` trong `.csproj`) — runtime API surface project build nhắm tới, quyết định app chạy trên runtime nào.
- **SDK version** (`global.json`) — phiên bản **công cụ build** (`dotnet build`/`publish`/CLI) dùng để build project đó. SDK mới hơn (VD: .NET 9 SDK) hoàn toàn build được project target framework cũ hơn (`net8.0`) — đây là hành vi multi-targeting bình thường của .NET, không phải lỗi.

Vì vậy cài đúng "channel 8.0" theo trực giác (khớp TargetFramework) là **sai** — phải cài đúng SDK version ghi trong `global.json`, không phải theo TargetFramework.

## Giải pháp

1. Luôn `cat global.json` (hoặc mở file) ở root repo **trước khi** quyết định channel cài `dotnet-install.sh` — đừng suy luận SDK version từ TargetFramework trong `.csproj`.
2. Cài đúng SDK version/channel ghi trong `global.json`:
   ```bash
   wget https://dot.net/v1/dotnet-install.sh -O /tmp/dotnet-install.sh
   bash /tmp/dotnet-install.sh --channel 9.0   # khớp "sdk.version": "9.0.313"
   ```
3. Không cần gỡ SDK cũ (8.x) — nhiều SDK version cài song song trong `~/.dotnet/sdk`, `dotnet` CLI tự chọn đúng bản theo `global.json` khi có `rollForward` phù hợp.

## Áp dụng lại (How to reuse)

- Khi build fail với message `A compatible .NET SDK was not found` + `Requested SDK version: X.Y.Z` + `global.json file: ...` → đọc thẳng dòng `Requested SDK version` trong error, đó chính là channel cần cài — không cần đoán.
- Trước khi viết bất kỳ hướng dẫn "cài .NET SDK" nào cho 1 repo → luôn `Read`/`cat` `global.json` trước, đừng mặc định channel = TargetFramework.
- Khi viết script/doc onboarding build cho project có `global.json`, nên thêm bước hiển thị rõ: "SDK cần cài là X, không nhất thiết trùng TargetFramework Y".

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `rollForward: latestFeature` chỉ roll-forward trong cùng major.minor (VD: 9.0.313 → 9.0.4xx), **không** tự nhảy sang major khác (8.x sẽ không bao giờ thoả 9.0.313) — nên lỗi vẫn xảy ra dù có SDK 8.x mới nhất.
- ⚠️ `dotnet --version` chỉ in ra SDK mà `global.json` đang chọn (hoặc mới nhất nếu không có global.json) — không liệt kê hết SDK đã cài; dùng `dotnet --list-sdks` để xem đầy đủ khi debug.

## Tham chiếu

- Project liên quan: `parking-v8-app-avalonia` — `scripts/linux-deb/build-deb.sh`, `docs/devops/DEPLOY-linux-deb-setup.md`, `docs/devops/INFRA-wsl-usage-guide.md`
- https://learn.microsoft.com/dotnet/core/tools/global-json
