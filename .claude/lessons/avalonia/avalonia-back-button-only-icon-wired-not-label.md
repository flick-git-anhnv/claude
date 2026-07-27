---
category: avalonia
tags: [winforms-port, click-event, hit-test, back-button, behavior-parity]
severity: medium
created: 2026-07-21
updated: 2026-07-21
project-origin: iPGSv4 (LocateVehicleView)
---

# Port nút "Quay lại" (Label + PictureBox icon) chỉ wire Click cho icon → bấm vào chữ không có tác dụng

## Tình huống gặp phải

> Port `frmLocateVehicle` (WinForms) sang Avalonia `LocateVehicleView.axaml`. Nút "Quay lại" gốc gồm 2 control cạnh nhau: `picGoBack` (PictureBox icon nhỏ) + `btnGoBack` (Label text "Quay lại").

## Triệu chứng / Lỗi

User báo: "nút quay lại bấm không có tác dụng, icon back quá lớn so với nút". Thực tế code-behind chỉ wire:
```csharp
BtnGoBack.Click += (_, _) => vm.GoBackCommand.Execute(null); // chỉ icon HoverImageButton
```
TextBlock hiển thị "Quay lại" (chiếm phần lớn diện tích trực quan của nút) không có handler nào. User tự nhiên bấm vào chữ (target lớn hơn, trực quan hơn) → không phản hồi. Ngoài ra icon bị set `Width="56" Height="56"` thay vì kích thước gốc.

## Nguyên nhân gốc rễ (Root Cause)

Đọc lại `frmLocateVehicle.cs` (`RegisterUIEvent()`):
```csharp
btnGoBack.Click += BtnBack_Click;   // Label
picGoBack.Click += BtnBack_Click;   // PictureBox icon
```
Bản gốc WinForms wire Click cho **CẢ HAI** control độc lập (Label và PictureBox đứng cạnh nhau, không nằm trong 1 container bấm được chung) — vì WinForms Label + PictureBox không tự động gộp thành 1 "nút" logic, dev gốc phải wire tay cả 2. Khi port sang Avalonia, agent chỉ nhìn thấy 1 `HoverImageButton` (đại diện icon) trong XAML và chỉ wire đúng phần tử đó, quên rằng bản gốc coi TOÀN BỘ cụm icon+label là vùng bấm được.

Riêng kích thước: `picGoBack.Size = new Size(19, 29)` (set runtime trong `SetSize()`), nhưng port đặt `Width="56" Height="56"` — không tra `SetSize()`/`SetLocation()` runtime mà chỉ áng chừng.

## Giải pháp

```xml
<StackPanel x:Name="BackButtonPanel" Orientation="Horizontal" Background="Transparent" Cursor="Hand">
  <controls:HoverImageButton x:Name="BtnGoBack" Width="19" Height="29" .../>
  <TextBlock Text="{Binding BackButtonText}" .../>
</StackPanel>
```
```csharp
BackButtonPanel.PointerPressed += (_, _) => vm.GoBackCommand.Execute(null);
```
1. Gộp icon + text vào 1 container (StackPanel/Border), set `Background="Transparent"` (Panel cần Background non-null để vùng trống cũng hit-test được).
2. Wire `PointerPressed` (hoặc `Tapped`) trên CONTAINER thay vì chỉ trên icon — bấm bất kỳ đâu trong cụm đều trigger.
3. Đối chiếu kích thước icon với `SetSize()`/runtime Size trong `.cs` gốc — KHÔNG lấy từ `.Designer.cs`/`.resx` (đó là design-time placeholder, có thể bị override lúc runtime).

## Áp dụng lại (How to reuse)

- Khi port 1 "nút" WinForms mà thực chất là 2+ control độc lập (Label + PictureBox, hoặc 2 control cạnh nhau) → `Grep` toàn bộ `.Click +=` trong file `.cs` gốc liên quan đến các control đó. Nếu ≥2 control cùng trỏ về 1 handler → PHẢI gộp thành 1 vùng bấm chung trong Avalonia, không chỉ wire 1 control đại diện.
- Khi thấy Avalonia code-behind chỉ wire Click cho ĐÚNG 1 control con trong khi bản gốc có Label+Icon đứng cạnh nhau → nghi ngờ ngay, kiểm tra lại `RegisterUIEvent()`/tương đương ở bản gốc.
- Lấy kích thước control luôn ưu tiên method `SetSize()`/`SetFont()`/runtime code trong `.cs`, KHÔNG dùng giá trị `.Designer.cs`/`.resx` (có thể bị ghi đè lúc chạy).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Avalonia `Panel`/`StackPanel` cần `Background` non-null (kể cả `Transparent`) để vùng trống (không có child) tham gia hit-test — nếu để mặc định null, `PointerPressed` sẽ không fire khi bấm vào khoảng trống giữa icon và text.
- ⚠️ Đừng chỉ tăng kích thước icon để "dễ bấm hơn" khi thực ra vùng bấm phải mở rộng ra cả text nhãn đi kèm — sửa sai vị trí (size) không giải quyết đúng root cause (thiếu wiring).

## Tham chiếu

- Project liên quan: iPGSv4 — `IPGS.Kiosk.Avalonia/Views/LocateVehicle/LocateVehicleView.axaml(.cs)`
- Gốc: `IPGS.Kiosk/LotteDesigns/frmLocateVehicle.cs` (`SetSize()`, `SetLocation()`, `RegisterUIEvent()`)
