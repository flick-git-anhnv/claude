---
category: camera-integration
tags: [lao-lpr, ocr, bien-so-lao, lao-script, yolo, dataset-labeling]
severity: medium
created: 2026-07-28
updated: 2026-07-28 (phụ lục: bảng class↔chữ Lào + 5 cặp dễ nhầm + gotcha template MSE)
project-origin: LAO-LPR-yolo
---

# Đọc chữ Lào trên biển số: phân biệt ນ / ມ / ຫ / ທ bằng VỊ TRÍ VÒNG XOẮN

## Tình huống gặp phải

> Gán nhãn / kiểm tra dataset `LAO-LPR-yolo`, đọc biển số Lào từ ảnh crop 640x379 (chất lượng camera, mờ).

Được hỏi "biển số này là gì" với ảnh biển vàng chữ đen Lào (`images/train/*.jpg`). Đọc bằng mắt trên ảnh gốc cho kết quả **sai thứ tự và sai ký tự** (`ຫນ` thay vì `ນຫ`), user phát hiện ngay.

## Triệu chứng / Lỗi

```
Đọc lần 1 (ảnh gốc, không zoom): "ຫນ 1777"   ← SAI
Đọc đúng (sau khi zoom + đối chiếu font): "ນຫ 1777"
Dòng trên biển: "ນະຄອນຫຼວງວຽງຈັນ" (Vientiane Capital) — KHÔNG phải phần số đăng ký
```

Sai ở 2 điểm: (1) đảo thứ tự 2 ký tự, (2) nhầm ນ ↔ ມ.

## Nguyên nhân gốc rễ (Root Cause)

Các phụ âm Lào khác nhau **chỉ ở vị trí vòng xoắn nhỏ (loop)** và số lượng "bụng chữ", ở ảnh mờ thì loop chỉ còn là 1 đốm đen 2-3 pixel:

| Chữ | Hình dạng | Dấu hiệu quyết định |
|---|---|---|
| ນ (no) | 1 bụng "u" | loop ở **TRÊN-trái** |
| ມ (mo) | 1 bụng "u" | loop ở **DƯỚI-trái** |
| ບ (bo) | 1 bụng "u" | **không** loop |
| ຫ (ho) | 2 bụng (u + vòm "n") | **2 loop** ở đỉnh mỗi phần |
| ທ (tho) | 2 bụng (u + vòm) | hẹp hơn, chỉ 1 loop bên trái |

Đọc "cảm tính" trên ảnh chưa zoom → loop bị mất/nhòe → đoán sai; và mắt dễ đọc ຫ (chữ 2 bụng, nổi bật) trước ນ nên đảo thứ tự.

## Giải pháp

Quy trình 3 bước, dùng PIL, ghi tạm vào `temp/read-plate/`:

```python
from PIL import Image, ImageDraw, ImageFont

# 1. Crop từng ký tự + upscale LANCZOS x4-x8
im = Image.open(path); w, h = im.size
im.crop((20, 150, 300, 340)).resize((280*4, 190*4), Image.LANCZOS).save('temp/read-plate/pair.png')

# 2. Render CHỮ THAM CHIẾU cùng cỡ lớn để đối chiếu loop
f = ImageFont.truetype(r'C:\Windows\Fonts\LeelaUIb.ttf', 300)   # Leelawadee UI Bold có glyph Lào
for ch in ['\u0e99', '\u0ea1', '\u0eab']:                        # ນ ມ ຫ
    img = Image.new('RGB', (400, 450), 'white')
    ImageDraw.Draw(img).text((40, 20), ch, font=f, fill='black')

# 3. Render cả cụm ứng viên ("ນຫ 1777", "ມຫ 1777", "ຫນ 1777"...) rồi so hình tổng thể
```

1. Zoom riêng phần chữ (nửa dưới biển) và phần dòng tỉnh (nửa trên) — hai dòng có font/kích thước khác nhau.
2. Với mỗi glyph, xác định: mấy bụng? loop ở trên hay dưới? → tra bảng trên.
3. Render 3-4 phương án ứng viên bằng font Lào rồi so sánh **hình dạng tổng thể** trước khi kết luận.

## Áp dụng lại (How to reuse)

- Khi được hỏi đọc biển số Lào/Thái → **KHÔNG đọc trực tiếp**, luôn crop + upscale trước.
- Font Lào sẵn có trên Windows: `C:\Windows\Fonts\LeelaUIb.ttf` (Leelawadee UI Bold). `DokChampa.ttf` / `Phetsarath` không chắc có.
- Dòng chữ nhỏ phía trên biển Lào là **tên tỉnh**, không thuộc số đăng ký. Vientiane Capital = `ນະຄອນຫຼວງວຽງຈັນ`. Dùng dòng này làm "bộ chuẩn hiệu chỉnh" vì nó chứa sẵn ນ và ຫ để so.
- Format biển Lào phổ biến: `<2 chữ Lào> <4 số>`.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Loop của ນ ở TRÊN, của ມ ở DƯỚI — đây là lỗi nhầm hay gặp nhất, và ນ cũng có "chân" chìa sang trái ở đáy nên rất dễ tưởng là loop dưới của ມ.
- ⚠️ ຫ (2 loop) vs ທ (1 loop) gần như giống nhau khi mờ — phải zoom ≥ x4 mới thấy.
- ⚠️ Mắt có xu hướng đọc glyph 2 bụng (ຫ) trước → **luôn xác nhận lại thứ tự trái→phải** bằng toạ độ x của crop, đừng tin thứ tự cảm nhận.
- ⚠️ Đừng render text Lào bằng font không hỗ trợ — PIL vẽ ra ô vuông/rỗng mà không báo lỗi.

## Phụ lục (2026-07-28, project TraningTiengLao): bảng class ↔ chữ Lào + 5 cặp dễ nhầm

Khi gán nhãn YOLO, class được đặt tên bằng chữ Latin A–Z + `AA` thay cho ký tự Lào gốc.
**Mapping chuẩn (27 phụ âm, đọc trái→phải, trên→dưới):**

| Class | Lào | Class | Lào | Class | Lào |
|---|---|---|---|---|---|
| A | ກ | K | ຖ | U | ຢ |
| B | ຂ | L | ທ | V | ຣ |
| C | ຄ | M | ນ | W | ລ |
| D | ງ | N | ບ | X | ວ |
| E | ຈ | O | ປ | Y | ຫ |
| F | ສ | P | ຜ | Z | ອ |
| G | ຊ | Q | ຝ | AA | ຮ |
| H | ຍ | R | ພ | | |
| I | ດ | S | ຟ | | |
| J | ຕ | T | ມ | | |

**Trục phân loại ĐÚNG là HƯỚNG VÒNG CUNG trước, rồi mới đến chi tiết cục bộ.**
Nhóm theo trục này thì số cặp dễ nhầm giảm từ ~10 xuống 5:

| Nhóm | Thành viên | Đặc điểm chung |
|---|---|---|
| Vòng cung LÊN ∩ | A ກ, C ຄ, I ດ, J ຕ | vòm ở trên, 2 chân xuống |
| Vòng cung XUỐNG ∪ | H ຍ, L ທ, M ນ, N ບ, P ຜ, T ມ | bụng ở dưới |
| 2 bụng | R ພ, Y ຫ | 2 bụng liên tiếp |
| Nét lượn / có vòng | AA ຮ, B ຂ, E ຈ, F ສ, V ຣ, W ລ, X ວ, Z ອ | không có vòm/bụng rõ |

**Cặp dễ nhầm THẬT SỰ** (user xác nhận bằng mắt, đối chiếu font sạch):

| Cặp | MSE | Phân biệt bằng |
|---|---|---|
| I ດ vs J ຕ | 9,1M | I đỉnh **TRÒN** trơn; J đỉnh **VUÔNG** hơn + có **1 đoạn ở giữa đỉnh chĩa XUỐNG** |
| W ລ vs X ວ | 11,5M | W có **khấc GẤP GÓC** ở thân; X cong **tròn trơn**, đáy tròn mở sang trái |
| M ນ vs T ມ | 12,8M | **M cạnh 1 đậm ở CẢ TRÊN và DƯỚI; T chỉ đậm ở DƯỚI** |
| AA ຮ vs V ຣ | 13,8M | cả 2 đều hình S — **AA đỉnh GẤP GÓC; V đỉnh cong TRÒN MƯỢT, không gấp góc** |

Đặc điểm riêng đáng ghi của Z ອ: **vòng KHÉP KÍN ở đỉnh** (như đầu số 9) + đuôi cuộn xuống,
phần đỉnh chỗ cuộn lên **hơi đậm hơn**.

### ⚠️⚠️ MSE toàn ảnh vừa MÙ vừa BÁO NHẦM — không dùng làm thước đo độ dễ nhầm

Dùng khoảng cách MSE để xếp hạng "cặp nào dễ nhầm" **cho kết quả sai theo CẢ HAI chiều**, đã kiểm chứng với user:

| Cặp | MSE nói | Thực tế (user xác nhận) |
|---|---|---|
| AA ຮ – Z ອ | 11,1M → "nguy hiểm nhất nhóm" | **Không giống nhau gì cả** (false positive) |
| X ວ – Z ອ | 11,4M → "nguy hiểm" | **Không giống nhau gì cả** (false positive) |
| I ດ – J ຕ | 9,1M → nguy hiểm | Đúng là dễ nhầm (chỉ khác 1 khấc nhỏ ở đỉnh) |
| W ລ – X ວ | 11,5M → nguy hiểm | Đúng là dễ nhầm |

Lý do: MSE bị chi phối bởi **lượng mực và silhouette bao ngoài**. Hai chữ có mật độ nét/khối tương đương
sẽ ra khoảng cách nhỏ dù hình thù khác hẳn (AA–Z, X–Z); ngược lại hai chữ chỉ khác nhau đúng một chi tiết
vài pixel lại không tách ra được (I–J). ⇒ **Đừng dùng bảng MSE để quyết định nên gom thêm mẫu cho cặp nào,
và cũng đừng tin nó khi báo an toàn.** Phải nhờ người đọc được chữ xác nhận từng cặp bằng mắt.

Các cặp đối xứng gương theo trục ngang (rất dễ lẫn nếu bỏ qua hướng vòng cung):
- **C ຄ (∩) ↔ H ຍ (∪)** — cùng có 1 đoạn ngang móc GIỮA thân, chỉ khác hướng vòng cung
- **A ກ (∩) ↔ T ມ (∪)** — cùng dạng, khác hướng vòng cung

**Chữ KHÔNG xuất hiện trên biển số thật** (xác nhận bởi user, khỏi phải gom mẫu):
D ງ, G ຊ, K ຖ, O ປ, Q ຝ, S ຟ, U ຢ → chỉ 20 class chữ cái thực sự cần nhận dạng.

### ⚠️ Hệ quả: template matching không dùng được cho bộ chữ này

Mọi đặc điểm phân biệt ở trên đều là **chi tiết CỤC BỘ rất nhỏ** (loop trên/dưới, độ đậm ở đầu/chân cạnh,
khấc gấp góc, đoạn ngang giữa thân, khấc nhỏ ở đỉnh). Template MSE không thấy được chúng (mục trên).
⇒ Mô tả đặc điểm chính xác đến đâu cũng vô nghĩa với template matching. Muốn dùng được bộ quy tắc này phải
**trích xuất đặc trưng tường minh** (dò hướng vòng cung; dò loop/độ đậm theo vùng trên–dưới của từng cạnh;
đếm vòng khép kín bằng `RETR_CCOMP` contour hierarchy) hoặc **train CNN nhỏ**.

**Mẹo dựng tài liệu QC:** ghép ảnh mẫu thật từ `dataset-base/<class>/` chèn ngay dưới đúng ô chữ trong bảng chữ cái
(dò vị trí ô bằng grid cố định, hoặc dò cụm pixel đỏ của nhãn) → nhìn 1 ảnh là verify được toàn bộ mapping 27 class,
nhanh hơn đối chiếu từng folder rất nhiều.

## ⛔ Phụ lục quan trọng nhất (2026-07-28): KHÔNG dùng mắt Claude làm ground truth chữ Lào

Trong 1 session làm dataset biển Lào, tôi (Claude) đọc sai chữ Lào **4 lần liên tiếp**, mỗi lần
đều trình bày như thể là sự thật rồi user phải sửa:

| # | Tôi khẳng định | Thực tế | Kiểu sai |
|:-:|---|---|---|
| 1 | ký tự đầu là **C** ຄ | **A** ກ | nhầm A/C (khác nhau ở móc ngang giữa thân) |
| 2 | H ຍ = "bụng U rộng, đuôi kéo dài bên phải" | H = vòng cung hướng XUỐNG + móc ngang giữa thân | mô tả sai hoàn toàn |
| 3 | "AA ຮ và Z ອ dễ nhầm (MSE 11,1M)" | "không giống nhau gì cả" | tin chỉ số MSE thay vì hình |
| 4 | biển đọc là **X ວ** AA 5455 | **W ລ** AA 5455 | nhầm W/X (khác nhau ở loop đáy) |

Cùng 2 ca đó, **CNN 96% đọc ĐÚNG cả hai** (W 97,2%, L 91,8%) trong khi tôi đọc sai cả hai.

**Quy tắc vận hành bắt buộc:**
1. **KHÔNG** viết "biển thật là X" / "ground truth là Y" dựa trên việc tự nhìn ảnh. Phải nói rõ
   "tôi đọc là X, cần bạn xác nhận" — vì mọi con số accuracy tính trên nhãn do mình tự đọc sẽ sai.
2. Khi model và mắt Claude bất đồng về chữ Lào → **ưu tiên model**, rồi hỏi user chốt.
3. Việc Claude làm tốt: dựng công cụ QC (ghép mẫu vào bảng chữ cái, zoom ×4-×6 kèm glyph tham
   chiếu từ font sạch, phát hiện mẫu lỗi/gán nhãn sai bằng đặc trưng cấu trúc), **không phải**
   tự gán nhãn.
4. Dùng **confidence của model** làm cờ review thay cho việc Claude tự soát: trong test 12 ký tự,
   ký tự sai duy nhất có conf **0,22** còn 11 ký tự đúng đều ≥ 0,94 → ngưỡng ~0,7 lọc đúng ca cần
   xem tay, khỏi soát toàn bộ 13.500 ảnh.

## Tham chiếu

- Unicode Lao block: ນ U+0E99, ມ U+0EA1, ບ U+0E9A, ຫ U+0EAB, ທ U+0E97
- Project liên quan: LAO-LPR-yolo (dataset gán nhãn YOLO cho biển số Lào), TraningTiengLao (auto-label + bảng QC)
