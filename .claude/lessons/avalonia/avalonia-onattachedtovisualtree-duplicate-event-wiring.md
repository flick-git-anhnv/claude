---
category: avalonia
tags: [event-wiring, OnAttachedToVisualTree, UserControl, toggle-button, duplicate-subscription]
severity: high
created: 2026-07-17
updated: 2026-07-17
project-origin: parking-v8-app-avalonia
---

# Nút toggle (eye/password) "bấm không có tác dụng" do gắn event trùng trong OnAttachedToVisualTree

## Tình huống gặp phải

`KzPasswordTextBox` (UserControl Avalonia) có nút mắt (EyeButton) để hiện/ẩn mật khẩu. User báo bug: bấm nút không có tác dụng gì.

## Triệu chứng / Lỗi

Không có exception. Bấm nút mắt, icon không đổi, `PasswordChar` không đổi — hoặc chỉ thỉnh thoảng có tác dụng (không nhất quán).

## Nguyên nhân gốc rễ (Root Cause)

Việc gắn sự kiện (`btn.Click += OnEyeToggle`, `tb.TextChanged +=`, `GotFocus`/`LostFocus`, `border.PointerEntered/PointerExited`) được đặt trong `OnAttachedToVisualTree(...)` mà KHÔNG có cờ chống gắn trùng, và không gỡ trong `OnDetachedFromVisualTree`.

Avalonia có thể gọi `OnAttachedToVisualTree` NHIỀU HƠN 1 LẦN cho cùng 1 control instance (control bị re-parent, TabItem được realize lại, Window ẩn/hiện lại, control nằm trong container thay đổi visibility...). Mỗi lần gọi lại, handler `OnEyeToggle` được `+=` thêm 1 lần nữa → khi user bấm 1 lần, handler chạy N lần → biến state (`_showPassword`) bị đảo N lần → nếu N chẵn, quay lại đúng trạng thái ban đầu → nhìn như "bấm không có tác dụng".

## Giải pháp

Thêm cờ `_eventsWired` để đảm bảo toàn bộ khối gắn sự kiện trong `OnAttachedToVisualTree` chỉ chạy đúng 1 lần trong vòng đời control:

```csharp
private bool _eventsWired = false;

protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnAttachedToVisualTree(e);
    ApplySize();
    ApplyInputState();
    ApplyWatermark();

    if (_eventsWired) return;
    _eventsWired = true;

    if (this.FindControl<Button>("EyeButton") is { } btn)
        btn.Click += OnEyeToggle;
    // ... các subscription khác cũng nằm trong guard này
}
```

1. Xác định toàn bộ nơi `+=` subscribe event trong `OnAttachedToVisualTree`/`OnLoaded`.
2. Thêm 1 boolean field cấp instance, check-and-return ngay đầu khối wiring.
3. Các method KHÔNG phụ thuộc trạng thái 1-lần (như `ApplySize`, `ApplyInputState`, `ApplyWatermark` — chạy lại vô hại) vẫn để ngoài guard, chạy lại mỗi lần attach là bình thường.

## Áp dụng lại (How to reuse)

- Khi thấy custom Control/UserControl có `+=` subscribe event bên trong `OnAttachedToVisualTree` (không phải constructor) → LUÔN kiểm tra có cờ chống gắn trùng chưa.
- Bug "bấm nút không có tác dụng" / "toggle phải bấm 2 lần mới thấy đổi" / "event xử lý nhiều lần không rõ lý do" → nghi ngay việc control bị attach lại nhiều lần và handler bị cộng dồn.
- Cách xác nhận nhanh: thêm `Console.WriteLine`/log số lần `OnAttachedToVisualTree` được gọi cho cùng 1 instance.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Guard 1-lần (`_eventsWired`) chỉ đúng nếu control KHÔNG bị destroy/tạo lại hoàn toàn (thực sự là instance mới thì field reset về false — vẫn đúng). Chỉ sai nếu cùng 1 field bị share giữa nhiều instance (static) — KHÔNG dùng static cho cờ này.
- ⚠️ Nếu logic bên trong khối wiring cần chạy lại theo state mới mỗi lần attach (hiếm khi cần) thì KHÔNG dùng cách này — phải tách riêng phần cần gắn 1 lần và phần cần refresh mỗi lần.
- ⚠️ Cách thay thế khác là gỡ handler trong `OnDetachedFromVisualTree` (`btn.Click -= OnEyeToggle`) — cách này đúng hơn về mặt "sạch" nhưng dễ quên gỡ hết tất cả handler đã thêm (kể cả lambda vô danh không gỡ được) — dùng cờ 1-lần đơn giản và an toàn hơn khi wiring không cần thay đổi theo state.

## Tham chiếu

- File: `src/ParkingV8.UI/Controls/Cs/KzPasswordTextBox.axaml.cs`
- Project liên quan: parking-v8-app-avalonia
- Lesson liên quan: [avalonia-property-subscription-before-visual-tree.md](avalonia-property-subscription-before-visual-tree.md)
