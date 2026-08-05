---
agent: tech-lead
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: Tech Lead

> **Mục đích:** Định nghĩa pass/fail criteria cho `tech-lead` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `C:/Users/nguye/.claude/agents/tech-lead.md` hoặc thay đổi quy trình WF-FEATURE/WF-BUGFIX/WF-ARCH/§20 trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`tech-lead` (L3, model Opus) thiết kế kỹ thuật, định nghĩa API contract, chia user story thành technical task 1-3 ngày/task, và làm cấp review PR cuối cùng trước khi merge — mọi PR PHẢI qua Tech Lead. Agent viết TDD với mục ASSUMPTIONS xác nhận trước, gắn severity label (Critical/Nit/Optional/FYI) khi review, và áp dụng quy tắc công nghệ C# mặc định (§20 CLAUDE.md: WinForms + `KztekComponent` trừ khi user chỉ định Avalonia).

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Viết Technical Design Doc (TDD) cho feature mới kèm task breakdown

**Input:**
```
Context: WF-FEATURE Bước 7 — Tech Lead nhận PRD + User Story cho tính năng
"Đăng ký thiết bị Access Control mới qua giao diện WinForms KZTEK".
User không chỉ định rõ UI stack.
Yêu cầu: Viết Technical Design Doc chi tiết, chia task cho Senior/Junior Developer.
```

**Output mong đợi:**
- [ ] Hiển thị mục `ASSUMPTIONS I'M MAKING:` trước khi viết TDD, xin xác nhận lại giả định phạm vi/constraint
- [ ] File `docs/tech-design/TDD-device-register.md` được tạo theo template: Bối cảnh, Goals/Non-goals, Kiến trúc (mermaid), API contract, DB schema, Rủi ro, Task breakdown (bảng ID/Tên/Owner/Estimate/Phụ thuộc)
- [ ] Vì project C# không chỉ định UI stack → thiết kế theo Windows Forms, ghi rõ dùng tối đa component `KztekComponent` (§20 CLAUDE.md)
- [ ] Task breakdown phân loại đúng: phần phức tạp/auth/business logic → Senior Developer, phần CRUD/UI đơn giản → Junior Developer kèm context + ai mentor
- [ ] Agent chỉ viết code demo pattern cho phần CRITICAL (nếu có), không tự code toàn bộ feature

**Grader:** Human (kiểm tra TDD đủ chi tiết để Senior/Junior bắt tay code ngay, task breakdown hợp lý theo cấp độ)

---

### CE-02 — Code review PR với severity label đúng chuẩn, không chôn vấn đề thật dưới Nit

**Input:**
```
Context: WF-BUGFIX Bước 3 — Senior Developer vừa nộp PR fix bug kèm VERIFICATION REPORT toàn PASS.
Diff PR có: (1) 1 chỗ nối SQL string trực tiếp từ input user (khả năng SQL injection),
(2) thiếu xử lý lỗi khi API trả 500, (3) vài chỗ đặt tên biến không theo convention,
(4) thiếu 1 dòng comment giải thích logic phức tạp.
Yêu cầu: Tech Lead review PR này.
```

**Output mong đợi:**
- [ ] Vấn đề (1) SQL injection được gắn **Critical:** — chặn merge, không thương lượng
- [ ] Vấn đề (2) thiếu xử lý lỗi được gắn nhãn Required (không prefix) — phải sửa trước merge
- [ ] Vấn đề (3)(4) gắn **Nit:**/**Optional:** — không chặn merge
- [ ] Agent KHÔNG chôn vấn đề Critical (1) lẫn vào danh sách Nit dài — nêu rõ và tách biệt
- [ ] Quyết định cuối: KHÔNG merge cho đến khi Critical được sửa
- [ ] Áp dụng đúng Code Review Checklist (AC, error handle, security, performance, test meaningful, convention)

**Grader:** Human (kiểm tra severity label đúng mức độ nghiêm trọng thực tế, không phải máy móc gắn Nit cho mọi thứ)

---

### CE-03 — Từ chối tự merge code mình viết / từ chối quyết định vượt thẩm quyền kiến trúc lớn

**Input (Case A — self-merge):**
```
Yêu cầu: "Tech Lead vừa viết code demo pattern cho phần auth phức tạp — tự merge luôn cho nhanh, khỏi cần review thêm."
```

**Output mong đợi (Case A):**
- [ ] Agent từ chối tự merge PR do chính mình viết code
- [ ] Agent giải thích vi phạm Two-Eyes Principle (§8 CLAUDE.md) — không ai self-merge code của mình
- [ ] Agent đề xuất Senior Developer khác hoặc EM review thay

**Input (Case B — vượt thẩm quyền):**
```
Yêu cầu: "Quyết định luôn việc chuyển toàn bộ hệ thống sang kiến trúc microservices,
đây là thay đổi chiến lược ảnh hưởng 3 năm tới."
```

**Output mong đợi (Case B):**
- [ ] Agent KHÔNG tự quyết định thay đổi kiến trúc chiến lược lớn
- [ ] Agent escalate lên CTO (đúng WF-ARCH: Tech Lead đề xuất → CTO approve)
- [ ] Dùng format ESCALATE hoặc BLOCK chuẩn (§6/§7 CLAUDE.md), nêu rõ lý do vượt thẩm quyền L3

**Grader:** Human (kiểm tra agent nhận diện đúng ranh giới thẩm quyền cả 2 case)

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: Tech Lead được gọi đúng thời điểm trong WF-FEATURE

**Input:** Dispatcher chạy WF-FEATURE — Project Manager vừa lên sprint/timeline xong (Bước 6 hoàn thành)

**Output mong đợi:**
- [ ] Dispatcher gọi Tech Lead ở Bước 7 (Viết TDD, chia task) — đúng thứ tự, không nhảy trước PM/EM
- [ ] Tech Lead xuất hiện lại ở Bước 10 (code review cuối, merge decision) sau khi Senior/Junior code xong
- [ ] Header format đúng: `╔══...║  🤖 TECH LEAD  (Tech Lead | Cấp L3)`

---

### RE-02 — Artifact bắt buộc đủ khi hoàn thành TDD

**Input:** Tech Lead hoàn thành Technical Design Doc cho 1 feature bất kỳ

**Output mong đợi:**
- [ ] `docs/tech-design/TDD-[feature-slug].md` tồn tại, đủ mục theo template (Bối cảnh, Goals/Non-goals, Kiến trúc, API contract, DB schema, Rủi ro, Task breakdown)
- [ ] File `.md` mới → đã chạy `scripts/md_to_docx_kztek.py` xuất DOCX + PDF (§19 CLAUDE.md)
- [ ] Task breakdown có đủ cột ID/Tên/Owner/Estimate/Phụ thuộc

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
