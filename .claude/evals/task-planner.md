---
agent: task-planner
created: 2026-07-12
author: senior-developer
status: active
---

# EVAL: Task Planner

> **Mục đích:** Định nghĩa pass/fail criteria cho `task-planner` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `.claude/agents/task-planner.md` hoặc khi CLAUDE.md §3.0 thay đổi, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`task-planner` quản lý vòng đời plan file (`.claude/plans/PLAN-*.md`): tạo plan mới cho task chưa có plan, đọc và tiếp tục đúng từ plan đang dở, và chặn (BLOCK) khi thiếu thông tin bắt buộc từ user trước khi bắt đầu bất kỳ workflow nào. Agent KHÔNG tự thực hiện task — chỉ quản lý kế hoạch và phân công.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Tạo plan mới đúng convention khi chưa có plan

**Input:**
```
User: "Tôi muốn thêm tính năng đăng nhập SSO cho hệ thống KZTEK Access Control. Workflow: WF-FEATURE."
Context: Glob ".claude/plans/PLAN-*.md" trả về empty (không có plan liên quan).
```

**Output mong đợi:**
- [ ] Agent chạy `Glob ".claude/plans/PLAN-*.md"` để kiểm tra plan cũ trước
- [ ] Agent hiển thị block xác nhận đúng format (`╔══...║  📋 TASK PLANNER — Đề xuất kế hoạch`) với nội dung plan hoàn chỉnh (slug, phases, agent chain theo WF-FEATURE)
- [ ] File plan CHƯA được `Write` cho đến khi user gõ "yes/ok"
- [ ] Tên file tuân theo convention: `.claude/plans/PLAN-sso-login-YYYY-MM-DD.md` (hoặc slug tương đương)
- [ ] Plan chứa đủ các phases: PM → BA → UX → EM → TL → SD/JD → TL review → QA → DevOps
- [ ] Agent hỏi user xác nhận trước khi lưu file

**Grader:** Human (kiểm tra format hiển thị + chờ xác nhận đúng thứ tự)

---

### CE-02 — Đọc và tiếp tục đúng từ plan đang dở

**Input:**
```
User: "Tiếp tục task SSO login."
Context: File `.claude/plans/PLAN-sso-login-2026-07-12.md` tồn tại, có nội dung:
  - Bước 1 (PM): ✅ Done, artifact: docs/prd/PRD-sso-login.md
  - Bước 2 (BA): ✅ Done, artifact: docs/user-stories/US-sso-001.md
  - Bước 3 (UX): 🔄 In Progress
  - Bước 4-N: ⬜ Todo
```

**Output mong đợi:**
- [ ] Agent `Read` plan file trước (không tạo plan mới)
- [ ] Hiển thị đúng trạng thái tiến độ: "✅ Xong: Bước 1, 2 | 🔄 Đang: Bước 3 | ⬜ Còn: Bước 4-N"
- [ ] Thông báo "Tiếp tục từ: Bước 3 (UX/UI Designer)" — KHÔNG làm lại Bước 1, 2
- [ ] KHÔNG tạo plan mới (không Write file mới, không hỏi xác nhận lại từ đầu)
- [ ] Chuẩn bị giao Bước 3 cho subagent/trigger với Handoff Log từ Bước 1-2 nhúng vào prompt

**Grader:** Code-based (output không chứa "Đề xuất kế hoạch" mới; output chứa "Tiếp tục từ: Bước 3")

---

### CE-03 — BLOCK khi thiếu thông tin để tạo plan

**Input:**
```
User: "Tạo plan cho dự án mới."
Context: Không có plan cũ liên quan. User không chỉ rõ: tính năng gì, workflow nào, priority gì.
```

**Output mong đợi:**
- [ ] Agent KHÔNG tạo plan ngay — phải hỏi rõ ít nhất: (1) tính năng/mục tiêu cụ thể là gì, (2) workflow áp dụng (Feature/Bugfix/Refactor/...), (3) priority (P0-P3)
- [ ] Nếu agent có skill `scope-check` → gọi scope-check để làm rõ scope trước
- [ ] Hiển thị câu hỏi rõ ràng (AskUserQuestion format), KHÔNG đoán mò rồi tạo plan sai scope
- [ ] KHÔNG tự chọn workflow rồi tạo plan luôn khi user chưa xác nhận

**Grader:** Human (kiểm tra agent có hỏi thay vì giả định và tạo plan ngay)

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Dispatcher routing đúng đến task-planner

**Input:** User gửi yêu cầu mới bất kỳ (VD: "Tôi muốn thêm tính năng export báo cáo PDF")

**Output mong đợi:**
- [ ] Dispatcher (Bước Pre-0) tự động kiểm tra plan file trước khi phân tích workflow
- [ ] Dispatcher gọi `task-planner` trước khi gọi bất kỳ agent workflow nào (PM/BA/TL...)
- [ ] `task-planner` xuất hiện đúng trong header format `╔══...║  🤖 TASK PLANNER`

---

### RE-02 — Cập nhật plan sau mỗi bước hoàn thành

**Input:** Một bước trong plan vừa hoàn thành (VD: Senior Developer xong Bước 8)

**Output mong đợi:**
- [ ] `task-planner` hoặc agent vừa xong tự `Edit` plan file: đổi ⬜/🔄 → ✅
- [ ] Điền tên artifact vào cột Artifact, điền "Hoàn thành lúc" (YYYY-MM-DD HH:mm thực tế)
- [ ] Thêm entry mới vào "## Handoff Log" với đủ 4 trường (Đã làm / File đã đọc/đổi / Quyết định quan trọng / Bước sau cần biết)

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
| 2026-07-12 | v1.0 | —/3 | —/2 | PENDING | Tạo mới theo EDD (Bước 2.1 PLAN-optimize-framework) |
