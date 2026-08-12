---
category: reverse-engineering
tags: [frida, hook-overhead, live-camera, ncnn, arcsoft, android]
severity: high
created: 2026-08-11
updated: 2026-08-11
project-origin: DecodeTools (ArcSoft IR-Liveness net5 live-camera verify)
---

# Hook Frida vao ham conv DUNG CHUNG toan pipeline -> camera live tu dong back

## Tinh huong
Monitor live-camera de verify net5 (so logit model vs `getIrLiveness()` thuc
te) hook 2 diem native: `0xa9b2c` (conv, de bat crop 128x128 dau vao) va
`0xec1f0` (FC, de bat 2-logit dau ra). Sau khi cai hook, vao man hinh xac thuc
khuon mat thi app **tu dong back ve Home** ngay khong bat duoc frame nao.

## Nguyen nhan
`0xa9b2c` la ham conv **dung chung cho TOAN BO pipeline** (detection net0 +
net3 + net4 + net5), duoc goi **hang tram lan/frame** o 30fps tren thiet bi
ARM yeu (Qualcomm MSM8953). Frida `Interceptor.attach` chen trampoline vao
diem nay lam tang overhead moi call -> xu ly frame cham -> watchdog trong
`DualCameraPreviewManager` timeout -> `closeCameraSafely()` -> Activity tu
back ve Home. Log xac nhan:
```
MessageQueue: Handler sending message to a Handler on a dead thread
  at DualCameraPreviewManager.lambda$closeCameraSafely$3
```
Day la loi da tung gap truoc do trong cung session ("sau khi cai hook thi ko
nhan dang duoc nua") nhung luc do chua xac dinh duoc root cause chinh xac.

## Fix
Bo hoan toan hook vao ham conv chung (`a9b2c`). Chi giu hook `0xec1f0` (FC) —
FC layer it duoc goi hon RAT NHIEU so voi conv (moi network chi co 2-3 FC vs
hang chuc conv). De phan biet output cua net5 voi net3/net4 (ca 3 deu qua
`ec1f0`), KHONG can crop-pairing bang network pointer nua — chi can loc theo
SHAPE: net3 FC output=452-dim, net4=226-dim, **chi net5 co output c==2**.
Filter `c===2 && h===1 && w===1` la DU DE xac dinh duy nhat net5, khong bi
lan voi network khac trong cung tien trinh.

```js
// nhe: chi hook FC, filter shape rieng cua net5
Interceptor.attach(base.add(0xec1f0), {
  onEnter: function (a) { this.net = a[0]; this.lv = a[0].add(a[2].toInt32()>>>0); },
  onLeave: function () {
    var b = rb(this.net, this.lv, 0x8);
    if (b.c === 2 && b.h === 1 && b.w === 1) {
      send({ t: 'logit', v: [b.dp.readFloat(), b.dp.add(b.cs*4).readFloat()] });
    }
  }
});
```

## Ap dung lai
- Hook native vao ham DUNG CHUNG nhieu network/nhieu layer (conv generic,
  goi hang tram lan/frame) tren camera LIVE se lam cham pipeline du de trigger
  timeout cua chinh app — dac biet nguy hiem tren thiet bi yeu/frame-rate cao.
  Uu tien hook diem IT GOI NHAT (FC/output layer) thay vi conv/preprocess.
  Test offline (`processIr()` mot lan) KHONG lo ra van de nay vi chi goi 1
  lan, khong co ap luc frame-rate.
- Neu can phan biet nhieu sub-network chung 1 dispatcher, thu loc bang
  SHAPE OUTPUT truoc (re, khong can hook them diem crop de pairing bang
  con tro) — chi dung crop-pairing khi shape thuc su trung nhau.

## Lien quan
- [[ncnn-conv-symmetric-pad-and-group-from-param12]] — kien truc + bit-exact
  cua net5.
- [[arcsoft-model-naming-and-app-usage-map]] — 5 mang trong .so, net3/4/5 la
  mang thuc chay khi camera live.
