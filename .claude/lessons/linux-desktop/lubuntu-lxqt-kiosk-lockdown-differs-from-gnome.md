---
category: linux-desktop
tags: [lubuntu, lxqt, openbox, kiosk, sddm, kiosk-lockdown, systemd]
severity: high
created: 2026-07-31
updated: 2026-07-31 (F02: chattr immutable phá idempotency khi chạy script lần 2)
project-origin: 6.RemoteControlTool (nhánh Lubuntu)
---

# Kiosk lockdown trên Lubuntu/LXQt hoàn toàn khác cơ chế GNOME — lối thoát thật nằm ở lxqt-globalkeyshortcuts, không phải Openbox rc.xml

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Port bộ script kiosk lockdown (`scripts/linux-kiosk/1-install-software.sh`,
`2-configure-system.sh` — vốn viết cho Ubuntu Desktop/GNOME Shell 42) sang nhánh
`Lubuntu` để chạy trên Lubuntu (LXQt + Openbox). Bản GNOME dùng `gsettings`,
`gnome-extensions` (Just Perfection, Block Caribou), dconf system-db lock, GDM
autologin — không cái nào tồn tại trên LXQt. Đã SSH vào máy Lubuntu thật
(Ubuntu 22.04.5 base, `lxqt-session` + `openbox` + `sddm`) để verify thay vì đoán mù.

## Triệu chứng / Lỗi

Giả định ban đầu (chưa test) sai ở NHIỀU điểm so với máy thật:

1. Đoán autostart desktop-icon là `pcmanfm-qt-desktop-pref.desktop` — **SAI**, thật
   ra là `lxqt-desktop.desktop` (`Exec=pcmanfm-qt --desktop --profile=lxqt`).
2. Đoán Openbox user config là `~/.config/openbox/lxqt-rc.xml` (theo suy luận từ
   quy ước LXDE `openbox-lxde` → `lxde-rc.xml`) — **SAI**. Không có file/symlink nào
   tên `lxqt-rc.xml` trên toàn hệ thống, không có binary `openbox-lxqt`.
   `lxqt-session` gọi thẳng `openbox` (xem `/usr/share/lxqt/windowmanagers.conf` mục
   `openbox`) nên Openbox dùng đúng quy ước MẶC ĐỊNH của nó:
   `$XDG_CONFIG_HOME/openbox/rc.xml`, sinh từ template `/etc/xdg/openbox/rc.xml`.
3. Quan trọng nhất: ban đầu chỉ định khoá phím tắt thoát kiosk bằng cách sửa
   `<keyboard>` trong Openbox rc.xml (Alt+F4, Alt+Tab...) — nhưng đó chỉ là phím tắt
   cấp WINDOW MANAGER. Test thật trên máy phát hiện các phím tắt NGUY HIỂM NHẤT để
   thoát kiosk lại nằm ở **daemon riêng của LXQt**
   (`~/.config/lxqt/globalkeyshortcuts.conf`, sinh từ
   `/etc/xdg/lxqt/globalkeyshortcuts.conf/globalkeyshortcuts.conf`), hoàn toàn tách
   biệt khỏi Openbox:
   - `Control+Alt+T` → mở `qterminal` (Terminal!)
   - `Control+Alt+Delete` → mở `qps` (Task Manager)
   - `Meta+E` → mở `pcmanfm-qt` (File Manager)
   - `Meta+R` → show/hide Runner (gõ lệnh chạy bất kỳ app nào)
   - `Super_L` → show/hide Main Menu (mở được mọi app cài trên máy)

   Nếu chỉ khoá Openbox rc.xml mà bỏ qua file này, kiosk vẫn thoát được dễ dàng bằng
   Ctrl+Alt+T mở terminal — coi như KHÔNG khoá gì cả.

## Nguyên nhân gốc rễ (Root Cause)

LXQt tách quản lý phím tắt "toàn cục" (global — hoạt động bất kể cửa sổ nào đang
focus, gồm cả app/launcher shortcuts) ra một daemon riêng
(`lxqt-globalkeyshortcutsd`, cấu hình qua `lxqt-config-globalkeyshortcuts`), KHÔNG
dùng cơ chế `<keybind>` của window manager (Openbox) như GNOME dồn hết vào
gsettings/dconf của Mutter. Openbox rc.xml chỉ còn giữ các phím tắt thuần WM
(chuyển cửa sổ, đóng cửa sổ, chuyển desktop) — không có shortcut mở app nào ở đó.

## Giải pháp

1. Xác định `OB_RC="$HOME/.config/openbox/rc.xml"` (KHÔNG phải `lxqt-rc.xml`), khởi
   tạo từ `/etc/xdg/openbox/rc.xml` nếu user chưa từng đăng nhập desktop.
2. Xác định `GKS_CONF="$HOME/.config/lxqt/globalkeyshortcuts.conf"`, khởi tạo từ
   `/etc/xdg/lxqt/globalkeyshortcuts.conf/globalkeyshortcuts.conf` nếu chưa có.
3. Parse file INI này bằng `python3 configparser` (BẮT BUỘC
   `interpolation=None` — value gốc chứa ký tự `%` như `\x2600` khiến configparser
   mặc định hiểu nhầm thành interpolation và raise lỗi). Section name là tổ hợp phím
   đã percent-encode kèm hậu tố số thứ tự (VD `Control%2BAlt%2BT.4`) — so khớp theo
   phần TRƯỚC dấu chấm cuối cùng bằng `section.rsplit(".", 1)[0]`.
4. Set `Enabled=false` cho các section nguy hiểm thay vì xoá — dễ đảo ngược (set lại
   `true`) đúng pattern "2 chiều" toggle của cả bộ script.
5. `pkill -x lxqt-globalkeyshortcutsd` sau khi sửa (best-effort, hiệu lực chắc chắn
   nhất vẫn là đăng nhập lại — daemon chỉ đọc file lúc khởi động).

Xem implementation đầy đủ: `scripts/lubuntu-kiosk/2-configure-system.sh` mục
`[6/9]` (Openbox rc.xml) và `[6b/9]` (lxqt-globalkeyshortcuts — lớp quan trọng hơn).

## Áp dụng lại (How to reuse)

- Khi khoá "phím tắt thoát kiosk" trên bất kỳ DE nào KHÔNG PHẢI GNOME → đừng mặc
  định goi tìm ở window-manager config. Tìm daemon quản lý global shortcut RIÊNG của
  DE đó trước (LXQt có `lxqt-globalkeyshortcutsd`; XFCE có `xfce4-keyboard-shortcuts`
  qua `xfconf`; MATE có `mate-keybinding` qua dconf riêng).
- Trước khi viết script cho 1 DE mới chưa từng động tới → SSH vào 1 máy thật, liệt kê
  toàn bộ `~/.config/lxqt/globalkeyshortcuts.conf` (hoặc tương đương) để lấy DANH
  SÁCH THẬT các shortcut mặc định, đừng đoán từ hiểu biết chung — đoán "lxqt-rc.xml"
  ở lesson này là ví dụ cụ thể của việc đoán sai do suy luận từ quy ước LXDE.
- `openbox --reconfigure` in message "Failed to open display" ra **STDOUT** (không
  phải stderr) khi chạy qua SSH không có `$DISPLAY` — `2>/dev/null` không che được,
  phải dùng `>/dev/null 2>&1`.

## Cập nhật 2026-07-31 (F02): chattr +i phá tính idempotent khi chạy lại script lần 2

Sau khi deploy Lubuntu thành công qua CcuUI, user chạy DEPLOY LẦN 2 lên CÙNG máy
(192.168.21.39) và gặp `exit 4` ngay gần đầu `2-configure-system.sh`, log chỉ hiện
đúng phần header (5 dòng) — không thấy dòng lỗi thật vì UI chỉ log 5 dòng cuối.
SSH vào chạy tay lại đúng lệnh mới lộ ra:

```
=== [2/9] Khoá còn 1 desktop tĩnh (Openbox <desktops><number>) ===
sed: cannot rename /home/kiennguyen/.config/openbox/sedXXXXX: Operation not permitted
EXITCODE=4
```

**Root cause**: bước `[6/9]` (khoá phím tắt) của LẦN CHẠY TRƯỚC đã set
`~/.config/openbox/rc.xml` thành `chmod 444` + `chattr +i` (immutable). Bước
`[2/9]` (khoá 1 desktop tĩnh) chạy TRƯỚC bước `[6/9]` trong CÙNG 1 lần chạy mới,
và `sed -i` (tạo file tạm rồi rename đè lên file gốc) cần quyền ghi trên file gốc —
immutable chặn cả rename lẫn ghi → `sed` tự thoát exit 4 → `set -e` abort toàn script.
Script vốn thiết kế để CHẠY LẠI ĐƯỢC NHIỀU LẦN (re-deploy) nhưng chỉ gỡ khoá cũ ở
đúng bước `[6/9]`, quên rằng bước `[2/9]` sớm hơn cũng cần ghi vào cùng file.

**Fix**: thêm `_sudo chattr -i "$OB_RC" 2>/dev/null || true` +
`chmod u+w "$OB_RC" 2>/dev/null || true` NGAY SAU khi xác nhận `$OB_RC` tồn tại ở
đầu bước `[2/9]` — vô điều kiện, trước bất kỳ thao tác ghi nào, không đợi tới `[6/9]`.
Bước `[6/9]` sẽ tự khoá lại (chattr +i) nếu lần này vẫn chọn `lockdown_shell=1`.

**Bài học chung**: khi 1 script làm cho chính file cấu hình của nó thành
read-only/immutable ở CUỐI luồng xử lý, mọi bước ĐỨNG TRƯỚC trong cùng script (kể cả
ở lần chạy kế tiếp) mà có ghi vào file đó đều phải tự gỡ khoá trước — không thể giả
định "khoá chỉ áp dụng sau khi script chạy xong lần này", vì lần chạy THỨ HAI sẽ thấy
khoá đó đã tồn tại từ đầu.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `configparser` mặc định bật `%`-interpolation — file gốc LXQt có value dạng
  `\x2600 \x2193` (escape unicode dạng chuỗi) khiến `cp.read()` ném
  `InterpolationSyntaxError` nếu không truyền `interpolation=None`.
- ⚠️ `chattr +i` (immutable) để khoá Openbox rc.xml cần filesystem hỗ trợ (ext4 OK,
  overlayfs/một số fs mạng KHÔNG hỗ trợ) — luôn kiểm tra kết quả, đừng coi thất bại
  là lỗi cứng (dùng `|| echo CẢNH BÁO`).
- ⚠️ Bật `ufw enable` qua SSH mà QUÊN `ufw allow OpenSSH` trước → tự khoá luôn kết
  nối SSH đang dùng để chạy script, không còn cách nào gỡ trừ khi có console vật lý.
  Luôn `allow OpenSSH` trước `--force enable`, đã verify thứ tự này an toàn trên máy
  thật (SSH vẫn sống sau khi enable).
- ⚠️ File `~/.config/lxqt/globalkeyshortcuts.conf` VÀ `~/.config/openbox/rc.xml`
  không tồn tại cho tới khi user đăng nhập GUI ít nhất 1 lần — script phải tự khởi
  tạo từ template hệ thống, không được giả định file luôn có sẵn.

## Tham chiếu

- Máy test thật: Lubuntu 22.04.5 (Ubuntu base), `lxqt-session`, `openbox` 3.6.1,
  `sddm`, SSH kiểm tra ngày 2026-07-31.
- Script liên quan: `scripts/lubuntu-kiosk/1-install-software.sh`,
  `scripts/lubuntu-kiosk/2-configure-system.sh`,
  `scripts/lubuntu-kiosk/3-toggle-panel.sh`.
- Lesson liên quan: [linux-desktop/dconf-system-db-profile-required.md](dconf-system-db-profile-required.md)
  (tương đương bên GNOME — dconf lock thay vì chattr+globalkeyshortcuts).
