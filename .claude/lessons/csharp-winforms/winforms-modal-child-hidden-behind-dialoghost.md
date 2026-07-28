---
category: csharp-winforms
tags: [winforms, modal-dialog, zorder, showdialog, kiosk-ui, topmost, maskeduserontrol]
severity: high
created: 2026-07-28
updated: 2026-07-28
project-origin: parking-v8-app
---

# ShowDialog() con hiển thị "im lặng" phía sau dialogHost (custom borderless Form) trong kiosk UI

## Tình huống gặp phải

> Hoàn thiện `btnEpass_Click` trong `UcConfirmOut.cs`/`UcConfirmOutSmall.cs` (Kztek.Control8) — thêm 1 Form con
> `FrmEpassQRPending` hiển thị mã QR chờ thanh toán EPASS, mở bằng `ShowDialog()` ngay trong dialog xác nhận ra xe
> (`dialogHost` — 1 `Form` borderless dùng làm khung chứa `UserControl` UcConfirmOut, hiển thị đè lên `maskedForm`).

## Triệu chứng / Lỗi

Code chạy qua đúng bước `ShowDialog()` (block đúng, không exception, `btnEpass` bị disable đúng như spec),
nhưng **không có cửa sổ nào hiện lên màn hình**. UI đứng yên ở dialog xác nhận ra xe như thể không có gì xảy ra,
chỉ khác là nút EPASS bị mờ đi (disabled). Nhìn thoáng qua tưởng dialog chưa được tạo/hiện, nhưng thực chất nó
đang chạy modal loop ở phía sau `dialogHost`.

## Nguyên nhân gốc rễ (Root Cause)

`dialogHost` trong các UserControl dialog kiểu này (`UcConfirmOut`, `UcConfirmOutSmall`) là 1 `Form` riêng,
`FormBorderStyle.None`, luôn hiện phía trên `maskedForm` trong suốt vòng đời dialog. Khi mở thêm 1 `Form` con
bằng `epassQrForm.ShowDialog(owner)` với `owner = maskedForm` (không phải `dialogHost`) và KHÔNG ẩn `dialogHost`,
`dialogHost` vẫn giữ z-order "trên cùng" tương đối so với owner được truyền vào — Form con hoàn toàn hợp lệ về
mặt code (modal loop chạy, `Invoke` từ thread khác vẫn được bơm) nhưng bị `dialogHost` che khuất trực quan.
Không có exception vì đây thuần là vấn đề Z-order, không phải lỗi logic.

Codebase đã có pattern xử lý đúng vấn đề này ở `BtnPayQR_Click` (form `FrmConfirmQRView`) nhưng lúc viết
`FrmEpassQRPending` đã không tra cứu lại pattern đó trước khi viết code mới tương tự.

## Giải pháp

Có 2 pattern hợp lệ trong codebase này để mở popup đè lên dialog đang hiển thị — ưu tiên pattern 2 (MaskedUserControl),
Form riêng (`BtnPayQR_Click` → `FrmConfirmQRView`, dùng `dialogHost.Visible=false` + `TopMost=true` +
`ShowDialog()` không owner) chỉ nên coi là workaround khi thực sự cần 1 cửa sổ Win32 độc lập.

**Pattern khuyến nghị — UserControl overlay qua `MaskedUserControl`** (giống `UcSelectVouchers`,
`UcSelectAccessKeyCollection`, và bản cuối cùng `UcEpassQRPending` áp dụng cho case này):

```csharp
// Trong UserControl con (vd UcEpassQRPending) — comptor riêng dialogHost + Guna2Elipse + MaskedUserControl
private readonly Form dialogHost = new();
private MaskedUserControl masked;
public UserControl TargetControl { set { masked?.Dispose(); masked = new MaskedUserControl(value); } }

public async Task<bool> ShowQRAsync(...)
{
    dialogHost.Location = ... // căn giữa theo masked.Width/Height
    dialogHost.Show(this.masked);   // Show KHÔNG modal — không cần TopMost/hide dialogHost cha
    masked.Show();
    tcs = new TaskCompletionSource<bool>();
    bool result = await tcs.Task;
    dialogHost.Hide(); masked.Hide();
    return result;
}
```

Trong `UcConfirmOut`/`UcConfirmOutSmall` (parent), khởi tạo 1 lần trong constructor giống `ucVouchers`:
```csharp
ucEpassQRPending = new UcEpassQRPending { TargetControl = this, BorderRadius = 24 };
...
bool isPaid = await ucEpassQRPending.ShowQRAsync(transaction, this.eventOut);
```
`MaskedUserControl` tự theo dõi `SizeChanged`/`LocationChanged`/`VisibleChanged` của `TargetControl` nên không có
vấn đề z-order — nó là 1 `Form` riêng track theo parent UserControl, hoàn toàn tách biệt khỏi `dialogHost` gốc
của parent dialog nên không bị che.

**Pattern workaround — Form riêng đè lên `dialogHost`** (chỉ dùng khi không tiện làm UserControl):
```csharp
dialogHost.Visible = false;          // 1. Ẩn dialogHost đang che
var frm = new FrmXxx(...);
frm.TopMost = true;                  // 2. Đảm bảo nổi lên trên mọi cửa sổ khác
DialogResult r = frm.ShowDialog();   // 3. KHÔNG truyền owner (dialogHost đã ẩn, không cần owner-chain)
frm.Dispose();
dialogHost.Visible = true;           // Khôi phục lại sau khi đóng, bất kể kết quả gì
```

## Áp dụng lại (How to reuse)

- Khi cần thêm 1 popup/overlay mới đè lên dialog xác nhận (`UcConfirmOut`, `UcConfirmOutSmall`, hoặc bất kỳ
  UserControl dialog nào dùng pattern `dialogHost` + `Guna2Elipse`) → làm 1 UserControl con theo mẫu
  `UcSelectVouchers`/`UcSelectAccessKeyCollection` (dùng `MaskedUserControl` + TCS), KHÔNG tạo `Form` mới trừ khi
  bắt buộc.
- Trước khi viết popup mới trong khu vực `Kztek.Control8/UserControls/DialogUcs/...`, luôn tra cứu các
  `ucXxx = new UcYyy { TargetControl = this, BorderRadius = 24 }` đã có trong constructor làm mẫu đầu tiên;
  chỉ xét `FrmConfirmQRView`-style (Form riêng) nếu overlay thực sự cần là cửa sổ Win32 độc lập.
- Nếu Form popup không hiện + không exception + code vẫn chạy tiếp bình thường sau khi đóng (test bằng cách
  bấm mù rồi ESC) → nghi ngay z-order/TopMost/owner, không phải lỗi tạo Form hay lỗi logic.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Test bằng cách "code build thành công + luồng chạy qua đúng bước" KHÔNG chứng minh UI hiển thị đúng —
  phải chạy app thật và nhìn màn hình.
- ⚠️ Đừng chỉ set `TopMost = true` mà quên ẩn `dialogHost` — nếu `dialogHost` cũng có khả năng được set
  TopMost sau này, 2 TopMost cạnh tranh vẫn có thể gây nhấp nháy/che khuất tùy thứ tự activate.
- ⚠️ Phải khôi phục `dialogHost.Visible = true` ở CẢ 2 nhánh kết quả (OK và Cancel) — không chỉ nhánh lỗi,
  để tránh dialog chính bị kẹt ẩn nếu có exception hoặc luồng thoát sớm.

## Tham chiếu

- Pattern khuyến nghị (UserControl + mask): `Kztek.Control8/5.Vouchers/UcSelectVouchers.cs`,
  `Kztek.Control8/UserControls/DialogUcs/MaskedUserControl.cs`,
  `Kztek.Control8/UserControls/DialogUcs/UserControlDialogs/UcEpassQRPending.cs`
- Pattern workaround (Form riêng): `Kztek.Control8/UserControls/DialogUcs/UserControlDialogs/UcConfirmOut.cs` → `BtnPayQR_Click`
- Project liên quan: parking-v8-app (IPARKING v8)
