---
name: extract-real-weights-via-pool-allocator-pointer-arithmetic
description: Trich xuat GIA TRI WEIGHT THAT (khong phai doan/random) tu custom pool allocator bang cach sap xep con tro theo dia chi + do khoang cach lien tiep, ket hop quet junk-run de xac dinh ranh gioi tung tensor con
metadata:
  type: reverse-engineering
---

# Trich xuat weight THAT tu custom pool allocator bang pointer arithmetic + junk-run detection

## Boi canh

Sau khi xac dinh layer::forward-like function (`a9b2c`) duoc goi 45 lan trong 1 lan
`detectFaces()` that (qua Frida Interceptor an toan, khong dung Stalker de tranh
crash), tham so thu 4 (`a3`) cua ham nay dam nhan 2 vai tro khac nhau tuy layer:
- Voi layer khong co blob weight (ReLU, Pooling...): la 1 SO NGUYEN NHO (config).
- Voi layer CO blob weight that (Convolution, InnerProduct...): la 1 CON TRO HEAP
  THAT tro toi vung du lieu weight da giai ma/load xong.

Van de: `libarcsoft_face.so` dung **bo cap phat bo nho tuy chinh (custom pool
allocator)** cho cac khoi lon (da xac nhan tu dau phien lam viec) — nen
`malloc_usable_size()` (ham chuan cua libc) tra ve **gia tri vo nghia** (hang
nghin ty byte) khi goi tren con tro thuoc pool nay, khong dung duoc de xac dinh
kich thuoc that cua tung blob.

## Giai phap: 2 ky thuat doc lap, dung ket hop

### 1. Pointer-delta (gia dinh pool cap phat tuan tu/lien tuc)

Bo cap phat dang bump/arena (pho bien trong cac thu vien suy luan AI toi uu cho
tinh huong "cap phat 1 lan, khong can free rieng le" nhu ncnn) thuong CAP PHAT
CAC KHOI LIEN TIEP NHAU trong bo nho, khong co gap/fragmentation. Neu bat duoc
NHIEU con tro thuoc CUNG 1 lan goi ham, sap xep chung theo dia chi tang dan,
**khoang cach toi con tro ke tiep = kich thuoc THAT cua khoi hien tai** (khong
can biet gi ve cau truc noi bo cua allocator).

```python
ptrs.sort()  # theo dia chi
for i in range(len(ptrs)-1):
    size_bytes = ptrs[i+1].addr - ptrs[i].addr  # = kich thuoc that cua ptrs[i]
```

Luu y: chi ap dung duoc GIUA cac con tro CUNG MOT VUNG/ARENA (kiem tra prefix
dia chi giong nhau) — con tro khac arena (vd 1 allocation nho qua malloc chuan
nam o vung nho hoan toan khac) se cho ra delta VO NGHIA (hang tram MB) neu tinh
lan.

### 2. Junk-run detection (phat hien ranh gioi tensor con NAM TRONG cung 1 khoi)

Mot khoi pool co the chua NHIEU tensor con noi tiep nhau (khong phai 1 khoi =
1 tensor). Ranh gioi giua chung thuong co 1 doan ngan gia tri "rac" — subnormal
float (|v|<1e-30, khac 0) xen ke voi 1 gia tri khong lo bat thuong (|v|>10,
thuong la >1e20) — do vung do la HEADER/METADATA cua dinh dang luu tru noi bo,
khong phai weight thuc.

```python
is_junk = (np.abs(arr) > 10) | ((np.abs(arr) < 1e-30) & (arr != 0))
junk_start = np.where(is_junk)[0][0] if is_junk.any() else None
true_tensor = arr[:junk_start]  # cat truoc diem junk dau tien
```

Ca 2 ky thuat cho ket qua **nhat quan voi nhau** khi ap dung tren cung 1 tap du
lieu — day la bang chung cho thay ca 2 deu dung, khong phai trung hop ngau nhien.

## Ket qua da verify

Tu 45 lan goi ham that, xac dinh duoc 6 tensor weight THAT (khong doan) voi
kich thuoc: 339312, 227072, 9224, 4624, 9224, 5795 phan tu — deu la gia tri
float THAT doc truc tiep tu tien trinh dang chay, khong phai random/blind-slice
tu file tinh nhu cac lan thu truoc trong cung du an.

## Ap dung lai (How to reuse)

1. Xac dinh ham "duyet + xu ly moi phan tu" that (qua Interceptor.attach an
   toan tren TOAN BO lan goi, KHONG dung Stalker cho buoc nay vi Stalker de
   crash tren mot so thiet bi/kernel — xem
   [[deep-network-reconstruction-needs-skip-connection-plus-clamp]] cho tinh
   huong tuong tu).
2. Voi MOI lan goi, luu ca tham so co the la pointer LAN gia tri co the la
   size/marker — dung heuristic don gian (`asNum > 0x1000000`) de phan biet
   pointer that voi so nguyen nho, TRUOC KHI thu doc bo nho (tranh crash).
3. Doc mot luong LON du lieu tu moi pointer (vi du 512KB-2MB, deu boc trong
   try/catch) — DUNG lo doc "qua" ranh gioi that, vi buoc sau (pointer-delta +
   junk-run) se tu dong cat dung.
4. Neu nghi ngo bo cap phat tuy chinh, **DUNG** cay dua vao
   `malloc_usable_size()` — no chi dung cho vung nho qua malloc/new chuan; hay
   dung 2 ky thuat tren thay the.

## Chu y / Gioi han

- ⚠️ Ky thuat nay chi cho biet **VI TRI va GIA TRI THAT** cua tung tensor, KHONG
  tu dong suy ra duoc **HINH DANG chinh xac** (out_channels, in_channels,
  kernel_h, kernel_w) — can them buoc rieng (vd doc struct mo ta layer o vong
  lap dau, hoac thu cac cach chia (out,in,k,k) sao cho tich = tong so phan tu
  that va hop ly ve mat kien truc).
- ⚠️ Mot so con tro "isLikelyPointer" hoa ra chi tro toi vung cap phat CHUAN
  (malloc thuong, chi 8 byte/2 phan tu) — KHONG phai loi, ma la vi layer do
  thuc su khong co blob weight lon (chi co 1-2 gia tri scalar cau hinh). Dung
  loai bo nhung entry nay ma khong kiem tra — chung van la du lieu that, chi
  la khong phai "weight tensor" theo nghia thong thuong.

## Tham chieu

- Lien quan: bo cap phat tuy chinh cua ArcSoft da duoc xac nhan tu dau du an
  (memcpy/malloc hook khong thay duoc tung tensor rieng le vi qua bo cap phat
  nay) — lesson nay la lan dau tien VUOT QUA duoc gioi han do bang pointer
  arithmetic thay vi co gang hook truc tiep ham cap phat.
- Project: DecodeTools —
  `temp/device-f10b/hook_capture_all_weights.js`,
  `temp/device-f10b/full_capture.py`,
  `reconstructed_model_4/build_from_real_captured_data.py`.
