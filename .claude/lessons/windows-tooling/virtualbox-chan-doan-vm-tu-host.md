# VirtualBox — Chẩn đoán VM "màn hình đen / treo" từ host, không cần vào guest

- **Category:** windows-tooling
- **Ngày tạo:** 2026-07-26
- **Môi trường:** Windows 11 Pro, VirtualBox 7.2.2, guest Ubuntu 22.04
- **Phân loại:** Gotcha

---

## Vấn đề gặp phải

Sau khi máy host bị tắt đột ngột, VM Ubuntu bật lên chỉ hiện **màn hình đen** trong cửa sổ VirtualBox.
Kết luận vội thường là "VM hỏng do mất điện" → định chạy `fsck`, thậm chí restore backup.

Thực tế: VM **vẫn boot bình thường**, chỉ là màn hình đang ở **Plymouth splash** (logo Ubuntu) hoặc nền GDM
chưa vẽ xong, và boot chậm hơn thường lệ. Không có hỏng hóc nào.

---

## Nguyên nhân

Cửa sổ VirtualBox render splash screen tối màu, ở độ phân giải nhỏ nhìn giống hệt màn hình đen chết.
Không có cách phân biệt bằng mắt nếu chỉ nhìn cửa sổ VM.

---

## Cách chẩn đoán đúng (chạy từ HOST, VM đang chạy)

```powershell
$vb = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

# 1. VM có thực sự chạy không
& $vb list runningvms

# 2. CHỤP MÀN HÌNH GUEST — quan trọng nhất, thấy ngay đang kẹt ở đâu
& $vb controlvm "<ten-vm>" screenshotpng C:\temp\vmshot.png

# 3. Guest Additions có báo về không → guest OS đã sống
& $vb guestproperty enumerate "<ten-vm>"
#    /VirtualBox/GuestInfo/Net/0/V4/IP        → mạng đã lên
#    /VirtualBox/GuestInfo/OS/LoggedInUsers   → 0 = chưa login xong, 1 = desktop OK

# 4. Gửi phím vào guest (Esc = tắt splash, xem log systemd)
& $vb controlvm "<ten-vm>" keyboardputscancode 01 81
```

**Đọc log để loại trừ hỏng thật:**
`<VM folder>\Logs\VBox.log` — nếu KHÔNG có `Guru Meditation`, `VERR_` liên quan ổ đĩa,
`VD: ... corrupt` thì đĩa ảo không hỏng.

> `supR3HardenedErrorV: ... VERR_LDRVI_NOT_SIGNED ... uvh64.dll` (UltraViewer) xuất hiện dày đặc
> trong log là **bình thường** — VirtualBox hardening chặn DLL inject của phần mềm remote desktop,
> không liên quan lỗi VM. Đừng nhầm đây là nguyên nhân.

---

## Bảng phân biệt nhanh

| Dấu hiệu từ host | Kết luận |
|---|---|
| `screenshotpng` ra logo Ubuntu / nền xám GDM | Đang boot — **CHỜ**, không phải hỏng |
| `guestproperty` có IP + Guest Additions version | Guest OS đã sống, chỉ vấn đề hiển thị |
| `LoggedInUsers = 0` rồi chuyển thành `1` | Boot hoàn tất bình thường |
| Log có `Guru Meditation` / `VERR_` ổ đĩa | Hỏng thật → mới cần fsck / restore |
| Guest ping được, port 22 mở | Vào bằng SSH lấy log, không cần dùng GUI |

---

## Bài học rút ra

1. **Luôn `screenshotpng` trước khi kết luận VM hỏng.** Mất 2 giây, tránh chạy `fsck` vô ích lên
   filesystem đang khỏe (bản thân `fsck` sai cách mới là thứ làm hỏng dữ liệu).
2. `guestproperty enumerate` là "nhịp tim" của guest — có IP nghĩa là kernel + network stack đã chạy.
3. Backup file `.vdi` PHẢI làm khi VM **tắt hoàn toàn**. Nếu VM được bật giữa lúc copy, bản backup
   không nhất quán (kích thước lệch, dữ liệu nửa vời) → coi như không dùng được để restore.
4. Mất điện đột ngột **không mặc định** làm hỏng ext4 — journal ext4 xử lý được đa số trường hợp.
   Chỉ can thiệp khi có bằng chứng lỗi cụ thể (remount read-only, lỗi I/O trong `dmesg`).

---

## Liên quan

- [[windows-tooling-powershell-encoding]]
