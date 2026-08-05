---
name: tdd
description: "PHẢI dùng khi: viết feature mới cần test, hoặc fix bug và muốn test trước khi sửa code (test-first approach). Trigger: 'viết feature mới có test', 'implement... với TDD', 'sửa bug theo TDD'. KHÔNG dùng khi: debug bug chưa biết nguyên nhân (→ /diagnosing-bugs trước); code không có seam testable nào và không thể refactor để tạo seam (→ viết integration test trước); hoặc task là cấu hình/infra không có logic test được."
---

# Skill: tdd — Red-Green-Refactor với Seam-based Testing

> Học từ `mattpocock/skills` `skills/engineering/tdd/SKILL.md`.
> Nguyên tắc cốt lõi: **"Test behavior, không test implementation. RED trước GREEN. Vertical slice, không horizontal."**

---

## 3 Anti-patterns phải tránh

Nhận biết và từ chối ngay khi thấy:

| Anti-pattern | Dấu hiệu | Fix |
|-------------|---------|-----|
| **Implementation-coupled** | Test gọi internal methods, check private fields, hoặc assert giá trị trung gian của thuật toán | Viết lại: test input → output của behavior, không quan tâm cách đạt được |
| **Tautological** | Test assert cùng logic sẽ có trong code. VD: `Assert(value * 2 == value * 2)` | Test với giá trị cụ thể đã biết trước (VD: `Assert(double(5) == 10)`) |
| **Horizontal slicing** | Test theo layer: unit test cho Repository, unit test cho Service, unit test cho Controller — độc lập nhau | Test theo user story (vertical slice): 1 test cover từ đầu đến cuối 1 scenario người dùng |

---

## Quy trình Red-Green-Refactor

### Bước 0 — Xác định Seam

> Seam = điểm trong code hiện tại có thể test mà không cần sửa code sản phẩm. Ưu tiên: interface, abstract class, function signature rõ ràng, dependency injection point.

ĐỌC code liên quan. Xác định:
- Seam nào có thể test behavior mong muốn?
- Có cần tạo seam mới không? (chỉ tạo khi thật sự không có)
- Dependency nào cần mock/stub?

Ghi lại: `Seam: [tên interface/function/class sẽ test qua]`

---

### Bước 1 — RED: Viết failing test

VIẾT test TRƯỚC khi có implementation.

Format test scenario theo user story:

```
// Scenario: [Mô tả behavior từ góc nhìn user]
// Given: [Context / initial state]
// When: [Action]
// Then: [Expected outcome — giá trị cụ thể, không phải "nên tăng" hay "nên thay đổi"]
```

Quy tắc viết test:
- Assert với giá trị LITERAL (5000, "error", true) — không với biến tính từ implementation
- Đặt tên: `[WhenCondition]_[Behavior]()` — VD: `WhenParkingIs35Minutes_FeeIs10000()`
- Mỗi test 1 scenario, không 1 test nhiều asserts cho nhiều scenarios
- CHẠY test ngay: phải fail vì lý do đúng (chưa có implementation), không fail vì compile error hay test setup sai

**DỪNG nếu:** Test fail vì lý do sai (exception trong setup, sai seam) → fix test setup trước, không viết code.

---

### Bước 2 — GREEN: Viết implementation tối thiểu

VIẾT implementation TỐI THIỂU để test pass.

Quy tắc:
- Làm test pass — không làm thêm gì khác (chưa handle edge case, chưa optimize)
- Nếu cần hardcode để pass → OK ở bước này (refactor sau)
- Chạy test: pass → tiếp tục. Fail → debug implementation (KHÔNG sửa test để pass)

---

### Bước 3 — Thêm test cho edge cases

Với mỗi edge case quan trọng → lặp lại Bước 1-2:
- Boundary values: 0, 1, max
- Error paths: invalid input, permission denied, not found
- Race conditions (nếu có concurrency)

Không viết tất cả edge case trước rồi mới code — từng cặp (test → pass) một.

---

### Bước 4 — REFACTOR

Khi tất cả test đã pass:
- Clean up code: remove duplication, rename variables, extract methods
- KHÔNG thêm feature mới ở bước này
- Sau mỗi thay đổi refactor: chạy toàn bộ test suite → phải vẫn pass

---

## Red Flags

| Thought | Reality |
|---------|---------|
| "Viết implementation trước rồi test sau cho nhanh" | Test sau = test confirms implementation, không test behavior. Anti-pattern: tautological |
| "Test này quá trivial, không cần" | Trivial test hôm nay là regression guard ngày mai. Viết ngay |
| "Tôi sẽ refactor test sau" | Test được refactor ít hơn code. Nếu test khó đọc ngay lúc viết → seam có thể sai |
| "Mock tất cả dependencies cho đơn giản" | Over-mocking = implementation-coupled test. Mock chỉ external dependencies (DB, HTTP, clock) |

---

## Verification (done gate)

- [ ] Có ≥ 1 failing test viết TRƯỚC khi có implementation
- [ ] Không có anti-pattern: implementation-coupled, tautological, horizontal slicing
- [ ] Mỗi test assert giá trị literal, không biểu thức phức tạp
- [ ] Test suite pass 100% sau khi xong
- [ ] Tên test mô tả behavior (không phải tên method đang test)
