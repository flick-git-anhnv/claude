#!/bin/bash
# _pack-deb-inner.sh — Việc đóng gói .deb thực sự, chạy TRONG Linux/WSL thật
# (dpkg-deb, chmod, symlink cần filesystem Linux thật, không phải /mnt DrvFs).
# Được gọi bởi build-deb.sh — KHÔNG chạy tay trừ khi debug.
#
# Args: $1=PKG_NAME $2=VERSION $3=ARCH $4=INSTALL_DIR $5=BIN_NAME
#       $6=PUBLISH_DIR (đường dẫn WSL tới output dotnet publish)
#       $7=DIST_DIR (đường dẫn WSL nơi copy .deb hoàn chỉnh ra)
set -e

PKG_NAME="$1"
VERSION="$2"
ARCH="$3"
INSTALL_DIR="$4"
BIN_NAME="$5"
PUBLISH_DIR="$6"
DIST_DIR="$7"
INSTALL_PARENT_DIR="$(dirname "$INSTALL_DIR")"

BUILD_DIR="/tmp/kztek-deb-build/$PKG_NAME"
PKG_ROOT="$BUILD_DIR/pkgroot"

rm -rf "$BUILD_DIR"
mkdir -p "$PKG_ROOT$INSTALL_DIR" "$PKG_ROOT/DEBIAN" "$PKG_ROOT/usr/bin" "$DIST_DIR"

echo "--- copy publish output vào filesystem Linux thật (tránh build .deb trên /mnt/*) ---"
cp -a "$PUBLISH_DIR"/. "$PKG_ROOT$INSTALL_DIR/"
chmod +x "$PKG_ROOT$INSTALL_DIR/$BIN_NAME" "$PKG_ROOT$INSTALL_DIR/run.sh" "$PKG_ROOT$INSTALL_DIR/install.sh"
ln -sf "$INSTALL_DIR/run.sh" "$PKG_ROOT/usr/bin/ipgskioskavalonia"

INSTALLED_SIZE=$(du -sk "$PKG_ROOT$INSTALL_DIR" | cut -f1)
cat > "$PKG_ROOT/DEBIAN/control" <<CTRL
Package: $PKG_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Installed-Size: $INSTALLED_SIZE
Maintainer: KZTEK <admin@kztek.net>
Depends: libc6, libgcc-s1, libstdc++6, zlib1g, libicu70 | libicu72 | libicu74 | libicu76
Description: IPGS Kiosk Avalonia - KZTEK parking payment kiosk (Avalonia UI)
 Ứng dụng kiosk thanh toán gửi xe IPGS, giao diện Avalonia, chạy self-contained
 trên Linux (net8.0, linux-x64).
CTRL

cat > "$PKG_ROOT/DEBIAN/postinst" <<PINST
#!/bin/bash
set -e
# GOTCHA: chown cả thư mục CHA ($INSTALL_PARENT_DIR), không chỉ INSTALL_DIR — thiếu quyền
# write lên cấp cha khiến app ghi log/temp bị denied ngầm -> chạy chậm/đơ, khó phát hiện.
TARGET_USER="\${SUDO_USER:-\$(logname 2>/dev/null || echo root)}"
chmod -R 777 "$INSTALL_DIR"
chown -R "\$TARGET_USER":"\$TARGET_USER" "$INSTALL_PARENT_DIR"
if [ "\$TARGET_USER" != "root" ]; then
    su - "\$TARGET_USER" -c "bash '$INSTALL_DIR/install.sh'" || true
else
    bash "$INSTALL_DIR/install.sh" || true
fi
exit 0
PINST

cat > "$PKG_ROOT/DEBIAN/postrm" <<'PRM'
#!/bin/bash
set -e
rm -f "$HOME/.local/share/applications/kztek-ipgskioskavalonia.desktop" 2>/dev/null || true
rm -f "$HOME/Desktop/kztek-ipgskioskavalonia.desktop" 2>/dev/null || true
exit 0
PRM

chmod +x "$PKG_ROOT/DEBIAN/postinst" "$PKG_ROOT/DEBIAN/postrm"

DEB_FILE="$BUILD_DIR/${PKG_NAME}_${VERSION}_${ARCH}.deb"
dpkg-deb --build --root-owner-group "$PKG_ROOT" "$DEB_FILE"
cp "$DEB_FILE" "$DIST_DIR/"
echo "WSL_DEB_FILE=$(basename "$DEB_FILE")"
