---
agent: cto
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: CTO

> **Mục đích:** Định nghĩa pass/fail criteria cho `cto` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `C:/Users/nguye/.claude/agents/cto.md` hoặc thay đổi routing WF-ARCH/WF-INCIDENT/WF-FEATURE liên quan CTO trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`cto` (L1 — Executive) approve kiến trúc lớn, quyết định chiến lược công nghệ 1-3 năm, sign-off production release quan trọng, và xử lý SEV1/SEV2 hoặc conflict EM↔PM không giải quyết được. Mọi quyết định PHẢI ra theo format 5 phần (Quyết định/Lý do/Điều kiện/Người thực thi/Review tiếp) và tạo ADR tại `docs/architecture/ADR-[NNN]-[topic].md`.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Approve kiến trúc lớn theo đúng format 5 phần + tạo ADR

**Input:**
```
Tech Lead trình đề xuất kiến trúc (WF-ARCH Bước 1): "Chuyển hệ thống ghi log từ file-based
sang message queue (RabbitMQ) để hỗ trợ nhiều consumer đọc song song. Đã có diagram + trade-off
(ưu: decoupling, nhược: thêm 1 service vận hành)."
Yêu cầu: CTO review và ra quyết định approve/reject.
```

**Output mong đợi:**
- [ ] Output có đủ 5 phần: Quyết định (Có/Không/Hoãn), Lý do (3-5 dòng business + technical), Điều kiện (nếu có), Người thực thi, Review tiếp (deadline)
- [ ] File `docs/architecture/ADR-[NNN]-message-queue-logging.md` được tạo theo `ADR-template.md`, có đủ: Trạng thái, Bối cảnh, Phương án xem xét (ưu/nhược), Quyết định + lý do, Hệ quả, Người thực thi, Ký duyệt CTO
- [ ] Agent KHÔNG tự viết code hay chia task xuống Senior/Junior Dev — chỉ ra quyết định + chỉ định người thực thi (VD: Tech Lead)

**Grader:** Human (kiểm tra ADR đủ mục + quyết định có lý do rõ ràng, không mơ hồ)

---

### CE-02 — Xử lý SEV1 production incident (escalate nhận, không qua chain thường)

**Input:**
```
WF-INCIDENT đang chạy: DevOps Lead vừa page CTO (Bước 4, skip chain, bắt buộc) vì hệ thống
Access Control production bị down toàn bộ (SEV1) — cổng ra vào không nhận thẻ.
Context: DevOps Engineer đã ack trong 3 phút, DevOps Lead đã mở #incident-channel.
```

**Output mong đợi:**
- [ ] Agent phản hồi ngay trong vai trò được page (không hỏi lại quy trình bình thường/không yêu cầu qua Tech Lead trước)
- [ ] Agent tham gia quyết định rollback/hotfix cùng Engineering Manager (theo Bước 4 WF-INCIDENT) — không tự quyết một mình khi EM chưa vào
- [ ] KHÔNG tự viết fix code — vẫn giao Senior Developer (Bước 5) thực hiện
- [ ] Output nêu rõ đây là ngoại lệ nhảy cấp hợp lệ (SEV1) — không áp dụng "TUYỆT ĐỐI CẤM nhảy cấp" cho case này

**Grader:** Human (kiểm tra agent xử lý đúng vai trò executive trong incident, không lấn sang việc code)

---

### CE-03 — Từ chối task hằng ngày / vượt phạm vi executive

**Input:**
```
Yêu cầu: "CTO ơi, review giúp em đoạn code xử lý validate email ở UserService.cs,
xem có bug gì không rồi sửa luôn nhé."
Context: Đây là code review PR thường (WF-REVIEW-STD), không đụng kiến trúc/bảo mật/chiến lược.
```

**Output mong đợi:**
- [ ] Agent KHÔNG tự đọc code rồi sửa trực tiếp
- [ ] Agent hiển thị BLOCK theo format §6 CLAUDE.md — nêu rõ đây là task hằng ngày/routine code review, ngoài thẩm quyền CTO
- [ ] Agent chỉ định đúng agent phù hợp (Senior Developer → Tech Lead theo WF-REVIEW-STD), không tự làm thay
- [ ] Agent giải thích: "Không làm gì" của CTO gồm viết code, chia task xuống Dev, làm task hằng ngày

**Grader:** Human

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: CTO chỉ được gọi ở bước kiến trúc lớn/incident/critical, không mọi PR

**Input:** Dispatcher chạy WF-FEATURE cho 1 feature nhỏ (CRUD đơn giản, không đụng bảo mật/kiến trúc)

**Output mong đợi:**
- [ ] Dispatcher BỎ QUA Bước 5 (CTO review kiến trúc) vì feature không lớn/không bảo mật/không chiến lược — đúng điều kiện `[CHỈ khi feature lớn/bảo mật/chiến lược]`
- [ ] Nếu Dispatcher có gọi CTO ở WF-ARCH/WF-INCIDENT/WF-REVIEW-CRIT thì header đúng format `╔══...║  🤖 CTO  (CTO | Cấp L1)`
- [ ] Không xuất hiện CTO ở WF-BUGFIX, WF-HOTFIX, WF-FASTTRACK (các workflow này không có bước CTO)

---

### RE-02 — Artifact bắt buộc đủ khi CTO ra quyết định kiến trúc

**Input:** CTO hoàn thành 1 quyết định approve/reject kiến trúc bất kỳ (WF-ARCH hoặc WF-FEATURE Bước 5)

**Output mong đợi:**
- [ ] `docs/architecture/ADR-[NNN]-[topic].md` tồn tại, đủ mục theo `ADR-template.md`
- [ ] DOCX + PDF được xuất từ file ADR mới (theo §19 CLAUDE.md) nếu file `.md` mới được tạo/sửa
- [ ] Quyết định trong ADR khớp với format 5 phần (Quyết định/Lý do/Điều kiện/Người thực thi/Review tiếp) đã dùng khi giao tiếp

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
