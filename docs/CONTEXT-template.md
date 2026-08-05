---
project: [Tên project / module]
domain: [Tên domain — VD: parking-management, access-control, attendance]
created: YYYY-MM-DD
updated: YYYY-MM-DD
maintainer: [Team / Agent tạo file]
---

# CONTEXT.md — Domain Vocabulary: [Project Name]

> **Mục đích:** File từ điển domain của project — đọc TRƯỚC khi viết code về domain này.
> Agents dùng file này để code với đúng terminology, không tự bịa term mới.
>
> **Học từ:** `mattpocock/skills` `skills/engineering/domain-modeling/SKILL.md`
> **Skill duy trì:** `/domain-modeling`

---

## 1. Entities (Thực thể domain chính)

> Entity = đối tượng có danh tính riêng biệt trong domain (không phải chỉ database table).
> Mỗi entity: definition 1-2 câu, attributes chính, phân biệt với entity gần giống.

### [Tên Entity 1]

**Definition:** [1-2 câu mô tả entity từ góc nhìn business, không phải tech]

**Attributes chính:** [Thuộc tính quan trọng nhất — không liệt kê hết field]

**Phân biệt:** [Khác gì với entity dễ nhầm lẫn nhất]

---

### [Tên Entity 2]

**Definition:** [...]

**Attributes chính:** [...]

**Phân biệt:** [...]

---

*(Thêm entity theo cùng format)*

---

## 2. Concepts (Khái niệm business không phải entity)

> Concept = khái niệm quan trọng trong domain nhưng không phải là object có danh tính (không persist riêng).

| Concept | Definition | Ví dụ |
|---------|-----------|-------|
| [Concept 1] | [1 câu] | [Ví dụ cụ thể] |
| [Concept 2] | [1 câu] | [Ví dụ cụ thể] |

---

## 3. Business Rules (Quy tắc business ảnh hưởng đến implementation)

> Rules ở đây = quy tắc domain mà developer PHẢI biết trước khi implement. Không phải tất cả business rule — chỉ những rule ảnh hưởng đến cách tính toán, validation, hoặc flow.

| # | Rule | Ảnh hưởng implementation |
|---|------|------------------------|
| BR-1 | [Quy tắc cụ thể] | [Code phải làm gì để tuân theo rule này] |
| BR-2 | [Quy tắc cụ thể] | [...] |

---

## 4. Boundaries (Ranh giới domain)

**Thuộc domain này:**
- [Gì nằm trong phạm vi module/domain này]
- [...]

**KHÔNG thuộc domain này (external systems):**
- [External system 1] — giao tiếp qua [interface/API]
- [External system 2] — [...]

---

## 5. Terms to Avoid (Tránh nhầm lẫn)

| Term nên tránh | Dùng thay bằng | Lý do |
|---------------|---------------|-------|
| [Term 1] | [Term đúng] | [Tại sao term cũ gây nhầm] |
| [Term 2] | [Term đúng] | [...] |

---

## 6. Lịch sử cập nhật

| Ngày | Phiên bản | Thay đổi | Người cập nhật |
|------|-----------|---------|---------------|
| YYYY-MM-DD | v1.0 | Tạo mới | [Agent/User] |

---

*File này được tạo và duy trì bởi skill `/domain-modeling`.*
*Mọi agent làm việc với domain [project name] đều phải đọc file này trước.*
