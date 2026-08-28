---
category: csharp-winforms
tags: [nullreferenceexception, designer-cs, usercontrol, initializecomponent]
severity: high
created: 2026-08-24
updated: 2026-08-24
project-origin: DoorAlarmv3 (v3)
---

# UserControl con khai báo trong Designer.cs nhưng không được khởi tạo/Add vào Controls → NullReferenceException

## Tình huống gặp phải

> Project WinForms DoorAlarmv3 (v3). Màn "Cài đặt hệ thống" > Bản đồ (`MapProperty`
> UserControl) dùng `mapControl` (kiểu `MapControl`, 1 canvas designer tuỳ biến) để
> hiển thị ảnh nền + cho phép kéo-thả thiết bị vào bản đồ. User bấm "Mở ảnh nền" để
> thêm map mới thì báo lỗi ("Lỗi ko thêm được bản đồ").

## Triệu chứng / Lỗi

```
NullReferenceException khi bấm "Mở ảnh nền" (BtnOpenFile_Click):
  mapControl.BackgroundPicture = ...   // mapControl == null
```

Vùng canvas bên phải màn hình (nơi lẽ ra hiển thị `mapControl`) hoàn toàn trống
(màu trắng) — dấu hiệu trực quan cho biết control chưa từng được add vào form.

## Nguyên nhân gốc rễ (Root Cause)

`MapProperty.Designer.cs` khai báo field `private MapControl mapControl;` nhưng
**`InitializeComponent()` không hề new nó lên và không `Controls.Add(mapControl)`**.
Trong khi đó `FrmMain.cs` (màn theo dõi/giám sát bản đồ, dùng MapControl ở chế độ
RunMode) lại khởi tạo `mapControl` **bằng code** trong `InitUI()`:

```csharp
this.mapControl = new MapControl(false) { RunMode = true, AllowDrop = false };
panelDashboard.Panel1.Controls.Add(mapControl);
mapControl.Dock = DockStyle.Fill;
```

→ Khi copy pattern y hệt cho màn cấu hình (`MapProperty`, chế độ edit/design),
bước "tạo + add vào Controls" đã bị bỏ sót — chỉ còn field declaration trong
Designer.cs (rất có thể do add control bằng Toolbox trong VS rồi lại xoá/hoặc
sinh code thủ công không đầy đủ). Các đoạn code dùng `mapControl` trong
`MapProperty.cs` (`MapProperty_Load`, `TxtMapName_TextChanged`,
`BtnOpenFile_Click`, `AddNewMapInfo`, `UpdateMapInfo`) đều giả định nó tồn tại
sẵn (một số chỗ dùng `?.`/`if (mapControl != null)` để né tránh — không fix gốc,
chỉ che triệu chứng và khiến canvas không bao giờ hiển thị).

## Giải pháp

Thêm khởi tạo + add control ngay trong `InitializeComponent()` của Designer.cs,
đúng như 1 control con bình thường (giống cách VS Designer thường sinh), thay vì
lazy-init trong code-behind:

```csharp
// trong InitializeComponent(), trước SuspendLayout() hoặc cùng khối khai báo field khác:
mapControl = new MapControl();
...
// trong khối gán property + Controls.Add:
mapControl.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
mapControl.Location = new Point(440, 64);
mapControl.Size = new Size(643, 456);
mapControl.Name = "mapControl";
mapControl.TabIndex = 17;
...
Controls.Add(mapControl);
```

Sau đó dọn sạch các chỗ né null (`mapControl?.`, `if (mapControl != null)`)
trong code-behind vì control giờ luôn tồn tại từ constructor.

1. Kiểm tra `Designer.cs` xem field UserControl con có được `new` lên trong
   `InitializeComponent()` không.
2. Nếu thiếu → thêm khởi tạo + set Location/Size/Anchor + `Controls.Add(...)`.
3. Xoá guard `?.`/`!= null` dư thừa trong code-behind (chúng che triệu chứng
   thay vì sửa gốc, và khiến bug im lặng thay vì lộ ra sớm lúc build/test).
4. Build lại để xác nhận.

## Áp dụng lại (How to reuse)

- Khi 1 UserControl con "vẽ ra không thấy gì" (canvas/panel trắng trơn) VÀ code
  dùng nó ném NullReferenceException ở lần thao tác đầu tiên → mở ngay
  `*.Designer.cs`, tìm dòng `<ten_field> = new <Type>(...)` trong
  `InitializeComponent()`. Không thấy dòng đó = control chưa từng được tạo.
- Khi thấy code-behind có nhiều chỗ `control?.Xxx` hoặc
  `if (control != null) { ... }` cho MỘT control con cố định (không phải control
  được tạo động theo điều kiện) → nghi ngờ ngay: đây có phải patch né triệu
  chứng cho case "control chưa init" không, thay vì null hợp lệ theo thiết kế?
- So sánh với chỗ khác trong cùng codebase dùng đúng class đó
  (VD: `FrmMain.InitUI()` dùng `MapControl`) để copy đúng cách khởi tạo.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Lazy-init 1 chỗ duy nhất (VD: chỉ trong `BtnOpenFile_Click`) KHÔNG đủ — nếu
  control cần hiển thị ngay từ `Load` (VD: load ảnh nền map đã lưu khi sửa map
  cũ), code ở `MapProperty_Load` vẫn sẽ NullReferenceException vì chạy trước khi
  người dùng bấm nút kích hoạt lazy-init.
- ⚠️ Sau khi thêm control vào `Controls.Add()`, PHẢI set `Anchor`/`Dock` phù hợp
  với cách form cha tự resize (ở đây `MapProperty_SizeChanged` tự set
  `Width`/`Height` theo Parent) — nếu không control con sẽ không co giãn theo.

## Tham chiếu

- File sửa: `DoorAlarmv3/UserControls/MapProperty.Designer.cs`,
  `DoorAlarmv3/UserControls/MapProperty.cs`
- Pattern tham chiếu (khởi tạo đúng bằng code): `DoorAlarmv3/FrmMain.cs` → `InitUI()`
- Project liên quan: DoorAlarmv3 v3 (WinForms .NET 8)
