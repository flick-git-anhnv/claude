---
category: csharp-winforms
tags: [suspendlayout, resumelayout, anchor, dock-fill, layout-engine, dialog, usercontrol]
severity: critical
created: 2026-07-25
updated: 2026-07-25
project-origin: parking-v8-app (IPARKING v8 — UcConfirmOut)
---

# SuspendLayout lệch cặp với ResumeLayout → Anchor của control con ngừng được tính lại, im lặng không báo lỗi

## Tình huống gặp phải

> Dialog xác nhận xe ra (`UcConfirmOut`) trên máy trạm thu phí bãi xe, WinForms .NET 8.

Dialog là 1 `UserControl` được host trong 1 `Form` (`dialogHost`, `FormBorderStyle.None`) với `Dock = DockStyle.Fill`.
Hàm `ShowDialog()` gọi `SuspendLayout()` cho 3 đối tượng (`maskedForm`, `dialogHost`, `this`) để tránh nháy
khi cập nhật hàng loạt control, rồi `ResumeLayout()` sau khi cập nhật xong.

## Triệu chứng / Lỗi

Không có exception nào. Chỉ sai hiển thị, và **chỉ "thỉnh thoảng" mới bị**:

```
- Nút đóng "X" (Anchor = Top|Right) MẤT HẲN, không thấy đâu
- Hàng nút bấm dưới cùng (Xác nhận / Voucher / Đổi thẻ) bị cắt, chỉ còn 1 sliver
- Label tiêu đề (Anchor = Top|Left|Right, TextAlign = Center) bị mất nửa phải,
  chữ lệch sang phải so với tâm dialog
- Cột nội dung bên phải bị cắt chữ ("Nhóm định danh" → "Nhóm định d.")
- Ảnh/nội dung nửa trên vẫn hiển thị BÌNH THƯỜNG
```

Đo bằng code thì `dialogHost.Size == UserControl.Size` — **kích thước hoàn toàn khớp nhau**, không hề lệch.
Điều này khiến việc chẩn đoán đi sai hướng rất lâu (nghi DPI scaling, nghi `MinimumSize` quá nhỏ,
nghi công thức tính kích thước theo màn hình, nghi `FlowLayoutPanel` wrap, nghi region bo góc `Guna2Elipse`...).

## Nguyên nhân gốc rễ (Root Cause)

Một dòng `SuspendLayout()` bị gõ sai vào **đúng vị trí đáng ra phải là `ResumeLayout()`**:

```csharp
this.SuspendLayout();          // 🛑 SAI — đáng ra là this.ResumeLayout(false)
dialogHost.ResumeLayout(false);
maskedForm.ResumeLayout(false);
```

Đếm suspend count cho mỗi đối tượng trong 1 lần mở dialog:

| Đối tượng | Suspend | Resume | Tổng |
|---|---|---|---|
| `maskedForm` | 2 | 2 | 0 ✔ |
| `dialogHost` | 2 | 2 | 0 ✔ |
| `this` (UserControl) | **3** | 1 | **+2** ❌ |

`Control.SuspendLayout()`/`ResumeLayout()` hoạt động theo **bộ đếm (reference count)**, không phải cờ bool.
Chỉ khi đếm về 0 thì layout engine mới chạy lại. Ở đây count **tăng thêm +2 sau MỖI lần mở dialog** và
không bao giờ về 0 → **layout engine của UserControl bị treo vĩnh viễn** cho tới khi restart app.

**Vì sao kích thước vẫn khớp mà nội dung vẫn sai:** `UserControl` là con của `dialogHost`, nên bounds của nó
do **layout engine của `dialogHost`** set (engine này khoẻ mạnh, count = 0) → `Dock=Fill` vẫn hoạt động,
`this.Size` luôn đúng. Nhưng các control **BÊN TRONG** UserControl (`btnCancel`, `tableLayoutPanel1`, `lblMessage`)
lại do **layout engine của chính UserControl** sắp đặt — engine đó đang treo → **`Anchor` không bao giờ được
tính lại**. Chúng giữ nguyên toạ độ thiết kế (hệ 599×768) trong khi container thực tế đã hẹp hơn
→ nút `X` ở `X=551` nằm ngoài vùng nhìn thấy, panel nội dung bị clip mép phải + mép dưới.

**Vì sao "thỉnh thoảng":** lần mở **đầu tiên** vẫn đúng (count = 0 tại thời điểm resize, resize xảy ra
TRƯỚC `SuspendLayout` đầu hàm). Từ lần mở **thứ 2** trở đi count ≥ 2 → mọi thay đổi kích thước/`Visible`
không còn được phản ánh.

## Giải pháp

```csharp
// 1. Sửa dòng gõ sai — dùng ResumeLayout(true) để buộc 1 lượt layout thật sự,
//    vì các thay đổi Visible/Height phía trên đều diễn ra khi layout đang treo
this.ResumeLayout(true);
dialogHost.ResumeLayout(false);
maskedForm.ResumeLayout(false);
```

```csharp
// 2. Thêm finally để không rò rỉ suspend count khi có ngoại lệ
//    (các SuspendLayout ở đầu hàm thường nằm NGOÀI khối try)
finally
{
    this.ResumeLayout(true);
    dialogHost.ResumeLayout(false);
    maskedForm.ResumeLayout(false);
}
```

1. Đếm số lần `SuspendLayout` vs `ResumeLayout` cho **từng đối tượng riêng biệt** trong toàn bộ vòng đời hàm.
2. Sửa dòng lệch cặp; dùng `ResumeLayout(true)` nếu đã đổi nội dung/`Visible` trong lúc treo.
3. Bọc `finally` để đường ngoại lệ cũng resume.
4. Kiểm tra các file "họ hàng" (copy-paste): ở ca này `UcConfirmIn.cs` cân bằng đúng, **chỉ `UcConfirmOut.cs` sai**
   — khớp với việc lỗi chỉ xảy ra ở dialog xe RA.

## Áp dụng lại (How to reuse)

- Khi thấy **`Anchor`/`Dock` của control con "không phản ứng"** với thay đổi kích thước, mà không có exception nào
  → **nghi ngờ suspend count lệch NGAY ĐẦU TIÊN**, trước khi đi điều tra DPI/MinimumSize/region.
- Dấu hiệu vàng phân biệt: **`Parent.Size == Child.Size` (khớp đúng) nhưng các cháu bên trong lại lệch/bị clip**
  → chắc chắn engine của `Child` bị treo, không phải lỗi kích thước.
- Cách xác nhận nhanh bằng log: nếu `uc.Size` đã nhỏ hơn thiết kế mà `btnX.Bounds` **vẫn giữ toạ độ thiết kế**
  → Anchor stale, đúng bệnh này.
- `grep -n "SuspendLayout\|ResumeLayout" <file>` rồi đếm theo từng đối tượng — 30 giây, loại được cả một hướng
  điều tra sai kéo dài hàng giờ.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `SuspendLayout`/`ResumeLayout` là **bộ đếm**, không phải cờ bool — gọi suspend 3 lần thì phải resume 3 lần.
- ⚠️ Lỗi này **hoàn toàn im lặng**: không exception, không warning compiler, build sạch 0 error.
- ⚠️ `ResumeLayout(false)` **không** thực hiện layout ngay. Nếu đã đổi `Visible`/`Size`/`Text` của control con
  trong lúc treo thì phải dùng `ResumeLayout(true)`, nếu không geometry vẫn cũ.
- ⚠️ Gọi `ResumeLayout` khi count đã = 0 là **vô hại** (WinForms có guard `if (layoutSuspendCount > 0)`),
  nên thêm resume trong `finally` không sợ resume 2 lần.
- ⚠️ Đừng vội "fix" bằng cách nâng `MinimumSize` hay bỏ giới hạn kích thước — nó chỉ **che triệu chứng**
  (kẹp dialog ở kích thước lớn hơn nên trông như hết bệnh) trong khi Anchor vẫn treo.
- ⚠️ Hardcode số pixel vào `MinimumSize` còn tệ hơn khi `AutoScaleMode = Font`: giá trị literal **không được
  DPI-scale**, còn giá trị gán từ `this.MinimumSize` (do Designer set) thì có → hardcode làm lỗi quay lại trên
  máy chạy 125%/150%.

## Tham chiếu

- Project liên quan: `parking-v8-app` — `Kztek.Control8/UserControls/DialogUcs/UserControlDialogs/UcConfirmOut.cs`
- Lesson liên quan: `winforms-usercontrol-anchor-right-invisible-in-flowlayoutpanel.md`,
  `winforms-flowlayoutpanel-clientsize-zero-after-modal.md`
