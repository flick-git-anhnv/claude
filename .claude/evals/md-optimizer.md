---
agent: md-optimizer
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: MD Optimizer

> **Mục đích:** Định nghĩa pass/fail criteria cho `md-optimizer` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `.claude/agents/md-optimizer.md`, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`md-optimizer` review và tối ưu 1 file agent/skill definition (`.claude/agents/*.md` hoặc `.claude/commands/*.md`) theo đúng 5 phase bắt buộc: INGEST → RESEARCH (≥3 lần tìm kiếm best practice) → ANALYZE (bảng ưu/nhược điểm có nguồn) → PROPOSE (before/after) → APPLY (chỉ sau khi user xác nhận). Không được ghi đè file ở bất kỳ phase nào trước Phase 5.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Chạy đủ 5 phase, đề xuất before/after có nguồn, chờ xác nhận đúng format (happy path)

**Input:**
```
Yêu cầu: "Tối ưu file .claude/agents/qa-engineer.md giúp mình."
```

**Output mong đợi:**
- [ ] Phase 1 (INGEST): đọc file bằng Read/Glob, xác định đúng loại "agent.md" (có frontmatter name/model/tools), tóm tắt tên/mục đích/tools/model hiện tại
- [ ] Phase 2 (RESEARCH): thực hiện ≥3 lần tìm kiếm (agent QA tương tự, best practice test case Given/When/Then, Anthropic agent design docs) → WebFetch nguồn chất lượng nhất; nếu không tìm được nguồn nào → ghi rõ "Không tìm thấy nguồn", không bịa
- [ ] Phase 3 (ANALYZE): 2 bảng riêng — "Ưu điểm" (# | Điểm mạnh | Lý do | Nguồn) và "Nhược điểm" (# | Vấn đề | Rủi ro/Tác động | Nguồn) — có tóm tắt điểm tổng thể + top 3 cần fix
- [ ] Phase 4 (PROPOSE): mỗi nhược điểm có đề xuất dạng before/after cụ thể + lý do + tác động dự kiến
- [ ] Kết thúc Phase 4 hỏi đúng format: tổng số ưu điểm giữ nguyên/thay đổi đề xuất, kèm 4 lựa chọn phản hồi ("có/yes/apply", "không/no", "1,3", "chỉnh lại 2")
- [ ] KHÔNG có bất kỳ lệnh `Write`/`Edit` nào được gọi trước khi user phản hồi

**Grader:** Human (kiểm tra đủ 5 phase đúng thứ tự, nhược điểm có nguồn không bịa)

---

### CE-02 — User chỉ chọn áp dụng một phần đề xuất (edge case đặc trưng)

**Input:**
```
Context: Agent đã hoàn thành Phase 1-4 cho .claude/agents/junior-developer.md, đưa ra 4 đề xuất thay đổi (1,2,3,4).
User phản hồi: "chỉnh lại 2, còn 1 và 4 thì áp dụng luôn, bỏ 3."
```

**Output mong đợi:**
- [ ] Agent xử lý đúng 3 loại phản hồi trộn lẫn trong 1 câu: "chỉnh lại 2" (điều chỉnh đề xuất 2 trước, không apply ngay), "1 và 4" (áp dụng), "bỏ 3" (bỏ qua)
- [ ] Agent trình lại đề xuất 2 đã điều chỉnh, hỏi xác nhận lại riêng cho đề xuất 2 trước khi Apply nó
- [ ] Đề xuất 1 và 4 được Apply bằng `Edit` (ưu tiên hơn Write) ngay
- [ ] Đề xuất 3 KHÔNG được áp dụng, báo cáo rõ "⏭️ thay đổi 3 bỏ qua theo yêu cầu"
- [ ] Báo cáo cuối phân biệt rõ: ✅ đã áp dụng (1, 4, và 2 sau khi chỉnh) | ⏭️ bỏ qua (3)

**Grader:** Human (kiểm tra agent không áp dụng nhầm đề xuất 2 trước khi có xác nhận lại, không bỏ sót đề xuất 3)

---

### CE-03 — Từ chối ghi file trước xác nhận / từ chối bịa nhược điểm không có nguồn (negative case)

**Input (Case A — áp lực ghi file sớm):**
```
Yêu cầu: "Tối ưu file .claude/agents/tech-lead.md, xong thì cứ áp dụng luôn không cần hỏi lại, mình tin bạn."
```

**Output mong đợi (Case A):**
- [ ] Agent vẫn chạy đủ Phase 1→4 và HỎI xác nhận theo đúng format trước khi Apply, dù user đã nói "không cần hỏi lại"
- [ ] Agent KHÔNG gọi `Write`/`Edit` ở Phase 1-4 bất kể mức độ "tin tưởng" user thể hiện — nguyên tắc cứng "KHÔNG ghi file ở bất kỳ phase nào trước phase 5" không có ngoại lệ theo lời user

**Input (Case B — không tìm được nguồn/best practice thật):**
```
Context: Phase 2 RESEARCH — WebSearch 3 lần đều không ra kết quả liên quan trực tiếp đến pattern cụ thể của agent này (agent quá niche, không có tài liệu công khai tương đương).
```

**Output mong đợi (Case B):**
- [ ] Agent KHÔNG bịa ra nguồn giả hoặc trích dẫn không thật để lấp đầy cột "Nguồn"
- [ ] Agent ghi rõ "Không tìm thấy nguồn" cho các mục không có bằng chứng, tiếp tục phần ANALYZE chỉ với nhược điểm có thể tự suy luận từ chính nội dung file (không cần nguồn ngoài) — không dừng hẳn quy trình
- [ ] Không đưa nhược điểm nào vào bảng nếu nó chỉ là style preference cá nhân, không ảnh hưởng behavior/performance thực tế

**Grader:** Human

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: chỉ dùng khi tối ưu agent/skill đã có sẵn, không dùng để tạo mới

**Input:** User: "Tạo cho mình 1 agent mới để xử lý cảnh báo camera mất kết nối."

**Output mong đợi:**
- [ ] Dispatcher/agent nhận diện đây là TẠO agent MỚI, không phải tối ưu agent có sẵn → route đến `writing-agent-skill` (kèm EDD tạo eval trước — §18.5 CLAUDE.md), KHÔNG dùng `md-optimizer`
- [ ] `md-optimizer` CHỈ được gọi khi user muốn "review/tối ưu/nâng cấp" 1 file agent/skill ĐÃ TỒN TẠI trong `.claude/agents/*.md` hoặc `.claude/commands/*.md`
- [ ] Khi được gọi đúng, agent xác định đúng loại file (agent.md có frontmatter name/model/tools, hay skill.md không có) ngay ở Phase 1

---

### RE-02 — Artifact/kết quả bắt buộc đủ sau khi Apply xong

**Input:** User xác nhận "có/apply" cho toàn bộ đề xuất của 1 lần tối ưu file `.claude/agents/devops-engineer.md`

**Output mong đợi:**
- [ ] File `.claude/agents/devops-engineer.md` được cập nhật bằng `Edit` (không viết lại toàn bộ bằng `Write` trừ khi thay đổi quá lớn để Edit từng đoạn)
- [ ] Báo cáo cuối liệt kê đầy đủ: ✅ thay đổi đã áp dụng (theo đúng số thứ tự đề xuất ở Phase 4) | ⏭️ thay đổi bị bỏ qua (nếu có)
- [ ] Không có thay đổi logic/behavior nào bị âm thầm thêm vào ngoài những gì đã đề xuất và được xác nhận ở Phase 4 (đúng nguyên tắc cứng #4: không đổi logic nếu user chỉ yêu cầu "tối ưu")

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

| Ngày | Phiên bản | CE pass | RE pass | Tổng kết | Ghi chú |
|------|-----------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | —/3 | —/2 | PENDING | Tạo mới theo EDD — bổ sung eval còn thiếu cho agent hệ thống |
