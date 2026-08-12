---
category: reverse-engineering
tags: [ncnn, weight-recovery, lstsq, dataset-size, hybrid-selection, arcsoft]
severity: high
created: 2026-08-11
updated: 2026-08-11
project-origin: DecodeTools (ArcSoft IR-Liveness, fix cuoi cung sau nhieu vong lap)
---

# Chon layout/weight theo "min forward-error" phai dung TOAN BO dataset, khong phai tap con da dung de fit

## Tinh huong gap phai

Model IR-Liveness (xem [[ncnn-int8-pack4-weight-activation-layout]]) dat
"hybrid" weight (14 layer direct-read + 29 layer lstsq, chon theo loi forward
nho nhat) tren 6 anh, ket qua ~2% loi logit trung binh — CO VE on nhung khi
test tren anh THAT ngoai tap (deo kinh, phan chieu IR manh) thi **lat nguoc
ca quyet dinh** (thiet bi=SPOOF chac chan 4.6-9.6, model=LIVE yeu 0.36-0.66).

## Trieu chung

- Dung diagnostic per-layer VOI INPUT THAT (khong propagate) tren 19-21 anh
  da capture: phat hien 24/33 layer dat **0.0000 tuyet doi** (bit-exact that
  su qua lstsq), nhung dung 4-11 layer CU THE (seq 237,241,245,247,248,250,
  252,254,256,258) co loi 10-60% — LUON O CUNG VI TRI, khong ngau nhien.
- Dieu ky la: seq233 (in=32,out=192, pointwise) dat 0.0000 hoan hao, nhung
  seq237/241/245 **CUNG SHAPE HET** (cung la bottleneck lap lai trong cung
  1 mang) lai FAIL — chung to khong phai loi shape/layout chung, ma la loi
  RIENG cho instance do.

## Nguyen nhan goc re

Buoc "hybrid": voi moi layer, tinh loi forward cua (a) direct-read pack4 va
(b) lstsq-tu-featuremap, ROI CHON cai nao loi nho hon — nhung **chi dung 6
anh** de tinh CA HAI (ca fit lstsq LAN danh gia loi). Voi 6 anh, mot so kenh
sau (channel std~0 tren toan bo 6 anh — vd do goc mat/anh sang khong da
dang) khong du rang buoc: lstsq tra ve gia tri SAI cho kenh do (duong tuyen
tinh bat ky di qua it diem), va vi loi danh gia CUNG dung 6 anh do nen
"loi nho hon" bi tinh sai — hybrid chon nham phuong an te hon ma khong biet.
Day la **overfitting vao chinh tap dung de chon**, khong phai loi cong thuc.

## Giai phap

1. Thu them ANH DA DANG (dac biet cac ca "kho" nhu deo kinh/phan chieu manh
   ma model dang sai) — tang tu 6 len 21 anh.
2. Tinh lai CA fit lstsq LAN danh gia loi tren TOAN BO 21 anh (khong chi
   dung tap nho cu). Ket qua: 29/33 layer -> 0.0000 tuyet doi, chi con 4
   layer du 2-14% (van con thieu du lieu o vai kenh, nhung KHONG DU de lat
   quyet dinh nua).
3. Verify lai chinh xac tren 4 anh that (bao gom 2 anh kinh da FAIL truoc
   do) -> ca 4 khop quyet dinh THIET BI, bao gom 2 ca SPOOF chac chan ma
   truoc do model doan nham thanh LIVE.

## Ap dung lai (How to reuse)

- Khi dung ky thuat "hybrid: chon phuong an loi nho hon" cho BAT KY buoc
  phuc hoi nao (weight, threshold, activation...): **KHONG danh gia loi tren
  chinh tap du lieu dung de fit** phuong an do — se luon thien vi phuong an
  overfit tap nho. Neu bat buoc dung chung 1 tap, phai la tap DU LON/DA DANG
  de moi kenh/dac trung deu duoc kich hoat it nhat 1 lan.
- Dau hieu nhan biet: layer CUNG SHAPE, CUNG VI TRI KIEN TRUC lap lai trong
  1 mang (vd bottleneck block lap 5-6 lan) ma 1 cai dung tuyet doi con cac
  cai con lai sai deu deu -> nghi ngo bo du lieu fit/chon khong du da dang,
  KHONG PHAI loi cong thuc/layout.
- Test tren CA THAT ("edge case" nhu deo kinh, anh sang la, tan cong gia
  mao) truoc khi ket luan model "du chinh xac" — sai so trung binh thap
  (~2%) van co the che giau viec MOT SO ca cu the bi lat nguoc hoan toan.

## Lien quan
- [[ncnn-int8-pack4-weight-activation-layout]] — boi canh IR-Liveness day du.
- [[lstsq-solved-weights-carry-global-bias-use-relative-threshold]] — loi
  he thong khac cua lstsq (bias/threshold), khac voi loi under-determination o day.
