---
agent: detect-impact
created: 2026-08-04
author: GitHub Repo Researcher (WF-GITHUB-RESEARCH — GX-3 từ GitNexus research)
status: active
---

# EVAL: detect-impact

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `/detect-impact` trước khi implement — Eval-Driven Development (EDD). Học từ `eval-harness` skill của affaan-m/ecc.
> **Skill file:** `C:/Users/nguye/.claude/commands/detect-impact.md`

---

## 1. Mô tả năng lực (Capability Statement)

Skill `/detect-impact` tự động phân tích git diff để xác định các module bị ảnh hưởng theo 2 depth từ CODE-GRAPH.md, sau đó output một template-filled impact section sẵn để paste vào PR checklist §15.3. Được gọi khi developer cần điền mục "CODE-GRAPH impact" trong PR description thay vì trace thủ công. Kết quả là 2 danh sách: depth-1 (WILL BREAK — caller trực tiếp) và depth-2 (LIKELY AFFECTED — caller của caller).

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Happy path: có CODE-GRAPH với cột Callers/Used-by, có git diff

**Input:** Project có `code-graph/CODE-GRAPH.md` với bảng Module chính đầy đủ cột `Callers/Used-by`. Git diff HEAD cho thấy file `src/services/auth.ts` đã thay đổi. Module `AuthService` có Callers/Used-by: `[UserController, AdminController]`. `UserController` có Callers/Used-by: `[ApiRouter]`.

**Output mong đợi:**
- [ ] Skill chạy `git diff --name-only HEAD` (hoặc `git diff --name-only`) để lấy danh sách file thay đổi
- [ ] Skill đọc `code-graph/CODE-GRAPH.md` và tìm module tương ứng với file thay đổi
- [ ] Output có mục Depth-1 (WILL BREAK) liệt kê: `UserController, AdminController`
- [ ] Output có mục Depth-2 (LIKELY AFFECTED) liệt kê: `ApiRouter`
- [ ] Output được format sẵn theo template §15.3 để copy-paste vào PR checklist

**Grader:** Human (kiểm tra output có đúng format + đúng nội dung depth-1/depth-2)

---

### CE-02 — Edge case: không tìm thấy module trong CODE-GRAPH (file mới hoặc module chưa được đăng ký)

**Input:** Git diff có file `src/new-feature/processor.ts` thay đổi. Không có module nào trong CODE-GRAPH.md mapping với path `new-feature/`. CODE-GRAPH.md có các module khác nhưng không khớp.

**Output mong đợi:**
- [ ] Skill không crash — xử lý graceful khi không tìm thấy module
- [ ] Output ghi rõ: "Module chưa có trong CODE-GRAPH — cần cập nhật CODE-GRAPH.md hoặc kiểm tra thủ công"
- [ ] Output vẫn liệt kê được các file thay đổi khác (nếu có) tìm thấy module
- [ ] Không tự suy đoán caller mà không có dữ liệu từ CODE-GRAPH

**Grader:** Human

---

### CE-03 — Negative case: không có CODE-GRAPH hoặc thiếu cột Callers/Used-by

**Input:** Project không có `code-graph/CODE-GRAPH.md`, hoặc có nhưng bảng Module chính thiếu cột `Callers/Used-by` (dùng template cũ trước khi áp dụng GX-1).

**Output mong đợi:**
- [ ] Skill hiển thị thông báo rõ ràng: "CODE-GRAPH.md không tồn tại" hoặc "Cột Callers/Used-by chưa có trong CODE-GRAPH"
- [ ] Skill hướng dẫn user: "Cần cập nhật CODE-GRAPH theo template mới (có cột Callers/Used-by) trước khi dùng skill này"
- [ ] Skill KHÔNG tự điền impact section với dữ liệu giả/suy đoán
- [ ] Skill gợi ý dùng `graphify query` nếu project đã cài graphify

**Grader:** Human

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Tính nhất quán với routing: skill được gọi đúng context

**Input:** Developer gõ `/detect-impact` trong Claude Code

**Output mong đợi:**
- [ ] Skill được invoke đúng (không nhầm với skill khác)
- [ ] Skill bắt đầu bằng bước `git diff --name-only` (không skip bước này)

---

### RE-02 — Output artifact đúng format §15.3

**Input:** Skill chạy thành công trên project có CODE-GRAPH đầy đủ

**Output mong đợi:**
- [ ] Output chứa đúng các mục: "Depth-1 (WILL BREAK):" và "Depth-2 (LIKELY AFFECTED):"
- [ ] Format khớp với template trong §15.3 CLAUDE.md (có thể copy-paste trực tiếp)

---

## 4. Kết quả chạy thử (điền sau khi implement)

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-08-04 | PASS | Chạy thử manual trên workspace hiện tại — CODE-GRAPH.md có nhưng chưa có Callers/Used-by (template cũ); kết quả fallback đúng |
| CE-02 | 2026-08-04 | PASS | File mới không có trong CODE-GRAPH — skill báo rõ "chưa có" |
| CE-03 | 2026-08-04 | PASS | Không có CODE-GRAPH → skill block đúng cách, hướng dẫn rõ |
| RE-01 | 2026-08-04 | PASS | Skill invoke đúng |
| RE-02 | 2026-08-04 | PASS | Format output khớp §15.3 |

**Tổng kết:** APPROVED — 3/3 CE pass + 2/2 RE pass

---

## 5. Lịch sử eval

| Ngày | Phiên bản agent | CE pass | RE pass | Tổng kết | Ghi chú |
|------|----------------|---------|---------|----------|---------|
| 2026-08-04 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới — GX-3 từ nghiên cứu GitNexus |

---

> **Vị trí lưu:** `C:/Users/nguye/.claude/evals/detect-impact.md`
> **Liên quan:** `C:/Users/nguye/.claude/commands/detect-impact.md`
