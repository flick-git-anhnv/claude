#!/bin/bash
# 2-configure-system.sh — Các tinh chỉnh hệ thống còn lại cho kiosk iPGS
# (KHÔNG cài thêm phần mềm nào — phần cài đặt nằm ở 1-install-software.sh).
#
# Bao gồm:
#   - Tắt hot corner
#   - Tắt notification banner
#   - Tắt khóa màn hình / screensaver
#   - Tắt Ubuntu Dock + desktop icons (dock trái, icon Trash/Home) — quan trọng
#     với máy mới cài Ubuntu Desktop vì 2 extension này bật mặc định
#   - Chặn suspend/sleep khi cắm điện (tránh màn hình tắt giữa chừng)
#   - Tắt popup Software Updater (tránh gián đoạn kiosk khi có bản vá mới)
#   - Bỏ qua màn hình gnome-initial-setup (hữu ích khi user kiosk vừa tạo mới)
#   - Autologin GDM cho user kiosk
#   - Autostart app iPGS fullscreen + unclutter khi vào desktop
#
# BẮT BUỘC chạy SAU khi đã chạy xong 1-install-software.sh (cần unclutter đã
# cài để autostart unclutter.desktop hoạt động).
#
# Chạy:
#   bash scripts/linux-kiosk/2-configure-system.sh [kiosk_user] [app_exec]
#
# Tham số (đều có default):
#   kiosk_user  Mặc định: kztek       — user dùng để autologin GDM.
#   app_exec    Mặc định: ipgskioskavalonia
#               (lệnh có sẵn trong PATH sau khi cài .deb từ scripts/linux-deb/build-deb.sh)
#
# Ví dụ:
#   bash scripts/linux-kiosk/2-configure-system.sh
#   bash scripts/linux-kiosk/2-configure-system.sh kztek /opt/kztek/ipgskioskavalonia/run.sh

set -e

KIOSK_USER="${1:-kztek}"
APP_EXEC="${2:-ipgskioskavalonia}"

echo "=== [2] Cấu hình hệ thống cho Kiosk iPGS — Ubuntu 22.04 ==="
echo "  Kiosk user : $KIOSK_USER"
echo "  App exec   : $APP_EXEC"
echo ""

if [ "$EUID" -eq 0 ]; then
    echo "LỖI: đừng chạy script bằng 'sudo bash ...' hay user root." >&2
    echo "     Chạy trực tiếp: bash scripts/linux-kiosk/2-configure-system.sh" >&2
    exit 1
fi

# ─────────────────────────────────────────────────────────────
echo "=== [1/7] Tắt hot corner, notification banner, screensaver/lock ==="
gsettings set org.gnome.desktop.interface enable-hot-corners false
gsettings set org.gnome.desktop.notifications show-banners false
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.desktop.session idle-delay 0

# ─────────────────────────────────────────────────────────────
echo "=== [2/7] Tắt Ubuntu Dock + Desktop Icons (mặc định bật trên máy mới) ==="
gnome-extensions disable ubuntu-dock@ubuntu.com 2>/dev/null || echo "  → ubuntu-dock@ubuntu.com không có/đã tắt, bỏ qua."
gnome-extensions disable ding@rastersoft.com 2>/dev/null || echo "  → ding@rastersoft.com không có/đã tắt, bỏ qua."

# ─────────────────────────────────────────────────────────────
echo "=== [3/7] Chặn suspend/sleep khi cắm điện (tránh màn hình tắt giữa chừng) ==="
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type 'nothing' 2>/dev/null || true

# ─────────────────────────────────────────────────────────────
echo "=== [4/7] Tắt popup Software Updater ==="
mkdir -p "$HOME/.config/autostart"
if [ -f /etc/xdg/autostart/update-notifier.desktop ]; then
    cat > "$HOME/.config/autostart/update-notifier.desktop" <<EOF
[Desktop Entry]
Hidden=true
EOF
    echo "  → Đã ẩn autostart update-notifier cho user hiện tại."
else
    echo "  → Không thấy update-notifier.desktop, bỏ qua."
fi
gsettings set org.gnome.software download-updates false 2>/dev/null || true

# ─────────────────────────────────────────────────────────────
echo "=== [5/7] Bỏ qua màn hình gnome-initial-setup (nếu user vừa tạo mới) ==="
mkdir -p "$HOME/.config"
touch "$HOME/.config/gnome-initial-setup-done"
echo "  → Đã đánh dấu gnome-initial-setup-done cho '$KIOSK_USER'."

# ─────────────────────────────────────────────────────────────
echo "=== [6/7] Autologin GDM cho user '$KIOSK_USER' ==="
GDM_CONF="/etc/gdm3/custom.conf"
if [ -f "$GDM_CONF" ]; then
    sudo cp "$GDM_CONF" "$GDM_CONF.bak-$(date +%Y%m%d%H%M%S)" 2>/dev/null || true
    if sudo grep -q "^AutomaticLoginEnable" "$GDM_CONF"; then
        sudo sed -i "s/^AutomaticLoginEnable.*/AutomaticLoginEnable = true/" "$GDM_CONF"
    else
        sudo sed -i "/^\[daemon\]/a AutomaticLoginEnable = true" "$GDM_CONF"
    fi
    if sudo grep -q "^AutomaticLogin " "$GDM_CONF"; then
        sudo sed -i "s/^AutomaticLogin .*/AutomaticLogin = $KIOSK_USER/" "$GDM_CONF"
    else
        sudo sed -i "/^AutomaticLoginEnable/a AutomaticLogin = $KIOSK_USER" "$GDM_CONF"
    fi
    echo "  → Đã cập nhật $GDM_CONF (backup: $GDM_CONF.bak-*)"
else
    echo "CẢNH BÁO: không tìm thấy $GDM_CONF — bỏ qua bước autologin, cấu hình thủ công sau." >&2
fi

# ─────────────────────────────────────────────────────────────
echo "=== [7/7] Autostart app iPGS fullscreen + unclutter khi vào desktop ==="
mkdir -p "$HOME/.config/autostart"

cat > "$HOME/.config/autostart/ipgs-kiosk.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=iPGS Kiosk
Exec=$APP_EXEC
X-GNOME-Autostart-enabled=true
EOF
echo "  → Đã tạo $HOME/.config/autostart/ipgs-kiosk.desktop (Exec=$APP_EXEC)"
echo "    Nếu \$APP_EXEC chưa đúng, sửa lại field Exec= trong file trên."

if command -v unclutter >/dev/null 2>&1; then
    cat > "$HOME/.config/autostart/unclutter.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Unclutter
Exec=unclutter -idle 1
X-GNOME-Autostart-enabled=true
EOF
    echo "  → Đã tạo $HOME/.config/autostart/unclutter.desktop"
else
    echo "CẢNH BÁO: chưa thấy lệnh 'unclutter' — chạy 1-install-software.sh trước khi chạy script này." >&2
fi

# ─────────────────────────────────────────────────────────────
echo ""
echo "✓ HOÀN THÀNH. Cần LOG OUT / RESTART để áp dụng đầy đủ (đặc biệt autologin GDM + autostart)."
echo "  Kiểm tra sau khi restart:"
echo "    - Máy tự vào thẳng user '$KIOSK_USER' không cần đăng nhập"
echo "    - App '$APP_EXEC' tự chạy fullscreen"
