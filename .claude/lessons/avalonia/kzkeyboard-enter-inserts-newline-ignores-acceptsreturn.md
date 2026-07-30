---
category: avalonia
tags: [kzkeyboard, textbox, acceptsreturn, virtual-keyboard, kiosk]
severity: medium
created: 2026-07-30
updated: 2026-07-30
project-origin: MolexAPP (MolexKioskApp)
---

# KzKeyboard ENTER luôn chèn "\n" — bỏ qua AcceptsReturn/TextWrapping của TextBox đích

## Tình huống gặp phải

> Kiosk app (Avalonia) dùng `kz:KzKeyboard` (bàn phím ảo on-screen) làm input chính cho các ô
> `kz:KzTextBox` (SearchBox, NameBox) không nên xuống dòng. Đã set `AcceptsReturn="False"`
> `TextWrapping="NoWrap"` trên XAML nhưng user báo "bấm Enter vẫn xuống dòng được".

## Triệu chứng / Lỗi

```
XAML: <kz:KzTextBox AcceptsReturn="False" TextWrapping="NoWrap" .../>
Thực tế: chạm phím "↵ ENTER" trên KzKeyboard vẫn tạo dòng mới trong ô nhập.
Không có exception — hành vi sai âm thầm, chỉ phát hiện khi test tay trên app thật.
```

## Nguyên nhân gốc rễ (Root Cause)

`KzKeyboard.ProcessKey()` (KztekComponentAvalonia/Controls/KzKeyboard.cs) xử lý phím ENTER
bằng cách gọi thẳng `TypeTextRaw("\n")` — hàm này thao tác trực tiếp lên `TargetTextBox.Text`
(chèn ký tự vào chuỗi qua `string.Insert`), KHÔNG đi qua pipeline phím vật lý của Avalonia
(`OnKeyDown`/`TextInput`). Vì vậy thuộc tính `AcceptsReturn` của `TextBox` — vốn chỉ chặn Enter
ở tầng xử lý phím vật lý — hoàn toàn không có tác dụng với bàn phím ảo tự chèn text bằng code.

## Giải pháp

```csharp
// KzKeyboard.cs — ProcessKey(), case "ENTER"
case "ENTER":
    TelexResetSyllable();
    if (TargetTextBox?.AcceptsReturn == true)
        TypeTextRaw("\n");
    KeyPressed?.Invoke(this, "ENTER");
    return;
```

1. Kiểm tra `TargetTextBox.AcceptsReturn` trước khi `TypeTextRaw("\n")`.
2. Vẫn luôn raise `KeyPressed?.Invoke(this, "ENTER")` — view có thể lắng nghe event này để
   coi ENTER như "Confirm/Submit" khi ô input là single-line (search, name...).
3. Không cần sửa gì ở phía view (`IdentitySearchView`, `RegistrationNameView`) — set
   `AcceptsReturn="False"` trên XAML giờ đã có tác dụng thật.

## Áp dụng lại (How to reuse)

- Khi thấy 1 control custom tự thao tác `TextBox.Text`/`CaretIndex` bằng code (thay vì gửi
  KeyEventArgs) → PHẢI tự kiểm tra các thuộc tính hành vi chuẩn (`AcceptsReturn`, `MaxLength`,
  `IsReadOnly`...) thủ công trong code đó — các thuộc tính này KHÔNG tự động áp dụng.
- Trước khi báo "đã fix xong" cho bug liên quan đến bàn phím ảo / input giả lập → luôn test
  bằng đúng con đường input đó (chạm phím ảo), không chỉ test bằng bàn phím vật lý.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `KzKeyboard` cũng tự chèn " " (space) và ký tự thường qua `TypeTextRaw` — nếu sau này cần
  giới hạn thêm (VD: `MaxLength`, ký tự cho phép theo `InputScope`) thì cũng phải tự check thủ
  công trong `ProcessKey`, không dựa vào thuộc tính chuẩn của `TextBox`.
- ⚠️ Đây là shared component (`KztekComponentAvalonia`, ProjectReference dùng chung nhiều
  project) — sửa ở đây ảnh hưởng TẤT CẢ project tham chiếu, không chỉ MolexKioskApp. Đã kiểm
  tra: NotesBox (RegistrationStep3View, `AcceptsReturn="True"`) vẫn xuống dòng bình thường sau
  fix vì check đúng theo cờ này.

## Tham chiếu

- File sửa: `E:\KZTEK\Code_Git\5.BaseUI\KztekComponentAvalonia\KztekComponentAvalonia\Controls\KzKeyboard.cs`
- Project liên quan: MolexAPP (MolexKioskApp) — `IdentitySearchView.axaml`, `RegistrationNameView.axaml`
