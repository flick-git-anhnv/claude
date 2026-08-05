---
name: code-review
description: "PHẢI dùng khi: cần review code theo 2 trục độc lập — chất lượng code (Standards) và đối chiếu với requirements (Spec). Trigger: 'review PR này', 'kiểm tra code trước khi submit', 'review xem đã đủ AC chưa', Senior/Junior Developer hoàn thành code và cần structured review trước khi gửi Tech Lead. KHÔNG dùng khi: chỉ cần check security (→ security-audit-stride); chỉ cần verify build/test pass (→ verify-pr); hoặc chỉ hỏi về naming/style convention (→ coding standards document)."
---

# Skill: code-review — 2-Axis Parallel Review

> Học từ `mattpocock/skills` `skills/engineering/code-review/SKILL.md`.
> Nguyên tắc cốt lõi: **"Hai trục độc lập — Standards (chất lượng) và Spec (yêu cầu). Báo cáo riêng, không gộp."**

---

## Hai trục review (luôn chạy đồng thời)

| Trục | Kiểm tra gì | Input cần | Output |
|------|------------|----------|--------|
| **Standards** | Code quality: Fowler smells + KZTEK repo standards | Code diff / files đã thay đổi | Danh sách smells tìm được, mỗi item có file:line + severity + fix suggestion |
| **Spec** | Requirements matching: AC/user story/TDD | Code diff + AC hoặc user story gốc | Mỗi AC: PASS / FAIL / PARTIALLY, kèm evidence |

---

## Bước 1 — Thu thập input

ĐỌC:
1. Code diff / files cần review (Glob, Read, Grep)
2. AC / user story / requirements (từ docs/user-stories/, PR description, hoặc user cung cấp)

BLOCK nếu:
- Không có code để review
- Spec axis: không có AC/user story → "Spec axis: BLOCKED — Cần cung cấp AC hoặc user story để check. Link: [yêu cầu link task]"

Không tự đoán requirements khi không có AC.

---

## Bước 2 — Standards Review (Trục 1)

### Fowler 12 Smells — checklist

Kiểm tra từng smell, đánh dấu: PASS / FAIL (có smell)

| # | Smell | Dấu hiệu | Severity |
|---|-------|---------|---------|
| 1 | Long Method | Method > 20 dòng (không counting comments) | P2 |
| 2 | Large Class | Class > 200 dòng hoặc > 15 public methods | P1 |
| 3 | Long Parameter List | > 4 parameters trong 1 method | P2 |
| 4 | Divergent Change | Class thay đổi vì nhiều lý do khác nhau (SRP violation) | P1 |
| 5 | Shotgun Surgery | 1 thay đổi logic → phải sửa nhiều class | P1 |
| 6 | Feature Envy | Method dùng data/method của class khác nhiều hơn của chính nó | P2 |
| 7 | Data Clumps | Cùng nhóm variables xuất hiện ở nhiều nơi, không được encapsulate | P2 |
| 8 | Primitive Obsession | Dùng string/int cho domain concept có thể là class | P3 |
| 9 | Switch Statements | `switch/if-else` dài có thể thay bằng polymorphism | P2 |
| 10 | Parallel Inheritance | Thêm subclass ở nơi này buộc thêm subclass ở nơi khác | P1 |
| 11 | Lazy Class | Class làm quá ít — nên inline vào class khác | P3 |
| 12 | Speculative Generality | Code "chuẩn bị cho tương lai" nhưng không ai dùng hiện tại | P3 |

### KZTEK Repo Standards

Kiểm tra thêm:
- [ ] UI code: có dùng `KztekComponent` / `KztekComponentAvalonia` thay vì native controls? (§20.1)
- [ ] C# code: có tách tab/section thành UserControl riêng? (§20.4)
- [ ] Có cập nhật tài liệu tương ứng? (§15.1)
- [ ] Có `## Checklist tài liệu đồng bộ` trong PR? (§15.3)

---

## Bước 3 — Spec Review (Trục 2)

Với mỗi AC / user story:

```
AC #[N]: [Nội dung AC gốc]
→ Status: PASS / FAIL / PARTIALLY
→ Evidence: [Tìm thấy implementation ở file:line] hoặc [Không tìm thấy]
→ Gap (nếu FAIL): [Cụ thể thiếu gì]
```

**PASS:** Code implement đúng và đủ theo AC.
**FAIL:** AC không được implement, hoặc implement sai behavior.
**PARTIALLY:** AC được implement nhưng thiếu edge case quan trọng.

---

## Bước 4 — Tổng hợp báo cáo

Output format bắt buộc:

```markdown
## Code Review Report — [PR title / task name]

### TRỤC 1 — STANDARDS

**Smells phát hiện:**
| # | Smell | File:Line | Severity | Đề xuất fix |
|---|-------|----------|---------|------------|
| 1 | Large Class | UserService.cs:1 | P1 | Extract PaymentUserService, AuthUserService |

**KZTEK Standards:**
- [ ] UI: KztekComponent ✅ / ❌
- [ ] UserControl tách đúng ✅ / ❌
- [ ] Tài liệu cập nhật ✅ / ❌

**Tổng: [N] smell, [M] standards issues. Severity cao nhất: [P0/P1/P2/P3]**

---

### TRỤC 2 — SPEC

| AC # | Nội dung | Status | Evidence |
|------|---------|--------|---------|
| AC-1 | Export PDF | PASS | ParkingExporter.cs:45 |
| AC-2 | Email notification | FAIL | Không tìm thấy EmailService call |

**Tổng: [N] AC pass, [M] fail, [K] partially.**

---

### Quyết định

> [APPROVE / REQUEST-CHANGES / NEEDS-DISCUSSION]

Lý do: [1-2 câu tóm tắt vấn đề chính nếu REQUEST-CHANGES]
```

---

## Red Flags

| Thought | Reality |
|---------|---------|
| "Smell nhỏ, không cần report" | Smell nhỏ hôm nay = tech debt tháng sau. Report với severity thấp (P3), không bỏ qua |
| "Có vẻ đúng spec rồi" | Đọc AC text gốc. "Có vẻ" chưa đủ — cần evidence file:line cụ thể |
| "Gộp Standards và Spec vào chung cho gọn" | Hai trục phục vụ hai audience khác nhau. Gộp làm khó track từng loại vấn đề |

---

## Verification (done gate)

- [ ] Standards report có đầy đủ 12 smell items (PASS hoặc FAIL)
- [ ] Spec report có mỗi AC được check (PASS/FAIL/PARTIALLY với evidence)
- [ ] Hai reports RIÊNG BIỆT trong output
- [ ] Mỗi FAIL/PARTIALLY item có action item cụ thể
- [ ] Quyết định cuối (APPROVE / REQUEST-CHANGES) được nêu rõ
