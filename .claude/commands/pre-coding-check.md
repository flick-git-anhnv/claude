---
description: >
  Compact pre-coding checklist cho coding agents (Senior Dev, Junior Dev, Tech Lead).
  Invoke trước khi bắt đầu viết/sửa code bất kỳ — thay thế việc đọc lại toàn bộ CLAUDE.md.
  Học từ pattern SKILL.md của MemMachine/MemMachine (packages/skills/memmachine-memory/SKILL.md).
---

# Pre-Coding Check — Compact Skill

> Chạy 3 bước này theo thứ tự trước khi viết/sửa bất kỳ dòng code nào.
> Tổng thời gian: ≤ 3–5 tool calls. Không cần đọc lại CLAUDE.md đầy đủ.

---

## Bước 1 — CODE-GRAPH (bắt buộc)

```
1. Glob "code-graph/CODE-GRAPH.md" → có file không?
2. Có → Read CODE-GRAPH.md → trả lời ≥ 3/5 câu:
     (a) Module/file liên quan đến task nằm ở đâu?
     (b) Module đó phụ thuộc vào package/module nào?
     (c) Ai gọi module/function này (callers)?
     (d) API endpoint hoặc class public interface ở file:line nào?
     (e) Có thay đổi gần đây ở module liên quan không?
3. ≥ 3/5 câu trả lời được → chuyển Bước 2.
4. Còn thiếu câu nào → Sufficiency tracking:
     → Ghi rõ câu (a/b/c/d/e) nào còn thiếu
     → Chỉ đọc ĐÚNG source file của câu đó (không đọc lan)
     → Xong → chuyển Bước 2.
5. Không có CODE-GRAPH → khảo sát project → tạo CODE-GRAPH.md từ template → chuyển Bước 2.
```

---

## Bước 2 — LESSONS (Simple Query Rule)

```
1. Glob "C:\Users\nguye\.claude\lessons\**\*.md" → đọc INDEX.md → xác định category.
2. Đọc 1 file lesson rõ nhất liên quan đến task (không đọc cả folder).
3. Đủ để tránh lỗi đã biết? → DỪNG. Chuyển Bước 3.
4. Còn thiếu gì cụ thể? → Đọc thêm đúng 1 file có chứa thông tin đó.
5. Tối đa 3 lượt đọc lesson → nếu vẫn thiếu → chuyển Bước 3 ngay
   (ghi lesson mới sau nếu gặp lỗi thực tế).
```

> **Nếu task liên quan Avalonia UI:** Bổ sung truy vấn nhanh qua UI UX Pro Max skill TRƯỚC KHI đọc lesson (tiết kiệm tool call):
> ```bash
> python .claude/skills/ui-ux-pro-max/scripts/search.py "<topic-keyword>" --stack avalonia
> ```
> Kết quả trả về Do/Don't + code example + link docs chính thức — dùng làm context chính.
> Nếu kết quả chưa đủ hoặc cần gotcha KZTEK-specific (VD: KzPasswordTextBox, KztekComponentAvalonia) → tiếp tục đọc lesson Avalonia theo Simple Query Rule như thường.
> Xem thêm lệnh: `.claude/commands/ui-ux-pro-max.md`

---

## Bước 3 — GOTCHAS (lọc theo Category)

```
1. Đọc GOTCHAS.md mục "Bảng lọc theo Category" ở đầu file.
2. Xác định category phù hợp với loại lỗi có thể gặp:
     [SCRIPT]     → lỗi Python script, ImportError, tool CLI
     [ENCODING]   → lỗi PowerShell encoding, tiếng Việt
     [UI-BINDING] → lỗi Avalonia/WinForms binding, UserControl
     [CONFIG]     → cài đặt sai, tên package sai, path sai
     [GIT]        → git workflow, hook, merge
     [AGENT-LOOP] → agent stuck, loop detection
3. Chỉ đọc entries thuộc category đó — bỏ qua entries category khác.
4. Nếu loại lỗi không thuộc category nào → đọc mục lục, chọn entry gần nhất.
```

---

## Sau 3 bước → Bắt đầu coding

Không cần đọc thêm file nào ngoài những gì đã xác định ở trên trừ khi task yêu cầu rõ ràng.

---

## Ghi nhớ sau khi coding xong

- Nếu thay đổi structure/API → cập nhật CODE-GRAPH.md + xuất PDF (§17 CLAUDE.md).
- Nếu phát hiện lỗi ngầm mới → thêm entry vào GOTCHAS.md ngay (§GOTCHAS.md template).
- Nếu học được pattern mới → ghi lesson vào `lessons/[category]/` ngay (§CLAUDE.md global).
