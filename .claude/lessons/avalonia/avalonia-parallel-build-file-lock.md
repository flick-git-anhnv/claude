# Avalonia — Build song song solution nhiều project gây file lock ngẫu nhiên

**Category:** avalonia
**Ngày:** 2026-07-26
**Loại:** Gotcha
**Project gặp:** iPGSv4 (IPGSUseCam, .NET 8, Avalonia)

---

## Bối cảnh

Solution có nhiều project Avalonia phụ thuộc lẫn nhau: `IPGSUseCam` → `IPGS.Control`, `ApplicationConfig`, `KztekComponentAvalonia`, `Kztek.Cameras.Avalonia`.

## Triệu chứng

`dotnet build` thất bại **ngẫu nhiên**, một trong hai lỗi:

```
MSBUILD : Avalonia error AVLN9999: The process cannot access the file
'...\ApplicationConfig\obj\Debug\net8.0\ApplicationConfig.dll' because it is being used by another process.

CSC : error CS0006: Metadata file
'...\KztekComponentAvalonia\obj\Debug\net8.0\ref\KztekComponentAvalonia.dll' could not be found
```

Không sửa gì, chạy lại có khi xanh. Rất dễ tưởng lỗi do code vừa viết → debug nhầm hướng, mất thời gian.

## Nguyên nhân

MSBuild mặc định build song song. Avalonia XAML compiler (`Avalonia.Build.Tasks`) **mở và ghi đè assembly output sau khi Roslyn đã emit**. Khi hai project cùng chạm output/ref-assembly của một dependency chung tại cùng thời điểm → một tiến trình giữ file, tiến trình kia lỗi.

`CS0006` là hệ quả dây chuyền: project dependency bị abort giữa chừng nên ref assembly chưa kịp sinh.

## Cách xử lý

```powershell
dotnet build-server shutdown                 # chỉ cần khi đã dính lock
dotnet build <project>.csproj -c Debug -m:1  # -m:1 = build tuần tự
dotnet test  <test>.csproj -m:1
```

## Điều KHÔNG cần làm

- Không cần xoá `obj/` hoặc `dotnet clean`.
- Không cần kiểm tra app có đang chạy không (đã xác nhận: không có process nào của app mở khi lỗi xảy ra).
- Không cần đổi cấu hình project.

## Bài học

Với solution Avalonia nhiều project chia sẻ dependency, đặt `-m:1` làm **mặc định** trong mọi script build/test tự động. Chậm hơn vài giây nhưng loại hẳn một lớp lỗi ngẫu nhiên không tái hiện được — vốn tốn nhiều thời gian chẩn đoán hơn nhiều.

Liên quan: [[avalonia-compiled-binding-x-datatype]]
