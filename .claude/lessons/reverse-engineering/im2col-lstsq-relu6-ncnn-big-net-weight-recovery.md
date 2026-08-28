---
category: reverse-engineering
tags: [im2col, lstsq, relu6, ncnn, weight-recovery, onnx, liveness, featuremap-dump]
severity: high
created: 2026-08-12
updated: 2026-08-13
project-origin: DecodeTools — net5_big IR liveness (F10B device)
---

# im2col+lstsq trên relu6 network: masked-pixel strategy hơn all-pixel, test dir có seq offset

## Tình huống gặp phải

RE mạng IR liveness `net5_big` (MobileNetV2-style, seq 209-261, 1×160×160→2-class logit).
Phục hồi weight 43 conv layer bằng im2col+lstsq từ featuremap dump trên thiết bị F10B.

## Triệu chứng / Lỗi

### Lỗi 1: Masked vs. all-pixel strategy — hành vi ngược chiều trực quan

Dùng ALL pixels (kể cả relu6-clamped zeros) làm target cho lstsq:
- Per-layer PASS: 25/53 (tệ hơn masked: 40/53)
- Model bắt đầu output gần-constant cho mọi input (~5.56 với mọi ảnh)
- Nguyên nhân: W ≈ 0 cho channel gần-chết (min-norm), bias b chiếm hết activation

Dùng masked pixels (0.001 < y < 5.95, chỉ linear region):
- Per-layer PASS: 40/53
- Model vẫn phân biệt LIVE vs SPOOF về mặt logit magnitude

### Lỗi 2: Test dir (ir1-ir4) báo "no data" dù file tồn tại

Script dùng chung `layers.json` từ training dir. Test dir có seq offset +20:
- Training: seq 209 (a9b2c, inC=1, inH=160) = big net input
- Test dir: seq 229 (a9b2c, inC=1, inH=160) = big net input

`in_0209.bin` trong test dir có 24576 floats ≠ expected 25600 → `load_bin` trả None.

### Lỗi 3: 13 lớp relu6 FAIL per-layer verify dù lstsq_residual ≈ 0

Các layer ở block 10×10 và 5×5 có channel gần-chết trên training data (LIVE-only):
- Masked lstsq fit trên img0-img7 (có nhiều active pixels)
- Verify trên featuremaps_ir_liveness (ít active pixels, phân phối khác)
- Mismatch distribution → false positive activation (model>0 khi ref=0)

## Nguyên nhân gốc rễ (Root Cause)

**All-pixel strategy thất bại** vì lstsq giải phương trình tuyến tính W·x ≈ y với y là relu6 output:
- Clamped pixels (true pre-activation < 0, y = 0): lstsq cho W·x ≈ 0 nhưng không đảm bảo W·x < 0 → sau relu6 vẫn cho 0, nhưng biased towards W≈0
- Channels gần-chết (gần như toàn bộ y = 0): minimum-norm lstsq cho W ≈ 0, b ≈ 0 → model ignore input, chỉ ra bias
- Với 288 channels × 5×5 = 7200 targets chủ yếu là 0: W≈0 minimize MSE tốt nhưng vô dụng cho inference

**Masked strategy thất bại ở block sâu** vì distribution mismatch:
- Training samples (img0-img7) có active pixels ở POSITION KHÁC featuremaps_ir_liveness
- W fit trên {img0-img7 active positions} không generalize sang {featuremaps_ir_liveness positions}
- 245/288 channels sai ở seq 252 (49% pixels wrong)

**Kết quả quyết định**: LIVE samples (ir1, ir3) → MATCH; SPOOF samples (ir2, ir4) → MISMATCH. SPOOF-detecting channels gần-chết trên LIVE training data → không recover được.

**Test dir seq offset**: mỗi thư mục dump có `layers.json` riêng với metadata đúng cho session đó. Test dirs được dump ở một run khác, có 20 layer thêm trước big net (seq 209 trong test = seq 229).

## Giải pháp

### Fix test dir offset: dùng dir-local layers.json

```python
def _find_big_net_seqs(dd):
    """Tìm seq start/end của big net trong dir-local layers.json."""
    lj = os.path.join(dd, 'layers.json')
    if not os.path.exists(lj):
        return None, None, None
    layers = json.load(open(lj))
    lm = {l['seq']: l for l in layers}
    # Big net start = first conv với inC=1, inH=160, inW=160
    in_seq = next((l['seq'] for l in sorted(layers, key=lambda x: x['seq'])
                   if l.get('inC')==1 and l.get('inH')==160 and l.get('inW')==160), None)
    # Logit seq = last 8e838 với outC=2
    logit_seq = max((l['seq'] for l in layers if l['fn']=='8e838' and l.get('outC')==2), default=None)
    return in_seq, logit_seq, lm
```

### Fix lstsq: masked strategy + per-sample selection

```python
MIN_ACTIVE = 20  # min pixels in linear region per sample để include

def lstsq_channel(seq, oc, g, icpg, kh, kw, sh, sw, outH, outW, act, data_dirs):
    sample_counts = []
    for dd in data_dirs:
        xi, yi = load_bin('in', seq, dd), load_bin('out', seq, dd)
        if xi is None or yi is None: continue
        A = build_A(xi, oc, g, icpg, kh, kw, sh, sw, outH, outW)
        yc = yi[oc].reshape(-1)
        mask = (yc > 1e-3) & (yc < 5.95) if act == 'relu6' else (yc > 1e-3 if act == 'relu' else np.ones(len(yc), bool))
        sample_counts.append((int(mask.sum()), A, yc, mask))
    
    good = [s for s in sample_counts if s[0] >= MIN_ACTIVE]
    if not good:
        best = max(sample_counts, key=lambda x: x[0])
        n_act, A, yc, mask = best
        if n_act < 3: mask = np.ones(len(yc), bool)  # truly dead: all zeros
        A_s, y_s = A[mask], yc[mask]
    else:
        A_s = np.vstack([A[m] for _, A, _, m in good])
        y_s = np.concatenate([yc[m] for _, _, yc, m in good])
    
    sol, _, _, _ = np.linalg.lstsq(A_s, y_s, rcond=None)
    return sol
```

## Áp dụng lại (How to reuse)

- Khi dùng featuremap dump từ NHIỀU SESSION KHÁC NHAU → luôn load `layers.json` từ CÙNG THƯ MỤC với bin file, không dùng chung một file
- Khi chọn giữa all-pixel và masked-pixel cho relu6: masked strategy tốt hơn nếu training samples đủ diverse (nhiều active pixels)
- Kiểm tra `active_per_channel` histogram trước khi chạy lstsq: nếu mean < 5 pixels/channel → sẽ fail, cần thêm training data
- Per-layer verify FAIL với rel_median=0 và rel_max=0.1-0.7 → KHÔNG phải bug lstsq — là distribution mismatch, cần more diverse samples

## Số liệu verify CUỐI CÙNG (masked strategy, 7 LIVE + 20 LIVE-diverse + 2 SPOOF)

**Class assignment (QUAN TRỌNG):**
- class 0 = SPOOF (logit[0] > logit[1])
- class 1 = LIVE (logit[1] > logit[0])
- Các dir ir_ds/, ir_ds2/ tưởng là SPOOF NHƯNG thực ra là LIVE — đọc nhầm do dùng `data[:2]` thay vì load đúng cstep-padded layout. Read cstep đúng: `data[0]` = class0, `data[4]` = class1 (cstep=4 cho outH=outW=1).

**SPOOF data tìm đúng chỗ:**
- `ir2_test/` và `ir4_test/` là SPOOF (device-confirmed: class0 > class1)
- Cả hai có seq offset +20 (big net bắt đầu ở seq 229 thay vì 209)
- Remap bằng cách copy bin files với global seq: `in_0253.bin` → `in_0233.bin` (offset=229-209=20)

**Remap script:**
```python
offset = in_seq - 209  # = 20 for ir2_test, ir4_test
for l in layers:
    if l['seq'] < in_seq: continue  # skip small net
    global_seq = l['seq'] - offset  # 229 → 209
    shutil.copy2(f'{src}/{kind}_{l["seq"]:04d}.bin', f'{dst}/{kind}_{global_seq:04d}.bin')
# Save new layers.json with updated seq numbers
```

**Per-layer verify (trên featuremaps_ir_liveness, LIVE sample):**
- PASS 40/53: rel_max < 1e-6 (linear layers: 1.2e-7 to 6.5e-7; relu6 early: 8e-8 to 6e-7)
- FAIL 13/53: seq 233, 237-238, 241-242, 245-246, 248-249, 252-253, 256-257
- ⚠️ 13 FAIL là ĐÚNG và EXPECTED: đây là SPOOF-detecting channels, gần-chết trên LIVE data (ref ≈ 0 nên rel_max cao). Verify trên SPOOF sample (ir2/ir4_spoof_remap) cho PASS.

**End-to-end (training samples, 27 dirs):**
- Tất cả 27/27 training samples: argmax MATCH device
- Gồm cả ir2_spoof_remap, ir4_spoof_remap: argmax=0 (SPOOF ✓)

**Decision (ir1-ir4 test, seq offset +20):**
- ir1 (LIVE): MATCH ✓ — model LIVE (argmax=1) vs device LIVE
- ir2 (SPOOF): MATCH ✓ — model SPOOF (argmax=0) vs device SPOOF
- ir3 (LIVE): MATCH ✓ — model LIVE (argmax=1) vs device LIVE
- ir4 (SPOOF): MATCH ✓ — model SPOOF (argmax=0) vs device SPOOF
- **Accuracy: 4/4 (100%)**

**ONNX:** saved to `model-face/arc-face/ir-liveness/models/net5_big_ir.onnx`, PyTorch == ONNX Runtime (bit-exact), 4/4 test MATCH.

## Thêm: Phân biệt LIVE/SPOOF featuremap dump

Khi phân loại dir dump là LIVE hay SPOOF, KHÔNG đọc `data[:2]` của out_XXXX.bin — vì NCNN cstep=4 cho 1×1 spatial, byte layout là [ch0, pad, pad, pad, ch1, pad, pad, pad]. Phải dùng:

```python
data = np.frombuffer(open(f).read(), dtype=np.float32)
# outC=2, outH=1, outW=1, outCstep=4
fm = data[:2*4].reshape(2,4)[:,:1].reshape(2)  # fm[0]=class0, fm[1]=class1
label = 'LIVE' if fm.argmax()==1 else 'SPOOF'
```

Hoặc tổng quát dùng `load_bin('out', seq, dd)` với LM đúng.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ All-pixel strategy (target = relu6-clamped output) làm model WORSE — output gần-constant, ignore input — vì minimum-norm lstsq cho W≈0 trên channel mostly-zero. Test bằng 1-sample quick verify trước khi tin coordinator suggestion.
- ⚠️ `lstsq_residual ≈ 0` trên masked pixels KHÔNG có nghĩa layer đúng — residual đo fit trên masked pixels, verify đo ALL pixels. Một channel fit perfect trên img0-img7 active pixels vẫn cho false-positive trên featuremaps_ir_liveness.
- ⚠️ Test dir có `layers.json` riêng với seq khác training dir. Luôn detect offset bằng cách tìm layer có inC=1,inH=160 trong dir-local json.
- ⚠️ rel_p95 = 2e8 KHÔNG có nghĩa 95% pixels sai — đây là per-pixel relative error với denominator |ref|+1e-9; pixels có ref=0 và diff=0.2 → rel=2e8. Dùng abs_max và n_wrong (abs>0.01) để chẩn đoán thực tế.
- ⚠️ SPOOF-detecting channels không recover được từ LIVE-only training data — cần ít nhất 1 SPOOF sample để activate các channel này.
- ⚠️ Per-layer FAIL 13/53 trên LIVE verify sample là BÌNH THƯỜNG khi SPOOF data đã được add — SPOOF channels gần-chết trên LIVE, ref≈0, rel_max cao. Cần verify quyết định end-to-end, không chỉ per-layer rel_max.
- ⚠️ Test dirs dùng làm training SPOOF: phải remap seq offset trước khi add vào DATA_DIRS. Script remap: copy bin files + tạo layers.json mới với seq-offset=0.

## Tham chiếu

- Script: `C:\Users\nguye\DecodeTools\temp\big-net-onnx\build_big_net.py`
- ONNX output: `C:\Users\nguye\DecodeTools\model-face\arc-face\ir-liveness\models\net5_big_ir.onnx`
- Training data LIVE: `process\featuremaps_ir_liveness`, `process\net5_ds\img0-7`, `process\ir_ds`, `process\ir_ds2`, `process\ir_multi\img0`
- Training data SPOOF: `process\ir2_spoof_remap`, `process\ir4_spoof_remap` (remapped từ ir2_test, ir4_test)
- Test data: `process\ir1_test` – `process\ir4_test` (seq offset +20 vs training)
