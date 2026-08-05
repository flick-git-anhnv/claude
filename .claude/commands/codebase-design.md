---
name: codebase-design
description: "PHẢI dùng khi: Tech Lead hoặc Senior Developer cần mô tả cấu trúc code một cách chính xác — khi nói về refactoring points, architectural decisions, code review feedback, hoặc technical design. Skill cung cấp vocabulary chuẩn để phân tích codebase. KHÔNG dùng khi: cần viết code mới (→ tdd); cần document cấu trúc hiện tại vào file (→ CODE-GRAPH.md); hoặc yêu cầu là business domain model (→ domain-modeling)."
---

# Skill: codebase-design — Vocabulary Layer cho Phân tích Codebase

> Học từ `mattpocock/skills` `skills/engineering/codebase-design/SKILL.md`.
> Nguyên tắc cốt lõi: **"Vague terms ('coupling cao', 'không clean') không actionable. Precise vocabulary → precise feedback → precise action."**

---

## 7 Terms Vocabulary

Dùng đúng 7 terms này khi phân tích hay mô tả codebase. Không invent term mới mâu thuẫn với định nghĩa dưới đây.

### 1. Module

**Định nghĩa:** Đơn vị code có ranh giới rõ ràng — class, assembly, namespace, hoặc folder với public API cụ thể. Module che giấu implementation và expose interface.

**Dùng khi:** Mô tả đơn vị độc lập trong codebase. "Module A phụ thuộc vào Module B thông qua interface X."

**Không nói:** "Component", "part", "piece" (quá vague) — dùng "module" + tên cụ thể.

---

### 2. Interface

**Định nghĩa:** Ranh giới public của một module — methods, properties, events mà các module khác có thể gọi. Bao gồm cả C# `interface` và bất kỳ abstraction boundary nào (abstract class, function signature, REST API endpoint).

**Dùng khi:** Mô tả contract giữa hai module. "Interface của ParkingService gồm: CalculateFee(), CreateTicket(), CloseTicket()."

---

### 3. Depth

**Định nghĩa:** Số tầng dependency chain từ entry point đến leaf node. VD: Controller → Service → Repository → Database = depth 4. Depth cao → thay đổi ở leaf ảnh hưởng nhiều tầng.

**Dùng khi:** Đánh giá complexity và coupling. "Feature này có depth 5 — mỗi thay đổi cần trace qua 5 tầng."

**Red flag:** Depth > 4 trong một call chain thường là signal cần refactor.

---

### 4. Seam

**Định nghĩa:** Điểm trong code có thể thay thế behavior mà không cần sửa code xung quanh. Ví dụ: interface injection point, abstract method, function parameter nhận callback. Seam = điểm có thể test với mock hoặc swap implementation.

**Dùng khi:** Tìm điểm để test hoặc refactor. "Không có seam ở đây → không thể test mà không khởi tạo database thật."

---

### 5. Adapter

**Định nghĩa:** Module chuyển đổi interface của external system sang interface mà domain code expect. Adapter ngăn domain code phụ thuộc trực tiếp vào external details.

**Dùng khi:** Mô tả integration boundary. "ZKTecoAdapter converts SDK callback → domain PunchEvent. Domain code không biết ZKTeco tồn tại."

---

### 6. Leverage

**Định nghĩa:** Điểm thay đổi nhỏ trong code tạo ra tác động lớn với caller. Leverage point tốt = thay đổi 1 chỗ, nhiều behavior thay đổi theo mà không sửa caller. Leverage point xấu = thay đổi nhỏ phá nhiều thứ (shotgun surgery).

**Dùng khi:** Chọn nơi để refactor hoặc add feature. "Service layer là leverage point — thêm validation ở đây, mọi UI đều được validate."

---

### 7. Locality

**Định nghĩa:** Mức độ code liên quan về mặt logic nằm gần nhau về mặt vật lý (cùng file, cùng class, cùng folder). Locality cao = dễ hiểu, dễ test. Locality thấp = logic liên quan bị scatter khắp nơi.

**Dùng khi:** Đánh giá tổ chức code. "ParkingFee logic rải rác ở 5 file khác nhau — locality thấp → khó debug khi fee tính sai."

---

## Cách sử dụng trong context cụ thể

### Code Review Feedback

Thay vì:
> "Code này coupling quá cao và không clean."

Dùng:
> "ParkingController có depth 5 (Controller → FeeService → TicketService → Repository → DB). Không có seam giữa FeeService và TicketService → không thể test riêng. Đề xuất: extract ITicketService interface làm seam, inject vào FeeService."

### Architectural Decision

Thay vì:
> "Nên thêm service layer."

Dùng:
> "Thêm ParkingService làm leverage point giữa Controller và Repository. Khi cần thêm business rule, chỉ sửa ở Service — không sửa Controller hay Repository. Cũng tạo seam để test business logic mà không cần database thật."

### Refactoring Discussion

Thay vì:
> "Module này quá phức tạp."

Dùng:
> "ReportModule có locality thấp — PrintService, ExportService, và FilterService nằm ở 3 folder khác nhau nhưng đều xử lý Report. Đề xuất consolidate thành Reports/ với LocalityPrinciple: mọi report logic trong 1 folder."

---

## Verification (done gate)

- [ ] Phân tích dùng ít nhất 3/7 terms từ vocabulary
- [ ] Mỗi vấn đề được mô tả bằng term cụ thể (không phải "complex" hay "messy")
- [ ] Đề xuất refactor/action dùng vocabulary (VD: "tạo seam ở X", "reduce depth từ 5 xuống 3")
- [ ] Không generate code implementation (chỉ describe structure)
