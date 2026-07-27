# `<Compile Remove>` trong csproj che giấu code chưa migrate — build xanh nhưng tính năng chết im lặng

**Category:** avalonia
**Ngày:** 2026-07-26
**Project:** iPGSv4 CCU (WinForms → Avalonia .NET 8)
**Loại:** Gotcha

---

## Triệu chứng

Migration được báo cáo "hoàn tất, 0 errors, sign-off production". Rà soát lại phát hiện **3 tính năng thật sự đã chết** mà build không hề cảnh báo:

1. Toàn bộ tầng điều khiển camera (Dahua/Hik SDK)
2. REST API server (`Controller/APIController.cs`, 38 KB)
3. Giao thức intercom Kocom (`KOCOM/KocomHelper.cs`, 22 KB)

Cả 3 chỉ bị loại khỏi build bằng `<Compile Remove>`, source vẫn nằm nguyên trong repo nên nhìn qua tưởng còn đủ.

## Nguyên nhân

Khi port sang framework mới, cách nhanh nhất để "làm cho nó build được" là loại file gây lỗi khỏi biên dịch:

```xml
<ItemGroup>
  <Compile Remove="Controller\**" />
  <Compile Remove="KOCOM\**" />
  <Compile Remove="Devices\CameraDevices\DahuaCameraController.cs" />
</ItemGroup>
```

Build xanh ngay. Nhưng:
- File vẫn tồn tại → `git status` sạch, code review không thấy gì mất.
- Không có test → không ai phát hiện tính năng không chạy.
- **Tệ nhất:** code gọi vào tầng đã gỡ bị "vá" thành no-op im lặng:

```csharp
public void GetCameraController()
{
    if (cameraController == null)
    {
        // controller excluded from cross-platform build
        cameraController = null;   // ⚠️ gán null cho null — luôn no-op
    }
}
```

`Start()`, `StartMonitoring()`, `IsRunning()` phía sau đều `if (cameraController != null)` → không chạy gì, **không log, không throw**. Vận hành sẽ thấy "camera không lên" mà không có manh mối nào.

## Cách phát hiện (checklist bắt buộc khi audit migration)

```bash
# 1) Liệt kê MỌI file bị loại khỏi build — đây là danh sách nghi phạm số 1
grep -rn "Compile Remove" --include="*.csproj" .

# 2) Với mỗi mục, phân loại:
#    - UI framework cũ (Forms/, *.Designer.cs, *.resx)  → thật sự chết, xóa được
#    - Logic nghiệp vụ (Controller/, protocol helper)    → CHƯA MIGRATE, phải báo

# 3) Tìm no-op giả migrate: gán null cho chính nó, method rỗng có comment "excluded"
grep -rn "excluded from\|not available in\|= null;" --include="*.cs" src/
```

Đối chiếu thêm: config vẫn được nạp nhưng consumer đã bị gỡ là dấu hiệu chắc chắn.
Ở đây `Program.cs` vẫn `LoadKocomConfig()` → `StaticPool.kocomConfig`, trong khi `KocomHelper.cs` không hề được biên dịch.

## Quy tắc rút ra

1. **`<Compile Remove>` phải kèm comment nêu rõ lý do và trạng thái**, phân biệt hai loại khác hẳn nhau:

```xml
<!-- Chưa migrate sang Avalonia — giữ nguyên source, tạm loại khỏi build:
     Startup.cs + Controller\APIController.cs : REST API (còn phụ thuộc WinForms)
     KOCOM\KocomHelper.cs                     : giao thức TCP Kocom -->
```

2. **Không bao giờ "vá" bằng no-op im lặng.** Nếu buộc phải bỏ tính năng thì gỡ hẳn cả API (xóa method/field), để compiler chỉ ra mọi caller — thay vì để runtime im lặng không làm gì.

3. **"0 errors" không phải bằng chứng migration đủ.** Bằng chứng đủ là: danh sách `<Compile Remove>` chỉ còn file UI framework cũ, và mọi module nghiệp vụ đều nằm trong build.

4. Xóa hẳn source WinForms sau khi đã có bản thay thế — giữ lại chỉ khiến người sau **sửa nhầm vào file không được biên dịch** (đã xảy ra thật: 4 file chết bị sửa branding, công sức mất trắng).

## Liên quan

- [[avalonia-migration-review-checklist]]
- [[avalonia-migration-silent-behavior-drop-loading-flow]]
- [[avalonia-migration-theme-drift-not-caught-by-build-pass]]
- [[avalonia-migration-from-winforms]]
