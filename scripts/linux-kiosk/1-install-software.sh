#!/bin/bash
# 1-install-software.sh — Cài phần mềm/extension cần thiết để ẩn Top Bar GNOME.
#
# Phần "phần mềm" trong bộ setup kiosk iPGS (tách từ setup-kiosk.sh):
#   - Cài python3-pip + gnome-extensions-cli (gext)
#   - Cài + bật extension "Just Perfection"
#   - Compile schema + set các key ẩn UI (panel/top bar, activities button, dash,
#     workspace switcher)
#   - Cài package "unclutter" (ẩn con trỏ chuột — cũng là 1 phần mềm cần cài)
#
# Đã test thực tế trên máy kiosk 192.168.21.230 (Ubuntu 22.04, GNOME Shell 42).
#
# BẮT BUỘC: chạy trong phiên desktop (GUI) thật của user kiosk — không SSH thuần,
# không "sudo bash ...” cả script (script tự sudo khi cần).
#
# GHI CHÚ QUAN TRỌNG rút ra từ lần test đầu: bước "gext install <uuid>" gọi
# D-Bus method InstallRemoteExtension của GNOME Shell — Shell sẽ hiện 1 popup
# xác nhận NGAY TRÊN MÀN HÌNH VẬT LÝ của máy (không thấy được qua SSH), và có
# timeout ngắn (~24s). Nếu không có người đứng trước màn hình bấm "Install"
# kịp, bước này sẽ báo lỗi "Timeout was reached (24)" — không phải lỗi script,
# chỉ cần chạy lại (script idempotent, đã cài rồi sẽ tự bỏ qua) sau khi đã bấm
# xác nhận, hoặc đứng trước màn hình kiosk khi chạy lần đầu để bấm popup đó.
#
# Chạy:
#   bash scripts/linux-kiosk/1-install-software.sh

set -e

EXT_UUID="just-perfection-desktop@just-perfection"
EXT_DIR="$HOME/.local/share/gnome-shell/extensions/$EXT_UUID"

echo "=== [1] Cài phần mềm cho Kiosk iPGS — Ubuntu 22.04 ==="
echo "  Home hiện tại: $HOME"
echo ""

if [ "$EUID" -eq 0 ]; then
    echo "LỖI: đừng chạy script bằng 'sudo bash ...' hay user root." >&2
    echo "     Chạy trực tiếp: bash scripts/linux-kiosk/1-install-software.sh" >&2
    exit 1
fi

# ─────────────────────────────────────────────────────────────
echo "=== [1/4] Cài python3-pip + gnome-extensions-cli ==="
if ! command -v pip3 >/dev/null 2>&1; then
    sudo apt install -y python3-pip
else
    echo "  → pip3 đã có, bỏ qua."
fi

export PATH="$HOME/.local/bin:$PATH"
if ! command -v gext >/dev/null 2>&1; then
    pip3 install --user gnome-extensions-cli
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "  → gext đã có, bỏ qua."
fi

if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi

# ─────────────────────────────────────────────────────────────
echo "=== [2/4] Cài + bật extension Just Perfection ==="
if ! gnome-extensions list 2>/dev/null | grep -q "^$EXT_UUID$"; then
    echo "  → LƯU Ý: GNOME Shell sẽ hiện popup xác nhận trên màn hình — hãy đứng"
    echo "    trước màn hình kiosk và bấm 'Install' trong vài giây tới."
    gext install "$EXT_UUID"
else
    echo "  → Extension đã cài, bỏ qua bước install."
fi
gnome-extensions enable "$EXT_UUID" || true

STATE="$(gnome-extensions info "$EXT_UUID" 2>/dev/null | grep 'State:' | awk '{print $2}')"
if [ "$STATE" != "ENABLED" ]; then
    echo "CẢNH BÁO: extension chưa ở trạng thái ENABLED (State: $STATE)." >&2
    echo "          Có thể cần log out/log in lại rồi chạy lại script." >&2
fi

# ─────────────────────────────────────────────────────────────
echo "=== [3/4] Compile schema + ẩn Top Bar + UI phụ ==="
if [ ! -d "$EXT_DIR/schemas" ]; then
    echo "LỖI: không tìm thấy $EXT_DIR/schemas — extension có cài đúng không?" >&2
    exit 1
fi
glib-compile-schemas "$EXT_DIR/schemas/"
gsettings --schemadir "$EXT_DIR/schemas/" set org.gnome.shell.extensions.just-perfection panel false
gsettings --schemadir "$EXT_DIR/schemas/" set org.gnome.shell.extensions.just-perfection activities-button false || true
gsettings --schemadir "$EXT_DIR/schemas/" set org.gnome.shell.extensions.just-perfection workspace-switcher-should-show false || true
gsettings --schemadir "$EXT_DIR/schemas/" set org.gnome.shell.extensions.just-perfection dash false || true
# Bản v26 không còn key "overview" riêng — đã bỏ (xem GHI CHÚ ở đầu file gốc
# setup-kiosk.sh / docs/devops/KIOSK-SETUP-hide-topbar-ubuntu2204.md).

# ─────────────────────────────────────────────────────────────
echo "=== [4/4] Cài unclutter (ẩn con trỏ chuột) ==="
if ! dpkg -s unclutter >/dev/null 2>&1; then
    sudo apt install -y unclutter
else
    echo "  → unclutter đã cài, bỏ qua."
fi

echo ""
echo "✓ Xong phần cài phần mềm. Chạy tiếp: bash scripts/linux-kiosk/2-configure-system.sh [kiosk_user] [app_exec]"
