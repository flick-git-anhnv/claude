---
category: avalonia
tags: [migration, visual-parity, theme, winforms, code-review]
severity: critical
created: 2026-07-20
updated: 2026-07-20
project-origin: iPGSv4 (migrate-ipgs-kiosk-avalonia)
---

# Migrate WinForms→Avalonia: agent tự ý đổi theme màu (dark/brand) thay vì giữ đúng bảng màu gốc — "build PASS" không phát hiện được

## Tình huống gặp phải

Đang thực hiện WF-MIGRATE cho `IPGS.Kiosk` (WinForms, kiosk thanh toán) sang Avalonia. Sau khi 9+ task migrate (Senior/Junior Developer) đều báo "Đã làm xong, build PASS 0 error" và được commit, user tự kiểm tra thực tế UI thì phát hiện SAI KHÁC rõ ràng so với bản gốc (bàn phím ảo khác, màu view kết quả khác).

## Triệu chứng / Lỗi

Không có exception, không có build error — hoàn toàn "xanh" theo mọi tiêu chí kỹ thuật (build PASS win-x64 + linux-x64, 0 error). Nhưng khi audit lại bằng cách đọc song song `.Designer.cs` gốc và code Avalonia đã port, phát hiện HÀNG LOẠT view bị đổi theme:
- Form gốc: `BackColor = White` (hoặc `SystemColors.ButtonHighlight`), chữ `#2A2F30`, giờ `#9EA1A2`, cảnh báo/số tiền còn lại màu đỏ `#DA291C`.
- Bản port: tự ý đổi thành nền navy tối (`#1A237E`, `#251C53`) + nút cam theo "brand KZTEK" mặc định, mất hẳn màu đỏ cảnh báo, một số label dùng ASCII không dấu thay tiếng Việt có dấu.
- Riêng `ArcButton` (control dùng chung ở hầu hết View): port ban đầu KHÔNG có bất kỳ hiệu ứng hover/pressed nào (`Render()` không phân biệt trạng thái con trỏ), trong khi 1 số nút gốc là PictureBox đổi hẳn ẢNH theo hover/pressed (`btnQr_normal.png` ↔ `btnQr_hover.png`) — bản port thay bằng ArcButton chỉ đổi màu chữ, MẤT hoàn toàn behavior đổi ảnh.

## Nguyên nhân gốc rễ (Root Cause)

1. Khi giao task migrate cho Senior/Junior Developer, prompt chỉ yêu cầu "giữ đúng logic nghiệp vụ" + "build PASS" làm tiêu chí hoàn thành — KHÔNG có bước bắt buộc đối chiếu `.Designer.cs` gốc (nơi chứa chính xác BackColor/ForeColor/Image property).
2. Agent code có xu hướng áp dụng "brand mặc định" (theme KZTEK Navy/Cam đã quen thuộc từ CLAUDE.md) thay vì tôn trọng màu THỰC TẾ của form đang port — vì không được yêu cầu tường minh "giữ NGUYÊN, không tự chọn brand".
3. `.cs` (code-behind form gốc) không chứa đủ thông tin màu/ảnh — phần lớn nằm trong `.Designer.cs` (do Visual Studio Designer generate). Agent chỉ đọc `.cs` mà bỏ qua `.Designer.cs` sẽ không có dữ liệu để đối chiếu.
4. Không có gate/checklist bắt buộc "audit visual parity" giữa các bước migrate — chỉ có gate build.

## Giải pháp

1. Audit lại từng View đã migrate: đọc `.Designer.cs` gốc (KHÔNG chỉ `.cs`) lấy `BackColor`, `ForeColor`, `Image`/`BackgroundImage`, `Location`, `Size`, `Font`.
2. Tìm mọi event handler `MouseEnter`/`MouseLeave`/`MouseDown`/`MouseUp` trong `.cs` gốc — nếu đổi `Image` theo trạng thái, đây là hành vi bắt buộc phải port lại đúng (tạo control chung nếu dùng lặp lại nhiều nơi, VD `HoverImageButton` port PictureBox-hover-swap-image).
3. Sửa lại toàn bộ màu/ảnh/layout cho khớp, build lại xác nhận không phá vỡ gì.
4. Khi tạo control chia sẻ (VD `ArcButton`) dùng ở nhiều View, sửa PHẢI làm ở control gốc 1 lần — không vá riêng từng View.

## Áp dụng lại (How to reuse)

- Khi giao task migrate UI (WinForms→Avalonia hay bất kỳ port UI nào), prompt PHẢI yêu cầu tường minh: "đọc `.Designer.cs` gốc lấy CHÍNH XÁC màu/ảnh/vị trí, KHÔNG tự ý đổi sang theme/brand khác — giữ nguyên 100% những gì user nhìn thấy ở bản gốc".
- Sau mỗi nhóm task migrate hoàn thành ("build PASS"), PHẢI có 1 bước audit RIÊNG (đọc song song source gốc — bao gồm `.Designer.cs` — và code đã port) trước khi coi là DONE. Không tin tưởng "build PASS + agent tự báo cáo Đã làm" làm tiêu chí duy nhất.
- Nếu 1 control dùng chung (button, keyboard...) thiếu tính năng cần thiết (đổi ảnh theo hover) so với bản gốc, sửa NGAY tại control gốc.
- Xem thêm `avalonia-migration-review-checklist.md` — bổ sung mục "đối chiếu màu/ảnh `.Designer.cs`" vào checklist đó.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ "Build PASS 0 error" KHÔNG đồng nghĩa với đúng giao diện — 2 tiêu chí độc lập, phải kiểm cả hai.
- ⚠️ Đọc chỉ `.cs` (không đọc `.Designer.cs`) sẽ THIẾU chính xác BackColor/ForeColor/Image — đây là nơi WinForms Designer lưu các giá trị này, không phải trong code thủ công.
- ⚠️ Agent có xu hướng áp brand/theme quen thuộc (từ CLAUDE.md hoặc project khác) thay vì tôn trọng màu gốc nếu không được nhắc rõ ràng — luôn nói rõ "KHÔNG tự đổi theme, giữ nguyên màu gốc" trong mọi task migrate UI.
- ⚠️ Một số label/text có thể bị port sai thành ASCII không dấu thay vì tiếng Việt có dấu — kiểm tra kỹ nội dung text, không chỉ màu/layout.

## Tham chiếu

- Project liên quan: `iPGSv4` — plan `PLAN-migrate-ipgs-kiosk-avalonia-2026-07-20`
- Liên quan: `avalonia/avalonia-migration-review-checklist.md` (nên bổ sung mục màu/ảnh Designer.cs)
