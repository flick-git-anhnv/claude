---
category: reverse-engineering
tags: [ncnn, conv, padding, groups, winograd, prelu, im2col, lstsq, arcsoft]
severity: high
created: 2026-08-11
updated: 2026-08-11
project-origin: DecodeTools (ArcSoft IR-Liveness net5, seq187-208)
---

# ncnn conv: padding ĐỐI XỨNG + groups đọc từ param[12] + Winograd→lstsq + PReLU fused

## Tình huống
Dựng lại net5 (mạng anti-spoof IR live, 1×128×128→2) của ArcSoft. Weight đọc thô
(offset formula) SAI (pos_err 3.3) dù cùng run → weight ở layout Winograd. Chuyển
sang im2col+lstsq từ featuremap thì vẫn lệch cao (residual 0.74-1.26) ngay trên
vùng đã fit — bất thường cho hệ over-determined.

## 4 gotcha gốc rễ (tìm ra tuần tự)

### 1. Weight Winograd → KHÔNG đọc thô được, phải im2col+lstsq
Conv nhỏ (net anti-spoof) lưu weight ở layout Winograd-transformed. Offset
formula (đúng cho GEMM `mf_ArcN_Conv_Full_Neon_FL` ở model4) trả weight biến đổi
→ conv sai cả ở giá trị dương. Dùng im2col+lstsq từ input/output feature-map thật.

### 2. Padding ĐỐI XỨNG (ph,pw cả 2 phía), KHÔNG bất đối xứng
Layer stride-2 (128→64, k3): pad phải là **symmetric (1,1)** — pad 1 cả trên/dưới
trái/phải. Trước đó suy pad từ shape rồi chia `ph//2, ph-ph//2` = (0,1) bất đối
xứng → **maxrel 1.27**; đổi sang symmetric (1,1) → **maxrel 0.0000**.
Đọc pad TRỰC TIẾP từ `params[21]=pad_h, params[20]=pad_w`, đừng suy từ shape.

### 3. Groups đọc từ `params[12]`, KHÔNG đoán theo (inC==outC)
Heuristic "inC==outC & k>1 → depthwise" SAI: net5 có conv 8→8 k3 nhưng là
**FULL conv (g=1)**, không phải depthwise. `params[12]` = số group thật
(1=full, =inC=depthwise). Đoán nhầm g=8 → maxrel 0.84; dùng g=params[12]=1 →
**maxrel 2e-07**.

### 4. PReLU FUSED trong conv (slope ~0.3), không phải layer riêng
Conv output (captured) đã qua PReLU. Recover W bằng lstsq trên **vùng y>0**
(PReLU=identity) để sạch, rồi đo slope vùng âm: `slope=median(y[pre<0]/pre[pre<0])`.
net5: một số conv slope=0.3 (PReLU), số khác slope=1.0 (linear/không activation).

## Kết quả
8/9 conv net5 recover **maxrel=0.0000** sau khi áp cả 4 fix. So với các model
trước (model3/4 dùng GEMM đọc thô được, depthwise thật, ReLU6) — net anti-spoof
này khác hoàn toàn về mọi mặt.

## Áp dụng lại
- Conv nhỏ đọc thô sai → nghi Winograd → im2col+lstsq.
- LUÔN đọc pad từ params[20/21] và pad ĐỐI XỨNG; groups từ params[12].
- lstsq residual cao trên chính vùng fit (over-determined) → SAI groups hoặc
  padding hoặc input-pairing, KHÔNG phải thiếu data.
- Recover conv có PReLU: fit vùng dương, đo slope vùng âm riêng.

## Liên quan
- [[recover-cnn-weights-via-im2col-lstsq-from-captured-featuremaps]]
- [[ncnn-int8-pack4-weight-activation-layout]] — net6(160) khác: INT8 pack4.
- [[arcsoft-model-naming-and-app-usage-map]] — app live dùng net3/4/5, KHÔNG net6(160).

## Cap nhat: net5 HOAN TAT bit-exact + la mang quyet dinh liveness live

- Them 2 gotcha activation:
  - PReLU FUSE THEO TUNG CONV: conv "expansion" (188,190,194,198,202) fuse PReLU
    (cap=prelu(conv)); conv "projection" (191,195,199,203) luu RAW (cap=conv).
    Phan loai bang so rel(raw) vs rel(prelu(raw)) voi output that.
  - concat (84cf0) = cat(PReLU(a), PReLU(b)) - prelu TRUOC khi ghep.
    sum (e5c14) = PReLU(a + b) - prelu SAU khi cong. FC (ec1f0) PReLU 0.3 (tru layer cuoi).
- Ket qua: net5 standalone rel=0.0000 tren 7 anh, ONNX rel=2.3e-07.
- QUAN TRONG: net5 (1x128x128->2) moi la mang QUYET DINH getIrLiveness khi app
  chay CAMERA LIVE (net6 1x160x160 chi chay khi goi processIr offline full-frame).
  Phat hien nay CHI lo ra khi hook luong camera that (test offline khong thay).
- class0=LIVE, class1=SPOOF (NGUOC voi net6). Xac minh: net5 phan biet real/fake
  17/17 tren dataset co nhan.
- Bai hoc lon: PHAI hook luong live moi biet mang nao thuc su chay; dung tin
  ket qua tu loi goi API offline cua chinh minh.
