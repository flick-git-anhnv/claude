#!/bin/bash
# kiosk-setup-gui.sh — GUI (zenity) chạy TẠI CHỖ trên máy kiosk để setup ẩn Top Bar
# + cấu hình kiosk iPGS, không cần gõ lệnh terminal thủ công.
#
# Dùng khi kỹ thuật viên đứng trực tiếp trước màn hình máy kiosk.
# (Muốn deploy từ xa cho nhiều máy cùng lúc — xem
#  scripts/windows-tools/KioskDeployTool.ps1 chạy trên máy Windows của IT.)
#
# Yêu cầu: gói `zenity` (thường có sẵn trên Ubuntu Desktop). Nếu chưa có:
#   sudo apt install zenity
#
# Chạy (double-click file .desktop tạo bên dưới, hoặc từ terminal):
#   bash scripts/linux-kiosk/kiosk-setup-gui.sh

set -e

# Ép locale UTF-8 tường minh cho zenity — phòng trường hợp script được gọi từ
# ngữ cảnh thiếu LANG/LC_ALL (autostart, cron, .desktop bị strip env...) khiến
# GTK hiển thị tiếng Việt sai (mojibake). Không sửa được nếu bản thân FILE đã
# bị hỏng encoding lúc copy — xem ghi chú "QUAN TRỌNG" bên dưới.
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="en_US.UTF-8"

# QUAN TRỌNG: nếu chữ tiếng Việt trong dialog zenity hiện ra ký tự lỗi
# (VD: "KhÃ´ng cÃ³ gÃ¬") dù đã export locale ở trên — đây LÀ DẤU HIỆU file
# .sh đã bị hỏng encoding trong lúc copy sang máy (thường gặp khi copy qua
# USB/Files app của trình quản lý file, hoặc mở bằng nano/gedit rồi paste).
# Cách fix: xóa file trên máy kiosk, copy lại bằng scp/pscp (giữ nguyên byte,
# không qua GUI file manager):
#   pscp scripts\linux-kiosk\kiosk-setup-gui.sh <user>@<ip>:~/
# Kiểm tra nhanh file trên máy kiosk có đúng UTF-8 không:
#   file kiosk-setup-gui.sh   # phải báo "UTF-8 Unicode text", không phải "ISO-8859" / "ASCII text, with..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT1="$SCRIPT_DIR/1-install-software.sh"
SCRIPT2="$SCRIPT_DIR/2-configure-system.sh"
SCRIPT3="$SCRIPT_DIR/3-toggle-topbar.sh"

if ! command -v zenity >/dev/null 2>&1; then
    echo "LỖI: chưa cài zenity. Chạy: sudo apt install zenity" >&2
    exit 1
fi

# ─────────────────────────────────────────────────────────────
# Bước 1: Chọn các bước muốn chạy
CHOICE=$(zenity --list --checklist \
    --title="Setup Kiosk iPGS" \
    --text="Chọn các bước muốn thực hiện:" \
    --width=520 --height=280 \
    --column="Chọn" --column="Bước" \
    TRUE  "1. Cài phần mềm (extension ẩn top bar + unclutter)" \
    TRUE  "2. Cấu hình hệ thống (autologin, autostart, tắt dock/sleep/update popup...)" \
    --separator=";")

if [ -z "$CHOICE" ]; then
    zenity --info --title="Đã hủy" --text="Không chọn bước nào — thoát." 2>/dev/null || true
    exit 0
fi

RUN_STEP1=false
RUN_STEP2=false
[[ "$CHOICE" == *"1. Cài phần mềm"* ]] && RUN_STEP1=true
[[ "$CHOICE" == *"2. Cấu hình hệ thống"* ]] && RUN_STEP2=true

# ─────────────────────────────────────────────────────────────
# Bước 1b: Ẩn / hiện lại Top Bar-Dock (độc lập, không cần cài lại phần mềm)
TOGGLE_CHOICE=$(zenity --list --radiolist \
    --title="Top Bar / Dock" \
    --text="Bạn muốn ẩn hay hiện lại Top Bar/Dock/Desktop Icons?" \
    --width=480 --height=220 \
    --column="Chọn" --column="Tùy chọn" \
    TRUE  "Không đổi (giữ nguyên trạng thái hiện tại)" \
    FALSE "Ẩn Top Bar/Dock/Desktop Icons" \
    FALSE "Hiện lại Top Bar/Dock/Desktop Icons (undo)")

TOGGLE_MODE=""
case "$TOGGLE_CHOICE" in
    "Ẩn Top Bar"*) TOGGLE_MODE="hide" ;;
    "Hiện lại"*)   TOGGLE_MODE="show" ;;
esac

if ! $RUN_STEP1 && ! $RUN_STEP2 && [ -z "$TOGGLE_MODE" ]; then
    zenity --info --title="Không có gì để làm" --text="Bạn chưa chọn hành động nào — thoát." 2>/dev/null || true
    exit 0
fi

# ─────────────────────────────────────────────────────────────
# Bước 2: Nếu chọn bước 2, hỏi kiosk_user + app_exec
KIOSK_USER="$USER"
APP_EXEC="ipgskioskavalonia"

if $RUN_STEP2; then
    FORM_RESULT=$(zenity --forms \
        --title="Cấu hình kiosk" \
        --text="Nhập thông tin cho bước cấu hình hệ thống:" \
        --add-entry="User dùng để autologin (mặc định: $USER)" \
        --add-entry="Lệnh chạy app iPGS (mặc định: ipgskioskavalonia)" \
        --separator="|")

    if [ -n "$FORM_RESULT" ]; then
        F_USER="$(echo "$FORM_RESULT" | cut -d'|' -f1)"
        F_EXEC="$(echo "$FORM_RESULT" | cut -d'|' -f2)"
        [ -n "$F_USER" ] && KIOSK_USER="$F_USER"
        [ -n "$F_EXEC" ] && APP_EXEC="$F_EXEC"
    fi
fi

# ─────────────────────────────────────────────────────────────
# Bước 3: Xác nhận
SUMMARY="Sẽ thực hiện:\n"
$RUN_STEP1 && SUMMARY="${SUMMARY}\n✓ Cài phần mềm (1-install-software.sh)"
$RUN_STEP2 && SUMMARY="${SUMMARY}\n✓ Cấu hình hệ thống (kiosk_user=$KIOSK_USER, app_exec=$APP_EXEC)"
[ "$TOGGLE_MODE" = "hide" ] && SUMMARY="${SUMMARY}\n✓ Ẩn Top Bar/Dock/Desktop Icons"
[ "$TOGGLE_MODE" = "show" ] && SUMMARY="${SUMMARY}\n✓ Hiện lại Top Bar/Dock/Desktop Icons"
SUMMARY="${SUMMARY}\n\nLƯU Ý: nếu chạy lần đầu bước 'Cài phần mềm', GNOME Shell sẽ hiện\npopup xác nhận cài extension trên màn hình — hãy bấm 'Install' khi thấy."

zenity --question --title="Xác nhận" --width=480 --text="$SUMMARY" || exit 0

# ─────────────────────────────────────────────────────────────
# Bước 4: Chạy trong 1 cửa sổ terminal thật (để sudo + popup xác nhận hoạt động
# bình thường — không cố gắng relay password qua zenity cho phức tạp/kém an toàn).
CMD=""
$RUN_STEP1 && CMD="${CMD}bash '$SCRIPT1'; "
$RUN_STEP2 && CMD="${CMD}bash '$SCRIPT2' '$KIOSK_USER' '$APP_EXEC'; "
[ -n "$TOGGLE_MODE" ] && CMD="${CMD}bash '$SCRIPT3' '$TOGGLE_MODE'; "
CMD="${CMD}echo; echo '=== Đã chạy xong — Enter để đóng cửa sổ này ==='; read"

# GHI CHÚ (gotcha đã gặp thực tế): `gnome-terminal` mặc định KHÔNG tự mở cửa
# sổ — nó gọi qua D-Bus tới service "org.gnome.Terminal" (factory) để 1 tiến
# trình gnome-terminal-server có sẵn mở window giúp. Nếu server đó chưa chạy/
# bị treo, D-Bus service activation timeout → lỗi
# "Error calling StartServiceByName for org.gnome.Terminal: Timeout was reached"
# và KHÔNG có cửa sổ nào mở ra. Dùng `--disable-factory` để gnome-terminal tự
# chạy như 1 tiến trình standalone, không phụ thuộc D-Bus factory — né lỗi này
# hoàn toàn. Nếu máy nào đó gnome-terminal vẫn lỗi kiểu khác → fallback xterm.
# `--disable-factory` làm gnome-terminal chạy như tiến trình standalone
# (không hỏi D-Bus factory nữa) NHƯNG cũng có nghĩa lệnh sẽ BLOCK đến khi cửa
# sổ đóng — phải tự `&` để background, rồi kiểm tra sau ~1s xem tiến trình còn
# sống không (proxy cho "mở thành công") trước khi fallback sang xterm.
ERR_LOG="$(mktemp)"
TERMINAL_LAUNCHED=false
if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal --disable-factory --title="Kiosk Setup iPGS" -- bash -c "$CMD" 2>"$ERR_LOG" &
    GT_PID=$!
    sleep 1
    if kill -0 "$GT_PID" 2>/dev/null; then
        TERMINAL_LAUNCHED=true
    else
        wait "$GT_PID" 2>/dev/null
        cat "$ERR_LOG" >&2 2>/dev/null || true
    fi
fi
if ! $TERMINAL_LAUNCHED && command -v xterm >/dev/null 2>&1; then
    xterm -T "Kiosk Setup iPGS" -e bash -c "$CMD" &
    TERMINAL_LAUNCHED=true
fi
if ! $TERMINAL_LAUNCHED; then
    zenity --error --text="Không mở được cửa sổ terminal (gnome-terminal lỗi D-Bus factory, không có xterm dự phòng).\n\nChạy tay bằng lệnh:\n$CMD" 2>/dev/null || true
    rm -f "$ERR_LOG"
    exit 1
fi
rm -f "$ERR_LOG"

zenity --info --title="Đã khởi chạy" \
    --text="Đã mở cửa sổ terminal để chạy setup.\nTheo dõi tiến trình và nhập mật khẩu sudo (nếu được hỏi) ngay trong cửa sổ đó.\n\nSau khi xong, RESTART máy để áp dụng đầy đủ (autologin + autostart)." \
    2>/dev/null || true
