# Cài .deb xong không có icon app — `.desktop` trỏ đường dẫn tuyệt đối + thiếu icon cấp hệ thống

**Category:** linux-desktop
**Ngày ghi:** 2026-07-27
**Project gặp:** iPGSv4 (`IPGSUseCam`, Avalonia, self-contained linux-x64)
**Phân loại:** Lỗi / Gotcha

---

## 1. Bối cảnh

Script `scripts/linux-deb/build-deb.sh` đóng gói app Avalonia thành `.deb`. Sau `sudo dpkg -i kztek-ipgsusecam_1.0.0_amd64.deb`:

- App chạy được bằng lệnh `ipgsusecam` ✅
- Menu ứng dụng KHÔNG thấy app ❌
- Shortcut Desktop (nếu có) hiện icon trắng/generic ❌
- Không có thông báo lỗi nào trong quá trình cài ❌

## 2. Nguyên nhân — HAI lỗi độc lập, phải sửa cả hai

### Lỗi 1 — Typo trong đường dẫn `Icon=`

`deploy-linux/kztek-ipgsusecam.desktop`:

```ini
Icon=__APP_DIR__/.iIPGSUseCam/appIcon.png   # ← thừa chữ "i"
```

`install.sh` lại tạo thư mục `.IPGSUseCam` (không có `i`). Đường dẫn không tồn tại → desktop environment **im lặng bỏ qua**, không log, không cảnh báo.

### Lỗi 2 — Gói .deb không chứa icon ở đường dẫn hệ thống

Gói chỉ dựa vào `postinst` gọi:

```bash
runuser -l "$TARGET_USER" -c "bash '$INSTALL_DIR/install.sh'" || true
```

Bước này **im lặng thất bại** (`|| true`) trong ít nhất 3 tình huống rất phổ biến:

| Tình huống | Vì sao hỏng |
|---|---|
| Cài bằng `apt install ./file.deb` hoặc gdebi | `SUDO_USER` rỗng → `TARGET_USER=root` → nhánh bị bỏ qua hoàn toàn |
| Máy tối giản/container không có `runuser` | Điều kiện `command -v runuser` false → bỏ qua |
| Máy nhiều user | Chỉ user cài mới có icon, user khác không có gì |

## 3. Cách xử lý đúng (đã áp dụng)

1. **Sửa typo** `.iIPGSUseCam` → `.IPGSUseCam` trong `.desktop` nguồn (vẫn cần cho bản giải nén thủ công).
2. **Đóng gói icon vào icon theme chuẩn** trong `build-deb.sh`:
   ```bash
   install -m 644 "$ICON_SRC" "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps/$ICON_NAME.png"
   install -m 644 "$ICON_SRC" "$BUILD_DIR/usr/share/pixmaps/$ICON_NAME.png"   # fallback DE cũ
   ```
   > Kích thước thư mục (`256x256`) PHẢI khớp kích thước thật của file PNG, nếu không icon bị scale xấu hoặc bị bỏ qua.
3. **Sinh `.desktop` hệ thống** tại `/usr/share/applications/` dùng **TÊN icon**, không phải đường dẫn:
   ```ini
   Exec=/usr/bin/ipgsusecam
   Icon=kztek-ipgsusecam        # ← không đuôi .png, không đường dẫn
   ```
4. **Refresh cache trong `postinst`** — thiếu bước này icon vẫn trống dù file đã đúng chỗ:
   ```bash
   gtk-update-icon-cache -f -t /usr/share/icons/hicolor >/dev/null 2>&1 || true
   update-desktop-database -q /usr/share/applications >/dev/null 2>&1 || true
   ```
5. **Shortcut Desktop:** lấy home qua `getent passwd "$TARGET_USER" | cut -d: -f6` — KHÔNG dùng `$HOME` (trong `postinst` `$HOME` là của root). Chỉ copy ra `~/Desktop`, **không** cài thêm vào `~/.local/share/applications` vì menu đã có bản hệ thống → tránh trùng 2 mục.
6. **`postrm`** dọn đúng file Desktop của user đó + refresh lại cache.

## 4. Bài học tổng quát

> Với gói `.deb` có GUI: icon phải nằm trong icon theme chuẩn (`/usr/share/icons/hicolor/<size>/apps/`) và `.desktop` phải dùng `Icon=<tên>`. **Không bao giờ** dựa vào script chạy theo user trong `postinst` để tạo shortcut — nó phụ thuộc biến môi trường không đảm bảo tồn tại (`SUDO_USER`, `logname`) và theo thông lệ luôn bị nuốt lỗi bằng `|| true`.

## 5. Mẹo chẩn đoán (nhanh, không cần cài thử)

```bash
dpkg -c file.deb | grep -E 'icons/hicolor|share/applications'
```

Không ra dòng nào → chắc chắn mất icon. Kiểm tra thêm nội dung `.desktop`:

```bash
dpkg-deb --fsys-tarfile file.deb | tar -xO ./usr/share/applications/*.desktop
```

`Icon=` mà là đường dẫn tuyệt đối → dấu hiệu sai chuẩn, dễ vỡ.

## 6. KHÔNG cần làm lại

- Không cần cố sửa `install.sh`/`runuser` cho chạy được — kể cả chạy đúng vẫn sai chuẩn Debian và hỏng khi cài bằng apt.
- Không cần thử đổi `Icon=` sang đường dẫn tuyệt đối "cho chắc" — nó vỡ khi gỡ cài/di chuyển thư mục.

## Liên quan

- `dconf-system-db-profile-required.md` — cùng nhóm "cấu hình desktop Linux bị bỏ qua âm thầm khi thiếu điều kiện ngầm".

## 7. Tái phát 2026-07-28 — regenerate skill copy lại đúng bản lỗi

`/gen-build-deb` quy trình 6 bước quy định "dùng file `.sh` hiện có trong repo làm nguồn" khi user yêu cầu tạo lại — nhưng bản `scripts/linux-deb/build-deb.sh`/`_pack-deb-inner.sh` đang nằm trong repo (project `IPGSv4`, đổi tên từ `IPGSUseCam`) lại CHÍNH LÀ bản lỗi mô tả ở mục 2 (chưa từng được áp fix này), không phải bản đã sửa. Agent đọc rồi ghi đè y hệt → khôi phục lại lỗi cũ, tưởng "tạo mới" là an toàn vì nội dung "trông đầy đủ, không thiếu gì".

**Bài học:** Khi regenerate/refresh 1 script build-deb đã tồn tại trong repo, PHẢI so nội dung với checklist mục 3 (icon theme, `.desktop` hệ thống dùng `Icon=<tên>`, `gtk-update-icon-cache`/`update-desktop-database` trong postinst) TRƯỚC khi coi bản hiện có là "đúng, không cần sửa gì". Không suy luận "file có vẻ đầy đủ + không báo lỗi build" = đã áp fix — phải grep trực tiếp các dấu hiệu (`icons/hicolor`, `gtk-update-icon-cache`) trong chính file, hoặc chạy lệnh chẩn đoán mục 5 trên `.deb` build ra.
