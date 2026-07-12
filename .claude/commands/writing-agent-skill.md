---
description: "Dùng khi muốn tạo agent/skill mới cho hệ thống KZTEK theo quy trình TDD-for-documentation — viết test scenario trước, verify agent hiện tại vi phạm (RED), viết định nghĩa agent/skill (GREEN), verify agent mới xử lý đúng, rồi tìm thêm edge case và vá (REFACTOR). KHÔNG dùng khi chỉ muốn sửa agent đã có (→ md-optimizer) hoặc kiểm tra trigger accuracy (→ skill-trigger-test)."
---

# Skill: writing-agent-skill — Tạo agent/skill mới theo TDD

> Học từ obra/superpowers `skills/writing-skills/SKILL.md` — "Writing skills IS Test-Driven Development applied to process documentation."
> (xem `docs/research/RESEARCH-superpowers-2026-07-12.md`, §1.3.7)

## Nguyên tắc cốt lõi

Viết agent/skill mới theo trực giác dẫn đến 2 vấn đề:
1. Agent/skill không thực sự thay đổi behavior — chỉ là documentation mà LLM bỏ qua.
2. Không biết agent/skill có hoạt động đúng không cho đến khi dùng thực tế.

TDD-for-documentation giải quyết cả hai: **bằng chứng trước, định nghĩa sau**.

---

## Quy trình 5 bước (RED → GREEN → REFACTOR)

### Bước 1 — Xác định vấn đề cần giải quyết (tình huống áp lực)

Mô tả rõ:
- **Tình huống gây ra vấn đề** là gì? (VD: agent hay bỏ qua bước scope-check khi user mô tả ngắn)
- **Hành vi vi phạm** cụ thể như thế nào? (VD: Dispatcher routing thẳng WF-FEATURE mà không hỏi priority/scope)
- **Hành vi mong muốn** là gì? (VD: Dispatcher luôn chạy scope-check khi yêu cầu có thể map vào nhiều workflow)

```
Tình huống   : [mô tả kịch bản thực tế gây ra vấn đề]
Vi phạm      : [behavior sai cụ thể — KHÔNG chung chung "chất lượng kém"]
Mong muốn    : [behavior đúng cần đạt được]
```

---

### Bước 2 — RED: Viết test scenario và xác nhận vi phạm

Viết 3–5 test scenario mô tả tình huống gây vi phạm:

```markdown
## Test Scenarios (RED — trước khi có agent/skill):

**Scenario 1:** [User gõ: "..."]
→ Hành vi hiện tại: [mô tả agent làm gì SAI]
→ Hành vi mong muốn: [mô tả agent nên làm gì ĐÚNG]

**Scenario 2:** [User gõ: "..."]
→ Hành vi hiện tại: [...]
→ Hành vi mong muốn: [...]

...
```

**Xác nhận vi phạm (simulation):** Với mỗi scenario, kiểm tra agent/Dispatcher hiện tại có xử lý sai không:
- Đọc definition file hiện có (nếu có) → confirm không có rule nào bắt behavior đúng
- Ghi: `Confirmed: agent hiện tại vi phạm scenario X` hoặc `Not confirmed: agent đã xử lý đúng → không cần skill mới`

Nếu không có scenario nào vi phạm → DỪNG, skill không cần thiết.

---

### Bước 3 — GREEN: Viết định nghĩa agent/skill

Dựa trên test scenarios, viết file agent/skill mới:

**Với Agent** (`.claude/agents/[name].md`):
```markdown
---
name: [kebab-case-name]
description: "[Use when/PHẢI dùng khi] [điều kiện trigger cụ thể từ Bước 1]. KHÔNG dùng khi: [near-miss cases]."
model: [claude-sonnet-4-6 hoặc claude-opus-4-7]
tools: [danh sách tools cần thiết]
---

# [Tên Agent]

## Làm gì
[Nhiệm vụ cụ thể, dựa trên hành vi mong muốn từ Bước 1]

## Red Flags (lý do hay bỏ qua — nhìn nhận lại khi thấy)
| Thought | Reality |
|---------|---------|
| "[Lý do hay bỏ qua]" | "[Phản bác — tại sao lý do đó sai]" |

## Artifact bắt buộc
[File cần tạo ra]
```

**Với Skill** (`.claude/commands/[name].md`):
```markdown
---
description: "[Điều kiện trigger cụ thể — khi nào invoke skill này, không chung chung]"
---

# Skill: [tên]

## Quy trình
[Step-by-step, mỗi bước có output rõ ràng]

## Verification (done gate)
- [ ] [Tiêu chí cụ thể để biết skill đã thực thi đúng]
```

**Quy tắc viết description (quan trọng nhất):**
- PHẢI bắt đầu bằng "Use when..." hoặc "PHẢI dùng agent này khi..." + điều kiện cụ thể
- Thêm "KHÔNG dùng khi:" + near-miss cases để tránh false positive routing
- Càng cụ thể càng tốt — description mơ hồ = LLM bỏ qua

---

### Bước 4 — GREEN verify: Xác nhận agent/skill mới xử lý đúng

Chạy lại test scenarios từ Bước 2 với định nghĩa mới:

```markdown
## Test Scenarios (GREEN — sau khi có agent/skill):

**Scenario 1:** [User gõ: "..."]
→ Description mới có trigger không?: [Có/Không — trích dẫn phần description liên quan]
→ Behavior đúng chưa?: [Pass/Fail — giải thích]

**Scenario 2:** [...]
→ ...
```

Nếu còn scenario Fail → quay lại Bước 3 sửa definition. KHÔNG đánh dấu GREEN khi còn Fail.

---

### Bước 5 — REFACTOR: Tìm edge case và vá

Đặt câu hỏi: "LLM sẽ tìm cớ gì để bỏ qua agent/skill này?"

Viết thêm 3–5 "rationalization scenarios" — tình huống mà agent có thể tự thuyết phục là không cần dùng skill:

```markdown
## Rationalization Scenarios (REFACTOR):

**R1:** "Tình huống này có vẻ quá đơn giản để dùng [skill]"
→ Có bị bỏ qua không?: [Có/Không]
→ Fix: [thêm vào Red Flags table / làm rõ description]

**R2:** "User đã nói rõ rồi, không cần [skill]"
→ ...
```

Với mỗi rationalization scenario bị bỏ qua → thêm dòng vào bảng Red Flags trong definition.

---

## Checklist hoàn thành

- [ ] File agent/skill đã tạo tại đúng vị trí (`.claude/agents/` hoặc `.claude/commands/`)
- [ ] Description bắt đầu bằng "Use when..." / "PHẢI dùng khi..." + điều kiện cụ thể
- [ ] Có "KHÔNG dùng khi:" với near-miss cases
- [ ] Có bảng Red Flags (nếu là agent/skill quan trọng hay bị bỏ qua)
- [ ] Tất cả test scenarios từ Bước 2 đã Pass ở Bước 4
- [ ] Chạy `skill-trigger-test` để verify routing accuracy (xem `.claude/commands/skill-trigger-test.md`)
- [ ] Nếu agent mới → cập nhật đầy đủ routing theo §10 CLAUDE.md (org chart, bảng routing, model assignment)
- [ ] Xuất DOCX+PDF theo §19 CLAUDE.md nếu file .md thuộc docs/

---

## Ví dụ nhanh

**Vấn đề:** Agent hay tuyên bố "Done" mà không chạy verify lệnh.

**RED scenario:** "Senior Developer báo 'code xong rồi' mà không paste output build/test."

**GREEN:** Thêm `## Verification Gate` vào `senior-developer.md` với Iron Law và format output bắt buộc.

**REFACTOR rationalization:** "Build chạy trong đầu rồi, paste output làm gì mất thời gian" → thêm vào Red Flags.
