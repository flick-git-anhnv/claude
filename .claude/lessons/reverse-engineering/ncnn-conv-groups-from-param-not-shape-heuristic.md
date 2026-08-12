---
category: reverse-engineering
tags: [ncnn, conv, groups, depthwise, param, arcsoft, landmark]
severity: high
created: 2026-08-11
updated: 2026-08-11
project-origin: DecodeTools (ArcSoft net1 landmark model)
---

# groups của conv phải ĐỌC từ param[12], KHÔNG suy từ heuristic shape (inC==outC)

## Tình huống gặp phải

Dựng lại mạng landmark 5 điểm (net1) của ArcSoft. Dùng heuristic quen thuộc để
đoán conv là depthwise: `groups = inC if (inC==outC and kh>1) else 1`.

## Triệu chứng / Lỗi

- Mọi conv verify riêng lẻ (input thật) đều PASS, nhưng model composed sai hoàn
  toàn (rel 1.3-1.6).
- Trace forward: diverge bắt đầu ở 1 conv `16→16 k3` — layer này bị đoán NHẦM là
  depthwise (groups=16) trong khi thực tế là REGULAR conv (groups=1).
- Với groups sai, số weight đọc sai: depthwise 16×1×3×3=144, regular 16×16×3×3=2304
  → đọc thiếu/sai vùng weight.

## Nguyên nhân gốc rễ

Heuristic "inC==outC và kh>1 ⇒ depthwise" SAI khi mạng có regular conv giữ nguyên
số kênh (16→16, 32→32...). Depthwise thật được đánh dấu bằng **trường group trong
param của layer**, không phải suy từ shape.

Với ncnn Convolution param array (đọc qua layer descriptor), **params[12] = group
count**:
- Regular conv: `params[12] == 1`
- Depthwise:   `params[12] == inC (== outC)`

Ví dụ thật (net1):
```
seq58 in16 out16 k3 s2: params[12]=1   -> REGULAR (heuristic đoán nhầm depthwise)
seq60 in24 out24 k3 s1: params[12]=24  -> depthwise
seq65 in32 out32 k3 s2: params[12]=32  -> depthwise
```

## Giải pháp

```python
p = layer['params']
g = p[12]
groups = g if g > 1 else 1     # đọc thẳng, KHÔNG suy từ inC==outC
wcount = (inC // groups) * outC * kh * kw
```

Sau khi sửa: net1 landmark model **bit-exact rel=2.2e-07** (10 giá trị = 5 điểm
mắt/mũi/miệng).

## Áp dụng lại (How to reuse)

- Khi dựng lại conv từ ncnn: LUÔN đọc groups từ `params[12]`, đừng đoán từ shape.
- Dấu hiệu bug groups: **mọi layer PASS riêng lẻ (input thật) nhưng composed sai**
  → 1 layer có groups/số-weight sai làm lệch toàn bộ chuỗi.
- Layer `CxC k3` (giữ nguyên kênh) có thể là regular HOẶC depthwise — chỉ param
  mới phân biệt được.
- Model 3/4 trước đó heuristic tình cờ đúng vì không có regular conv giữ-nguyên-kênh;
  net1 lộ ra bug này.

## Liên quan
- [[extract-exact-ncnn-weights-via-layer-descriptor-offset-formula]]
- [[arcsoft-model-naming-and-app-usage-map]] — net1 là mạng landmark trong detection engine
