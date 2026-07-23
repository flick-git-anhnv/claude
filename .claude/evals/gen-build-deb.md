---
agent: gen-build-deb
created: 2026-07-21
author: senior-developer (rút ra từ session fix linux-deb/icon/permission của ParkingV8 Avalonia)
status: draft
---

# EVAL: gen-build-deb

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `/gen-build-deb` trước khi implement — Eval-Driven Development (EDD).
> **Khi tạo:** File này PHẢI có TRƯỚC `.claude/commands/gen-build-deb.md`.
> **Khi chạy:** Sau khi implement, chạy thử từng example và ghi kết quả vào bảng "Kết quả chạy thử".

---

## 1. Mô tả năng lực (Capability Statement)

`gen-build-deb` khảo sát 1 project .NET/Avalonia (WinExe/Exe, có publish `linux-x64`) do user chỉ định, rồi sinh ra `scripts/linux-deb/build-deb.sh` cùng các file phụ trợ bắt buộc (`deploy-linux/run.sh`, `install.sh`, `<pkg>.desktop`, `appIcon.png`, target `PublishLinuxLauncher` trong `.csproj`) — đóng gói toàn bộ bài học đã rút ra từ ParkingV8 (icon PNG không dùng `.ico`, `postinst` chown cả thư mục cha, wrapper `LD_LIBRARY_PATH`, build ở `/tmp` tránh lỗi DrvFs). Được gọi khi user muốn tạo cơ chế đóng gói `.deb` cho 1 project khác, không tự chạy build.

---

## 2. Capability Evals

### CE-01 — Happy path: project Avalonia có sẵn icon `.ico`

**Input:** `/gen-build-deb path/to/SomeApp` — project có 1 `.csproj` loại `WinExe`/`Exe`, có 1 file `.ico` tìm được trong project hoặc project WinForms cùng solution.

**Output mong đợi:**
- [ ] Tạo `scripts/linux-deb/build-deb.sh` với `PKG_NAME`/`APP_PROJECT`/`INSTALL_DIR` đúng theo project đó (không copy nguyên si tên `ParkingV8`/`kztek-parkingv8`)
- [ ] Tạo `deploy-linux/appIcon.png` trích từ `.ico` tìm được (không giữ `.ico` làm Icon= cuối cùng)
- [ ] `.desktop` sinh ra trỏ `Icon=` đúng đường dẫn `.png` trong thư mục ẩn cạnh binary
- [ ] `postinst` trong script có cả `chmod -R 777` và `chown -R $TARGET_USER` áp dụng lên **thư mục cha** của install dir

**Grader:** Code-based (grep các pattern trên trong file sinh ra) + Human review nội dung.

---

### CE-02 — Edge case: project không có icon `.ico`/`.png` nào tìm được

**Input:** `/gen-build-deb path/to/HeadlessTool` — project không có bất kỳ file icon nào trong cây thư mục.

**Output mong đợi:**
- [ ] Skill KHÔNG tự bịa/generate icon giả — hỏi user cung cấp đường dẫn icon, hoặc tạo script với `Icon=` bỏ trống/dùng icon theme mặc định kèm cảnh báo rõ ràng
- [ ] Vẫn tạo được `build-deb.sh` hoàn chỉnh (icon là optional, không block phần còn lại)

**Grader:** Human.

---

### CE-03 — Negative case: user yêu cầu build .deb thật, không chỉ sinh script

**Input:** "Chạy build-deb cho project X luôn đi" (không phải "tạo skill/sinh script")

**Output mong đợi:**
- [ ] Skill nhận diện đây ngoài phạm vi `gen-build-deb` (skill chỉ sinh file, không tự chạy `dotnet publish`/`dpkg-deb`)
- [ ] Đề xuất chạy `bash scripts/linux-deb/build-deb.sh` sau khi đã sinh xong, KHÔNG tự chạy khi user chỉ gọi `/gen-build-deb`

**Grader:** Human.

---

## 3. Regression Evals

### RE-01 — Không phá vỡ project ParkingV8 gốc

**Input:** Chạy `/gen-build-deb` chỉ định lại chính `parking-v8-app-avalonia`

**Output mong đợi:**
- [ ] Không overwrite `scripts/linux-deb/build-deb.sh` hiện có mà không hỏi xác nhận trước (đã qua nhiều vòng fix thực tế: icon PNG, chown thư mục cha, INSTALL_DIR `/opt/kztek/parkingv8`)

---

### RE-02 — File sinh ra chạy được thật (syntax + dry-run)

**Input:** Bất kỳ project nào từ CE-01/CE-02

**Output mong đợi:**
- [ ] `bash -n scripts/linux-deb/build-deb.sh` không lỗi cú pháp
- [ ] `bash -n deploy-linux/install.sh` không lỗi cú pháp

---

## 4. Kết quả chạy thử (điền sau khi implement)

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | | | |
| CE-02 | | | |
| CE-03 | | | |
| RE-01 | | | |
| RE-02 | | | |

**Tổng kết:** _(điền sau khi chạy thử ≥ 1 project thật ngoài ParkingV8)_

---

## 5. Lịch sử eval

| Ngày | Phiên bản agent | CE pass | RE pass | Tổng kết | Ghi chú |
|------|----------------|---------|---------|----------|---------|
| 2026-07-21 | v1.0 | -/3 | -/2 | DRAFT | Tạo mới, đóng gói kinh nghiệm từ session fix linux-deb ParkingV8 |

---

> **Vị trí lưu:** `.claude/evals/gen-build-deb.md`
> **Liên quan:** `.claude/commands/gen-build-deb.md`, `scripts/linux-deb/build-deb.sh` (bản gốc ParkingV8 dùng làm template)
