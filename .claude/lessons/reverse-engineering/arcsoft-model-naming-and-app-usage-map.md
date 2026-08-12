---
category: reverse-engineering
tags: [arcsoft, faceengine, model-mapping, smali, process-mask, license]
severity: high
created: 2026-08-11
updated: 2026-08-11
project-origin: DecodeTools (ArcSoft ilocker app)
---

# ArcSoft: 5 mạng CNN trong .so + luồng app nào gọi model nào (đừng grep tên hằng)

## Tình huống gặp phải

Cần xác định "4 model" trong `libarcsoft_face.so` là gì, và model nào verify được
qua app `com.example.ilocker`. Suýt kết luận SAI vì (a) nhầm tên model, (b) grep
tên hằng số thay vì giá trị hex.

## Phát hiện chính

### 1. Bản đồ tên model THẬT (từ `reconstructed_models_123/` của session trước)
- **Model 1** = Age + Gender + Liveness (RGB) — thuộc tính khuôn mặt.
- **Model 2** = **Mask (khẩu trang)** — KHÔNG phải IR-Liveness (dễ nhầm).
- **Model 3** = Recognition (feature extract 256-d).
- **Model 4** = Detection.
- **NGOÀI RA còn 1 mạng thứ 5**: IR-Liveness (chống giả mạo bằng camera hồng
  ngoại) — mạng riêng, chạy qua `processIr()`.

### 2. App có 4 FaceEngine instance riêng, mỗi cái init mask khác nhau
Trong `InitEngine.smali` (`com.example.ilocker.engine_face.InitEngine`):
- `initRGBEngine` → `FaceUtil.faceDetectEngine`, mask `0x1201`
  (DETECT|IMAGEQUALITY|MASK_DETECT).
- `initExtractEngine` → `FaceUtil.faceExtractEngine`, mask `0x4` (RECOGNITION).
- `initIREngine` → `FaceUtil.faceLiveNessEngine`, mask `0x401` (DETECT|IR_LIVENESS).
- `initEngineOffline` — chỉ copy/validate license `ArcFacePro32.dat`, KHÔNG init engine.

Gọi API trên SAI engine → lỗi license 86018/86019/86020 (không phải bug code).
`extractFaceFeature` phải gọi trên `faceExtractEngine`, KHÔNG phải `faceDetectEngine`.

### 3. Đừng grep TÊN hằng — app dùng giá trị HEX thô
Grep `"ASF_AGE"`/`"getAge"` ra 0 kết quả → suýt kết luận "app không dùng age".
Nhưng app truyền mask `process(..., 0x1008)` = `MASK_DETECT|AGE(0x8)` bằng hex
literal. Phải giải mã hex, không grep tên. Hằng số (từ `FaceEngine.smali`):
`DETECT=0x1, RECOGNITION=0x4, AGE=0x8, GENDER=0x10, LIVENESS=0x80,
IMAGEQUALITY=0x200, IR_LIVENESS=0x400, MASK_DETECT=0x1000`.

### 4. Model nào VERIFY được qua app này (kiểm bằng smali thật)
- Detection (M4), Recognition (M3): ✅ dùng khắp nơi.
- Mask (M2): ✅ `process(mask=0x1000)` + `getMask()` khắp nơi (FaceIdentity,
  NewFace, LoginAdmin, PreRegister...).
- IR-Liveness: ✅ `processIr(mask=0x400)` + `getIrLiveness()` — nhưng dùng
  format `0x802`(=CP_PAF_NV21) trên buffer camera IR, KHÔNG cần camera IR thật
  để chạy pass (ảnh RGB thường vẫn cho `ret=0`, chỉ ra spoof).
- Age/Gender/RGB-Liveness (M1): app truyền cờ `0x8` vào process nhưng **KHÔNG
  engine nào init với AGE/GENDER/LIVENESS**, và **KHÔNG có getAge/getGender/
  getLiveness(RGB)** trong toàn app → không lấy được ground-truth ⇒ không verify
  được qua app này (dù mạng có tồn tại trong .so).

## Áp dụng lại (How to reuse)

- Trước khi kết luận "app không dùng feature X" → grep CẢ tên hằng LẪN giá trị
  hex của X trong tham số `process`/`processIr`/`init`.
- Mỗi feature ArcSoft cần: (1) engine init đúng mask, (2) đúng API `process` vs
  `processIr`, (3) đúng getter. Thiếu bất kỳ cái nào → 86018/86019/86020.
- Muốn biết model verify được không: tìm nơi app ĐỌC KẾT QUẢ (getMask/getIrLiveness/
  extractFaceFeature), không chỉ nơi gọi process.

## Liên quan
- [[android-native-sdk-self-validates-despite-app-level-check-missing]]
- [[ncnn-int8-pack4-weight-activation-layout]]
