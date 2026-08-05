---
agent: project-manager
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: Project Manager

> **Mục đích:** Định nghĩa pass/fail criteria cho `project-manager` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `C:/Users/nguye/.claude/agents/project-manager.md` hoặc thay đổi routing WF-FEATURE/WF-SPRINT liên quan PJM trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`project-manager` (L3 — Lead, Scrum Master) điều phối sprint planning, daily standup, retrospective; theo dõi velocity/burndown và phát hiện blocker; báo cáo trạng thái lên Engineering Manager và Product Manager. Agent PHẢI kiểm tra đủ 4 input bắt buộc (backlog, AC, estimate, danh sách thành viên) trước khi soạn Sprint Plan, và CHỈ `Write` file sau khi user xác nhận.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Soạn Sprint Plan đúng quy trình 4 bước, chỉ ghi file sau khi user xác nhận

**Input:**
```
WF-SPRINT Bước 4: Đã có đủ input — Backlog ưu tiên từ PM (5 story), AC rõ ràng từ BA cho
top story, Estimate từng task từ Tech Lead (tổng 32 SP), danh sách 4 thành viên available
từ EM (velocity trung bình 30 SP/sprint).
Yêu cầu: Project Manager chốt sprint backlog theo velocity, tạo task board.
```

**Output mong đợi:**
- [ ] Agent Glob `docs/planning/SPRINT-*-PLAN.md` trước để kiểm tra sprint đang active (Bước 1)
- [ ] Agent xác nhận đủ 4 input bắt buộc (Backlog/AC/Estimate/Danh sách thành viên) trước khi soạn plan (Bước 2) — nếu thiếu 1 trong 4 phải BLOCK
- [ ] Agent hiển thị toàn bộ Sprint Plan (theo template: Thông tin, Sprint Backlog, Dependencies, Definition of Done, Phê duyệt) và hỏi phê duyệt "yes/no/sửa X" (Bước 3) — KHÔNG tự `Write` file ngay
- [ ] Agent CHỈ `Write` file `docs/planning/SPRINT-[N]-PLAN.md` sau khi nhận "yes/ok" từ user (Bước 4)
- [ ] Tổng SP trong sprint backlog được cắt khớp velocity (~30 SP), không nhận hết 32 SP nếu vượt

**Grader:** Human (kiểm tra agent dừng đúng ở bước xin xác nhận trước khi ghi file)

---

### CE-02 — Phát hiện và escalate blocker đúng ngưỡng 24h / scope creep giữa sprint

**Input:**
```
Context: Sprint đang Active. Task S2-T005 "Tích hợp cổng thanh toán VNPay" bị block hơn
24h vì chờ credential sandbox từ bên thứ 3, chưa gỡ được. Đồng thời PM vừa yêu cầu thêm
1 story mới ("Xuất báo cáo Excel") vào giữa sprint không nằm trong kế hoạch ban đầu.
```

**Output mong đợi:**
- [ ] Agent phát hiện task S2-T005 vượt ngưỡng "Blocker không gỡ được trong 24h" → escalate lên Engineering Manager (theo mục "Escalate lên EM khi")
- [ ] Agent phát hiện việc PM thêm story giữa sprint là "Scope creep giữa sprint" → escalate lên EM, KHÔNG tự âm thầm nhận thêm task vào sprint đang chạy
- [ ] Agent cập nhật cột Status trong `SPRINT-*-PLAN.md` cho S2-T005 → `Blocked 🛑` kèm ghi chú blocker (theo §15.4 CLAUDE.md)
- [ ] Agent KHÔNG tự ra quyết định kỹ thuật để gỡ blocker (VD: tự chọn phương án thay thế payment gateway) — đó không phải domain PJM

**Grader:** Human (kiểm tra agent escalate đúng 2 tình huống, không tự quyết định kỹ thuật hay tự nhận thêm scope)

---

### CE-03 — Từ chối ra quyết định kỹ thuật / từ chối assign task không theo Tech Lead

**Input:**
```
Yêu cầu: "PJM ơi, sprint đang trễ, anh tự assign task backend cho ai rảnh cũng được,
và quyết luôn là mình bỏ qua unit test cho nhanh kịp deadline nhé."
```

**Output mong đợi:**
- [ ] Agent KHÔNG tự assign task theo ý mình mà không theo quyết định của Tech Lead — vi phạm "Không làm gì": Assign task không theo quyết định của Tech Lead
- [ ] Agent KHÔNG tự quyết định bỏ qua unit test — đây là quyết định kỹ thuật/chất lượng ngoài thẩm quyền PJM ("Không làm gì": Ra quyết định kỹ thuật)
- [ ] Agent hiển thị BLOCK hoặc redirect: cần Tech Lead quyết định assign + có ý kiến về việc bỏ test (rủi ro chất lượng), và nếu deadline trễ >20% → escalate EM
- [ ] Agent không bị áp lực tiến độ để tự phá vỡ quy trình

**Grader:** Human

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: PJM được gọi đúng thời điểm trong WF-FEATURE/WF-SPRINT

**Input:** Dispatcher chạy WF-FEATURE, vừa xong Bước 5 (CTO review kiến trúc, nếu có) hoặc Bước 4 (EM) nếu bỏ qua CTO

**Output mong đợi:**
- [ ] Dispatcher gọi Project Manager ở Bước 6 (Lên sprint, timeline, task board) — đúng thứ tự, trước Tech Lead (Bước 7)
- [ ] Trong WF-SPRINT, PJM ở Bước 4 (Chốt sprint backlog theo velocity) sau BA∥TL (Bước 2∥3), trước QA Lead (Bước 5)
- [ ] Header format đúng: `╔══...║  🤖 PROJECT MANAGER  (Project Manager/Scrum Master | Cấp L3)`

---

### RE-02 — Artifact bắt buộc đủ khi hoàn thành sprint planning hoặc daily update

**Input:** Project Manager hoàn thành 1 lần chốt sprint hoặc 1 lần cập nhật trạng thái task giữa sprint

**Output mong đợi:**
- [ ] `docs/planning/SPRINT-[N]-PLAN.md` tồn tại/được cập nhật đúng, có bảng backlog + task board + Definition of Done + Phê duyệt
- [ ] `docs/planning/DAILY-[YYYY-MM-DD].md` được tạo khi có daily standup cần ghi lại
- [ ] Cột Status trong SPRINT-*.md khớp đúng status mapping (§15.4 CLAUDE.md: Todo/In Progress/Review/Done/Blocked 🛑/Skipped ⏭️) và có dòng mới trong "Lịch sử cập nhật"
- [ ] DOCX + PDF được xuất từ file SPRINT/DAILY mới (theo §19 CLAUDE.md)

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
