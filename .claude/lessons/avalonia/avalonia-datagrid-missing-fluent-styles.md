---
name: avalonia-datagrid-missing-fluent-styles
description: DataGrid render trắng hoàn toàn trong Avalonia 11 khi thiếu StyleInclude DataGrid Fluent theme
metadata:
  type: feedback
---

# Avalonia DataGrid render trắng — thiếu StyleInclude Fluent theme

## Tình huống gặp phải

Dự án iPGSv4 (branch `zcu-avalonia`): cả hai DataGrid trong app (event grid ở MainWindow và camera list grid ở SettingsWindow) không hiển thị gì — hoàn toàn trắng, không có header, không có row.

## Triệu chứng

- `DataGrid` render ra một vùng trắng
- Không có column header
- Không có row dù đã set `ItemsSource`
- Không có exception hoặc lỗi build

## Nguyên nhân gốc rễ

Trong Avalonia 11, `DataGrid` là control riêng biệt từ package `Avalonia.Controls.DataGrid`. Package này có **theme riêng phải được load tường minh** — `<FluentTheme />` **KHÔNG** tự động include DataGrid styles.

Nếu không load theme này, `DataGrid` không có template visual → render trắng.

## Giải pháp

Thêm vào `App.axaml` (TRƯỚC các style override như `KzDataGrid.axaml`):

```xml
<Application.Styles>
  <FluentTheme />

  <!-- DataGrid base template — phải đặt TRƯỚC KzDataGrid overrides -->
  <StyleInclude Source="avares://Avalonia.Controls.DataGrid/Themes/Fluent.xaml" />

  <!-- Các style override của KZTEK -->
  <StyleInclude Source="avares://KztekComponentAvalonia/Themes/KzDataGrid.axaml" />
</Application.Styles>
```

## Áp dụng lại

- Bất kỳ khi nào thêm `DataGrid` vào project Avalonia → kiểm tra `App.axaml` có dòng này chưa
- Dòng này phải đặt TRƯỚC style override để override hoạt động đúng
- Cần cả NuGet package `Avalonia.Controls.DataGrid` VÀ StyleInclude — thiếu một trong hai đều không render được

## Chú ý / Cạm bẫy

- ⚠️ `DataGrid` không báo lỗi khi thiếu theme — chỉ render trắng
- ⚠️ `<FluentTheme />` không include DataGrid styles dù bạn đã thêm NuGet `Avalonia.Controls.DataGrid`
- ⚠️ Custom style override (`Classes="kz-grid"`) cũng không hoạt động nếu base template chưa load

## Tham chiếu

- Project: iPGSv4, branch `zcu-avalonia`
- Verified: 2026-06-25, Avalonia 11.2.7
- Affected files: `IPGSUseCam/App.axaml`
