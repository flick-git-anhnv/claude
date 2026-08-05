---
name: diagnosing-bugs
description: "PHẢI dùng khi: đang stuck với bug khó reproduce, không biết debug từ đâu, đã fix nhiều lần mà bug vẫn quay lại, hoặc debug bừa theo kiểu 'thử cái này xem có hết không'. Cũng dùng khi: cần review quy trình debug hiện tại để chắc Phase 1 (feedback loop) đã sẵn sàng trước khi tiếp tục. KHÔNG dùng khi: đã có failing test và biết chính xác dòng code cần sửa (→ fix thẳng); đây là lỗi typo/config rõ ràng không cần debug loop (→ WF-FASTTRACK)."
---

# Skill: diagnosing-bugs — 6-phase Debug Loop

> Học từ `mattpocock/skills` `skills/engineering/diagnosing-bugs/SKILL.md`.
> Nguyên tắc cốt lõi: **"Không có tight feedback loop → không có debugging."** Phase 1 là prerequisite cứng cho mọi phase còn lại.

---

## Quy tắc cứng (không được bỏ qua)

> **PHASE 1 GATE:** Trước khi chuyển sang Phase 2, agent PHẢI có khả năng reproduce bug trong ≤ 1 phút (unit test, script, hay manual step cố định). Nếu chưa có → DỪNG tại Phase 1, không đi tiếp.

Dấu hiệu Phase 1 đã sẵn sàng:
- Có test script / unit test chạy và reproduce bug nhất quán
- Cycle từ "sửa code" → "thấy bug" < 1 phút
- Không phụ thuộc vào "may mắn" hay "đúng lúc"

---

## 6 Phases

### Phase 1 — Build Tight Feedback Loop

**Mục tiêu:** Tạo cách reproduce bug nhất quán, nhanh.

Hành động:
1. Tìm test/script/step tối thiểu có thể trigger bug — không cần toàn bộ app chạy nếu unit test đủ
2. Nếu bug intermittent → tìm pattern trigger: input cụ thể? timing? state nào? user action nào?
3. Viết test capture bug (failing test) — đây là "proof" mà không phụ thuộc vào memory
4. Verify: chạy test → thấy fail → đây là feedback loop

**BLOCK nếu:** Sau 15 phút không tìm được cách reproduce nhất quán → báo user, mô tả những gì đã thử, hỏi có thêm context về khi nào bug xảy ra không.

---

### Phase 2 — Make the Bug Visible

**Prerequisite:** Phase 1 đã có tight feedback loop.

Hành động:
1. Thêm logging/tracing minimal để thấy state tại điểm bug xảy ra
2. Isolate: thu hẹp phạm vi — bug ở layer nào? (UI / service / data / config?)
3. Binary search với git bisect hoặc comment out sections nếu cần định vị
4. Không thêm quá nhiều log cùng lúc — thêm 1 checkpoint, chạy, quan sát, rồi mới thêm tiếp

---

### Phase 3 — Understand the Bug

**Mục tiêu:** Biết CHÍNH XÁC tại sao bug xảy ra trước khi viết bất kỳ fix nào.

Hành động:
1. Đọc code liên quan với failing test đang chạy trong đầu
2. Hỏi: "Tại sao code này làm điều này thay vì điều kia?"
3. Xác định root cause — không phải symptom. Symptom: NullReferenceException. Root cause: object X không được khởi tạo vì Y
4. Ghi lại hypothesis về nguyên nhân trước khi thử fix

**BLOCK nếu:** Không thể giải thích tại sao bug xảy ra → quay lại Phase 2, cần thêm visibility.

---

### Phase 4 — Fix the Bug

**Prerequisite:** Phase 1-3 đã xong.

Hành động:
1. Viết fix nhắm đúng root cause (không phải symptom)
2. Chạy failing test → verify test pass
3. Chạy regression test để chắc không phá thứ khác
4. Nếu fix làm thêm test fail → bug ở nơi khác hoặc fix sai → quay Phase 3

---

### Phase 5 — Reflect

**Mục tiêu:** Rút bài học từ bug này.

Hỏi:
- Tại sao bug tồn tại? (design flaw? missing guard? race condition? assumption sai?)
- Có thể prevent loại bug này trong tương lai bằng test hay type safety không?
- Fix hiện tại có thể gây ra bug tương tự ở nơi khác không?

Ghi lại 1-3 câu mô tả bài học.

---

### Phase 6 — Learn (Ghi lại nếu là lỗi ngầm)

**Điều kiện:** Bug là hành vi bất ngờ không có trong docs, hoặc mất > 30 phút để debug.

Hành động:
- Thêm entry vào `.claude/shared/GOTCHAS.md` với format chuẩn (category + mô tả + fix)
- Hoặc thêm lesson vào `C:\Users\nguye\.claude\lessons\` nếu liên quan đến SDK/platform cụ thể

---

## Red Flags (lý do hay bỏ qua skill này)

| Thought | Reality |
|---------|---------|
| "Tôi thấy vấn đề rồi, fix luôn cho nhanh" | Không có failing test = không biết fix đúng không. Fix xong có thể vẫn broken hoặc break thứ khác |
| "Bug này quá rõ, không cần loop" | Nếu rõ, viết test capture nó < 5 phút. Test đó cũng phục vụ regression testing sau này |
| "Logging thêm sẽ mất thời gian" | Debug không có visibility mất nhiều thời gian hơn. Thêm 3 dòng log tiết kiệm 30 phút |
| "Tôi đã fix rồi nhưng test vẫn fail — chắc test sai" | Rarely. Hầu hết thời gian: fix chưa đúng root cause |

---

## Verification (done gate)

- [ ] Phase 1: Có failing test / script reproduce bug nhất quán
- [ ] Phase 2: Đã identify được vị trí bug (file/function/layer)
- [ ] Phase 3: Có thể giải thích root cause bằng 1-2 câu
- [ ] Phase 4: Failing test đã pass sau fix + không có regression
- [ ] Phase 5: Đã ghi bài học ≥ 1 câu
- [ ] Phase 6 (nếu applicable): Entry GOTCHAS.md hoặc lesson đã được tạo
