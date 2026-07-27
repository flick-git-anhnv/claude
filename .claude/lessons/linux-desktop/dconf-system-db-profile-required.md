---
category: linux-desktop
tags: [dconf, gsettings, gnome, kiosk, ubuntu, lockdown]
severity: high
created: 2026-07-27
updated: 2026-07-27
project-origin: 6.RemoteControlTool (kiosk ZCU, F09)
---

# dconf system-db bị bỏ qua âm thầm nếu thiếu `/etc/dconf/profile/user`; session đang chạy không nhận profile mới cho tới khi re-login

## Tình huống gặp phải

Khoá "lối thoát kiosk" trên Ubuntu 22.04 (GNOME Shell 42.9, X11): vô hiệu phím Super/Alt+F2/Ctrl+Alt+T... bằng dconf DB hệ thống + lock (`/etc/dconf/db/local.d/` + `locks/`) để user không tự đổi lại được — thay vì `gsettings set` theo user.

## Triệu chứng / Lỗi

```
1) Ghi settings + locks vào /etc/dconf/db/local.d/, chạy `sudo dconf update`
   → thành công, KHÔNG lỗi — nhưng không có tác dụng gì cả.
2) Sau khi tạo đủ profile: process MỚI (gsettings get) thấy giá trị khoá ngay,
   nhưng GNOME Shell ĐANG CHẠY vẫn dùng keybinding cũ (Alt+F2 vẫn mở
   "Run a Command" — có screenshot kiểm chứng).
```

## Nguyên nhân gốc rễ (Root Cause)

1. Ubuntu KHÔNG có sẵn `/etc/dconf/profile/user`. Khi thiếu, dconf dùng profile mặc định chỉ gồm `user-db:user` → toàn bộ `system-db:local` bị bỏ qua âm thầm (`dconf update` vẫn compile DB thành công).
2. dconf profile chỉ được libdconf đọc MỘT LẦN lúc process khởi động → mọi process chạy trước khi tạo profile (gnome-shell, gnome-settings-daemon) không bao giờ thấy system-db mới cho tới khi re-login/reboot.

## Giải pháp

```bash
# 1. BẮT BUỘC tạo profile trước/cùng lúc:
printf 'user-db:user\nsystem-db:local\n' | sudo tee /etc/dconf/profile/user
# 2. Ghi settings vào /etc/dconf/db/local.d/00-kiosk-lockdown
#    và LOCK vào /etc/dconf/db/local.d/locks/00-kiosk-lockdown (mỗi dòng 1 key path)
sudo dconf update
# 3. REBOOT / re-login rồi mới kiểm chứng hành vi thật
```

1. Kiểm chứng lock nhanh: `gsettings set <key bị lock> ...` phải trả **"The key is not writable"**.
2. Kiểm chứng hành vi thật qua SSH: `xdotool key super/alt+F2` + `gnome-screenshot` — so ảnh trước/sau.

## Kiến thức liên quan

- Gesture cảm ứng vuốt 3 ngón mở overview (GNOME 40+) là hard-code, KHÔNG có gsettings key để tắt — đừng mất công tìm. Giảm nhẹ bằng extension Just Perfection: `search=false`, `type-to-search=false`, `startup-status=0` (không boot vào overview).
- Gói `gnome-kiosk` không có trong repo Ubuntu 22.04 (chỉ 23.04+).

## Checklist tránh tái phạm

- [ ] Dùng system-db → đã tạo `/etc/dconf/profile/user` chưa?
- [ ] Đã có file trong `locks/` chưa? (thiếu lock = user vẫn set ngược lại được)
- [ ] Đã reboot/re-login trước khi kết luận "không hoạt động"?
