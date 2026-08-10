---
name: deep-network-reconstruction-needs-skip-connection-plus-clamp
description: Dung lai mang CNN sau (nhieu tang) tu weight that khi khong biet chinh xac ranh gioi tung layer - can residual connection + clamp moi block de tranh no so, khac voi mang nong chi can khop tong tham so
metadata:
  type: reverse-engineering
---

# Mang CNN CANG SAU thi khop TONG THAM SO thoi CHUA DU — can residual + clamp moi block

## Boi canh

Sau khi dung lai thanh cong `model_4_detection.bin` (mang nong, 2-3 tang backbone + 5
head) chi bang cach khop dung TONG SO THAM SO that (xem
[[onnx-nan-fix-via-real-param-count-matching]]), ap dung Y HET phuong phap do cho
`model_1_liveness_age_gender.bin` va `model_2_mask_liveness_ir.bin` (mang SAU hon,
suy tu quet BatchNorm running_var: ~23 lan xuat hien width~128 lien tiep -> dac trung
mang co NHIEU block cung do rong, kieu ResNet) — dung kien truc MobileNet-style TUAN
TU PHANG (khong skip connection), khop 98.8-98.9% tong tham so — nhung output NO SO
(gia tri ~1e34, hoac Inf that su).

## Nguyen nhan goc re

- Voi mang NONG (2-3 tang), khop tong tham so gan dung la du: sai lech nho o 1-2 layer
  khong du "khong gian" (do sau) de nhan don thanh gia tri khong kiem soat duoc.
- Voi mang SAU (6+ tang BatchNorm noi tiep KHONG co skip connection), MOI tang nhan
  (multiply) qua gamma/conv-weight cua tang do. Neu 1 tang bat ky bi gan sai vi tri
  byte that (chac chan xay ra it nhat 1 lan khi khong biet ranh gioi chinh xac tung
  layer), sai so do se **nhan don qua tat ca cac tang con lai phia sau**, khien gia
  tri phinh to theo cap so nhan (exponential blow-up theo do sau mang).
- Doi sang kien truc CO RESIDUAL/SKIP CONNECTION (kieu ResNet BasicBlock,
  `out = relu(x + f(x))`) giam duoc phan nao (vi it nhat nhanh identity giu duoc gia
  tri goc), NHUNG KHONG DU: neu nhanh `f(x)` (nhanh Conv+BN chinh) tu no da sinh gia
  tri lon do sai lech shape, phep CONG (khong phai nhan) van co the TICH LUY (drift)
  qua nhieu block lien tiep (12+ block) va van dan den NaN/Inf khi cac phep toan sau
  do (vd AdaptiveAvgPool tren Inf duong + Inf am) tao ra `NaN`.

## Giai phap (da verify: healthy tren ca 2 mang sau)

Ket hop 2 ky thuat, khong dung 1 minh:

1. **Doi kien truc tuan tu phang -> ResNet BasicBlock co skip connection** — day la
   buoc CAN THIET (giam đa so truong hop no so do nhan don) nhung chua du.
2. **Them `torch.clamp(x, -30, 30)` sau MOI block** (ca BasicBlock lan DownBlock, va
   ngay sau lop stem dau tien) — chan cung moi gia tri trung gian, dam bao KHONG co
   activation nao vuot nguong truoc khi di vao block tiep theo. Day la buoc QUYET
   DINH giai quyet hoan toan NaN/Inf, khong chi giam bot.
3. **Them 1 lop `InstanceNorm2d(affine=False)` ngay truoc pooling/head cuoi cung** —
   InstanceNorm tu tinh mean/std tren CHINH activation hien tai (khac BatchNorm eval
   mode dung running_mean/var co san = mac dinh 0/1, KHONG phan anh thuc te da bi
   troi), nen luon "don dep" duoc bat ky do lech nao con sot lai truoc khi vao head
   phan loai/embedding cuoi cung.

Ca 3 buoc deu CHI la bien phap on dinh so hoc THEM VAO, khong phai mot phan kien truc
that cua ArcSoft — phai ghi ro trong code/tai lieu de nguoi dung khong hieu nham day
la "kien truc goc", ma la "kien truc + safety-net de dung duoc voi weight that khi
chua co ground-truth ranh gioi layer chinh xac".

## Ket qua

| Model | Kien truc | Tong tham so khop | % weight that nap | Ket qua |
|---|---|---|---|---|
| model_3 (recognition) | Backbone phang, 3 tang | 97.6% | 97.6% | HEALTHY (khong can clamp/skip) |
| model_4 (detection) | Backbone phang, 2-3 tang + 5 head | 99.97% | 100% | HEALTHY (khong can clamp/skip) |
| model_1 (liveness/age/gender) | ResNet BasicBlock, 14 block + clamp + InstanceNorm | 99.98% | 100% | HEALTHY (CAN ca 3 ky thuat) |
| model_2 (mask/liveness) | ResNet BasicBlock, 20 block + clamp + InstanceNorm | 99.83% | 97.4% | HEALTHY (CAN ca 3 ky thuat) |

## Ap dung lai (How to reuse)

- Truoc khi dung lai 1 mang tu weight blob, **uoc luong do sau** (so tang
  Conv+BatchNorm noi tiep) truoc — co the suy tu so luong BatchNorm-like run trung
  lap cung do dai khi quet thong ke (vd nhieu lan xuat hien cung 1 do dai ~128 ->
  nhieu block cung width -> mang sau kieu ResNet).
- Mang NONG (<=3-4 tang): chi can khop tong tham so, thu forward truoc, neu sach thi
  dung, khong can them safety-net.
- Mang SAU (>=5-6 tang): BAT BUOC dung kien truc co skip connection + `clamp` sau
  MOI block + 1 lop chuan hoa "don dep" (InstanceNorm hoac tuong duong) truoc head
  cuoi — dung mong doi chi doi kien truc (residual) la du, phai co ca clamp.
- Nguong clamp `[-30,30]` la kinh nghiem (du rong de khong cat mat tin hieu that,
  du hep de chan luy thua) — co the dieu chinh theo pham vi gia tri thuc te quan sat
  duoc o cac mang da HEALTHY san (thuong |gia tri trung gian| < 15-20).

## Chu y / Cam bay

- ⚠️ Dung nham "HEALTHY (0 NaN/Inf)" la "chinh xac ve mat nhan dang/phan loai" — day
  chi la XAC NHAN ON DINH SO HOC (mang chay duoc, khong crash, dung weight that),
  KHONG phai xac nhan gia tri output (bounding box, embedding, xac suat lop) dung voi
  y nghia that cua ArcSoft. Muon dung trong san xuat can them buoc xac minh
  layer-by-layer that (vd giai ma bang anchor that, hoac dynamic-capture layer
  type tu ncnn dispatcher).
- ⚠️ InstanceNorm2d khi export ONNX se canh bao "train=True" du dang o eval() — day la
  hanh vi BINH THUONG cua InstanceNorm (luon tinh tren batch/instance hien tai bat ke
  train/eval), khong phai loi; da verify ONNX Runtime van chay dung/on dinh du co
  canh bao nay.

## Tham chieu

- [[onnx-nan-fix-via-real-param-count-matching]] — buoc dau tien (khop tong tham so,
  du cho mang nong).
- Project: DecodeTools — `reconstructed_model_4/build_all_models_v2.py`,
  `reconstructed_model_4/test_all_models.py`.
