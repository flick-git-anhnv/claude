---
category: reverse-engineering
tags: [ncnn, int8, pack4, quantization, weight-layout, arcsoft, lstsq]
severity: high
created: 2026-08-11
updated: 2026-08-11
project-origin: DecodeTools (ArcSoft IR-Liveness model, opcode 8e838)
---

# Conv INT8 pack4 trong ncnn: weight FLOAT nhưng LAYOUT interleave + activation cũng packed

## Tình huống gặp phải

Dựng lại mạng IR-Liveness của ArcSoft. Toàn bộ conv trong mạng này dùng opcode
`8e838` (khác `a9b2c` = conv float của các mạng detection/recognition). Cần
trích weight để dựng model dùng được.

## Triệu chứng / Phát hiện

1. **Opcode khác KHÔNG có nghĩa là int8-stored-weight.** Đọc vùng weight của
   `8e838` bằng đúng công thức offset descriptor (giống `a9b2c`) thấy mỗi byte
   thứ 4 luôn ~`0x3E`/`0x3F` → **weight là FLOAT32 thô**, không phải int8. Opcode
   `8e838` chỉ là code-path SIMD/pack khác, không đổi kiểu lưu số.

2. **Depthwise (3×3, groups=inC) đọc plain layout `(outC,1,kh,kw)` — ĐÚNG.**
   Verify 15/43 conv khớp tuyệt đối (rel<1e-3) ngay, toàn bộ là depthwise +
   conv float đầu + head 2 lớp cuối (outC=2, không đủ 4 để pack).

3. **Pointwise (1×1, groups=1, outC%4==0) lưu PACK4 theo output channel.**
   Value-match cho thấy `raw[oc_block*inC*4 + ic*4 + oc_inner] = W[oc_block*4+oc_inner, ic]`
   — tức 4 output-channel xen kẽ nhau theo từng input-channel. Đọc plain sẽ sai
   hoàn toàn (forward lệch ~0.5–1.9).

4. **Activation (feature-map) của layer pointwise INT8 CŨNG packed.** Ngay cả khi
   unpack weight đúng, forward vẫn lệch vì blob input/output đọc qua field
   `data@0x50` bị interleave channel theo pack4 → featuremap capture sai kênh.

## Nguyên nhân gốc rễ

ncnn tối ưu INT8/SIMD bằng cách "pack4" (đóng gói 4 phần tử theo chiều channel)
cho cả **weight** lẫn **blob trung gian**. Kiểu số vẫn là float32 sau dequant,
nhưng THỨ TỰ LƯU bị hoán vị. Layer depthwise và layer có outC<4 không pack nên
đọc plain vẫn đúng — dễ đánh lừa rằng "chỉ vài layer sai".

## Giải pháp

### Phương án A — im2col + lstsq (đã dùng, layout-agnostic, cho model DÙNG ĐƯỢC)
Vì output đã là float sau dequant, giải `Y=conv(X,W)+b` bằng least-squares từ
feature-map thật. **Bỏ qua hoàn toàn vấn đề layout** (cả weight lẫn activation
packed đều tự triệt tiêu vì lstsq fit trong cùng không gian đã đọc). Gotcha:
- Mask vị trí bão hoà ReLU6 (`0<y<6`) để chỉ giữ phương trình tuyến tính.
- Channel bão hoà nặng thiếu điểm interior → dùng NHIỀU ảnh (joint lstsq).
- Suy padding TỪ shape output (ncnn pad bất đối xứng, thêm ở dưới/phải).

Kết quả: model tra về **đúng quyết định live/spoof** như thiết bị (prob_live khớp
3–4 chữ số), sai số logit ~2–3% — KHÔNG bit-exact.

### Phương án B — direct read + unpack pack4 (bit-exact, phức tạp)
Đọc weight float thô + unpack:
- depthwise / outC<4 / conv float: plain `(outC, inC/g, kh, kw)`.
- pointwise outC%4==0: `raw.reshape(outC//4, inC, 4)` với
  `W[ob*4+oi, ic] = raw[ob, ic, oi]`.
- **Còn phải unpack activation blob tương ứng** mới verify per-layer được —
  đây là phần chưa giải trọn (finicky, mỗi channel-group một kiểu). Nếu chỉ cần
  WEIGHT đúng và tự chạy forward PyTorch sạch (không pack) thì về lý thuyết đủ,
  nhưng phải chắc chắn 100% layout mọi loại layer.

## Áp dụng lại (How to reuse)

- Gặp opcode conv lạ → đọc thử vùng weight, xem byte thứ 4 có ~0x3E/0x3F không:
  có → weight vẫn float32, chỉ khác layout/packing.
- **Depthwise đọc đúng nhưng pointwise sai** → nghi pack4 theo output channel.
- Cần model DÙNG ĐƯỢC nhanh cho mạng INT8 → dùng lstsq từ featuremap (layout-
  agnostic), chấp nhận ~vài % sai số; đủ đúng cho classifier nhị phân (liveness).
- Cần BIT-EXACT → phải reverse trọn layout pack4 cho cả weight và activation.

## Liên quan
- [[ncnn-blob-cstep-padding-breaks-flat-read]] — cstep padding (vấn đề khác).
- [[extract-exact-ncnn-weights-via-layer-descriptor-offset-formula]] — công thức offset (dùng chung).
- [[recover-cnn-weights-via-im2col-lstsq-from-captured-featuremaps]] — kỹ thuật lstsq.

## Cap nhat (2026-08-11): ket qua hybrid tot nhat dat duoc

- pack4 pointwise da crack: khop multi-image lstsq 3.9e-08 tren LIVE channels.
- NHUNG pack4 doc SAI weight o DEAD channel (channel std~0 moi anh) -> forward
  te hon lstsq khi channel do hoi kich hoat. => pack4 layout con subtle o boundary.
- **Hybrid tot nhat**: per-layer chon direct-read (14 depthwise, bit-exact) HOAC
  multi-image lstsq (29 pointwise) theo forward-error nho hon. Ket qua final:
  sai so logit trung binh ~2% (0.9-4.7%), DUNG quyet dinh live/spoof 6/6 anh.
- De BIT-EXACT hoan toan can: (a) giai not pack4 dead-channel HOAC (b) emulate
  day du INT8 (input scale + weight scale + requant) - rat sau, chua lam.
- Bai hoc: voi mang phan loai nhi phan (liveness), ~2% logit la du (quyet dinh
  luon dung); dung do thoi gian vo han cho bit-exact khi decision da chinh xac.
