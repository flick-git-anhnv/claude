# `dotnet build <sln> -r <RID>` bị chặn (NETSDK1134) + `dotnet new sln` mặc định ra `.slnx`

**Ngày:** 2026-07-26
**Category:** dotnet-general
**Loại:** Gotcha
**Bối cảnh:** iPGSv4 — tạo solution file đầu tiên cho `IPGS.Kiosk.Avalonia` (bước 2.1 plan cải tiến), project vốn chỉ build được bằng `dotnet build <csproj>`.

---

## Triệu chứng

**Gotcha 1 —** Sau khi tạo `.sln` và thêm project, chạy đúng lệnh vẫn dùng hằng ngày ở cấp project:

```
dotnet build IPGS.Kiosk.Avalonia.sln -c Release -r win-x64
```

báo lỗi, KHÔNG phải lỗi cấu hình project:

```
Microsoft.NET.Sdk.Solution.targets(27,5): error NETSDK1134:
Building a solution with a specific RuntimeIdentifier is not supported.
If you would like to publish for a single RID, specify the RID at the individual project level instead.
```

**Gotcha 2 —** `dotnet new sln -n Ten -o .` chạy báo *"The template Solution File was created successfully"* nhưng lệnh kế tiếp lại lỗi:

```
dotnet sln Ten.sln add ...
→ Could not find solution or directory `Ten.sln`.
```

---

## Nguyên nhân

**Gotcha 1:** RuntimeIdentifier là thuộc tính **cấp project**, không phải cấp solution. Một solution có thể chứa nhiều project với `TargetFramework`/`RuntimeIdentifiers` khác nhau (VD: app `net8.0` có RID + test project `net8.0` KHÔNG có RID) — SDK không có cách áp 1 RID cho tất cả một cách đúng đắn, nên chặn thẳng thay vì đoán. Đây là hành vi CÓ CHỦ ĐÍCH của SDK, không phải bug.

**Gotcha 2:** Từ .NET SDK 10, `dotnet new sln` mặc định sinh định dạng XML mới **`.slnx`**, không phải `.sln` cổ điển. Thư mục sau khi chạy có `Ten.slnx` chứ không có `Ten.sln` → mọi lệnh gõ tay `Ten.sln` đều "not found".

---

## Cách xử lý

**Gotcha 1 —** Tách rõ 2 mức:

| Việc | Lệnh |
|---|---|
| Build/kiểm tra toàn solution | `dotnet build App.sln -c Release` (KHÔNG `-r`) |
| Build/publish theo RID | `dotnet build App/App.csproj -c Release -r win-x64` |

Ghi quy tắc này vào CODE-GRAPH / script CI ngay khi tạo solution — nếu không, người viết pipeline sau sẽ mất thời gian tưởng project cấu hình sai.

**Gotcha 2 —** Ép định dạng cổ điển nếu cần tương thích IDE/tooling cũ:

```powershell
dotnet new sln -n IPGS.Kiosk.Avalonia -o . --format sln
```

Hoặc chấp nhận `.slnx` và luôn gọi đúng đuôi file.

---

## Điều bất ngờ đáng ghi thêm

`dotnet sln add A.csproj` **tự động kéo theo toàn bộ project được A tham chiếu** (kể cả project nằm ở repo khác qua ProjectReference tương đối). Ở iPGSv4, thêm 1 project sinh ra solution 10 project. Không sai — nhưng nếu bạn kỳ vọng solution chỉ có đúng 1 project thì kết quả sẽ gây bất ngờ; kiểm tra lại bằng `dotnet sln list` sau khi add.

---

## Checklist khi tạo solution mới cho project đã có

- [ ] Dùng `--format sln` nếu muốn `.sln` cổ điển (SDK 10+ mặc định `.slnx`)
- [ ] `dotnet sln list` để xem thực tế đã kéo theo bao nhiêu project
- [ ] Build kiểm chứng ở CẢ 2 mức: `sln` (không RID) và `csproj` (có RID)
- [ ] Ghi rõ trong CODE-GRAPH/README: "build theo RID phải ở cấp project"

---

## Liên quan

- `dotnet-general/csproj-absolute-projectref-fixed-relative-wsl-build.md`
- `dotnet-general/projectreference-swap-drops-transitive-deps-silently.md`
