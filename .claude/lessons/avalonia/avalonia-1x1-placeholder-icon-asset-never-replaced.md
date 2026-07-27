---
category: avalonia
tags: [assets, migration, placeholder, resx, icon, silent-failure]
severity: critical
created: 2026-07-22
updated: 2026-07-22
project-origin: iPGSv4 (KIOSK VERTICAL — LocationAndPayment)
---

# Icon "hoàn toàn không hiện" sau port WinForms→Avalonia: file `.png` là placeholder 1×1 trong suốt, không phải icon thật

## Tình huống gặp phải

User báo icon cảnh báo (⚠️ dấu "i" đỏ, `icon_infor.png`) trên `CarInforDetailView`/`MotorInforDetailView` "mất" hoàn toàn — không nhấp nháy, không hiện dù đã fix xong bug layout (Canvas alignment, row-height jitter) và đã rebuild + restart app thật (user xác nhận rõ ràng, loại trừ nguyên nhân build cũ).

## Triệu chứng / Lỗi

- Binding đúng (`IsInfoIconVisible`/`IsInforVisible` toggle đúng qua `DispatcherTimer` 500ms, verify bằng code review).
- `Source="avares://IPGS.Kiosk.Avalonia/Assets/Resources/img/icon_infor.png"` đúng path, file tồn tại (`Glob` xác nhận).
- Build PASS 0 Error, không exception, không log lỗi nào.
- Icon vẫn không hiện ở BẤT KỲ trạng thái nào (không phải do đang ở pha "off" của nhịp nhấp nháy).

## Nguyên nhân gốc rễ (Root Cause)

Dùng Python/Pillow mở trực tiếp file `icon_infor.png` để kiểm tra pixel:
```python
from PIL import Image
im = Image.open("icon_infor.png")
print(im.size, im.mode)          # → (1, 1) LA
print(im.convert('RGBA').getextrema())  # → ((0,0),(0,0),(0,0),(0,0)) — hoàn toàn trong suốt
```
File chỉ là **placeholder 1×1 pixel, alpha=0** (trong suốt tuyệt đối) — KHÔNG phải icon thật. Rất có thể trong quá trình migrate, dev tạo file rỗng làm chỗ trống (`New-Item`/`touch`-style placeholder) để build không lỗi thiếu file, với ý định thay bằng ảnh thật sau, nhưng bước đó bị bỏ sót — không có build error/warning nào cảnh báo vì đây là file ảnh hợp lệ về mặt định dạng (chỉ là nội dung rỗng).

## Giải pháp

1. Tìm control gốc trong project WinForms cũ tương ứng (PictureBox nào hiển thị icon này) qua `Designer.cs` (đối chiếu `Location`/`Size` khớp vị trí trong `.axaml` đã port).
2. Ảnh gốc WinForms PictureBox nhúng dạng base64 trong file `.resx` cùng tên form, key `<PictureBoxName>.Image`. Trích xuất bằng Python:
```python
import re, base64
content = open("frmCarInforDetail.resx", encoding="utf-8").read()
m = re.search(r'<data name="picInfor\.Image"[^>]*>(.*?)</data>', content, re.DOTALL)
b64 = re.search(r'<value>(.*?)</value>', m.group(1), re.DOTALL).group(1).strip()
open("icon_infor_real.png", "wb").write(base64.b64decode(b64))
```
3. Verify ảnh trích xuất có kích thước/nội dung hợp lý (không phải lại 1×1) bằng Pillow, xem trực tiếp bằng Read tool (image) để xác nhận đúng icon trước khi ghi đè.
4. Ghi đè file placeholder trong `Assets/Resources/img/` bằng ảnh thật vừa trích xuất — path/tên file giữ nguyên (không cần sửa XAML).
5. **Quét toàn bộ thư mục Assets tìm placeholder khác cùng loại** (bug thường không đơn lẻ):
```python
from PIL import Image
import os
for dirpath, _, files in os.walk("Assets"):
    for f in files:
        if f.lower().endswith((".png",".jpg",".jpeg",".bmp",".gif")):
            im = Image.open(os.path.join(dirpath, f))
            if im.size[0] <= 4 and im.size[1] <= 4:
                print("PLACEHOLDER?", f, im.size)
```
Áp dụng lần này phát hiện thêm `icon_success.png` (BikePaymentResultView) cùng lỗi — trích từ `frmBikePaymentResult.resx` key `pic.Image`.

## Áp dụng lại (How to reuse)

- Khi 1 icon/ảnh "hoàn toàn không hiện" (không phải do binding/logic — đã verify code đúng, build PASS, đã rebuild+restart thật) → **nghi ngờ ngay bản thân file ảnh**, mở bằng Pillow kiểm tra `size`/`getextrema()` trước khi đào sâu logic thêm.
- Sau khi phát hiện 1 file placeholder trong 1 project port từ WinForms → **luôn quét toàn bộ thư mục Assets** tìm placeholder khác cùng đợt migrate — xác suất cao bug lặp lại (case thực tế: tìm thấy đúng 1 file thứ 2 ngay lần quét đầu).
- Nguồn ảnh thật đáng tin cậy nhất khi port từ WinForms: file `.resx` cùng tên Form/UserControl gốc, tìm theo control name khớp `Location`/`Size` trong `.Designer.cs`.
- LUÔN xem lại ảnh đã trích xuất bằng Read tool (hiển thị trực quan) để xác nhận đúng icon mong đợi TRƯỚC khi ghi đè — tránh trích nhầm resource khác cùng form.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ File ảnh rỗng/placeholder là hợp lệ về định dạng (`.png` thật, mở được, không lỗi) — build/compile/`AvaloniaResource` glob KHÔNG có cơ chế nào phát hiện "nội dung rỗng" này. Chỉ phát hiện được bằng cách MỞ ảnh và kiểm tra kích thước/pixel thực tế.
- ⚠️ Đừng dừng lại sau khi tìm thấy 1 file lỗi — luôn quét toàn bộ để tìm các file cùng loại bug, đặc biệt trong project vừa migrate hàng loạt màn hình.
- ⚠️ `.resx` cũ có thể chứa NHIỀU `<data name="X.Image">` cho nhiều PictureBox trong cùng form — phải đối chiếu đúng tên control (qua `Designer.cs`) trước khi trích, không đoán bừa theo tên gần giống.

## Tham chiếu

- Liên quan: [avalonia-canvas-direct-child-horizontalalignment-ignored.md](avalonia-canvas-direct-child-horizontalalignment-ignored.md), [avalonia-avaloniaresource-not-copied-to-output.md](avalonia-avaloniaresource-not-copied-to-output.md) (cùng nhóm "asset silent failure" khi migrate)
- Project liên quan: iPGSv4 — `IPGS.Kiosk.Avalonia/Assets/Resources/img/icon_infor.png`, `icon_success.png`; nguồn gốc `IPGS.Kiosk/LotteDesigns/CarUserControls/frmCarInforDetail.resx`, `IPGS.Kiosk/LotteDesigns/BikeUserControls/frmBikePaymentResult.resx`
