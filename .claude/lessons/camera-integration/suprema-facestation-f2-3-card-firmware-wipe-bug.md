---
category: camera-integration
tags: [suprema, bs2-sdk, facestation-f2, biometric, firmware-bug, enroll, card]
severity: critical
created: 2026-08-25
updated: 2026-08-25
project-origin: iAccess Desktop v2 (App-Access-V2)
---

# Suprema FaceStation F2: user có đúng 3 thẻ → BẤT KỲ enroll tiếp theo đều bị thiết bị xóa trắng (silent wipe, SDK vẫn trả SUCCESS)

## Tình huống gặp phải

> Đang debug lỗi `-702`/`-716` khi nạp/hủy thẻ + vân tay nhiều lần trên thiết bị Suprema FaceStation F2
> thật (BS_SDK_V2, P/Invoke, .NET 8, `iAccess.Devices.Suprema/FSF2Controller.cs`). User báo: "1 thẻ +
> nhiều vân tay thì ổn, nhiều thẻ thì có vấn đề". Đã fix nhiều root cause thật khác trong cùng session
> (dùng `BS2_GetUserInfosFaceEx` sai → đổi `BS2_GetUserDatasFaceEx` + mask ALL; thiếu
> `EnsureUserAccessGroup` trước `EnrollUserFaceEx`; race condition với `CheckConnectLoop` polling nền)
> nhưng lỗi vẫn tái diễn có chủ đích, gửi lại lệnh nhiều lần vẫn bị — chứng minh đây KHÔNG phải lỗi
> tạm thời/timing.

## Triệu chứng / Lỗi

Sau khi user đã có ĐÚNG 3 thẻ trên thiết bị (`BS2User.numCards == 3`, xác nhận qua
`BS2_GetUserDatasFaceEx`), gọi `BS2_EnrollUserFaceEx` lần tiếp theo — DÙ KHÔNG ĐỔI GÌ (kể cả re-enroll
y nguyên 1 thẻ cũ, không thêm/sửa gì) — trả về `result = 0` (`BS_SDK_SUCCESS`), nhưng đọc lại ngay sau
đó bằng `BS2_GetUserDatasFaceEx` cho thấy TOÀN BỘ user bị xóa trắng:

```
userId (device trả về) =      (rỗng)
flag = 0
numCards = 0
numFingers = 0
numFaces = 0
accessGroupId[0..3] = 0,0,0,0
```

Tái hiện 100% qua tool test độc lập (`TestSupremaWindow`, WinForms, gọi trực tiếp `Suprema.API`,
KHÔNG qua business layer của app) — loại trừ hoàn toàn nguyên nhân ở tầng ứng dụng.

## Nguyên nhân gốc rễ (Root Cause)

Đây là hành vi/giới hạn (rất có thể là **bug firmware**) của chính thiết bị FaceStation F2 — KHÔNG
phải lỗi marshaling hay logic ở tầng C#. Đã loại trừ lần lượt các nghi vấn ở tầng app bằng test có đối
chứng (tool `TestSupremaWindow`, mode `headless <userId> <ip> <cardsCount> <fingersCount>`):

| Kịch bản | Kết quả |
|---|---|
| 1 thẻ + 1 vân tay | ✅ OK |
| 2 thẻ + 1 vân tay | ✅ OK |
| 2 thẻ + 2 vân tay (tổng 4 credential) | ✅ OK |
| 3 thẻ (đăng ký lần đầu, enroll thứ 3) | ✅ OK (`numCards=3`) |
| 3 thẻ → **enroll lần thứ 4 bất kỳ** (dù chỉ re-enroll y nguyên Card1, không đổi gì, không đụng vân tay) | ❌ **Xóa trắng toàn bộ user** |

Kết luận: KHÔNG liên quan đến "nhiều thẻ" nói chung, KHÔNG liên quan đến việc "thêm vân tay" — chính
xác là: **user đã có `numCards == 3` → lệnh `EnrollUserFaceEx` KẾ TIẾP (bất kỳ nội dung gì) làm thiết
bị corrupt/xóa bản ghi, dù trả `SUCCESS`.**

Đã loại trừ các nghi vấn tầng app trước khi kết luận là firmware:
1. Truyền thẳng con trỏ SDK cấp cho ĐỌC (`cardObjs`/`fingerObjs` từ `BS2_GetUserDatasFaceEx`) ngược vào
   lệnh GHI (`BS2_EnrollUserFaceEx`) — code cũ ở `DownloadFingerCore`/`DownloadFaceCore` có làm điều
   này với `cardObjs` (không rebuild) → đã fix (rebuild toàn bộ cardObjs/fingerObjs/faceObjs/
   faceExObjs/user_photo_obj từ dữ liệu app-side trước mọi `Enroll`) → **lỗi vẫn xảy ra**.
2. Struct `BS2Card`/`BS2SmartCardData` marshaling sai kích thước (`cardUnion` ByValArray SizeConst=1656
   vs `Util.StructToBytes<BS2SmartCardData>` — đã verify khớp, không throw exception ở bất kỳ lần gọi
   nào, kể cả lần enroll thứ 3 thành công).
3. Race condition với polling nền — tool test KHÔNG có polling nền (WinForms đơn luồng, không gọi
   `CheckConnectLoop`), lỗi vẫn 100% tái diễn.

## Giải pháp

**Workaround ở tầng ứng dụng** (không thể fix từ code — cần Suprema xác nhận/fix firmware):
giới hạn CỨNG tối đa **2 thẻ/user** (thấp hơn hằng số SDK `BS2Environment.BS2_MAX_NUM_OF_CARD_PER_USER
= 8`), tránh hoàn toàn việc `numCards` chạm mốc 3.

```csharp
// FSF2Controller.cs
private const int MaxCardsPerUserWorkaround = 2;

// Trong DownloadUserCore, thay điều kiện giới hạn từ BS2Environment.BS2_MAX_NUM_OF_CARD_PER_USER
// sang MaxCardsPerUserWorkaround:
else if (mergedCards.Count >= MaxCardsPerUserWorkaround)
{
    skipEnroll = true;
    result = -1;
}
```

Kết hợp: **1-2 thẻ + không giới hạn số vân tay** là combo đã test ổn định, dùng làm giới hạn nghiệp vụ
chính thức cho tới khi có phản hồi từ Suprema.

## Áp dụng lại (How to reuse)

- Khi thấy thiết bị Suprema (hoặc SDK BS2 nói chung) trả `SUCCESS` cho `EnrollUserFaceEx` nhưng đọc lại
  bằng `GetUserDatasFaceEx` thấy dữ liệu bị mất/reset → ĐỪNG vội nghi marshaling/race condition trước
  — dựng 1 tool test độc lập (KHÔNG qua business layer, gọi trực tiếp API) để soi CHÍNH XÁC ngưỡng số
  lượng credential (thẻ/vân tay/face) gây lỗi, bằng cách tăng dần số lượng và có bước "re-enroll không
  đổi gì" để tách biệt "do thêm dữ liệu mới" khỏi "do đạt ngưỡng count".
- Kỹ thuật tool test hiệu quả: thêm mode CLI headless (`args[0]=="headless"`) chạy Form1 KHÔNG hiện
  UI, tất cả thông báo qua `Console.WriteLine` thay `MessageBox.Show` (MessageBox sẽ treo vô hạn nếu
  không có người bấm) — tự động lặp Register→Check sau MỖI bước để cô lập chính xác bước nào gây lỗi.
- Nếu nghi ngờ 1 field/con trỏ cụ thể gây corrupt (VD `cardObjs`/`faceObjs` truyền thẳng từ đọc sang
  ghi) — SỬA và TEST LẠI NGAY trước khi kết luận đó là nguyên nhân; đừng dừng ở "có vẻ hợp lý" — ở đây
  sau khi sửa xong (rebuild toàn bộ con trỏ từ app-side), lỗi VẪN xảy ra, chứng minh giả thuyết sai.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Thiết bị Suprema chỉ cho phép **1 kết nối SDK cùng lúc** — nếu BioStar (phần mềm chính hãng) đang
  mở và giữ kết nối, mọi `BS2_ConnectDeviceViaIP` từ code khác sẽ timeout với `-601` liên tục dù ping
  mạng vẫn bình thường. Đừng nhầm với lỗi kết nối thật.
- ⚠️ Kill cứng (force-stop) một process đang giữ session SDK (không gọi `BS2_DisconnectDevice` trước)
  có thể khiến thiết bị giữ session "zombie" một lúc, khiến lần connect kế tiếp cũng bị `-601` — cần
  chờ hoặc thiết bị tự timeout session cũ.
- ⚠️ `BS2Card.cardUnion` là `byte[]` với `[MarshalAs(ByValArray, SizeConst=1656)]` — PHẢI gán đúng
  array có ĐÚNG 1656 byte (dùng `Util.StructToBytes<T>` trả về `Marshal.SizeOf(T)` byte), không phải
  nguyên nhân của bug này nhưng là điểm dễ gây `ArgumentException`/corrupt nếu tự tạo card thủ công.
- ⚠️ ĐỪNG mặc định coi giới hạn số thẻ trong SDK header (`BS2_MAX_NUM_OF_CARD_PER_USER=8`) là giới hạn
  THẬT của thiết bị — SDK khai báo giới hạn lý thuyết, thiết bị/firmware cụ thể có thể có bug ở ngưỡng
  thấp hơn nhiều (ở đây là 3).

## Tham chiếu

- Project liên quan: iAccess Desktop v2 (`App-Access-V2`), branch `fix/suprema-sdk-audit-2026-08-25`
- Tool test độc lập: `iAccessDesktopv2.Avalonia/TestSupremaWindow/` (WinForms, mode `headless`/`wipe`)
- File production đã fix: `iAccessDesktopv2.Avalonia/iAccess.Devices.Suprema/FSF2Controller.cs`
  (`MaxCardsPerUserWorkaround`)
