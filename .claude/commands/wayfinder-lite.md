---
name: wayfinder-lite
description: "PHẢI dùng khi: user mô tả work 'large and foggy' — biết muốn đi đến đâu nhưng không biết bắt đầu từ đâu, hoặc không chắc destination cụ thể là gì. Trigger: 'không biết bắt đầu từ đâu', 'foggy work', 'cần figure out approach trước', 'cải thiện X nhưng không rõ path'. KHÔNG dùng khi: đã có destination rõ VÀ path rõ (→ task-planner ngay); đây là bug report (→ diagnosing-bugs); hoặc cần phân tích requirements chi tiết (→ grilling)."
disable-model-invocation: true
---

# Skill: wayfinder-lite — Decision Ticket cho Foggy Work

> Học từ `mattpocock/skills` `skills/engineering/wayfinder/SKILL.md`.
> Nguyên tắc cốt lõi: **"Destination first. Identify fog. Make key decisions. THEN plan."**
>
> **Phân biệt với task-planner:** wayfinder-lite = pre-planning (navigate foggy territory). task-planner = planning (build execution plan khi destination đã rõ). Wayfinder trước, task-planner sau.

---

## Khi nào là "foggy work"?

Dấu hiệu cần wayfinder:
- Không biết kết quả cuối trông như thế nào
- Biết destination nhưng không biết path qua "fog"
- Có nhiều unknowns ảnh hưởng đến approach (chưa profile, chưa benchmark, chưa research options)
- Task lớn mà scope chưa rõ ranh giới

Không phải foggy work → bỏ qua wayfinder:
- Task có AC cụ thể, approach rõ ràng → dùng task-planner ngay
- Bug report với steps to reproduce → dùng diagnosing-bugs

---

## Quy trình

### Bước 1 — Clarify destination

Destination = "Sau khi hoàn thành, thế giới trông như thế nào?" — cụ thể và có thể quan sát được.

HỎI (nếu destination mơ hồ):
- "Kết quả bạn muốn đo được là gì? (VD: response time < 200ms, không còn lỗi X, tính năng Y hoạt động)"
- "Bạn biết mình 'xong' khi nào?"

KHÔNG bắt đầu phân tích fog khi chưa có destination rõ ràng.

Sau khi có destination → ghi ngắn gọn (1 câu):
> **Destination:** [Kết quả cụ thể và có thể quan sát]

---

### Bước 2 — Map the fog (Fog of War)

Liệt kê unknowns ngăn cản việc bắt đầu hoặc chọn approach:

| # | Unknown | Có thể resolve bằng | Priority |
|---|---------|-------------------|---------|
| F1 | [Gì chưa biết?] | [Research / Profile / Benchmark / Hỏi user] | High/Med/Low |
| F2 | [...] | [...] | [...] |

**Fog priority:**
- **High:** Resolve trước — answer sẽ ảnh hưởng đến toàn bộ approach
- **Med:** Cần biết trước khi code, nhưng không block design
- **Low:** Nice to know — có thể quyết định sau

---

### Bước 3 — Key decisions

Decisions cần được made TRƯỚC khi bắt đầu để không bị paralyzed giữa chừng:

| # | Decision | Options | Ảnh hưởng |
|---|---------|---------|---------|
| D1 | [Quyết định gì?] | [A] vs [B] | [Nếu A: ... / Nếu B: ...] |

Với mỗi decision:
- Nếu có đủ thông tin để quyết định ngay → quyết định và ghi rationale
- Nếu phụ thuộc vào fog → ghi "TBD sau F[N] được resolve"

---

### Bước 4 — Tạo wayfinder file

GHI `_workspace/WAYFINDER-[slug].md` với format:

```markdown
# WAYFINDER: [Work description]

**Created:** YYYY-MM-DD
**Status:** Navigating / Ready-for-plan

## Destination

[1 câu mô tả kết quả cuối cụ thể]

## Fog of War

| # | Unknown | Resolve bằng | Priority | Status |
|---|---------|------------|---------|--------|
| F1 | | | High | Open |
| F2 | | | Med | Open |

## Key Decisions

| # | Decision | Choice | Rationale |
|---|---------|-------|---------|
| D1 | | TBD / [choice] | |

## Next action

[1 action cụ thể nhất để bắt đầu resolve fog — thường là F1 (highest priority)]

---
*Sau khi fog resolved + decisions made → chạy `/task-planner` để tạo execution plan.*
```

---

## Sau khi wayfinder

Skill wayfinder-lite KHÔNG tạo plan. Sau khi sử dụng wayfinder:

1. **Resolve fog:** Thực hiện actions được liệt kê (research, benchmark, profile...)
2. **Update wayfinder file:** Đánh dấu fog items Resolved, fill in decisions
3. **Khi fog = 0 Open, decisions = 0 TBD:** Status → "Ready-for-plan"
4. **Invoke task-planner:** Tạo execution plan từ destination + decisions đã rõ

---

## Red Flags

| Thought | Reality |
|---------|---------|
| "Tôi đã biết destination rồi, không cần wayfinder" | Nếu path cũng rõ → đúng, skip wayfinder. Nếu chỉ destination rõ mà path foggy → wayfinder giúp resolve fog trước khi plan |
| "Wayfinder là plan, không khác gì task-planner" | Khác hoàn toàn: wayfinder không có steps, estimates, hay sprint. Wayfinder = compass. task-planner = map với turn-by-turn directions |
| "Tôi sẽ figure out fog khi làm" | "Fog in flight" = sửa đổi plan giữa chừng = tốn gấp 3x thời gian. Resolve trước, plane trước |

---

## Verification (done gate)

- [ ] Destination được chốt (1 câu cụ thể, có thể quan sát)
- [ ] Fog items được liệt kê với priority
- [ ] Mỗi fog item có "resolve bằng" cụ thể
- [ ] Key decisions được identify (dù chưa resolved)
- [ ] File `_workspace/WAYFINDER-[slug].md` được tạo
- [ ] Next action cụ thể được nêu
