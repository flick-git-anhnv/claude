# Ghi config lần đầu crash `DirectoryNotFoundException` vì thư mục "config" chưa tồn tại

**Category:** dotnet-general
**Ngày ghi:** 2026-07-28
**Project gặp:** iPGSv4 (`GetAppConfig()` trong `IPGSv4/Program.cs`)
**Phân loại:** Lỗi

---

## 1. Bối cảnh

Khởi động app lần đầu trên máy mới (hoặc build output mới, `bin/x64/Debug/net8.0/` chưa từng chạy) crash ngay ở `GetAppConfig()`:

```
System.IO.DirectoryNotFoundException: Could not find a part of the path
'E:\...\bin\x64\Debug\net8.0\config\options.txt'
```

```csharp
private static void GetAppConfig()
{
    string path = SettingPathManagement.GetOptionPath;   // "<base>/config/options.txt"
    if (File.Exists(path)) { ... }
    else
    {
        File.WriteAllText(path, JsonConvert.SerializeObject(StaticPool.optionalConfig)); // ← crash
    }
}
```

## 2. Nguyên nhân

`File.WriteAllText` **không tự tạo thư mục cha** — khác iOS/Node.js quen thuộc. Thư mục `config/` bình thường tồn tại vì được commit/copy kèm theo lần deploy trước, nên lỗi này **không lộ ra trong môi trường dev đã chạy quen** — chỉ crash trên máy mới/build output mới/sau khi dọn `bin/obj`. Không phải riêng `options.txt`: mọi field khác trong `SettingPathManagement` (`GetCashPath`, `GetKocomPath`, `GetLprPath`, `GetShortcutPath`...) đều dùng chung `SaveConfigFolder/config/*.txt` và có cùng lỗ hổng ở bất kỳ chỗ nào gọi `File.WriteAllText` lần đầu (`ApplicationConfig/ViewModels/MainViewModel.cs`, `IPGSv4/ViewModels/LoginViewModel.cs`, `ShortcutSettingViewModel.cs`, `AppSettingsJson.Save()`).

## 3. Cách xử lý đúng (đã áp dụng)

Sửa tại gốc — 1 chỗ duy nhất (`IPGS.Object/SettingPathManagement.cs`) thay vì vá từng call site `File.WriteAllText`: đổi `SaveConfigFolder` từ field public sang property có side-effect, tự `Directory.CreateDirectory(Path.Combine(value, "config"))` ngay khi được gán. Cả `IPGSv4/Program.cs` và `ApplicationConfig/Program.cs` đều chỉ gán `SettingPathManagement.SaveConfigFolder = AppContext.BaseDirectory` 1 lần lúc khởi động trước khi gọi bất kỳ hàm đọc/ghi config nào → sửa đúng 1 điểm che phủ toàn bộ các file `config/*.txt` phía sau.

```csharp
private static string saveConfigFolder = string.Empty;
public static string SaveConfigFolder
{
    get => saveConfigFolder;
    set
    {
        saveConfigFolder = value;
        if (!string.IsNullOrEmpty(saveConfigFolder))
            Directory.CreateDirectory(Path.Combine(saveConfigFolder, "config"));
    }
}
```

## 4. Bài học tổng quát

> `File.WriteAllText`/`StreamWriter` không tự tạo thư mục cha trên .NET (khác một số runtime khác). Khi nhiều nơi trong code cùng ghi vào 1 thư mục con cấu hình (`config/`, `logs/`...) dẫn xuất từ 1 base path gán ở entry point, ưu tiên đảm bảo thư mục tồn tại **ngay tại điểm gán base path** (setter/property), không vá từng `File.WriteAllText` riêng lẻ — tránh bỏ sót call site khác dùng chung base path.

## 5. Mẹo chẩn đoán

Lỗi chỉ lộ ra khi thư mục con chưa từng được tạo — test trên máy dev quen thuộc (đã chạy app nhiều lần, thư mục cũ còn sót) sẽ KHÔNG bắt được bug này. Muốn verify: xoá thử thư mục `bin/<config>/net8.0/config` rồi chạy lại app, hoặc build vào output dir hoàn toàn mới.

## Liên quan

- Không có lesson liên quan trực tiếp trong `dotnet-general/` — đây là gotcha `File.WriteAllText` cơ bản nhưng dễ bỏ sót khi base path được set 1 lần rồi dùng lại ở nhiều `Path.Combine` khác nhau.
