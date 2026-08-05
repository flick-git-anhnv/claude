---
name: domain-modeling
description: "PHẢI dùng khi: bắt đầu project mới cần shared vocabulary, onboard agent vào codebase chưa biết, phát hiện agent dùng terminology không nhất quán trong domain, hoặc khi grilling/requirements reveal nhiều domain terms mới. KHÔNG dùng khi: project đã có CONTEXT.md đầy đủ và không có entity mới (→ đọc CONTEXT.md hiện có là đủ); domain là generic/không có business rules đặc thù (CRUD thuần túy không cần domain model); hoặc chỉ cần data modeling DB schema (→ TDD-*.md trong docs/tech-design/)."
---

# Skill: domain-modeling — Tạo và Duy trì CONTEXT.md

> Học từ `mattpocock/skills` `skills/engineering/domain-modeling/SKILL.md`.
> Nguyên tắc cốt lõi: **"CONTEXT.md là shared vocabulary — agent đọc trước khi viết code về domain. Không bịa term mới khi đã có trong CONTEXT.md."**

---

## Vai trò của CONTEXT.md

`CONTEXT.md` là file từ điển domain của project — nơi define rõ:
- Mỗi entity trong domain nghĩa là gì (không phải tên database table)
- Business rules sử dụng term nào (VD: "ticket" hay "session"? "fee" hay "charge"?)
- Ranh giới domain: gì thuộc module này, gì không thuộc
- Terms nên tránh vì gây nhầm lẫn

Agent đọc CONTEXT.md → code với đúng ngôn ngữ domain → không có drift terminology giữa code, comments, docs, và communication.

---

## Bước 1 — Kiểm tra CONTEXT.md có sẵn chưa

ĐỌC `CONTEXT.md` ở root project hoặc `docs/CONTEXT.md`:

- Nếu có → sang Bước 4 (Update mode)
- Nếu không → sang Bước 2 (Create mode)

---

## Bước 2 — Thu thập domain information (Create mode)

BLOCK nếu không có ít nhất 1 trong 3 nguồn:
- Mô tả domain từ user (entities, business rules, use cases)
- Code hiện tại để đọc (models, DTOs, services)
- Existing documentation (PRD, user story)

Thu thập từ nguồn có sẵn:
1. ĐỌC user story / PRD để lấy terminology từ business perspective
2. ĐỌC model/entity classes để lấy terminology từ code perspective
3. HỎI user để resolve conflict khi có (VD: business dùng "ticket" nhưng code dùng "session")

---

## Bước 3 — Tạo CONTEXT.md từ template

GHI `CONTEXT.md` dùng template từ `docs/CONTEXT-template.md`. Điền đầy đủ:

**Entities:** Mỗi entity = 1 subsection với definition, attributes chính, ranh giới
**Concepts:** Business concepts không phải entity (VD: "session" là concept, không phải table)
**Business Rules:** Rule ảnh hưởng đến implementation (VD: "phí tính theo tròn 30 phút, tối thiểu 1 chu kỳ")
**Boundaries:** Gì thuộc domain này, gì là external system
**Terms to Avoid:** Synonyms gây nhầm lẫn, technical jargon không dùng trong business context

---

## Bước 4 — Update CONTEXT.md (Update mode)

ĐỌC CONTEXT.md hiện tại trước khi thay đổi bất cứ gì.

Khi thêm entity/concept mới:
1. Kiểm tra: term mới có conflict với term đã có không?
   - Nếu conflict → flag cho user: "Term '[X]' có vẻ trùng với '[Y]' đã có. Bạn muốn: (a) replace, (b) thêm như concept phân biệt, (c) thêm vào 'Terms to Avoid'?"
   - KHÔNG tự quyết định khi có conflict
2. Thêm definition vào đúng section (Entity/Concept/Rule)
3. Update "Last updated" trong frontmatter

---

## Quy tắc viết definition

Definition tốt:
- 1-2 câu, đủ để developer không quen domain hiểu ngay
- Phân biệt entity này với entity gần giống (VD: "Ticket khác Session ở chỗ...")
- Không dùng tech jargon (không viết "ParkingTicket entity maps to Tickets table")

Definition xấu:
- "A parking fee is the fee for parking" (tautological)
- "Object representing a vehicle" (không có thông tin domain)
- Quá dài (> 3 câu) — nếu cần dài hơn → thêm mục "Detail" riêng

---

## Hướng dẫn sử dụng CONTEXT.md cho Agents

> Nhúng vào prompt của agent khi làm task domain-specific:

```
Đọc CONTEXT.md trước khi code:
- Dùng đúng tên entity/concept từ CONTEXT.md (không tự đặt tên mới)
- Nếu gặp term không có trong CONTEXT.md → dùng /domain-modeling để add trước khi code
- Business rules trong CONTEXT.md → phải được reflect trong test scenarios
```

---

## Verification (done gate)

- [ ] CONTEXT.md tồn tại ở root project hoặc docs/CONTEXT.md
- [ ] Tất cả entities chính có definition
- [ ] Business rules liên quan đến implementation được list
- [ ] Có mục "Terms to Avoid"
- [ ] Có mục "Boundaries" (gì thuộc/không thuộc domain)
- [ ] Không có conflict terminology chưa được resolve
