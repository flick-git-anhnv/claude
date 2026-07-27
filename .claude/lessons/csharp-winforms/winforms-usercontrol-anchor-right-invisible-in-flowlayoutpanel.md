---
category: csharp-winforms
tags: [winforms, flowlayoutpanel, anchor, usercontrol, layout, invisible-control]
severity: high
created: 2026-07-24
updated: 2026-07-24
project-origin: LinuxDeployTool
---

# UserControl set `Anchor` (đặc biệt `Right`) trên chính nó → co về gần như 0 kích thước khi add vào FlowLayoutPanel

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

WinForms .NET 8, app `Kztek.LinuxDeployTool`. `SolutionItemControl` (UserControl) được tạo động lúc runtime và add vào `FlowLayoutPanel` (`flowPanel.Controls.Add(ctrl)`) mỗi khi user bấm "Thêm solution". Designer của `SolutionItemControl` set `Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right` cho CHÍNH UserControl đó (không phải control con bên trong nó), với ý định ban đầu (nhầm) là để nó "co giãn theo chiều ngang" khi form resize.

## Triệu chứng / Lỗi

User báo: "tôi đã chọn nhưng sau đó không thấy gì" — bấm "Thêm solution", chọn folder qua `FolderBrowserDialog` xong (dialog hoạt động bình thường, `DialogResult.OK`), model được tạo, `AddItemControl()` chạy, `flowPanel.Controls.Add(ctrl)` được gọi — nhưng KHÔNG có gì hiển thị trong danh sách. Không có exception, không có crash — code logic chạy đúng, chỉ là control invisible/co về kích thước gần 0.

## Nguyên nhân gốc rễ (Root Cause)

WinForms `Anchor` hoạt động dựa trên "khoảng cách cố định tới các cạnh được anchor của PARENT hiện tại", được ghi nhận (cached) tại thời điểm Anchor được set / control được parent hóa. Khi `InitializeComponent()` chạy, `Parent` của `SolutionItemControl` còn là `null` (chưa add vào `FlowLayoutPanel`). Việc set `Anchor` bao gồm `Right` trên CHÍNH UserControl (không phải control con) khiến WinForms tính khoảng-cách-tới-cạnh-phải dựa trên bounds lúc đó (Parent=null). Khi `MainForm.AddItemControl()` set `ctrl.Width = flowPanel.ClientSize.Width - 10` NGAY SAU khi khởi tạo (trước khi add vào flowPanel thật), rồi mới `flowPanel.Controls.Add(ctrl)`, WinForms re-anchor lại theo parent MỚI (flowPanel) dựa trên khoảng cách đã cache sai lệch từ bước trước → kết quả Width/Height thực tế bị tính sai, co về gần như 0 — control tồn tại trong `Controls` collection (logic đúng, item có trong list) nhưng không render gì nhìn thấy được.

`FlowLayoutPanel` tự quản lý VỊ TRÍ (Location) của các control con theo flow, nhưng KHÔNG can thiệp vào việc tính KÍCH THƯỚC dựa trên Anchor của chính control con đó — hai cơ chế này độc lập và có thể xung đột.

## Giải pháp

Bỏ `Right` (và nói chung là KHÔNG set `Anchor` gì đặc biệt) trên chính UserControl sẽ được add vào `FlowLayoutPanel` — chỉ giữ `Top | Left` (giá trị mặc định), để `Size` cố định (set 1 lần, hoặc override `Width` sau khi add vào parent thật, không phải trước).

```csharp
// SAI — set Anchor bao gồm Right trên chính UserControl sẽ add vào FlowLayoutPanel
Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
Size = new Size(680, 138);

// ĐÚNG
Anchor = AnchorStyles.Top | AnchorStyles.Left;
Size = new Size(680, 138);
```

Anchor trên các CONTROL CON bên trong UserControl (VD `txtSolutionPath.Anchor = Top|Left|Right` để textbox giãn theo chiều ngang của UserControl cha) vẫn HOÀN TOÀN ĐÚNG và nên giữ — vấn đề chỉ nằm ở Anchor của chính UserControl cấp ngoài cùng khi nó là con của FlowLayoutPanel.

1. Xác định UserControl nào sẽ được add động vào `FlowLayoutPanel`/`Panel` runtime.
2. Trong Designer của UserControl đó, đảm bảo dòng `Anchor = ...` ở cấp UserControl (không phải control con) KHÔNG bao gồm `Right`/`Bottom` trừ khi thực sự cần và đã test kỹ với parent thật.
3. Nếu cần control con giãn theo UserControl cha khi cha đổi kích thước (VD form resize), set `Anchor` đó trên CONTROL CON, không phải trên UserControl gốc — và để code gọi (VD `MainForm`) chủ động set lại `Width` của UserControl mỗi khi cần (qua `SizeChanged` event của panel cha), thay vì để WinForms tự tính qua Anchor.

## Áp dụng lại (How to reuse)

- Khi thấy "control được add vào list/collection đúng logic (add thành công, count tăng) nhưng KHÔNG hiển thị gì, không exception" → nghi ngay Anchor/Size = 0 trước khi nghi z-order, Visible, hay exception bị nuốt.
- Kiểm tra Designer file của UserControl động: tìm dòng set `Anchor` ở cấp UserControl gốc (không phải control con) — nếu có `Right`/`Bottom` và UserControl này add vào `FlowLayoutPanel`/`Panel` runtime → xóa hoặc đổi lại `Top | Left`.
- Debug nhanh: log `ctrl.Size` / `ctrl.Bounds` ngay SAU `flowPanel.Controls.Add(ctrl)` — nếu Width/Height gần 0 hoặc âm, xác nhận đúng bug này.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Không nhầm với việc set `Dock` — `Dock` trên control con của FlowLayoutPanel bị FlowLayoutPanel ép về kích thước flow, hành vi khác với `Anchor`.
- ⚠️ Set `ctrl.Width = ...` TRƯỚC khi `Controls.Add(ctrl)` (parent còn null) khiến WinForms cache khoảng-cách-anchor sai; nếu bắt buộc phải set Width thủ công, làm SAU khi đã add vào parent thật, hoặc bỏ hẳn Anchor Right và luôn set Width tường minh qua code, không dựa vào auto-anchor.
- ⚠️ Bug này KHÔNG throw exception, KHÔNG xuất hiện trong Output/Debug log mặc định — chỉ phát hiện được bằng cách nhìn UI thật hoặc log Size/Bounds tường minh. Rất dễ bị bỏ qua trong code review nếu chỉ đọc code mà không chạy UI thật.

## Tham chiếu

- Project liên quan: `E:\KZTEK\Code_Git\7.LinuxDeployTool` (Kztek.LinuxDeployTool — WinForms dev tool publish nhiều solution .deb)
