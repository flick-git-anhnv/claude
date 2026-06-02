# TDD-[feature-slug]: [Tên feature]
## Tham chiếu
- PRD: docs/prd/PRD-[feature-slug].md
- User Story: docs/user-stories/US-[XXX].md
- ADR: docs/architecture/ADR-[NNN].md (nếu có)

## Goals / Non-goals
- Goals: ...
- Non-goals: ...

## Kiến trúc đề xuất
```mermaid
[diagram]
```

## API Contract
```typescript
POST /api/v1/[endpoint]
Authorization: Bearer <token>
Body: {
  field: type // mô tả
}
Response 200: {
  ...
}
Response 400: { error: string }
Response 401: { error: "Unauthorized" }
```

## Database schema thay đổi
```sql
-- Migration: add_xxx_to_yyy
ALTER TABLE yyy ADD COLUMN xxx TYPE;
```

## Migration plan
1. ...
2. ...

## Rủi ro & cách giảm thiểu
| Rủi ro | Ảnh hưởng | Cách giảm |
|--------|-----------|-----------|
| ... | High | ... |

## Task breakdown
| ID | Tên task | Owner | Estimate | Phụ thuộc |
|----|----------|-------|----------|-----------|
| T-001 | [tên] | senior-developer | 2d | - |
| T-002 | [tên] | junior-developer | 1d | T-001 |

## Code Review Checklist
- [ ] Đúng AC?
- [ ] Có test (unit + integration)?
- [ ] Handle error đúng?
- [ ] Không có security issue?
- [ ] Performance ổn?
- [ ] Tuân thủ convention?
