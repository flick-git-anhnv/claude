---
category: csharp-winforms
tags: [flowlayoutpanel, clientsize, modal-dialog, beginInvoke, winforms-layout]
severity: high
created: 2026-07-24
updated: 2026-07-24
project-origin: LinuxDeployTool (Kztek.LinuxDeployTool)
---

# FlowLayoutPanel.ClientSize.Width = 0 khi AddItemControl gọi từ chuỗi đóng modal dialog

## Tình huống gặp phải

Đang implement WinForms app có FlowLayoutPanel (`TopDown`, `AutoScroll`, `WrapContents=false`). Khi user bấm nút "Thêm solution", `FolderBrowserDialog.ShowDialog()` mở modal. Sau khi user chọn và dialog đóng, code gọi `AddItemControl(model)` để thêm `SolutionItemControl` vào `flowPanel.Controls`.

Bên trong `AddItemControl`, cần đặt `Width` cho UserControl con theo chiều rộng hiện tại của FlowLayoutPanel:

```csharp
ctrl.Width = flowPanel.ClientSize.Width - 10;  // ← SẼ TRẢ VỀ 0
```

## Triệu chứng / Lỗi

UserControl được thêm vào danh sách (có trong `_itemControls`, có trong `flowPanel.Controls`) nhưng **không hiển thị gì** trên màn hình. Không exception. Status bar phản chiếu đúng số lượng item.

Debug: `ctrl.Width == 0` sau khi set. `flowPanel.ClientSize.Width` trả về 0 tại thời điểm gọi.

## Nguyên nhân gốc rễ (Root Cause)

Khi `FolderBrowserDialog.ShowDialog()` đóng và trả điều khiển về cho `btnAddSolution_Click`, **Windows vẫn đang trong quá trình re-layout cửa sổ chính** (unblock WM_PAINT, recalculate layout). Trong khoảng thời gian cực ngắn này, `flowPanel.ClientSize` chưa được cập nhật — nó vẫn là giá trị cũ hoặc trả về `(0, 0)`.

Cụ thể: `ClientSize` phụ thuộc vào `Bounds` đã được tính toán qua Measure/Arrange của WinForms layout engine. Khi gọi đồng bộ ngay sau modal đóng, layout chưa kịp chạy xong.

## Giải pháp

Dùng `BeginInvoke` để trì hoãn việc set Width sang sau khi WinForms hoàn thành layout:

```csharp
private void AddItemControl(SolutionItemModel model)
{
    var ctrl = new SolutionItemControl(model);
    ctrl.RemoveRequested += OnRemoveRequested;
    _itemControls.Add(ctrl);
    flowPanel.Controls.Add(ctrl);

    // PHẢI dùng BeginInvoke — ClientSize.Width chưa sẵn sàng ngay lúc này
    BeginInvoke(UpdateControlWidths);
}

private void UpdateControlWidths()
{
    // Math.Max để đảm bảo không bao giờ set width = 0
    int targetWidth = Math.Max(400, flowPanel.ClientSize.Width - 10);
    foreach (var c in _itemControls)
        c.Width = targetWidth;
}
```

Thêm SizeChanged handler khi Form load để đồng bộ width khi cửa sổ resize:

```csharp
protected override void OnLoad(EventArgs e)
{
    base.OnLoad(e);
    flowPanel.SizeChanged += (_, _) => UpdateControlWidths();
    // ... load items từ config
}
```

## Áp dụng lại (How to reuse)

- Bất cứ khi nào cần đọc `ClientSize`, `Bounds`, `Width`, `Height` của Panel/Form **ngay sau** `ShowDialog()`, `OpenFileDialog`, `FolderBrowserDialog` đóng → dùng `BeginInvoke` thay vì đọc đồng bộ.
- Luôn có `Math.Max(MIN_VALUE, ...)` khi dùng `ClientSize` để làm kích thước — đề phòng trường hợp layout chưa hoàn tất.
- Đăng ký `SizeChanged` handler sau khi items được load để đồng bộ width khi user resize cửa sổ.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Vấn đề này **không xảy ra** khi item được add trong `OnLoad` (khi load từ config) vì lúc đó FlowLayoutPanel đã được layout xong. Chỉ xảy ra khi gọi từ chuỗi đóng modal dialog.
- ⚠️ Cùng dự án có lesson khác liên quan: `winforms-usercontrol-anchor-right-invisible-in-flowlayoutpanel.md` — đó là về `Anchor` Right tự thân trên UserControl (gốc rễ KHÁC — Anchor tạo phụ thuộc lên Parent.Width khi Parent chưa có). Hai vấn đề có triệu chứng giống nhau (item không hiển thị, Width=0) nhưng nguyên nhân và fix khác nhau.
- ⚠️ `flowPanel.ClientSize.Width - 10` có thể âm nếu FlowLayoutPanel chưa layout — `Math.Max` là bắt buộc.

## Tham chiếu

- Project: `E:\KZTEK\Code_Git\7.LinuxDeployTool` — `MainForm.cs`, `SolutionItemControl.cs`
- Liên quan: `winforms-usercontrol-anchor-right-invisible-in-flowlayoutpanel.md` (vấn đề Anchor khác nhưng triệu chứng tương tự)
