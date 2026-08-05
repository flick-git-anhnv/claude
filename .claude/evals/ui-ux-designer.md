---
agent: ui-ux-designer
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: UI/UX Designer

> **Mục đích:** Định nghĩa pass/fail criteria cho `ui-ux-designer` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `C:/Users/nguye/.claude/agents/ui-ux-designer.md` hoặc thay đổi quy trình Design System / WF-FEATURE trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`ui-ux-designer` vẽ wireframe/mockup cho tính năng mới, duy trì design system (color/typography/component), và đánh giá accessibility (contrast, keyboard nav, screen reader). Agent BẮT BUỘC xác định Design System (Bước 0 — dùng skill UI UX Pro Max) trước khi wireframe, và KHÔNG vẽ khi yêu cầu còn mơ hồ — PHẢI có PRD + user story rõ ràng trước khi bắt đầu.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Vẽ wireframe/mockup + hand-off spec khi đã có đủ PRD + user story

**Input:**
```
Đã có: docs/prd/PRD-device-register.md (Goals, Non-goals rõ ràng)
       docs/user-stories/US-001-device-register.md (AC Given/When/Then đầy đủ)
Yêu cầu: UI/UX Designer thiết kế màn hình đăng ký thiết bị mới.
```

**Output mong đợi:**
- [ ] Bước 0 chạy trước: kiểm tra `design-system/*/MASTER.md` đã có chưa (Glob) — nếu chưa có, sinh mới bằng script `ui-ux-pro-max/scripts/search.py --design-system --persist`
- [ ] File `docs/design/DESIGN-device-register.md` được tạo theo template `DESIGN-template.md`, có user flow vẽ bằng mermaid + wireframe + Design Spec hand-off
- [ ] Design Spec hand-off đủ mục: Mục đích, States (Default/Hover/Active/Disabled/Loading/Error/Empty), Components (kèm variant cụ thể), Tokens (color/spacing/font token), Accessibility
- [ ] Trước khi commit thiết kế, agent hỏi Senior Developer "cái này làm được trong X ngày không?"

**Grader:** Human (kiểm tra DESIGN-*.md có đủ mục hand-off và design system MASTER.md có được tạo/tái dùng đúng cách)

---

### CE-02 — Tái sử dụng design system MASTER.md đã có sẵn (không sinh lại lãng phí)

**Input:**
```
Context: design-system/kztek-parking/MASTER.md đã tồn tại từ task trước (feature khác cùng project).
Yêu cầu: Thiết kế thêm 1 màn hình mới trong cùng project, PRD + user story đã có sẵn.
```

**Output mong đợi:**
- [ ] Agent Glob `design-system/*/MASTER.md` TRƯỚC, phát hiện file đã tồn tại
- [ ] Agent đọc và dùng MASTER.md hiện có làm nguồn sự thật — KHÔNG chạy lại script sinh design system (không dùng `--force` khi không cần)
- [ ] Màn hình mới vẫn nhất quán về palette/typography/style với MASTER.md đã có
- [ ] File `docs/design/DESIGN-[feature-slug-mới].md` được tạo riêng cho màn hình mới, không ghi đè MASTER.md

**Grader:** Human (kiểm tra agent có tránh sinh lại design system không cần thiết)

---

### CE-03 — Từ chối vẽ khi thiếu PRD/user story (negative case)

**Input:**
```
Yêu cầu: "Vẽ giúp mình cái màn hình quản lý thiết bị, làm sao cho đẹp là được."
Context: Không có file docs/prd/PRD-*.md hoặc docs/user-stories/US-*.md nào liên quan tồn tại trong project.
```

**Output mong đợi:**
- [ ] Agent KHÔNG tự vẽ wireframe ngay khi yêu cầu còn mơ hồ, thiếu PRD/user story
- [ ] Agent hiển thị BLOCK theo format §6 CLAUDE.md: lý do block (thiếu PRD/US), cần từ (Product Manager/Business Analyst), yêu cầu cụ thể cần cung cấp
- [ ] Agent KHÔNG tự suy diễn scope/AC để lấp khoảng trống

**Grader:** Human (kiểm tra agent block đúng chuẩn, không tự vẽ khi thiếu input)

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: UI/UX Designer được gọi đúng thời điểm trong workflow

**Input:** Dispatcher chạy WF-FEATURE — Business Analyst vừa hoàn thành user story (Bước 2), cần chuyển bước tiếp theo

**Output mong đợi:**
- [ ] Dispatcher gọi UI/UX Designer ở Bước 3 (Thiết kế mockup, wireframe, user flow) — đúng thứ tự theo CLAUDE.md §4 WF-FEATURE
- [ ] Trong WF-UI, UI/UX Designer được gọi ở Bước 2 (sau Product Manager cung cấp brief ở Bước 1), rồi PM review lại ở Bước 3
- [ ] Header format đúng: `╔══...║  🤖 UI/UX DESIGNER  (UI/UX Designer | Cấp L4)`

---

### RE-02 — Artifact bắt buộc đủ khi hoàn thành thiết kế

**Input:** UI/UX Designer hoàn thành thiết kế cho 1 feature bất kỳ

**Output mong đợi:**
- [ ] `docs/design/DESIGN-[feature-slug].md` tồn tại, có user flow (mermaid) + wireframe + spec hand-off
- [ ] `design-system/<project-slug>/MASTER.md` tồn tại (tạo mới nếu chưa có, hoặc tái dùng nếu đã có)
- [ ] DOCX + PDF được xuất cho `DESIGN-*.md` theo §19 CLAUDE.md

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
