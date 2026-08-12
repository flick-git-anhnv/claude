---
category: reverse-engineering
tags: [ncnn, frida, blob, cstep, memory-layout, arcsoft, featuremap]
severity: critical
created: 2026-08-11
updated: 2026-08-11
project-origin: DecodeTools (ArcSoft libarcsoft_face.so — dựng lại model nhận diện)
---

# Blob ncnn pad theo cstep — đọc phẳng C*H*W là sai khi H*W không chia hết cho 4

## Tình huống gặp phải

Dump feature-map từng layer của `libarcsoft_face.so` (engine kiểu ncnn) qua Frida
để dựng lại mạng nhận diện khuôn mặt. Hook đọc blob theo mô tả struct:
`c@0x30, h@0x34, w@0x38, data@0x50`, rồi đọc liền `c*h*w` float.

## Triệu chứng / Lỗi

Hai biểu hiện, cùng một gốc, xuất hiện cách nhau khá xa nên rất dễ chẩn đoán sai:

```
1) Verify conv: 65/100 layer khớp corr=1.0, nhưng TẤT CẢ layer từ một mốc
   trở đi (khi spatial còn 7x6) corr ~= 0.00x — trong khi weight/offset đã
   xác nhận đúng (gap offset khớp chính xác wcount+bias).

2) Feature 256-d đọc về: phần tử [0] đúng, các phần tử sau lệch hẳn.
   feat_doc  = [-0.197, 2.864, 2.355, 3.479, -0.690, ...]
   feat_that = [-0.197, -0.690, -0.676, -0.533,  0.191, ...]
   -> feat_doc[4] == feat_that[1]  => bước nhảy 4.
```

## Nguyên nhân gốc rễ

ncnn cấp phát Mat theo **cstep** đã align, không phải `h*w` liền mạch:

```
cstep = alignUp(h * w, 4)      // với float32 / packing 4
tổng số float = c * cstep      // KHÔNG phải c * h * w
```

Mỗi channel có padding ở cuối. Khi `h*w` chia hết cho 4 (56×48=2688, 28×24=672,
14×12=168) thì `cstep == h*w` nên đọc phẳng **tình cờ đúng** — đó là lý do 65
layer đầu khớp hoàn hảo và ta tin rằng cách đọc đúng. Chỉ khi `h*w` không chia
hết cho 4 mới lệch:

| shape | h*w | cstep | lệch? |
|---|---|---|---|
| 56×48 | 2688 | 2688 | không |
| 14×12 | 168 | 168 | không |
| 7×6 | 42 | **44** | **có** |
| 1×1 (vector 256/512-d) | 1 | **4** | **có** — lệch nặng nhất |

Trường hợp `1×1` là bẫy tệ nhất: mọi tensor vector (embedding, output FC,
output global-pool, SE gate) đều có `cstep=4`, tức 3/4 dữ liệu đọc về là padding.

## Giải pháp

Đọc `c * cstep` float rồi cắt bỏ padding từng channel:

```python
def load_blob(path, C, H, W):
    cstep = -(-(H * W) // 4) * 4          # alignUp(H*W, 4)
    a = np.frombuffer(open(path, 'rb').read(), dtype=np.float32)
    assert a.size >= C * cstep
    return np.ascontiguousarray(
        a[:C * cstep].reshape(C, cstep)[:, :H * W]
    ).reshape(C, H, W)
```

Phía hook Frida phải đọc đúng số byte ngay từ đầu:

```js
const cstep = Math.ceil((h * w) / 4) * 4;
const n = c * cstep;                       // KHÔNG dùng c*h*w
const bytes = dp.readByteArray(n * 4);
```

Với vector 1×1 (feature/embedding), lấy phần tử đầu mỗi channel:

```python
feat = raw[:C * cstep].reshape(C, cstep)[:, 0]     # cstep = 4
```

Kết quả sau khi sửa: 100/100 layer conv corr=1.0, embedding 256-d
`cosine = 1.00000000` so với thiết bị.

## Áp dụng lại (How to reuse)

- Khi dump blob của **bất kỳ** engine kiểu ncnn: luôn tính `cstep = alignUp(h*w, 4)`
  ngay từ hook, đừng bao giờ giả định layout phẳng.
- Dấu hiệu nhận biết đặc trưng: **layer đầu khớp hoàn hảo, layer sâu (spatial nhỏ)
  sai hoàn toàn** trong khi weight/offset đã kiểm chứng đúng → nghi cstep trước
  khi nghi weight, layout weight, hay wiring.
- Dấu hiệu thứ hai: mảng đọc về có phần tử đúng ở vị trí `i*k` (k=4) → đang đọc
  qua vùng padding, chia lại theo `reshape(C, cstep)`.
- Chọn ảnh test có spatial size **không** chia hết cho 4 để bug lộ sớm, thay vì
  chỉ test ở tầng đầu.
- Đừng đổ lỗi cho weight khi khoảng cách offset giữa 2 layer liên tiếp đã khớp
  đúng `wcount + outC` — khi đó weight chắc chắn đúng, lỗi nằm ở phía đọc tensor.

## Liên quan

- [[extract-exact-ncnn-weights-via-layer-descriptor-offset-formula]] — công thức
  lấy con trỏ weight thật.
- [[extract-real-weights-via-pool-allocator-pointer-arithmetic]] — `poolBase`
  phải đọc theo **từng** `param_1` (mỗi engine instance có pool riêng).
- [[deep-network-reconstruction-needs-skip-connection-plus-clamp]]
