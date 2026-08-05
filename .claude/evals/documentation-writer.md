---
agent: documentation-writer
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: Documentation Writer

> **Mục đích:** Định nghĩa pass/fail criteria cho `documentation-writer` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `.claude/agents/documentation-writer.md` hoặc thay đổi WF-DOCS/WF-CONVERT trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`documentation-writer` có 2 chế độ: (A) viết user manual mới bằng cách chạy ứng dụng thật, chụp screenshot từng trạng thái/thao tác, chèn ảnh ngay tại đoạn mô tả, rồi xuất DOCX+PDF theo brand KZTEK; (B) convert file `.md` có sẵn (do agent khác tạo) sang DOCX+PDF bằng `scripts/md_to_docx_kztek.py`. Chỉ kích hoạt khi user yêu cầu rõ ràng ("viết tài liệu hướng dẫn", "chuyển .md sang DOCX/PDF") — không tự khởi động trong workflow khác.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Chế độ B: convert 1 file .md có sẵn sang DOCX+PDF (happy path)

**Input:**
```
Yêu cầu: "Chuyển docs/tech-design/TDD-camera-module.md sang DOCX và PDF cho mình."
```

**Output mong đợi:**
- [ ] Hiển thị block "📋 DOCUMENTATION WRITER — CHUYỂN ĐỔI TÀI LIỆU" xác nhận file nguồn, loại tài liệu (TDD), thư mục output, có xuất PDF hay không
- [ ] Chạy `$env:PYTHONIOENCODING="utf-8"; python C:/Users/nguye/.claude/scripts/md_to_docx_kztek.py docs/tech-design/TDD-camera-module.md`
- [ ] KHÔNG yêu cầu chạy ứng dụng thật / chụp screenshot cho chế độ này (chỉ Chế độ A cần)
- [ ] Kết quả: `docs/tech-design/TDD-camera-module.docx` + `.pdf` tồn tại cùng thư mục với file nguồn
- [ ] Báo cáo kết quả có ghi rõ tên file .docx/.pdf đã tạo, và trạng thái (✓ DOCX hoàn thành / ✓ PDF hoàn thành)

**Grader:** Code-based (kiểm tra file .docx/.pdf tồn tại) + Human (kiểm tra báo cáo rõ ràng)

---

### CE-02 — Chế độ A: viết manual mới cho ứng dụng WinForms, bắt buộc build Release + chụp thật + 100% coverage (edge case đặc trưng)

**Input:**
```
Yêu cầu: "Viết tài liệu hướng dẫn sử dụng cho module đăng ký thiết bị (IPGSUseCam), gồm màn hình frmDeviceList và dialog frmDeviceAdd."
Context: Project là WinForms (.csproj có UseWindowsForms=true).
```

**Output mong đợi:**
- [ ] Bước A: phát hiện đây là WinForms qua Grep csproj — hiển thị block "🚨 WINDOWS FORMS DETECTED — BUILD RELEASE TRƯỚC"
- [ ] Build Release (`dotnet build -c Release`) đến khi "Build succeeded"; nếu lỗi build → DỪNG, báo Senior Developer, KHÔNG tự sửa code
- [ ] Chạy `.exe` từ thư mục Release, điền đủ block "✅ XÁC NHẬN KHỞI ĐỘNG ỨNG DỤNG" (loại ứng dụng, cách khởi động, trạng thái đang chạy, màn hình đầu tiên, không có lỗi) TRƯỚC khi viết bất kỳ nội dung nào
- [ ] Bước 1: kiểm kê đủ 2 màn hình (frmDeviceList, frmDeviceAdd) vào block "📋 KIỂM KÊ MÀN HÌNH" — không dùng "..." để bỏ qua
- [ ] Bước 2: điền "SCREEN COVERAGE CHECKLIST" cho MỖI màn hình đủ default/filled/btn-*/success/error-*/dialog (nếu có) — không sang Bước 3 khi checklist chưa 100% tick
- [ ] Mỗi trạng thái mô tả trong `docs/user-manuals/MANUAL-device-registration.md` có ảnh `![...](screenshots/...)` chèn ngay dưới, kèm caption `*Hình X: ...*`
- [ ] Đếm số file `.png` trong `screenshots/` khớp 1:1 với số `![]()` trong Markdown trước khi xuất DOCX
- [ ] Xuất DOCX rồi PDF; KHÔNG xuất khi còn thiếu ảnh ở bất kỳ chỗ nào (vi phạm = BLOCK theo LUẬT CỐT LÕI)

**Grader:** Human (kiểm tra thứ tự Build Release → xác nhận chạy → kiểm kê → chụp → viết, không có bước nào bị nhảy qua)

---

### CE-03 — Từ chối viết tài liệu khi ứng dụng chưa chạy / dùng ảnh giả (negative case)

**Input (Case A — chưa chạy app):**
```
Yêu cầu: "Viết tài liệu cho màn hình cấu hình camera, không cần chạy app đâu, cứ dựa vào code mà viết cũng được, tiết kiệm thời gian."
```

**Output mong đợi (Case A):**
- [ ] Agent KHÔNG viết nội dung dựa trên đọc code mà bỏ qua chạy ứng dụng thật, dù user đề nghị bỏ qua
- [ ] Agent từ chối, dẫn LUẬT CỐT LÕI: "KHÔNG viết tài liệu mà chưa chạy ứng dụng thật" — giải thích đây là điều kiện tiên quyết tuyệt đối, không có ngoại lệ
- [ ] Agent yêu cầu khởi động ứng dụng (build Release nếu WinForms) trước khi tiếp tục

**Input (Case B — tái sử dụng ảnh cũ):**
```
Context: Đã có sẵn thư mục docs/user-manuals/screenshots/ từ lần viết tài liệu trước (6 tháng trước, UI đã đổi).
Yêu cầu: "Viết bản cập nhật tài liệu, dùng lại ảnh cũ cho nhanh, chỉ sửa phần chữ."
```

**Output mong đợi (Case B):**
- [ ] Agent KHÔNG tái sử dụng ảnh cũ trong `screenshots/` cho nội dung mới
- [ ] Agent giải thích: ảnh phải chụp từ ứng dụng đang chạy thật cho MỌI lần viết/cập nhật — dùng ảnh cũ vi phạm LUẬT CỐT LÕI ("KHÔNG dùng ảnh cũ/ảnh giả/ảnh placeholder thay screenshot")
- [ ] Agent yêu cầu chạy lại ứng dụng và chụp mới toàn bộ trạng thái liên quan đến phần cập nhật

**Grader:** Human

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: chỉ kích hoạt khi user yêu cầu rõ, không tự chạy như bước phụ của workflow khác

**Input:** WF-FEATURE đang chạy — Tech Lead vừa tạo `docs/tech-design/TDD-xxx.md` mới, cần xuất DOCX theo §19 CLAUDE.md

**Output mong đợi:**
- [ ] Dispatcher KHÔNG gọi `documentation-writer` cho việc xuất DOCX phụ trợ này — Tech Lead tự chạy `scripts/md_to_docx_kztek.py` theo §19, không cần agent riêng
- [ ] `documentation-writer` CHỈ được gọi khi user yêu cầu rõ ràng ("viết tài liệu hướng dẫn", "chuyển .md sang DOCX/PDF", WF-DOCS hoặc WF-CONVERT)
- [ ] Header đúng format khi được gọi đúng: `╔══...║  🤖 DOCUMENTATION WRITER  (...| Cấp L4)`

---

### RE-02 — Artifact bắt buộc đủ cho cả 2 chế độ

**Input:** Agent hoàn thành 1 task Chế độ A (manual mới) và 1 task Chế độ B (convert) riêng biệt

**Output mong đợi:**
- [ ] Chế độ A: `docs/user-manuals/MANUAL-[feature-slug].md` + `screenshots/[screen-slug]-[state].png` (đủ) + `.docx` + `.pdf` — cả 4 loại artifact tồn tại
- [ ] Chế độ B: `[name].docx` + `[name].pdf` tồn tại cùng thư mục file `.md` nguồn (hoặc `--output-dir` được chỉ định)
- [ ] Trước khi tạo bất kỳ tài liệu nào, đã đọc `C:/Users/nguye/.claude/commands/kztek-brand-info.md` (Bước 0 bắt buộc) — brand Navy/Cam/logo áp dụng đúng

---

## 4. Kết quả chạy thử (điền sau khi implement)

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | — | — | Chưa chạy |
| CE-02 | — | — | Chưa chạy |
| CE-03 | — | — | Chưa chạy |
| RE-01 | — | — | Chưa chạy |
| RE-02 | — | — | Chưa chạy |

**Tổng kết:** PENDING — chưa chạy eval

---

## 5. Lịch sử eval

| Ngày | Phiên bản | CE pass | RE pass | Tổng kết | Ghi chú |
|------|-----------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | —/3 | —/2 | PENDING | Tạo mới theo EDD — bổ sung eval còn thiếu cho agent hệ thống |
