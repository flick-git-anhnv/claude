---
category: avalonia
tags: [avaloniaresource, sound, printer, asset, silent-failure, output-directory]
severity: high
created: 2026-07-22
updated: 2026-07-22
project-origin: iPGSv4 (IPGS.Kiosk.Avalonia)
---

# `AvaloniaResource` không copy file ra output dir — code đọc bằng đường dẫn vật lý sẽ fail âm thầm

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Port âm thanh hướng dẫn (SoundServiceImpl dùng `System.Media.SoundPlayer` trên Windows, SoundServiceLinux dùng `paplay/aplay` process trên Linux) cho project Avalonia migrate từ WinForms. File `.wav` nằm trong `Assets/Sound/`, đường dẫn vật lý được cấp bởi `AppPathService.SoundRoot => Combine("Assets", "Sound")` (dựa trên `AppContext.BaseDirectory`).

## Triệu chứng / Lỗi

> Lỗi hiện ra như thế nào? Exception message? Behavior sai?

Chạy app thật trên Windows, chuyển màn hình (đổi ngôn ngữ, chọn loại xe, ...) — không nghe thấy âm thanh hướng dẫn nào, nhưng app KHÔNG crash, KHÔNG có lỗi hiển thị ra UI. Log hệ thống (`SystemUtils.logger`) có ghi lại exception `SoundServiceImpl.PlayAsync error` (FileNotFoundException) nhưng bị nuốt bởi try/catch nội bộ trong `SoundServiceImpl`/`SoundServiceLinux` — chỉ log, không throw ra ngoài.

Kiểm tra `bin/Debug/net8.0/` → **không có thư mục `Assets/Sound` nào cả**, chỉ có DLL + `appsettings.json`.

## Nguyên nhân gốc rễ (Root Cause)

`.csproj` chỉ khai báo:
```xml
<AvaloniaResource Include="Assets\**" />
```

`AvaloniaResource` nhúng file vào bên trong assembly (truy cập qua `avares://AssemblyName/Assets/...`), **KHÔNG copy file vật lý ra thư mục output** như `Content`/`None` với `CopyToOutputDirectory`. Đây là hành vi đúng và hữu ích cho Font (`FontHelper` dùng `avares://` để load `FontFamily` — không cần file vật lý) và ảnh hiển thị qua `Bitmap.Load(Stream)`.

Nhưng `System.Media.SoundPlayer(string path)`, `Process.Start("paplay", path)`, và `File.ReadAllText(path)` (đọc `Ticket.html` cho in phiếu) đều cần **đường dẫn file thật trên đĩa** — chúng không biết gì về `avares://`. Vì vậy bất kỳ service nào dùng `IPathService.SoundRoot`/`TicketTemplatePath`/`ImageRoot` (tất cả là physical path qua `AppContext.BaseDirectory`) đọc file vật lý sẽ luôn fail nếu file đó chỉ được khai báo `AvaloniaResource`.

## Giải pháp

Khai báo THÊM `Content` song song với `AvaloniaResource` cho các thư mục Assets nào có code đọc bằng đường dẫn vật lý (Sound, Templates — không phải Fonts vì Fonts chỉ dùng qua `avares://`):

```xml
<ItemGroup>
  <AvaloniaResource Include="Assets\**" />
  <!-- Sound (SoundServiceImpl/SoundServiceLinux) và Templates (PrinterServiceImpl) cần đường dẫn
       file thật trên đĩa — AvaloniaResource CHỈ nhúng vào assembly, không copy ra output dir. -->
  <Content Include="Assets\Sound\**;Assets\Templates\**">
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </Content>
</ItemGroup>
```

1. Xác định thư mục Assets nào được code đọc bằng physical path (`IPathService.*Root`, `File.ReadAllText`, `Process.Start` với path argument, `new SoundPlayer(path)`...).
2. Thêm `<Content Include="Assets\<ThưMục>\**">` với `CopyToOutputDirectory=PreserveNewest` cho đúng những thư mục đó — KHÔNG cần thêm cho Fonts/Images nếu chúng chỉ load qua `avares://` stream.
3. Build lại, kiểm tra `bin/Debug/<TFM>/Assets/<ThưMục>/` đã có file vật lý.
4. Chạy app thật, xác nhận âm thanh/in phiếu hoạt động (không chỉ dựa vào build pass — bug này build luôn pass, chỉ fail runtime).

## Áp dụng lại (How to reuse)

- Khi thấy `AvaloniaResource Include="Assets\**"` trong `.csproj` mà có code dùng `AppContext.BaseDirectory` + `Path.Combine` để tạo physical path đọc file trong `Assets/` → kiểm tra ngay file đó có được copy ra `bin/` không trước khi kết luận code logic sai.
- Trước khi debug sâu vào logic service (SoundServiceImpl, PrinterServiceImpl...), luôn `Glob`/`find` thư mục output (`bin/<Config>/<TFM>/Assets/...`) để loại trừ nguyên nhân "file không tồn tại vật lý".
- Any `ISoundService`/`IPrinterService`/service nào port từ WinForms sang Avalonia mà dùng physical file path — PHẢI verify có `Content`+`CopyToOutputDirectory`, không chỉ `AvaloniaResource`.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Lỗi này **build luôn pass, 0 Error** — vì compiler không biết gì về việc file .wav/.html có tồn tại đúng chỗ lúc runtime hay không. Chỉ phát hiện khi chạy app thật.
- ⚠️ Exception bị nuốt âm thầm (catch-log-only pattern phổ biến trong service layer để không crash UI) khiến triệu chứng trông giống "logic sai" hơn là "thiếu file" — luôn kiểm tra log trước khi đoán mò code.
- ⚠️ Một file có thể vừa là `AvaloniaResource` vừa là `Content` cùng lúc (2 item type khác nhau) — không xung đột, không cần chọn 1 trong 2.
- ⚠️ `dotnet build` có thể fail với `AVLN9999: process cannot access file` nếu app đang chạy hoặc MSBuild build-server (nodeReuse) đang giữ handle — chạy `dotnet build-server shutdown` trước khi build lại nếu gặp lỗi này mà không chắc app còn chạy hay không.

## Tham chiếu

- Project liên quan: `iPGSv4/IPGS.Kiosk.Avalonia` — [App.axaml.cs](../../../../../e/KZTEK/Code_Git/1.Window/2.PGS/v4/3.KIOSK/2.VERTICAL/2.LocationAndPayment/2.v8/iPGSv4/IPGS.Kiosk.Avalonia/App.axaml.cs), `IPGS.Kiosk.Avalonia.csproj`
- Liên quan: `FontHelper.cs` (dùng đúng cách — `avares://` cho Font, không cần Content copy)
