---
category: avalonia
tags: [binding, INotifyPropertyChanged, nested-path, mvvm, textbox]
severity: high
created: 2026-07-17
updated: 2026-07-17
project-origin: parking-v8-app-avalonia (ParkingV8.Configuration)
---

# Binding đường dẫn lồng ("Vm.Model.Field") không refresh khi raise PropertyChanged trên object CÙNG reference

## Tình huống gặp phải

Đang bổ sung chức năng "Lấy mã thiết bị" thật cho tab LPR trong `ParkingV8.Configuration` (Avalonia).
Model cấu hình (`LprConfig`) là POCO thường, KHÔNG implement `INotifyPropertyChanged` — pattern
phổ biến trong project vì các model config này dùng chung với serialize JSON/Newtonsoft.

Code-behind set trực tiếp `viewModel.Lpr.AIDeviceCode = deviceCode;` rồi gọi 1 helper
`RefreshLprBindings()` chỉ làm `RaisePropertyChanged(nameof(Lpr))` (raise trên property gốc
"Lpr" của ViewModel, không phải trên field con).

## Triệu chứng / Lỗi

- Bấm nút "Lấy mã thiết bị": không có exception, service trả về mã hợp lệ, notify "thành công"
  hiển thị đúng.
- NHƯNG: TextBox bind `Text="{Binding Lpr.AIDeviceCode}"` KHÔNG cập nhật giá trị mới trên UI.
- Đọc lại giá trị qua code (VD nút "Sao chép") vẫn lấy đúng giá trị mới — chỉ riêng UI không vẽ lại.

## Nguyên nhân gốc rễ (Root Cause)

Binding path 2 cấp `"Lpr.AIDeviceCode"`:
- Cấp 1 (`Lpr`): Avalonia binding engine subscribe `PropertyChanged` trên ViewModel cho property "Lpr".
- Cấp 2 (`AIDeviceCode`): vì `LprConfig` không có `INotifyPropertyChanged`, Avalonia không có cách
  nào tự biết field con đổi giá trị.

`RefreshLprBindings()` cố "ép" binding refresh bằng cách raise `PropertyChanged("Lpr")` — nhưng
giá trị trả về của `Lpr` (property getter) vẫn là **CÙNG 1 object reference** như trước (không đổi
instance). Avalonia's binding/`ExpressionObserver` khi nhận PropertyChanged cho node gốc sẽ lấy giá
trị mới, nhưng khi so sánh thấy reference không đổi, nó không coi đây là "thay đổi thật" nên KHÔNG
lan truyền re-evaluate xuống node con `AIDeviceCode`. Kết quả: đường dẫn lồng đứng yên, dù giá trị
thực tế bên trong đã đổi.

Đây LÀ pattern khác với trường hợp thường gặp (gán hẳn 1 object `LprConfig` MỚI cho property `Lpr`
— lúc đó reference đổi thật, binding mới refresh đúng).

## Giải pháp

Không dựa vào "raise PropertyChanged trên object cha, hy vọng lan xuống con" khi object cha là
cùng reference. Thay vào đó: expose thẳng 1 **proxy property** trên ViewModel cho field cần
update từ code-behind, bind UI vào property này (KHÔNG bind vào path lồng nữa):

```csharp
public string AIDeviceCode
{
    get => Lpr.AIDeviceCode;
    set
    {
        if (Lpr.AIDeviceCode == value) return;
        Lpr.AIDeviceCode = value;
        RaisePropertyChanged(); // raise đúng tên property này, không phải "Lpr"
    }
}
```

```xml
<!-- Trước: Text="{Binding Lpr.AIDeviceCode}"  -->
<TextBox Text="{Binding AIDeviceCode}" />
```

```csharp
// Code-behind: set qua proxy, không set thẳng model rồi "refresh" object cha
viewModel.AIDeviceCode = deviceCode;
```

1. Xác định field nào trong model non-INPC sẽ bị code-behind mutate trực tiếp (ngoài luồng binding
   2 chiều thông thường của control input).
2. Thêm 1 proxy property tương ứng trên ViewModel (get/set pass-through + RaisePropertyChanged đúng tên).
3. Đổi XAML bind vào proxy, đổi code-behind set qua proxy.
4. Xóa mọi helper kiểu "RaisePropertyChanged(nameof(ParentModelProperty))" nếu không còn field nào cần — đây là dead code mang sẵn bug pattern, dễ bị copy lại ở chỗ khác.

## Áp dụng lại (How to reuse)

- Khi thấy code set giá trị qua `viewModel.SomeNonINPCModel.SomeField = x;` rồi gọi 1 hàm
  "Refresh...Bindings()" chỉ raise PropertyChanged trên property CHA (không phải field con) →
  nghi ngờ ngay đây là bug pattern này, kiểm tra UI có thật sự cập nhật không.
- Trước khi viết binding `"{Binding A.B}"` với `A` là model không INPC và `B` sẽ bị code-behind
  mutate trực tiếp (không qua TwoWay input control) → mặc định dùng proxy property ngay từ đầu,
  đừng đợi phát hiện bug rồi mới sửa.
- Field chỉ hiển thị 1 lần lúc load (không bao giờ bị code-behind set lại sau khi UI đã hiển thị)
  thì binding lồng vẫn OK — pattern này chỉ vỡ khi có mutation SAU khi UI đã render.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Bug này KHÔNG xuất hiện lỗi/exception nào — chỉ là UI "im lặng" không cập nhật, dễ bị nhầm là
  do service trả sai giá trị (trong khi service đúng, chỉ là UI không vẽ lại).
- ⚠️ Nếu đổi hẳn property cha sang instance MỚI (`viewModel.Lpr = new LprConfig {...}`) thì raise
  PropertyChanged("Lpr") lại hoạt động đúng bình thường — bug chỉ xảy ra khi mutate field bên trong
  CÙNG instance.
- ⚠️ Áp dụng tương tự cho MỌI field khác trong các model config non-INPC (`ServerConfig`,
  `OEMConfig`, `PaymentKioskConfig`...) nếu sau này có code-behind set trực tiếp thay vì qua binding
  TwoWay control chuẩn.

## Tham chiếu

- Project liên quan: `parking-v8-app-avalonia` — `src/ParkingV8.Configuration/ViewModels/ConfigurationWindowViewModel.cs`,
  `src/ParkingV8.Configuration/Views/Tabs/LprTabView.axaml(.cs)`
- Plan: `.claude/plans/PLAN-configuration-gap-2026-07-17/`
