#!/bin/bash
# 3-toggle-topbar.sh — Ẩn HOẶC hiện lại Top Bar/Dock GNOME bất kỳ lúc nào,
# không cần cài lại phần mềm (dùng khi cần bật lại giao diện đầy đủ để debug,
# bảo trì, hoặc bàn giao máy).
#
# Chạy:
#   bash scripts/linux-kiosk/3-toggle-topbar.sh hide   # ẩn top bar + dock + icon desktop
#   bash scripts/linux-kiosk/3-toggle-topbar.sh show   # hiện lại như mặc định Ubuntu

set -e

MODE="$1"
if [ "$MODE" != "hide" ] && [ "$MODE" != "show" ]; then
    echo "Cách dùng: bash $0 {hide|show}" >&2
    exit 1
fi

EXT_UUID="just-perfection-desktop@just-perfection"
EXT_DIR="$HOME/.local/share/gnome-shell/extensions/$EXT_UUID"
SCHEMA_DIR="$EXT_DIR/schemas"

if [ "$MODE" = "hide" ]; then
    VALUE="false"
    DOCK_ACTION="disable"
    echo "=== Ẩn Top Bar + Dock + Desktop Icons ==="
else
    VALUE="true"
    DOCK_ACTION="enable"
    echo "=== Hiện lại Top Bar + Dock + Desktop Icons ==="
fi

if [ -d "$SCHEMA_DIR" ]; then
    gsettings --schemadir "$SCHEMA_DIR" set org.gnome.shell.extensions.just-perfection panel $VALUE
    gsettings --schemadir "$SCHEMA_DIR" set org.gnome.shell.extensions.just-perfection activities-button $VALUE || true
    gsettings --schemadir "$SCHEMA_DIR" set org.gnome.shell.extensions.just-perfection workspace-switcher-should-show $VALUE || true
    gsettings --schemadir "$SCHEMA_DIR" set org.gnome.shell.extensions.just-perfection dash $VALUE || true
    echo "  → Đã đặt panel/activities-button/workspace-switcher/dash = $VALUE"
else
    echo "CẢNH BÁO: chưa cài extension Just Perfection (chạy 1-install-software.sh trước)." >&2
fi

gnome-extensions $DOCK_ACTION ubuntu-dock@ubuntu.com 2>/dev/null || echo "  → ubuntu-dock@ubuntu.com không có, bỏ qua."
gnome-extensions $DOCK_ACTION ding@rastersoft.com 2>/dev/null || echo "  → ding@rastersoft.com không có, bỏ qua."

echo "✓ Xong. Có thể áp dụng ngay, không cần restart."
