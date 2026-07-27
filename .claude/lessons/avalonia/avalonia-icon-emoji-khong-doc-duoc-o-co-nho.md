---
category: avalonia
tags: [icon, emoji, toolbar, font-rendering, ui-small-size]
severity: medium
created: 2026-07-27
updated: 2026-07-27
project-origin: IPGSUseCam
---

# Emoji/pictograph làm icon nút bị nát ở cỡ toolbar — không phải lỗi thiếu font

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Đang làm việc với control `KzToolBar` trong thư viện `KztekComponentAvalonia` (repo `E:\KZTEK\Code_Git\5.BaseUI`), dùng trong app Avalonia `IPGSUseCam`. Toolbar có 6 nút, mỗi nút gồm 1 `TextBlock` icon + 1 `TextBlock` nhãn.

## Triệu chứng / Lỗi

> Lỗi hiện ra như thế nào? Exception message? Behavior sai?

Nút "Sửa" (icon `✏` U+270F) hiện ra như một **gạch ngang**, nút "Xóa" (icon `🗑` U+1F5D1) hiện ra như một **ô đặc**. Trong khi cùng toolbar đó, `+` (Thêm), `↺` (Làm mới), `📥`/`📤` (Import/Export) lại hiện rõ ràng, đọc được bình thường.

```
Không có exception — chỉ là hiển thị sai/mờ ở 2 icon cụ thể trong 6 icon của toolbar.
```

## Nguyên nhân gốc rễ (Root Cause)

> Tại sao xảy ra? Không ghi "chưa rõ" — phải điều tra đến cùng.

**Chẩn đoán SAI ban đầu:** Tưởng app dùng font Inter không chứa emoji nên Avalonia vẽ ô vuông tofu. Đã thử thêm `FontFamily="Segoe UI Symbol, Segoe UI Emoji, Noto Color Emoji, $Default"` cho các TextBlock icon → không đổi gì. Sau đó thử tăng `FontSize` từ mặc định lên 15 → vẫn không đọc được.

**Nguyên nhân thật:** Glyph VẪN render đúng — phóng to ảnh chụp màn hình 5× thì thấy rõ đó đúng là hình bút chì và hình thùng rác. Vấn đề là **độ phức tạp của hình so với kích thước hiển thị**: pictograph nhiều chi tiết (bút chì có thân + đầu + tẩy; thùng rác có nắp + thân + gân) khi vẽ ở 12–15px thì các nét dồn vào nhau thành một khối mờ. Còn `+`, `↺`, mũi tên chỉ có 2–3 nét đơn nên vẫn đọc được ở cùng cỡ.

## Giải pháp

> Làm gì để fix? Bước nào theo thứ tự nào?

1. Bước 1: Phóng to ảnh chụp màn hình 4–5× để xác nhận đây là vấn đề "glyph đúng nhưng quá nhỏ" chứ không phải tofu/thiếu font.
2. Bước 2: Bỏ hẳn icon ở 2 nút phức tạp (Sửa, Xóa), chỉ giữ nhãn chữ ("Sửa", "Xóa") — nhãn cộng với màu/variant của nút đã đủ phân biệt.
3. Bước 3: Giữ nguyên các icon hình nét đơn giản (`+`, `↺`, mũi tên, `✓`, `×`) vì chúng vẫn đọc được ở cỡ nhỏ.

## Áp dụng lại (How to reuse)

> Lần sau gặp tình huống tương tự, làm gì ngay lập tức?

- Khi thấy icon Unicode/emoji hiển thị mờ/nát trong toolbar/badge/nút cỡ nhỏ → KHÔNG vội kết luận "thiếu font". Trước tiên phóng to ảnh chụp màn hình 4–5×.
- Khi chọn ký tự làm icon cho UI cỡ nhỏ (toolbar, badge, nút Sm), CHỈ dùng hình nét đơn giản: mũi tên, `+`, `×`, `✓`, `↺`. Tránh emoji/pictograph nhiều chi tiết.
- Nếu bắt buộc cần icon dạng hình phức tạp, dùng bộ icon font thiết kế riêng cho UI nhỏ (Segoe Fluent Icons / Segoe MDL2 Assets) chứ đừng dùng emoji Unicode.

## Chú ý / Cạm bẫy (Gotchas)

> Điều gì dễ sai khi apply solution này?

- ⚠️ Ô vuông tofu thật là hình chữ nhật rỗng viền đều; còn glyph render đúng nhưng quá nhỏ thì phóng to sẽ thấy hình thù thật. Hai trường hợp này cần cách sửa hoàn toàn khác nhau (đổi FontFamily vs đổi icon).
- ⚠️ Tăng `FontSize` không giải quyết được vấn đề độ phức tạp glyph — nếu cần giữ icon phức tạp, phải tăng đáng kể (không chỉ vài px) hoặc đổi hẳn sang icon font chuyên dụng.

## Tham chiếu

- Commit tham chiếu: `56c6c55` (repo 5.BaseUI), phát hiện 2026-07-27 trên project iPGSUseCam.
- Project liên quan: IPGSUseCam
