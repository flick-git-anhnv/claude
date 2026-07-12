---
agent: [tên agent hoặc skill — kebab-case, khớp với tên file .md]
created: YYYY-MM-DD
author: [GitHub Repo Researcher / task-planner / người tạo]
status: draft | active | deprecated
---

# EVAL: [Tên Agent/Skill]

> **Mục đích:** Định nghĩa pass/fail criteria cho agent/skill trước khi implement — Eval-Driven Development (EDD). Học từ `eval-harness` skill của affaan-m/ecc.
> **Khi tạo:** PHẢI tạo file này TRƯỚC khi viết file định nghĩa agent `.claude/agents/[name].md` hoặc skill `.claude/commands/[name].md`.
> **Khi chạy:** Sau khi implement, chạy thử từng example và ghi kết quả vào bảng "Kết quả chạy thử".

---

## 1. Mô tả năng lực (Capability Statement)

> Mô tả 2-3 câu: agent/skill này làm gì, khi nào được gọi, output mong đợi là gì.

[VD: `code-migrator` có khả năng khảo sát 1 codebase C# WinForms, lập bảng inventory 2 cấp (module/class), mapping sang target stack, và tạo plan migration có thể thực thi được. Được gọi khi user yêu cầu rõ migrate framework.]

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

> Mỗi eval là 1 cặp input/output mong đợi. Agent/skill PHẢI pass ít nhất 2/3 capability eval để được coi hoàn thành.

### CE-01 — [Tên eval: happy path cơ bản]

**Input:** [Mô tả input cụ thể — prompt, file, context]

**Output mong đợi:**
- [ ] [Tiêu chí 1: output chứa gì, format thế nào]
- [ ] [Tiêu chí 2: quyết định gì được đưa ra]
- [ ] [Tiêu chí 3: artifact nào được tạo]

**Grader:** Code-based (output chứa text X) / Human (xem xét judgment) / Model-based (so sánh với expected)

---

### CE-02 — [Tên eval: edge case quan trọng]

**Input:** [Mô tả input — edge case, input không hoàn chỉnh, hoặc case phức tạp]

**Output mong đợi:**
- [ ] [Tiêu chí 1]
- [ ] [Tiêu chí 2]

**Grader:** [Code-based / Human / Model-based]

---

### CE-03 — [Tên eval: negative case — khi nào KHÔNG làm]

**Input:** [Input nằm ngoài scope của agent — để kiểm tra agent biết từ chối]

**Output mong đợi:**
- [ ] Agent hiển thị BLOCK format đúng chuẩn
- [ ] Agent KHÔNG tự xử lý task ngoài scope
- [ ] Agent giải thích lý do từ chối rõ ràng

**Grader:** Human

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

> Chạy lại các eval này mỗi khi CLAUDE.md thay đổi phần liên quan đến agent này, hoặc khi sửa file định nghĩa agent.

### RE-01 — [Tên: kiểm tra tính nhất quán với routing table]

**Input:** Dispatcher nhận yêu cầu đúng trigger của agent này

**Output mong đợi:**
- [ ] Dispatcher routing đúng đến agent này (không nhầm agent khác)
- [ ] Agent được gọi đúng format header (`╔══...║`)

---

### RE-02 — [Tên: kiểm tra artifact output bắt buộc]

**Input:** Agent chạy xong 1 task đơn giản

**Output mong đợi:**
- [ ] File artifact bắt buộc được tạo (theo §11 CLAUDE.md)
- [ ] DOCX được xuất nếu có file .md mới

---

## 4. Kết quả chạy thử (điền sau khi implement)

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | YYYY-MM-DD | PASS / FAIL | [Quan sát thực tế so với mong đợi] |
| CE-02 | YYYY-MM-DD | PASS / FAIL | |
| CE-03 | YYYY-MM-DD | PASS / FAIL | |
| RE-01 | YYYY-MM-DD | PASS / FAIL | |
| RE-02 | YYYY-MM-DD | PASS / FAIL | |

**Tổng kết:** [APPROVED — ≥ 2/3 CE pass + ≥ 1/2 RE pass] / [NEEDS REVISION — liệt kê CE/RE nào fail và lý do]

---

## 5. Lịch sử eval

| Ngày | Phiên bản agent | CE pass | RE pass | Tổng kết | Ghi chú |
|------|----------------|---------|---------|----------|---------|
| YYYY-MM-DD | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới |

---

> **Vị trí lưu:** `.claude/evals/[agent-or-skill-name].md`
> **Liên quan:** `.claude/agents/[name].md` hoặc `.claude/commands/[name].md`
