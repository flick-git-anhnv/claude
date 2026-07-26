---
agent: run-plan-step
created: 2026-07-26
author: Dispatcher (workflow tool-improvements, 7.LinuxDeployTool)
status: active
---

# EVAL: run-plan-step (Skill)

> **Mục đích:** Định nghĩa pass/fail criteria trước khi implement — EDD.

---

## 1. Mô tả năng lực (Capability Statement)

Skill `run-plan-step` thực thi MỘT bước (STEP-N.M) trong plan `docs/plans/PLAN-*/` qua subagent theo session isolation (§16.5 CLAUDE.md): tự đọc PLAN-MASTER xác định bước, Grep Handoff Log bước liền trước để nhúng nguyên văn (R11), phát hiện bước làm dở qua `git status`, dựng prompt chuẩn 8 phần, gọi đúng agent theo cột Agent, và verify artifact (step file done + MASTER ✅ + commit) sau khi subagent xong. Được gọi khi Dispatcher/user muốn "chạy bước tiếp theo" hoặc "làm STEP-N.M" của một plan đã được duyệt.

## Test Scenarios (RED — trước khi có skill)

**Scenario 1:** Dispatcher cần chạy STEP-3.2 của plan đang dở.
→ Hành vi hiện tại: soạn prompt tay mỗi lần, có nguy cơ quên nhúng Handoff Log STEP-3.1 → subagent tự đọc lại codebase (vi phạm R11), hoặc quên yêu cầu cập nhật MASTER/xuất DOCX.
→ Mong muốn: skill tự Grep `## Handoff Log` của bước liền trước, nhúng nguyên văn vào prompt; prompt luôn đủ 8 phần cố định.

**Scenario 2:** STEP-5.2 bị gián đoạn giữa chừng (working tree có file untracked/modified thuộc bước đó, step file vẫn `status: todo`).
→ Hành vi hiện tại: nếu Dispatcher không để ý git status, subagent mới làm lại từ đầu hoặc vứt bỏ code dở.
→ Mong muốn: skill check `git status` trước, nếu có thay đổi liên quan → prompt chứa chỉ thị "audit `git diff` từng file, HOÀN TẤT phần thiếu, KHÔNG làm lại từ đầu".

**Scenario 3:** Subagent trả về "xong" nhưng quên đổi status trong MASTER.
→ Hành vi hiện tại: Dispatcher tin tóm tắt → plan lệch thực tế, bước sau đọc MASTER thấy bước "chưa xong".
→ Mong muốn: skill verify sau khi subagent xong: step file `status: done` + `completed_at`, dòng MASTER ✅, commit mới tồn tại đúng format — thiếu thì yêu cầu bổ sung trước khi báo hoàn thành.

**Scenario 4 (negative):** Plan chỉ có 1 bước duy nhất, hoặc bước hiện tại là "User xác nhận/duyệt".
→ Mong muốn: skill KHÔNG spawn subagent (ngoại lệ §16.5) — báo rõ chạy trực tiếp/chờ user.

**Scenario 5 (negative):** Chưa có plan nào khớp.
→ Mong muốn: skill BLOCK và chỉ về `task-planner`, không tự tạo plan.

**Xác nhận vi phạm:** Confirmed — không có skill/rule nào tự động hóa khuôn này; workflow tool-improvements 2026-07-26 phải soạn tay 10 prompt, và Scenario 2 đã xảy ra thật (STEP-5.2).

---

## 2. Capability Evals

### CE-01 — Happy path: chạy bước kế tiếp

**Input:** "Chạy bước tiếp theo của plan docs/plans/PLAN-tool-improvements-2026-07-26/" (giả định STEP-4.1 là bước ⬜ đầu tiên, STEP-3.3 đã ✅ có Handoff Log).

**Output mong đợi:**
- [ ] Đọc PLAN-MASTER, xác định đúng STEP-4.1 và agent phụ trách theo cột Agent
- [ ] Prompt dựng ra chứa NGUYÊN VĂN Handoff Log của STEP-3.3 + đủ 8 phần khuôn (nhiệm vụ từ step file, build/test gate, cập nhật step file + MASTER + DOCX MASTER, commit format `[slug] Bước N.M: ...`, giới hạn scope, KHÔNG push nếu môi trường không có credential)
- [ ] Gọi Agent tool với subagent_type đúng mapping (VD "Senior Developer" → `senior-developer`)

**Grader:** Human (đọc prompt dựng ra, đối chiếu checklist 8 phần)

### CE-02 — Edge case: bước làm dở

**Input:** "Tiếp tục plan X" khi `git status` có file code untracked/modified khớp phạm vi bước ⬜ hiện tại.

**Output mong đợi:**
- [ ] Skill phát hiện và KHÔNG bỏ qua trạng thái dở
- [ ] Prompt chứa danh sách file dở + chỉ thị audit diff, hoàn tất phần thiếu, không làm lại từ đầu

**Grader:** Human

### CE-03 — Negative: ngoại lệ §16.5 / chưa có plan

**Input:** (a) Plan chỉ 1 bước duy nhất; (b) bước hiện tại là "User duyệt plan"; (c) không tồn tại plan khớp.

**Output mong đợi:**
- [ ] (a)(b): KHÔNG spawn subagent, nêu rõ ngoại lệ §16.5, hướng dẫn chạy trực tiếp / chờ user
- [ ] (c): BLOCK format chuẩn, trỏ về `task-planner`
- [ ] Không tự xử lý task thay agent

**Grader:** Human

---

## 3. Regression Evals

### RE-01 — Routing đúng, không lấn task-planner

**Input:** "Tạo plan mới cho task ABC" (trigger của task-planner, KHÔNG phải run-plan-step)

**Output mong đợi:**
- [ ] run-plan-step KHÔNG được invoke (description có "KHÔNG dùng khi: chưa có plan")
- [ ] Dispatcher routing về task-planner

### RE-02 — Verify artifact sau bước

**Input:** Subagent hoàn thành 1 bước đơn giản

**Output mong đợi:**
- [ ] Skill kiểm tra step file `status: done`, MASTER ✅, commit tồn tại trước khi báo hoàn thành
- [ ] Báo cáo theo format §5 CORE.md (tóm tắt ngắn, không dán nguyên log subagent)

---

## 4. Kết quả chạy thử

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-07-26 | PASS | Cold-read subagent dựng prompt đủ 8/8 phần, chọn đúng agent từ cột Agent |
| CE-02 | 2026-07-26 | PASS | Cold-read nhận diện đúng: bước dở → audit diff, không làm lại |
| CE-03 | 2026-07-26 | PASS | (a)(b) từ chối spawn nêu ngoại lệ §16.5; (c) BLOCK trỏ task-planner |
| RE-01 | 2026-07-26 | PASS | 10 query trigger-test: 5/5 should-trigger, 5/5 should-NOT (trong đó "tạo plan mới" → task-planner) |
| RE-02 | 2026-07-26 | PASS | Cold-read liệt kê đủ 3 mục verify trước khi báo hoàn thành |

**Tổng kết:** APPROVED — 3/3 CE pass + 2/2 RE pass (cold-read qua subagent không context, 2026-07-26)

---

## 5. Lịch sử eval

| Ngày | Phiên bản agent | CE pass | RE pass | Tổng kết | Ghi chú |
|------|----------------|---------|---------|----------|---------|
| 2026-07-26 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới sau workflow tool-improvements (7.LinuxDeployTool) |
