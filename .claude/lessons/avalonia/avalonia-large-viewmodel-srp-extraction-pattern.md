---
category: avalonia
tags: [solid, srp, mvvm, viewmodel, refactor]
severity: medium
created: 2026-08-06
updated: 2026-08-06
project-origin: App-Access-V2 (iAccess.Tools.ZkPushMonitor)
---

# ViewModel Avalonia phình to thành God Object — tách theo SRP bằng composition, KHÔNG đổi interface DI

## Tình huống gặp phải

`MainWindowViewModel` (Avalonia, `iAccess.Tools.ZkPushMonitor`) gom quá nhiều trách nhiệm trong 1 class
sealed ~700 dòng: điều khiển proxy/capture, lọc danh sách hiển thị, dedupe "chuỗi lệnh khởi tạo",
buffer log UI, quản lý row buffer, export. User yêu cầu sửa để đảm bảo SOLID (trọng tâm SRP).

## Triệu chứng

Không phải lỗi runtime — đây là code smell: field/method liên quan đến 3 mối quan tâm khác nhau
(filter, init-step dedupe, log buffer) nằm chung 1 class, dùng chung private field
(`_initStepIndex`, `MaxLogLines`, `_filterSn`/`_selectedRouteFilter`/`_hideHeartbeat`), khó test độc lập,
khó review vì mỗi PR động vào file này đụng nhiều mối quan tâm không liên quan nhau.

## Nguyên nhân gốc rễ

ViewModel Avalonia (không dùng CommunityToolkit.Mvvm, chỉ có `ViewModelBase`/`SetField` tối giản — xem
`ViewModelBase.cs`) rất dễ phình to vì mọi logic phụ trợ (filter, dedupe, buffer) đều "tiện tay" viết
thẳng vào VM thay vì tách class riêng — không có barrier kiến trúc nào ép tách.

## Giải pháp

Tách từng trách nhiệm thành 1 class nhỏ, sealed, KHÔNG cần interface/DI (project tool nội bộ, không cần
mock để test) — VM chỉ compose (giữ instance riêng) và delegate property/method:

```csharp
private readonly ExchangeRowFilter _filter = new();       // route/SN/heartbeat filter + Matches()
private readonly InitStepTracker _initStepTracker = new(); // dedupe "chuỗi lệnh khởi tạo" + Steps
private readonly ProxyLogBuffer _logBuffer = new();        // buffer N dòng log gần nhất
```

- Property bindable cũ (`InitSteps`, `LogLines`) đổi từ field `{ get; } = new()` sang
  **computed property trỏ vào collection do class con sở hữu**: `public ObservableCollection<...> InitSteps => _initStepTracker.Steps;`
  — Avalonia binding vẫn hoạt động bình thường vì binding theo instance collection, không cần setter.
- Property 2 chiều cũ dùng `SetField(ref _field, value)` (field nằm ngay trong VM) phải viết lại thành
  so sánh giá trị thủ công + `OnPropertyChanged()` vì field giờ nằm trong object con:
  ```csharp
  public string FilterSn
  {
      get => _filter.SnFilter;
      set { if (_filter.SnFilter == value) return; _filter.SnFilter = value; OnPropertyChanged(); ApplyFilter(); }
  }
  ```
- `const string AllRoutesFilter` (dùng ở nhiều nơi, kể cả `RouteFilters.Add(...)`) chuyển "nguồn sự thật"
  sang class filter mới, VM giữ alias `public const string AllRoutesFilter = ExchangeRowFilter.AllRoutesFilter;`
  để KHÔNG breaking bất kỳ chỗ nào đang tham chiếu `MainWindowViewModel.AllRoutesFilter`.

## Áp dụng lại (How to reuse)

- Khi thấy 1 ViewModel Avalonia có > 400-500 dòng và > 1 nhóm field/method rõ ràng không liên quan
  nhau (VD: "lọc" vs "log" vs "tracking/dedupe") → tách ngay thành class `sealed` riêng trong cùng
  namespace `ViewModels`, KHÔNG cần interface nếu project không có nhu cầu test/mocking.
- Trước khi tách: `Grep` toàn bộ field/property cũ trong file XAML liên quan (`ItemsSource="{Binding X}"`)
  để đảm bảo property public trên VM (tên + kiểu) giữ nguyên sau refactor — XAML binding theo tên string,
  compiler KHÔNG báo lỗi nếu binding bị lệch.
- Ưu tiên "computed property trỏ instance con" (`=> _sub.Collection`) thay vì copy dữ liệu qua lại giữa
  VM và class con — giữ đúng 1 nguồn sự thật, tránh đồng bộ 2 chiều thủ công.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Property 2 chiều cũ dùng `SetField(ref field, value)` — khi field chuyển sang property của object
  con, KHÔNG thể dùng `SetField` (cần `ref` tới field thật) — phải viết so sánh + `OnPropertyChanged()` tay.
- ⚠️ Nếu VM có method `Clear()` reset toàn bộ state (danh sách, filter, tracker) — nhớ gọi `Clear()`
  tương ứng trên TỪNG class con (VD: `_initStepTracker.Clear()`), không chỉ xoá riêng collection top-level.
- ⚠️ `const` public cũ (dùng trong nhiều property/logic) khi di chuyển "nguồn sự thật" sang class mới —
  PHẢI giữ lại alias `public const ... = NewClass.OldConstName;` trên VM để không breaking chỗ khác
  đang tham chiếu qua `MainWindowViewModel.TenConst`.

## Tham chiếu

- Project liên quan: `App-Access-V2` — `iAccessDesktopv2.Avalonia/iAccess.Tools.ZkPushMonitor/ViewModels/`
  (`MainWindowViewModel.cs`, `ExchangeRowFilter.cs`, `InitStepTracker.cs`, `ProxyLogBuffer.cs`)
