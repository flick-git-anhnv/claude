---
agent: product-manager
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: Product Manager

> **Mục đích:** Định nghĩa pass/fail criteria cho `product-manager` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `C:/Users/nguye/.claude/agents/product-manager.md` hoặc thay đổi routing WF-FEATURE/WF-SPRINT/WF-UI liên quan PM trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`product-manager` (L2 — Management) thu thập yêu cầu, viết PRD theo format cố định (vì sao làm/làm gì/thành công là gì), quản lý backlog theo mức P0→P3, và quyết định cắt scope. Agent đại diện người dùng trong mọi cuộc họp và tạo artifact `docs/prd/PRD-[feature-slug].md` — KHÔNG viết code hoặc ra quyết định kỹ thuật.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Viết PRD đầy đủ theo đúng format cho tính năng mới

**Input:**
```
WF-FEATURE Bước 1: User yêu cầu "Xây dựng tính năng cho khách vãng lai (visitor) đăng ký
xin phép ra vào tòa nhà qua QR code, lễ tân duyệt trên app, hết hạn tự động sau thời gian
đăng ký." Đây là ý tưởng sản phẩm mới, cần PM viết PRD trước khi qua BA.
```

**Output mong đợi:**
- [ ] File `docs/prd/PRD-visitor-qr-registration.md` được tạo theo đúng format: Tổng quan (Vấn đề/Đối tượng/Giá trị), Goals/Non-goals, User Story sơ lược, Acceptance Criteria mức cao (checklist AC1, AC2...), Metric đo lường thành công, Rủi ro/Câu hỏi mở
- [ ] Nội dung PRD trả lời rõ "vì sao làm, làm gì, thành công là gì" — không chỉ mô tả tính năng mà thiếu lý do business
- [ ] Non-goals được nêu rõ (VD: không xử lý check-in bằng vân tay, không tích hợp hệ thống chấm công) — tránh scope creep
- [ ] Agent KHÔNG quyết định chi tiết kỹ thuật (schema DB, API contract) — đó là phần của Tech Lead

**Grader:** Human (kiểm tra PRD đủ mục, không lẫn quyết định kỹ thuật)

---

### CE-02 — Cắt giảm scope khi backlog quá tải / ưu tiên P0→P3

**Input:**
```
WF-SPRINT Bước 1: Backlog hiện có 8 story cho sprint tới nhưng velocity team chỉ đủ cho ~5 story
(theo báo cáo Project Manager sprint trước). Có 2 story P0 (bắt buộc theo hợp đồng khách hàng),
3 story P1, 3 story P2.
Yêu cầu: PM chuẩn bị backlog ưu tiên cho sprint.
```

**Output mong đợi:**
- [ ] Agent chốt danh sách backlog ưu tiên khớp velocity (≈5 story), giữ đủ 2 P0 bắt buộc
- [ ] Agent giải thích rõ story nào bị đẩy ra sprint sau và lý do (theo mức P0-P3, không tuỳ tiện)
- [ ] Agent KHÔNG tự quyết định estimate kỹ thuật (đó là việc Tech Lead pre-estimate ở Bước 3 WF-SPRINT) — chỉ quyết định business priority
- [ ] Output có thể dùng trực tiếp làm input cho Business Analyst (Bước 2, đảm bảo AC top stories) và Tech Lead (Bước 3)

**Grader:** Human (kiểm tra cắt scope hợp lý theo priority, không lẫn sang estimate kỹ thuật)

---

### CE-03 — Từ chối quyết định kỹ thuật / từ chối giao việc thẳng Developer

**Input:**
```
Yêu cầu: "PM ơi, chị quyết luôn giúp em là API đăng ký visitor nên dùng REST hay GraphQL,
rồi giao thẳng cho Junior Dev code luôn đi, khỏi qua Tech Lead cho nhanh."
```

**Output mong đợi:**
- [ ] Agent KHÔNG tự quyết định REST vs GraphQL — đây là quyết định kỹ thuật ngoài domain PM ("Không làm gì": viết code, quyết định kỹ thuật)
- [ ] Agent KHÔNG giao việc thẳng cho Developer — "Không làm gì": giao việc thẳng cho Tech Lead/Developer (phải qua EM)
- [ ] Agent hiển thị BLOCK hoặc redirect đúng chain: giao lại cho Tech Lead (qua EM) quyết định kỹ thuật, giải thích lý do vi phạm chain of command
- [ ] Agent tiếp tục domain của mình: có thể nêu yêu cầu nghiệp vụ/AC liên quan nhưng không đụng vào lựa chọn công nghệ

**Grader:** Human

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: PM luôn là bước đầu tiên trong WF-FEATURE/WF-SPRINT/WF-UI

**Input:** Dispatcher nhận yêu cầu tính năng mới từ user (trigger WF-FEATURE)

**Output mong đợi:**
- [ ] Dispatcher gọi Product Manager ở Bước 1 (đầu tiên) — không bỏ qua, không đổi thứ tự với Business Analyst
- [ ] Trong WF-SPRINT, PM ở Bước 1 (chuẩn bị backlog) trước Business Analyst/Tech Lead (Bước 2∥3)
- [ ] Header format đúng: `╔══...║  🤖 PRODUCT MANAGER  (Product Manager | Cấp L2)`

---

### RE-02 — Artifact bắt buộc đủ khi hoàn thành PRD

**Input:** Product Manager hoàn thành PRD cho 1 feature bất kỳ trong WF-FEATURE

**Output mong đợi:**
- [ ] `docs/prd/PRD-[feature-slug].md` tồn tại, đủ mục theo `PRD-template.md`
- [ ] DOCX + PDF được xuất từ file PRD mới (theo §19 CLAUDE.md)
- [ ] PRD được chuyển đúng cho Business Analyst (Bước 2) làm input chi tiết hóa user story

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
