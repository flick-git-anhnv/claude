#!/bin/bash
# build-deb.sh — Đóng gói IPGS.Kiosk.Avalonia thành file .deb cho Linux (Debian/Ubuntu).
#
# Sinh bởi /gen-build-deb, viết theo spec đúc kết từ ParkingV8 (KHÔNG có sẵn template
# ParkingV8 để copy 1:1 trong repo này — xem .claude/commands/gen-build-deb.md).
#
# Chạy: bash scripts/linux-deb/build-deb.sh [version]
# Version mặc định "1.0.0" nếu không truyền.
set -e

VERSION="${1:-1.0.0}"
ARCH="amd64"

PKG_NAME="kztek-ipgskioskavalonia"
INSTALL_DIR="/opt/kztek/ipgskioskavalonia"
INSTALL_PARENT_DIR="$(dirname "$INSTALL_DIR")"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
APP_PROJECT="$REPO_ROOT/IPGS.Kiosk.Avalonia/IPGS.Kiosk.Avalonia.csproj"
BIN_NAME="IPGS.Kiosk.Avalonia"
DIST_DIR="$REPO_ROOT/dist"
mkdir -p "$DIST_DIR"

# ─────────────────────────────────────────────────────────────────────────
# GOTCHA (đặc thù máy dev hiện tại — KHÔNG áp dụng nếu chạy trên CI Linux thuần):
# IPGS.Kiosk.Avalonia.csproj có <ProjectReference> trỏ tuyệt đối kiểu Windows
# ("E:\KZTEK\...\parking-v8-app-avalonia\...") sang repo song song. dotnet của
# WSL/Linux không hiểu path này (đường dẫn ổ đĩa Windows + backslash không phải
# tuyệt đối trên Linux) → MSBuild nối nhầm thành path con vô nghĩa và "Skip"
# project đó, kéo theo lỗi CS0246/CS0234 (thiếu namespace Kztek.Tool/Object/Api).
# Do đó: dotnet publish PHẢI chạy bằng dotnet.exe NGUYÊN GỐC TRÊN WINDOWS
# (Git Bash/PowerShell) — nơi các path đó hợp lệ. dpkg-deb thì chỉ có trên
# Linux/WSL. Script tự dò môi trường và tách 2 việc này cho đúng chỗ.
# ─────────────────────────────────────────────────────────────────────────
IS_WINDOWS_SHELL=false
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) IS_WINDOWS_SHELL=true ;;
esac

PUBLISH_DIR="$REPO_ROOT/IPGS.Kiosk.Avalonia/bin/Release/net8.0/linux-x64/deb-publish"

echo "=== [1/7] dotnet publish (self-contained linux-x64) ==="
rm -rf "$PUBLISH_DIR"
mkdir -p "$PUBLISH_DIR"

if $IS_WINDOWS_SHELL; then
    if ! command -v dotnet >/dev/null 2>&1; then
        echo "LỖI: không tìm thấy dotnet trên PATH (cần dotnet SDK Windows để publish do ProjectReference dùng path tuyệt đối Windows)." >&2
        exit 1
    fi
    dotnet publish "$APP_PROJECT" -c Release -r linux-x64 --self-contained true -p:PublishSingleFile=false -o "$PUBLISH_DIR"
else
    # Đang chạy trong Linux/WSL thật: thử dotnet local trước; nếu ProjectReference
    # tuyệt đối Windows làm publish fail, GỌI NGƯỢC ra dotnet.exe Windows qua wsl.exe
    # không khả dụng từ trong WSL — trường hợp này cần user tự publish trên Windows
    # rồi trỏ PUBLISH_DIR vào output đó bằng biến môi trường PUBLISH_DIR_OVERRIDE.
    if [ -n "$PUBLISH_DIR_OVERRIDE" ]; then
        PUBLISH_DIR="$PUBLISH_DIR_OVERRIDE"
    else
        dotnet publish "$APP_PROJECT" -c Release -r linux-x64 --self-contained true -p:PublishSingleFile=false -o "$PUBLISH_DIR"
    fi
fi

echo "=== [2/7] Kiểm tra binary + launcher đã publish ==="
if [ ! -f "$PUBLISH_DIR/$BIN_NAME" ]; then
    echo "LỖI: không thấy binary $BIN_NAME sau khi publish tại $PUBLISH_DIR." >&2
    exit 1
fi
if [ ! -f "$PUBLISH_DIR/run.sh" ]; then
    echo "LỖI: thiếu run.sh — kiểm tra target PublishLinuxLauncher trong .csproj." >&2
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────
# GOTCHA: build .deb ở /tmp (filesystem Linux thật), KHÔNG build trực tiếp
# trên /mnt/<ổ Windows> khi chạy qua WSL. DrvFs (mount ổ Windows trong WSL2)
# không đảm bảo đầy đủ permission bit/symlink mà dpkg-deb cần — build ngay
# trên /mnt/* từng gây lỗi ngầm khó chẩn đoán (dpkg-deb báo lỗi permission
# vô lý, hoặc .deb thiếu file). Nếu đang ở Windows shell, phần đóng gói
# dpkg-deb PHẢI nhảy sang WSL qua wsl.exe.
# ─────────────────────────────────────────────────────────────────────────
INNER_SCRIPT="$SCRIPT_DIR/_pack-deb-inner.sh"

pack_in_wsl() {
    local publish_dir_wsl="$1"
    local dist_dir_wsl="$2"
    local inner_script_wsl="$3"

    # GOTCHA: Git Bash/MSYS tự dịch argument dạng "/mnt/e/..." thành path Windows
    # (chèn "C:/Program Files/.../Git" phía trước) trước khi truyền cho wsl.exe —
    # vì wsl.exe là native exe, không phải MSYS binary. Phải set MSYS_NO_PATHCONV=1
    # để tắt dịch path, nếu không wsl.exe nhận path sai và báo "No such file or directory".
    MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash "$inner_script_wsl" "$PKG_NAME" "$VERSION" "$ARCH" "$INSTALL_DIR" "$BIN_NAME" "$publish_dir_wsl" "$dist_dir_wsl"
}

# Chuyển path Windows (E:\... hoặc /e/... của Git Bash) sang path WSL (/mnt/e/...)
to_wsl_path() {
    local p="$1"
    p="$(cd "$p" 2>/dev/null && pwd -W 2>/dev/null || echo "$p")"   # ưu tiên pwd -W nếu có (Git Bash)
    p="${p//\\//}"
    if [[ "$p" =~ ^([A-Za-z]):(.*)$ ]]; then
        local drive="${BASH_REMATCH[1],,}"
        echo "/mnt/$drive${BASH_REMATCH[2]}"
    elif [[ "$p" =~ ^/([A-Za-z])/(.*)$ ]]; then
        local drive="${BASH_REMATCH[1],,}"
        echo "/mnt/$drive/${BASH_REMATCH[2]}"
    else
        echo "$p"
    fi
}

echo "=== [3/7] Chuẩn bị đóng gói .deb ==="
if command -v dpkg-deb >/dev/null 2>&1 && ! $IS_WINDOWS_SHELL; then
    echo "=== [4-7/7] dpkg-deb chạy local (đang ở Linux/WSL thật) ==="
    OUT="$(bash "$INNER_SCRIPT" "$PKG_NAME" "$VERSION" "$ARCH" "$INSTALL_DIR" "$BIN_NAME" "$PUBLISH_DIR" "$DIST_DIR")"
    echo "$OUT"
    DEB_BASENAME="$(echo "$OUT" | sed -n 's/^WSL_DEB_FILE=//p' | tr -d '\r')"
else
    if ! command -v wsl.exe >/dev/null 2>&1; then
        echo "LỖI: không có dpkg-deb local và cũng không có wsl.exe để đóng gói .deb." >&2
        exit 1
    fi
    PUBLISH_DIR_WSL="$(to_wsl_path "$PUBLISH_DIR")"
    DIST_DIR_WSL="$(to_wsl_path "$DIST_DIR")"
    INNER_SCRIPT_WSL="$(to_wsl_path "$INNER_SCRIPT")"
    echo "    Publish dir (WSL view): $PUBLISH_DIR_WSL"
    echo "=== [4-7/7] dpkg-deb chạy trong WSL (Ubuntu) ==="
    OUT="$(pack_in_wsl "$PUBLISH_DIR_WSL" "$DIST_DIR_WSL" "$INNER_SCRIPT_WSL")"
    echo "$OUT"
    DEB_BASENAME="$(echo "$OUT" | sed -n 's/^WSL_DEB_FILE=//p' | tr -d '\r')"
fi

if [ -z "$DEB_BASENAME" ] || [ ! -f "$DIST_DIR/$DEB_BASENAME" ]; then
    echo "LỖI: không thấy file .deb sau khi đóng gói trong $DIST_DIR." >&2
    exit 1
fi

echo ""
echo "✓ Build thành công: $DIST_DIR/$DEB_BASENAME"
echo "  Cài thử (trong WSL/Linux): sudo dpkg -i $DIST_DIR/$DEB_BASENAME"
