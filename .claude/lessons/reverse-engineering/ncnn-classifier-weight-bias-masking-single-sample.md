---
category: reverse-engineering
tags: [ncnn, weight-extraction, bias, classifier, lstsq, featuremap, frida]
severity: critical
created: 2026-08-13
updated: 2026-08-13
project-origin: DecodeTools (big net IR liveness net5_big_ir)
---

# NCNN classifier weight sai mà rel=0 trên LIVE: bias estimation che giấu hoàn toàn lỗi weight

## Tình huống gặp phải

> Đang RE (reverse engineer) big net IR-liveness của ArcSoft, 43 conv layers. Layer cuối (seq260): outC=2, inC=320, kernel 1x1 — là classifier LIVE/SPOOF. Weight đọc từ pool memory (Frida) theo plain format (vì outC=2 không chia hết cho 4, không dùng pack4). Bias estimate từ LIVE featuremap. Kiểm tra trên LIVE sample cho rel=0. Tưởng đúng.

## Triệu chứng / Lỗi

```
E2E verification:
  featuremaps_ir_liveness [LIVE]: model=[-10.4, 10.4] ref=[-10.4, 10.4]  MATCH  ← rel=0 LIVE
  ir1_test [LIVE]: MATCH
  ir2_test [SPOOF]: model=[-9.38, 9.96] ref=[4.64, -4.64]  MISMATCH  ← sai hoàn toàn
  ir4_test [SPOOF]: model=[-9.11, 9.77] ref=[9.58, -9.58]  MISMATCH

Decision accuracy: 3/5 (LIVE correct, SPOOF always misclassified as LIVE)
```

Kiểm tra trực tiếp: apply model W260 lên device GAP (seq259 out) của SPOOF sample:
```
LIVE_main:   model=[-10.4, 10.4] device=[-10.4, 10.4]  rel=0.000  ← perfect
SPOOF_rem2:  model=[-9.38, 9.96] device=[4.64, -4.64]  rel=3.146  ← sai hoàn toàn
SPOOF_rem4:  model=[-9.10, 9.77] device=[9.58, -9.58]  rel=2.019  ← sai hoàn toàn
```

## Nguyên nhân gốc rễ (Root Cause)

**Bias estimation từ 1 sample LIVE luôn cho rel=0 bất kể weight đúng hay sai:**

```python
# Bias estimation trong fix_biases.py (linear layer):
bias_est = (outFM - conv_no_bias).mean(axis=(1,2))
# = outFM[c,0,0] - (W_wrong[c,:] @ gap_live)  cho seq260 (1x1)
```

Khi dùng bias_est này để predict trên cùng LIVE sample:
```
W_wrong @ gap_live + bias_est
= W_wrong @ gap_live + (outFM_live - W_wrong @ gap_live)
= outFM_live  ← luôn bằng nhau, rel=0 BY CONSTRUCTION
```

→ Bias hấp thụ TOÀN BỘ sai số của weight cho sample đó. rel=0 trên LIVE không chứng minh W đúng.

Khi predict trên SPOOF:
```
W_wrong @ gap_spoof + bias_est
= W_wrong @ gap_spoof + (outFM_live - W_wrong @ gap_live)
= outFM_live + W_wrong @ (gap_spoof - gap_live)  ← phụ thuộc vào W_wrong!
```

Nếu W_wrong không cùng hướng với W_true, phép chiếu lên (gap_spoof - gap_live) cho kết quả sai.

**Nguyên nhân thực sự của W260 sai:** pool offset f8 cho seq260 có thể trỏ sai vị trí trong PW pool, hoặc weight format đọc sai (không thể verify vì LIVE bias always absorbs error).

## Giải pháp

### 1. Phát hiện lỗi weight: test trực tiếp với device GAP của class KHÁC

```python
# Đọc device GAP (seq259 out) từ featuremaps của SPOOF sample
gap_spoof = load_fm('out', 259, 'ir2_spoof_remap', lm)  # device ground truth
logit_dev_spoof = load_fm('out', 260, 'ir2_spoof_remap', lm)

# Apply model W260
logit_model = W260 @ gap_spoof.reshape(320) + b260

# Nếu kết quả sai → W260 WRONG
print(f'device: {logit_dev_spoof}  model: {logit_model}')
```

Dấu hiệu chắc chắn: residual_std qua nhiều sample rất cao (>5) → W sai.

### 2. Thu hồi W260 đúng: lstsq từ nhiều (GAP, logit) pairs

```python
import glob, json, numpy as np

def collect_pairs(process_dir):
    pairs = []
    for dd in glob.glob(process_dir + '/**/out_0260.bin', recursive=True):
        dd = os.path.dirname(dd)
        lm = load_layers_json(dd)
        gap_seq, logit_seq = find_final_classifier(lm)  # tìm GAP và logit seqs
        gap = load_fm('out', gap_seq, dd, lm)
        logit = load_fm('out', logit_seq, dd, lm)
        if gap is not None and logit is not None:
            pairs.append((gap.reshape(-1), logit.reshape(-1)))
    return pairs

pairs = collect_pairs(process_dir)  # thu thập từ TẤT CẢ dirs có out_0260.bin
X = np.array([g for g, _ in pairs])  # (N, 320)
Y = np.array([v for _, v in pairs])  # (N, 2)
Xa = np.hstack([X, np.ones((len(X), 1))])  # bias aug

sol, _, _, _ = np.linalg.lstsq(Xa, Y, rcond=None)
W_est = sol[:320].T.astype(np.float32)   # (2, 320)
b_est = sol[320].astype(np.float32)      # (2,)
```

**Điều kiện để lstsq cho kết quả đủ tốt:**
- Cần ít nhất rank(X) ≈ 27-30 (số hướng độc lập trong không gian GAP)
- Cần có sample cả LIVE và SPOOF để cover đủ classifier boundary
- Với 36 pairs (30 LIVE + 6 SPOOF), rank=27 → 5/5 test accuracy

## Áp dụng lại (How to reuse)

- Khi verify layer cuối (linear, outC nhỏ) → KHÔNG tin rel=0 trên LIVE đơn thuần
- Luôn test với class KHÁC (SPOOF) để kiểm tra W có đúng hướng không
- Công thức chuẩn: `residual_std` qua nhiều sample — nếu > 2 → W sai
- Khi W sai mà không có Frida access → dùng lstsq trên tất cả featuremap dirs

**Kiểm tra nhanh W đúng/sai (không cần Frida):**
```python
# Thu thập residuals từ nhiều sample
residuals = [logit_dev_i - W260 @ gap_dev_i for i in all_samples]
std = np.array(residuals).std(axis=0)
# Nếu std < 0.1 → W đúng (bias chỉ là constant offset)
# Nếu std > 2   → W sai (bias không thể compensate cho W sai trên inputs khác nhau)
```

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ rel=0 trên LIVE sample SAU KHI estimate bias LUÔN xảy ra by construction — không phải bằng chứng W đúng
- ⚠️ NCNN layer với outC<4 dùng plain format (không pack4) — nhưng bias estimation vẫn có thể che sai số
- ⚠️ lstsq recovery cần cả LIVE lẫn SPOOF featuremap dirs — chỉ LIVE thì không đủ để chọn hướng classifier
- ⚠️ rank(X) < outC (320 ở đây) → solution là min-norm, không phải unique W_true; đủ để classify đúng training set nhưng chưa chắc generalize hoàn hảo với samples ngoài training set
- ⚠️ outCstep=4 tại 1x1 spatial = pack1 với 3 padding floats/channel, KHÔNG phải pack4. load_fm vẫn đúng: `a[:C*cs].reshape(C,cs)[:,:1]` lấy đúng float đầu mỗi slot 4.

## Tham chiếu

- Project: DecodeTools → `model-face/arc-face/ir-liveness/models/net5_big_ir.onnx`
- Scripts: `temp/big-net-onnx/rebuild_v3.py` (lstsq W260 recovery)
- NPZ: `device-f10b-scripts/big_net_bitexact_v3.npz`
- Lesson liên quan: `ncnn-blob-cstep-padding-breaks-flat-read.md` (outCstep issue tại 5x5)
- Lesson liên quan: `recover-cnn-weights-via-im2col-lstsq-from-captured-featuremaps.md`
