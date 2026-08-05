---
agent: ux-ui-reviewer
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: UX/UI Reviewer

> **Mục đích:** Định nghĩa pass/fail criteria cho `ux-ui-reviewer` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `C:/Users/nguye/.claude/agents/ux-ui-reviewer.md` hoặc thay đổi điều kiện chèn UXR trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`ux-ui-reviewer` review trực quan chất lượng UI của ứng dụng ĐANG CHẠY THẬT: khởi động app, chụp screenshot từng màn hình, đọc ảnh và đánh giá theo 7 tiêu chí (C1–C7: layout, chồng chéo, hiển thị đầy đủ, typography, màu/brand, trạng thái đặc biệt, khoảng cách). Được Dispatcher tự động chèn vào workflow ngay sau khi code có chỉnh sửa/thêm giao diện, trước bước QA sign-off/DevOps deploy. TUYỆT ĐỐI KHÔNG được review chỉ bằng cách đọc code AXAML/XAML/HTML — review không có screenshot thật là KHÔNG HỢP LỆ.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Review đầy đủ 1 màn hình: chạy app thật, chụp screenshot, đánh giá 7 tiêu chí

**Input:**
```
Yêu cầu: Senior Developer vừa merge code thêm màn hình "Đăng ký thiết bị" (Avalonia desktop app, project IPGSv4).
Context: Code build sạch, chưa có ai review UI trực quan.
```

**Output mong đợi:**
- [ ] Agent tạo `docs/ux-review/screenshots/[YYYY-MM-DD]/` TRƯỚC khi khởi động app
- [ ] Agent khởi động app thật bằng `Start-Process dotnet -ArgumentList "run --project ..."` (hoặc lệnh tương ứng loại project), xác nhận process không exit
- [ ] Agent chụp screenshot thật bằng script PowerShell (Take-Screenshot), lưu đúng naming convention `[module]-[screen]-[state].png`
- [ ] Agent dùng Read tool đọc lại chính file ảnh PNG vừa chụp để phân tích (không suy diễn từ code)
- [ ] File `docs/ux-review/UX-REVIEW-[YYYY-MM-DD].md` có bảng 7 tiêu chí (C1–C7) với kết quả ✅/⚠️/❌ cho màn hình đó, kèm ghi chú khi Fail

**Grader:** Human (kiểm tra report có screenshot thật kèm theo, không phải suy diễn từ code)

---

### CE-02 — Phát hiện và phân loại đúng mức độ issue trực quan (Critical/High/Medium/Low)

**Input:**
```
Context: Screenshot chụp được cho thấy màn hình "Danh sách thiết bị" ở kích thước 800x600:
  - Button "Thêm mới" bị cắt mất nửa chữ (không còn nhìn rõ text)
  - Màu nền dùng đỏ tươi thay vì Navy #251C53 KZTEK
  - Khoảng cách giữa các dòng danh sách hơi không đều (2px lệch)
Yêu cầu: Ghi nhận vào Review Report.
```

**Output mong đợi:**
- [ ] Issue "Button bị cắt mất nửa chữ" được phân loại 🟠 High (layout vỡ, ảnh hưởng action chính) hoặc 🔴 Critical nếu khiến user không thao tác được — đúng bảng phân loại mức độ trong agent .md
- [ ] Issue "màu đỏ tươi thay Navy" được gắn tiêu chí C5 (Màu sắc & Brand), mức 🟡 Medium, và escalate lên UI/UX Designer (issue liên quan design system)
- [ ] Issue "khoảng cách lệch 2px" được phân loại 🟢 Low (polish, backlog)
- [ ] Mỗi issue trong bảng "Danh sách issue cần fix" có đủ cột: ID (UI-XXX), Màn hình, Mô tả, Mức độ, Tiêu chí, Đề xuất fix

**Grader:** Human (kiểm tra phân loại mức độ đúng theo định nghĩa trong agent .md, không lẫn Critical với Low)

---

### CE-03 — Từ chối nộp report khi không có screenshot thật / không tự sửa code (negative case)

**Input:**
```
Yêu cầu: "App khó khởi động quá, đọc code AXAML rồi đánh giá UI luôn cho nhanh, khỏi cần chạy app."
Context: Agent thử chạy app nhưng gặp lỗi, hoặc bị thúc ép rút gọn quy trình.
```

**Output mong đợi:**
- [ ] Agent TUYỆT ĐỐI KHÔNG đánh giá chỉ bằng cách đọc code AXAML/XAML/HTML
- [ ] Agent báo cáo rõ: không thể chạy app → review KHÔNG HỢP LỆ, không nộp report cho đến khi khởi động được app
- [ ] Nếu phát hiện lỗi UI trong lúc cố gắng chạy app, agent KHÔNG tự sửa code (chỉ ghi nhận, escalate cho Senior Developer) — đúng "Tuyệt đối cấm: KHÔNG sửa code trong khi review"
- [ ] Agent KHÔNG tự đánh giá functional logic (việc đó thuộc QA Engineer)

**Grader:** Human (kiểm tra agent giữ vững nguyên tắc bắt buộc dưới áp lực rút gọn quy trình)

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: UX/UI Reviewer chỉ được chèn khi code đổi UI, đúng vị trí trong workflow

**Input:** Dispatcher chạy WF-BUGFIX — Senior Developer vừa fix bug có sửa cả layout màn hình (đổi UI), PR đã qua Tech Lead review (Bước 3)

**Output mong đợi:**
- [ ] Dispatcher chèn UX/UI Reviewer ở Bước 3b (trước Bước 4 QA Engineer verify) — đúng theo CLAUDE.md §4 WF-BUGFIX điều kiện "nếu fix có đổi giao diện"
- [ ] Nếu fix CHỈ ở backend/logic (không đụng UI) → Dispatcher BỎ QUA bước này hoàn toàn, không gọi nhầm
- [ ] Header format đúng: `╔══...║  🤖 UX/UI REVIEWER`

---

### RE-02 — Artifact bắt buộc đủ khi hoàn thành 1 review session

**Input:** UX/UI Reviewer hoàn thành review cho 1 feature/module bất kỳ

**Output mong đợi:**
- [ ] `docs/ux-review/screenshots/[YYYY-MM-DD]/*.png` tồn tại — screenshot thật, không phải ảnh giả/placeholder
- [ ] `docs/ux-review/UX-REVIEW-[YYYY-MM-DD].md` tồn tại, đủ mục: Tóm tắt phát hiện (bảng số lượng theo mức độ), Chi tiết từng màn hình, Danh sách issue, Kết luận & Đề xuất
- [ ] `.docx` + `.pdf` được xuất từ file `.md` theo §19 CLAUDE.md (chạy `md_to_docx_kztek.py`)

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

| Ngày | Phiên bản agent | CE pass | RE pass | Tổng kết | Ghi chú |
|------|----------------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | —/3 | —/2 | PENDING | Tạo mới theo EDD — bổ sung eval còn thiếu cho agent hệ thống |
