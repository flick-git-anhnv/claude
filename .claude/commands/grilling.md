---
name: grilling
description: "PHẢI dùng khi: yêu cầu feature/task có nhiều unknowns không thể chốt bằng 5 câu scope-check đơn giản — cần khám phá có cấu trúc theo design tree. Trigger: 'tôi muốn tính năng X nhưng chưa rõ', scope-check gợi ý cần grilling, hoặc Tech Lead nhận thấy requirements có ambiguity khó resolve nhanh. KHÔNG dùng khi: yêu cầu đã đủ rõ (frontier trống ngay — xem CE-03); chỉ cần 1-2 câu để clear ambiguity (→ scope-check); hoặc đây là bug report (không phải feature spec)."
---

# Skill: grilling — Structured Requirements Interview

> Học từ `mattpocock/skills` `skills/engineering/grilling/SKILL.md`.
> Nguyên tắc cốt lõi: **"Tự tìm thông tin — không hỏi user về điều có thể tra được. Dừng khi frontier trống."**

---

## Khái niệm cốt lõi

**Design tree:** Phân rã feature thành prerequisites theo cấu trúc cây. VD: "Export báo cáo" → {format?, data source?, permissions?, schedule?, destination?}

**Frontier:** Tập hợp prerequisites CHƯA RÕ hiện tại. Bắt đầu = toàn bộ lá của design tree. Kết thúc = frontier trống.

**Round:** Mỗi round xử lý 1 item từ frontier. Agent hoặc tự tìm thông tin (search, read code, read docs) hoặc hỏi user đúng 1 câu nếu không thể tự tìm.

---

## Quy trình

### Bước 1 — Xây dựng design tree

ĐỌC yêu cầu. Phân rã thành prerequisites ở các tầng:

```
[Feature]
├── [Sub-feature A]
│   ├── [Prerequisite A1] — có thể tự tìm? [Y/N]
│   └── [Prerequisite A2] — có thể tự tìm? [Y/N]
├── [Sub-feature B]
│   └── [Prerequisite B1] — có thể tự tìm? [Y/N]
└── [Constraint C] — có thể tự tìm? [Y/N]
```

Đánh dấu ngay: prerequisite nào có thể tự tra (code, docs, context) vs cần hỏi user.

**Khởi tạo Frontier** = tất cả prerequisites có label [N] (cần hỏi user) + những prerequisite [Y] chưa tra.

### Bước 2 — Kiểm tra frontier

Nếu frontier trống → BỎ QUA các bước còn lại, sang Bước 5 ngay.

Nếu không → tiếp tục Bước 3.

### Bước 3 — Xử lý frontier (lặp từng round)

Với mỗi item còn trong frontier:

**Trước tiên: Tự tìm thông tin**
- Đọc file code liên quan (`Read`, `Grep`, `Glob`)
- Đọc docs hiện tại (README, TDD, user story)
- Kiểm tra có pattern tương tự đã được implement chưa

Nếu tìm được → mark item đó là RESOLVED, thêm answer vào design tree, không hỏi user.

**Chỉ hỏi user khi:** Sau khi tự tìm, vẫn không có answer (VD: business decision mà chỉ user biết: "format export muốn là PDF hay Excel?")

Hỏi đúng 1 câu cụ thể, chờ answer → mark RESOLVED.

Sau mỗi round: cập nhật frontier (xóa item đã RESOLVED, thêm item mới nếu answer làm xuất hiện prerequisite mới).

### Bước 4 — Repeat Bước 2-3

Tiếp tục cho đến khi frontier trống.

### Bước 5 — Output requirements spec

Khi frontier trống, viết requirements spec:

```markdown
## Requirements Spec — [Feature Name]

### Đã xác định

| Prerequisite | Answer | Nguồn |
|-------------|--------|-------|
| Format export | Excel (.xlsx) | User confirmed |
| Data source | ParkingReport table, lọc theo date range | Đọc từ ParkingRepository.cs |
| Permissions | Manager role trở lên | Đọc từ AuthConfig.cs |

### Constraints
- [constraint 1]
- [constraint 2]

### Out of scope
- [gì không làm trong iteration này]

### Ready for implementation: [Có / Không]
```

---

## Quy tắc cứng

**KHÔNG được hỏi user về:**
- Tên file, tên class, database schema → đọc code
- Cách feature hiện tại hoạt động → đọc code
- Có API nào không → đọc code, docs
- Config settings → đọc config files

**CHỈ hỏi user về:**
- Business decisions: ưu tiên thế nào, trade-off nào chấp nhận được
- UX preferences: flow nào user muốn khi có ambiguity
- Requirements không có trong codebase: future feature, new domain

---

## Red Flags

| Thought | Reality |
|---------|---------|
| "Câu hỏi này đơn giản, hỏi user cho nhanh" | Nếu có thể đọc code/docs trong < 2 phút → ĐỌC, không hỏi. User time > agent time |
| "Frontier còn dài, câu hỏi sẽ mất thời gian" | Tự tìm giải quyết được nhiều item hơn bạn nghĩ. Hỏi user = last resort |
| "Tôi đã hỏi đủ rồi, có thể bắt đầu code" | KHÔNG. Chỉ bắt đầu khi frontier trống — không phải khi đã hỏi N câu |

---

## Verification (done gate)

- [ ] Design tree đã được xây dựng với tất cả prerequisites
- [ ] Frontier = 0 item
- [ ] Mọi item RESOLVED đều có answer cụ thể (không có "TBD")
- [ ] Output requirements spec đủ để Tech Lead/Dev bắt đầu TDD
