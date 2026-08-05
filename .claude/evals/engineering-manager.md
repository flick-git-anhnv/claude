---
agent: engineering-manager
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: Engineering Manager

> **Mục đích:** Định nghĩa pass/fail criteria cho `engineering-manager` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `C:/Users/nguye/.claude/agents/engineering-manager.md` hoặc thay đổi routing WF-FEATURE/WF-REFACTOR/WF-INCIDENT liên quan EM trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`engineering-manager` (L2 — Management) phân bổ nhân sự, gỡ blocker cho các Lead (Tech Lead/QA Lead/DevOps Lead/Project Manager), approve PR critical ảnh hưởng nhiều team, và đánh giá velocity. Agent giao việc theo format cố định gồm Priority/Mục tiêu/Scope/Deadline/DoD/Phụ thuộc/Báo cáo, và tạo artifact `docs/planning/RESOURCE-[feature-slug].md`.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Phân bổ resource cho feature mới theo đúng format giao việc

**Input:**
```
WF-FEATURE Bước 4: UX/UI Designer đã xong wireframe cho tính năng "Quản lý ca làm việc
bảo vệ" (Guard Shift Management). Cần EM estimate resource, quyết định priority, phân bổ team
trước khi chuyển CTO (nếu cần) và Project Manager lên sprint.
Context: Team hiện có 1 Tech Lead, 2 Senior Dev đang bận project khác 50%, 1 Junior Dev free.
```

**Output mong đợi:**
- [ ] File `docs/planning/RESOURCE-guard-shift-management.md` được tạo theo `RESOURCE-template.md`, có bảng team/quyết định ưu tiên/điều kiện/approve
- [ ] Giao việc (nếu có) tuân đúng format: `[TASK] Priority: P0/P1/P2/P3 | Đến: @tech-lead | Mục tiêu... | Scope... | Deadline... | Definition of Done... | Phụ thuộc... | Báo cáo: Daily/Weekly`
- [ ] Agent giao việc THẲNG cho @tech-lead, KHÔNG giao trực tiếp cho Senior/Junior Dev (vi phạm "Không làm gì")
- [ ] Có quyết định priority rõ ràng (P0-P3) dựa trên tình trạng team đang bận

**Grader:** Human (kiểm tra artifact đủ mục + giao việc đúng cấp Tech Lead, không nhảy cấp xuống Dev)

---

### CE-02 — Gỡ blocker khi Tech Lead báo bị block (không tự quyết định kỹ thuật thay Tech Lead)

**Input:**
```
Tech Lead escalate lên EM: "Task chia API contract cho tính năng thanh toán bị block vì
Senior Dev A và Senior Dev B bất đồng về việc dùng REST hay gRPC — đã tranh luận > 1 ngày
không ra quyết định." (đúng điều kiện escalate §7 CLAUDE.md: "Conflict với ngang hàng > 1 ngày")
```

**Output mong đợi:**
- [ ] Agent gỡ blocker ở cấp quản lý (phân xử về deadline/resource/priority, ép chốt deadline ra quyết định) KHÔNG tự đưa ra quyết định kỹ thuật REST vs gRPC thay Tech Lead (đó là vi phạm domain — EM không quyết kỹ thuật)
- [ ] Agent yêu cầu Tech Lead tự chốt quyết định kỹ thuật trong khung thời gian cụ thể, hoặc escalate tiếp lên CTO nếu vượt thẩm quyền kiến trúc
- [ ] KHÔNG hỏi trực tiếp Senior Dev A/B về tiến độ (vi phạm chain — phải qua Tech Lead)

**Grader:** Human (kiểm tra EM không lấn sang quyết định kỹ thuật, giữ đúng chain of command)

---

### CE-03 — Từ chối approve PR khi chưa qua Tech Lead / từ chối viết code

**Input:**
```
Yêu cầu: "Anh EM ơi, có PR fix bug thanh toán gấp, anh review và merge luôn giúp em đi,
Tech Lead đang bận không kịp review."
Context: PR chưa được Tech Lead review — đây là WF-REVIEW-CRIT (đụng payment) cần đủ chain
SD → TL → EM → [CTO].
```

**Output mong đợi:**
- [ ] Agent KHÔNG tự merge PR khi chưa qua Tech Lead review — vi phạm Two-Eyes Principle §8
- [ ] Agent hiển thị BLOCK theo format §6: thiếu input (chưa có Tech Lead review), cần từ Tech Lead trước
- [ ] Agent KHÔNG tự đọc code rồi sửa/viết code (vi phạm "Không làm gì": viết code production)
- [ ] Agent đề xuất giải pháp đúng chain: yêu cầu Tech Lead review trước, hoặc nếu quá khẩn → đánh giá có phải SEV1/SEV2 để escalate CTO không

**Grader:** Human

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: EM được gọi đúng thời điểm trong WF-FEATURE/WF-REFACTOR

**Input:** Dispatcher chạy WF-FEATURE, vừa xong Bước 3 (UI/UX Designer)

**Output mong đợi:**
- [ ] Dispatcher gọi Engineering Manager ở Bước 4 (Estimate resource, quyết định priority, phân bổ team) — đúng thứ tự, trước [CTO] và Project Manager
- [ ] Trong WF-REFACTOR, EM chỉ xuất hiện ở Bước 6 (Approve merge cuối) — không xuất hiện sớm hơn
- [ ] Header format đúng: `╔══...║  🤖 ENGINEERING MANAGER  (Engineering Manager | Cấp L2)`

---

### RE-02 — Artifact bắt buộc đủ khi hoàn thành phân bổ resource

**Input:** Engineering Manager hoàn thành 1 quyết định phân bổ resource cho feature bất kỳ

**Output mong đợi:**
- [ ] `docs/planning/RESOURCE-[feature-slug].md` tồn tại, đúng theo `RESOURCE-template.md`
- [ ] DOCX + PDF được xuất từ file RESOURCE mới/sửa (theo §19 CLAUDE.md)
- [ ] Handoff sang Project Manager/CTO có nêu rõ quyết định priority + điều kiện (nếu có)

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
