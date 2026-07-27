---
category: avalonia
tags: [xmlns, clr-namespace, using, AVLN2000, StringConverters, Converters, build-error]
severity: high
created: 2026-06-25
updated: 2026-06-25
project-origin: iPGSv4 - KztekComponentAvalonia
---

# Avalonia AXAML: dùng `using:Namespace` thay `clr-namespace:` cho Avalonia built-in types

## Tình huống gặp phải

Đang viết ControlTheme trong AXAML, cần dùng `StringConverters.IsNotNullOrEmpty` từ `Avalonia.Data.Converters`. Khai báo namespace theo cú pháp WPF/XAML thông thường.

## Triệu chứng / Lỗi

```
Error AVLN2000: Unable to resolve type 'StringConverters' from namespace 'Avalonia.Data.Converters'
  clr-namespace:Avalonia.Data.Converters;assembly=Avalonia
```

Build thất bại. Visual Studio Intellisense cũng không gợi ý được type.

## Nguyên nhân gốc rễ (Root Cause)

Avalonia's compiled XAML processor (`XamlX`) không resolve `clr-namespace:...;assembly=Avalonia` cho các type thuộc Avalonia's own assemblies — đặc biệt khi compiled XAML chạy qua `XamlX` compiler (khác WPF dùng `BamlWriter`). Cú pháp `clr-namespace:` hoạt động cho assemblies bên ngoài (user code, NuGet packages), nhưng Avalonia built-in types cần cú pháp `using:` riêng của Avalonia.

## Giải pháp

Dùng cú pháp `using:` thay vì `clr-namespace:` cho Avalonia built-in namespaces:

```xml
<!-- ❌ SAI — gây AVLN2000 -->
xmlns:conv="clr-namespace:Avalonia.Data.Converters;assembly=Avalonia"

<!-- ✅ ĐÚNG -->
xmlns:conv="using:Avalonia.Data.Converters"
```

Ví dụ đầy đủ trong ControlTheme:

```xml
<ResourceDictionary xmlns="https://github.com/avaloniaui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                    xmlns:kz="clr-namespace:KztekComponentAvalonia.Controls"
                    xmlns:conv="using:Avalonia.Data.Converters">

  <ControlTheme x:Key="{x:Type kz:KzSidebarItem}" TargetType="kz:KzSidebarItem">
    ...
    <TextBlock IsVisible="{TemplateBinding ItemIcon,
               Converter={x:Static conv:StringConverters.IsNotNullOrEmpty}}" />
  </ControlTheme>
</ResourceDictionary>
```

## Áp dụng lại (How to reuse)

- Khi dùng bất kỳ type nào từ `Avalonia.*` namespace trong AXAML → dùng `using:Avalonia.Xyz` (KHÔNG dùng `clr-namespace:`)
- Khi dùng type từ user code / NuGet package → vẫn dùng `clr-namespace:MyNamespace;assembly=MyAssembly`
- Khi gặp `AVLN2000 unable to resolve type` trên Avalonia type → kiểm tra xmlns ngay

**Các Avalonia namespace hay dùng:**
```xml
xmlns:conv="using:Avalonia.Data.Converters"
xmlns:media="using:Avalonia.Media"
xmlns:interactivity="using:Avalonia.Xaml.Interactivity"
xmlns:ia="using:Avalonia.Xaml.Interactions.Core"
```

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Lỗi `AVLN2000` trông giống "type không tồn tại" nhưng thực ra là sai cú pháp namespace — type hoàn toàn tồn tại, chỉ cần đổi từ `clr-namespace:` sang `using:`
- ⚠️ `clr-namespace:` vẫn hoạt động cho local user code trong cùng assembly (không cần `;assembly=` khi cùng project) — chỉ Avalonia built-in mới cần `using:`
- ⚠️ Intellisense trong VS Code / Rider đôi khi gợi ý sai cú pháp `clr-namespace:` cho Avalonia types — không tin tưởng autocomplete, kiểm tra bằng build

## Tham chiếu

- Project liên quan: iPGSv4 / KztekComponentAvalonia / `Themes/KzSidebarItem.axaml`
- Avalonia version: 11.2.7
- Verified: 2026-06-25
