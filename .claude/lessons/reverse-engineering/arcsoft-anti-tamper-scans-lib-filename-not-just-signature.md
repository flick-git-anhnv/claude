---
name: arcsoft-anti-tamper-scans-lib-filename-not-just-signature
description: libarcsoft_face_engine.so tu choi JNI_OnLoad khi phat hien TEN FILE nhay cam (vd "frida") ton tai trong thu muc lib cua APK, du file do CHUA HE duoc goi loadLibrary - khong chi kiem tra chu ky APK
metadata:
  type: reverse-engineering
---

# ArcSoft anti-tamper quet TEN FILE trong lib/, khong chi kiem tra chu ky APK

## Boi canh

Da xac nhan tu truoc: `libarcsoft_face_engine.so` (ban armeabi-v7a) tu choi
`JNI_OnLoad` (tra ve `JNI_ERR`, gay `UnsatisfiedLinkError` khi Java goi
`FaceEngine.<clinit>`) neu APK duoc **ky lai bang keystore khac** ban goc — da fix
bang cach ky lai dung keystore that cua du an (xem `keystore.jks` trong repo).

Sau khi fix chu ky, van tiep tuc gap LAI DUNG LOI NAY khi thu gan Frida gadget vao
APK (ca qua objection/apktool lan qua patch DEX thu cong bang baksmali/smali
chuan, deu that bai voi CUNG 1 thong bao loi). Ban dau nghi ngo do DEX bi hong
(dung tu baksmali/smali gay loi giong het apktool).

## Nguyen nhan goc re (da verify bang thi nghiem doi chung)

Lam thi nghiem CHI THEM 1 FILE `lib/armeabi-v7a/libfrida-gadget.so` vao dung ban
APK DA XAC NHAN CHAY OK (ky dung keystore, KHONG dong DEX, KHONG goi
`System.loadLibrary` cho file do o dau ca) — **van bi JNI_ERR y het**.

=> Ket luan: `libarcsoft_face_engine.so` co co che anti-tamper **quet ten file
trong thu muc lib cua chinh APK dang chay** (rat co the qua doc
`/proc/self/maps`, hoac liet ke `ApplicationInfo.nativeLibraryDir`, hoac doc
truc tiep danh sach entry trong file APK zip) luc `JNI_OnLoad`, tim cac ten nhay
cam nhu "frida" — VA CO Y TU CHOI dang ky native method neu phat hien, BAT KE
file do co thuc su duoc `dlopen`/`loadLibrary` hay khong.

Day la co che HOAN TOAN KHAC voi kiem tra chu ky APK (ca 2 co che cung ton tai
doc lap, phai qua CA HAI thi native mois hoat dong).

## Vi sao de nham lan

- Nhieu lan thu nghiem TRUOC DO deu VUA doi ky (sai keystore) VUA co gadget cung
  luc, nen khong the ra dinh chinh xac nguyen nhan la do ky hay do gadget.
- Loi bao "Failed to register native method
  com.arcsoft.face.FaceEngine.nativeSetCustomDeviceInfo" luon giong het nhau du
  nguyen nhan that su khac nhau moi lan — khong nen tin tuong day la dau hieu
  chi ra CHINH XAC nguyen nhan; day chi la PHUONG THUC DAU TIEN trong danh sach
  dang ky bi huy do JNI_OnLoad tu choi som, khong phai bang chung ve nguyen nhan.

## Cach xac dinh dung nguyen nhan (phuong phap khoa hoc da dung)

Thi nghiem doi chung tung buoc mot, MOI LAN CHI THAY DOI DUNG 1 BIEN SO:
1. Test 0: APK goc, khong doi gi -> hoat dong.
2. Test 1: chi doi chu ky (ky lai bang keystore khac/debug) -> LOI.
3. Test 2: ky dung lai keystore that, khong doi gi khac -> HOAT DONG (xac nhan
   nguyen nhan 1 la chu ky).
4. Test 3: ky dung keystore that + THEM DEX patch (loadLibrary) + gadget file ->
   LOI (nghi ngo DEX).
5. Test 4: ky dung keystore that + CHI them file gadget (KHONG dong DEX, KHONG
   goi loadLibrary) -> VAN LOI => loai tru gia thuyet DEX, xac nhan nguyen nhan
   that la su TON TAI cua file co ten nhay cam.

Nho co Test 4 (isolate bien so con lai) moi tim ra dung nguyen nhan that.

## Ap dung lai (How to reuse)

- Khi mot native lib nghi co anti-tamper va lien tuc that bai voi CUNG 1 thong
  bao loi du da doi nhieu thu khac nhau cung luc, PHAI lam thi nghiem doi chung
  **doi TUNG bien so mot, giu nguyen tat ca con lai** — dung doan nguyen nhan tu
  1 lan thu thay doi nhieu thu cung luc.
- SDK bao mat cao (nhu ArcSoft) co the co NHIEU LOP anti-tamper doc lap (chu ky
  APK + quet ten file lib + co the con nua chua kiem tra: quet process
  map/xproc, kiem tra debuggable flag, kiem tra ptrace...) — dung dung lai khi
  fix duoc 1 lop, luon gia dinh co the con lop khac phia sau.

## Chu y / Gioi han dao duc-ky thuat

- ⚠️ Buoc tiep theo hop ly de vuot qua lop nay la DOI TEN file cong cu debug
  (gadget) sang ten khong nhay cam — day la ky thuat **detection evasion**
  (ne tranh co che phat hien cua chinh nha cung cap SDK). Du muc dich la nghien
  cuu hop phap tren app/thiet bi cua chinh minh, day la ranh gioi ma agent
  KHONG nen tu y thuc hien — phai de nguoi dung (chu so huu hop phap) tu quyet
  dinh va tu chay buoc nay.

## Cap nhat: xac nhan them lop thu 3 (cap nhat 2026-08-10)

Thu huong khac de tranh dung lib/DEX: chi bat `android:debuggable="true"` trong
manifest (dung apktool `d --no-src` de decode CHI manifest, giu nguyen 100% ca
3 file DEX, khong dung lib) + `run-as` de chay frida-server khong can root.

Ket qua: **VAN THAT BAI**, nhung theo kieu khac — khong con `JNI_ERR`/
`UnsatisfiedLinkError` nua, thay vao do la `SIGABRT` voi thong diep
`JNI DETECTED ERROR IN APPLICATION: JNI NewGlobalRef called with pending
exception NoSuchMethodError: nativeSetCustomDeviceInfo` — **CUNG MOT loi goc**
nhung lo ra ro hon vi ART tu dong bat che do CheckJNI nghiem ngat khi app o
che do debuggable.

=> Xac nhan: `libarcsoft_face_engine.so` co the **tu kiem tra co
`ApplicationInfo.FLAG_DEBUGGABLE`** va co y pha hong dang ky JNI ngay ca khi
KHONG co file la nao trong thu muc lib va KHONG doi chu ky. Day la **lop anti-
tamper THU 3 doc lap** (ngoai chu ky APK va tinh toan ven thu muc lib).

Ca 3 lop deu phai vuot qua dong thoi de dung Frida tren ban v7 — day la
diem dung hop ly, vi tiep tuc se can ky thuat evasion escalate (gia mao
ApplicationInfo flags o native level, hook truoc khi JNI_OnLoad chay...) —
vuot qua ranh gioi nghien cuu hop ly sang doi dau truc tiep voi thiet ke bao
mat co chu dich cua nha cung cap SDK.

## Tham chieu

- Lien quan: license/anti-tamper that da tim thay truoc do (kiem tra chu ky
  APK truoc khi cho FaceEngine khoi tao) — ca 3 co che cung thuoc "anti-tamper
  suite" cua ArcSoft, khong phai 1 co che duy nhat.
