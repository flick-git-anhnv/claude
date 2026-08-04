---
description: "Dùng khi cần điền mục 'CODE-GRAPH impact' trong PR checklist (§15.3 CLAUDE.md). Skill tự động chạy git diff → tra CODE-GRAPH → xuất depth-1/depth-2 impact section sẵn để paste. Gọi bằng '/detect-impact' trước khi tạo PR hoặc khi cần đánh giá blast radius của một thay đổi."
---

# Skill: /detect-impact

> **Mục đích:** Semi-automate phần "CODE-GRAPH impact" trong PR checklist §15.3 — thay vì trace thủ công qua CODE-GRAPH.md, skill này làm tự động và output template-filled sẵn để paste.
>
> **Học từ:** `detect_changes` MCP tool của GitNexus (abhigyanpatwari/GitNexus) — nhận git diff → map sang affected nodes → trả về theo depth. Pattern áp dụng vào KZTEK workflow với CODE-GRAPH.md tĩnh thay vì graph DB.
>
> **Phụ thuộc:** Cần `code-graph/CODE-GRAPH.md` có cột `Callers/Used-by` trong bảng Module chính (áp dụng từ template v2 — GX-1). Nếu project dùng `graphify`, ưu tiên `graphify query --node <module>` thay vì đọc CODE-GRAPH.md thủ công.

---

## Quy trình thực hiện

### Bước 1 — Lấy danh sách file thay đổi

```bash
git diff --name-only HEAD
```

Nếu muốn so với nhánh cụ thể (VD: main):
```bash
git diff --name-only main...HEAD
```

Ghi lại danh sách file thay đổi. Nếu không có file nào → output "Không có thay đổi nào trong working tree / so với HEAD."

### Bước 2 — Kiểm tra CODE-GRAPH

**Nếu project đã cài `graphify`** (kiểm tra: `pip show graphifyy` hoặc có file `graph.json` ở root):
- Dùng `graphify query --node <module-name>` để lấy callers/used-by cho mỗi module thay đổi
- `graphify update --diff` để đảm bảo graph cập nhật với git diff hiện tại
- Bỏ qua Bước 2b-2c, dùng output của graphify cho Bước 3

**Nếu không có graphify** → đọc thủ công:

```
Read: code-graph/CODE-GRAPH.md
```

Kiểm tra 2 điều kiện:
1. File `code-graph/CODE-GRAPH.md` có tồn tại không?
2. Bảng "Module chính" có cột `Callers/Used-by` không?

**Nếu CODE-GRAPH không tồn tại:**
```
BLOCK: code-graph/CODE-GRAPH.md không tồn tại.
→ Cần tạo CODE-GRAPH.md từ template trước khi dùng skill này.
→ Tham khảo: .claude/templates/CODE-GRAPH-template.md và CLAUDE.md §17.
```

**Nếu CODE-GRAPH có nhưng thiếu cột Callers/Used-by:**
```
BLOCK: Bảng Module chính trong CODE-GRAPH.md chưa có cột 'Callers/Used-by'.
→ Cần cập nhật CODE-GRAPH.md theo template mới (GX-1 — thêm cột Callers/Used-by).
→ Sau khi cập nhật, chạy lại /detect-impact.
→ Nếu project đã cài graphify: dùng 'graphify query --node <module>' để lấy caller info.
```

### Bước 3 — Map file thay đổi → module

Với mỗi file trong danh sách từ Bước 1:
- Tìm module tương ứng trong bảng Module chính của CODE-GRAPH (so sánh theo cột `Path`)
- Nếu không tìm thấy module → ghi chú "File `<path>` chưa có module tương ứng trong CODE-GRAPH"

### Bước 4 — Traverse depth-1 và depth-2

**Depth-1 (WILL BREAK):** Với mỗi module đã tìm được ở Bước 3 → đọc cột `Callers/Used-by` → đây là danh sách depth-1.

**Depth-2 (LIKELY AFFECTED):** Với mỗi module trong danh sách depth-1 → tìm module đó trong bảng CODE-GRAPH → đọc cột `Callers/Used-by` của nó → đây là danh sách depth-2.

Gộp và deduplicate (loại bỏ trùng lặp).

### Bước 5 — Output impact section

Output theo format §15.3 CLAUDE.md, sẵn sàng copy-paste vào PR checklist:

```
## CODE-GRAPH Impact (tự động từ /detect-impact — YYYY-MM-DD)

- Depth-1 (WILL BREAK):
  [danh sách module depth-1, mỗi module 1 dòng, hoặc "Isolated change — không có module nào phụ thuộc trực tiếp"]

- Depth-2 (LIKELY AFFECTED):
  [danh sách module depth-2, hoặc "Không xác định được — cần trace thêm thủ công" nếu depth-1 module không có trong CODE-GRAPH]

- Module chưa map được trong CODE-GRAPH:
  [danh sách file không tìm thấy module tương ứng, hoặc "Không có"]

- Lưu ý: Impact section được tạo tự động dựa trên CODE-GRAPH.md tĩnh.
  Xác minh thủ công nếu có thay đổi gần đây chưa cập nhật vào CODE-GRAPH.
```

---

## Xử lý ngoại lệ

| Tình huống | Hành động |
|---|---|
| Không có git diff (commit clean) | Thông báo "Không có file nào thay đổi so với HEAD" |
| Module có `Callers/Used-by: []` hoặc để trống | Depth-1 = "Isolated change" |
| Depth-1 module không tìm thấy trong CODE-GRAPH | Depth-2 = "Cần trace thêm thủ công cho [module X]" |
| CODE-GRAPH entry có `Last verified` > 30 ngày + module có commit gần đây | Cảnh báo: "Module [X] có thể stale (Last verified: YYYY-MM-DD, xem §17.2) — xác nhận thủ công" |
| Project đã cài graphify | Ưu tiên dùng `graphify query` — nhanh hơn và chính xác hơn CODE-GRAPH.md tĩnh |

---

## Ví dụ output hoàn chỉnh

```
## CODE-GRAPH Impact (tự động từ /detect-impact — 2026-08-04)

Files thay đổi: src/services/auth.ts, src/models/user.ts

- Depth-1 (WILL BREAK):
  - UserController (src/controllers/user.ts) — gọi AuthService trực tiếp
  - AdminController (src/controllers/admin.ts) — gọi AuthService trực tiếp

- Depth-2 (LIKELY AFFECTED):
  - ApiRouter (src/routes/index.ts) — gọi UserController và AdminController

- Module chưa map được trong CODE-GRAPH:
  Không có

- Lưu ý: Impact section được tạo tự động dựa trên CODE-GRAPH.md tĩnh.
  Xác minh thủ công nếu có thay đổi gần đây chưa cập nhật vào CODE-GRAPH.
```

---

> **Sau khi dùng:** Copy phần output vào mục "CODE-GRAPH impact" trong PR checklist §15.3. Tech Lead đọc depth-1 để ước lượng rủi ro review.
