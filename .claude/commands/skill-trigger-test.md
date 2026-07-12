---
description: "Dùng khi muốn kiểm tra trigger accuracy của một agent hoặc skill mới/vừa sửa — chạy bộ test 'should-trigger' (8-10 query thực tế) và 'should-NOT-trigger' (8-10 near-miss query) để xác nhận Dispatcher routing đúng. Gọi sau khi tạo/sửa .claude/agents/*.md hoặc .claude/commands/*.md, hoặc khi nghi ngờ routing conflict giữa 2 agent."
---

# Skill: skill-trigger-test — Kiểm thử trigger accuracy của agent/skill

> Học từ revfactory/harness `skill-testing-guide.md` §7 — kiểm tra WITH-skill vs WITHOUT-skill, should-trigger vs should-NOT-trigger cases.

## Mục đích

Xác nhận rằng một agent/skill mới hoặc vừa sửa:
1. Được Dispatcher gọi đúng khi cần (should-trigger).
2. KHÔNG bị gọi nhầm trong các tình huống tương tự nhưng khác (should-NOT-trigger / near-miss).

## Quy trình thực hiện

### Bước 1 — Xác định đối tượng test

```
Agent/skill cần test : [tên file, VD: .claude/agents/code-migrator.md]
Phiên bản            : [mới tạo / vừa sửa description ngày ...]
Trigger chính        : [tóm tắt 1 câu điều kiện kích hoạt]
```

### Bước 2 — Viết bộ test should-trigger (8–10 query)

Viết 8–10 câu prompt thực tế mà user có thể gõ — Dispatcher PHẢI gọi agent/skill này khi nhận những prompt đó.

```markdown
## Should-trigger queries (Dispatcher PHẢI routing sang [agent]):

1. "[Câu user có thể gõ thực tế — trigger rõ ràng]"
2. "[Câu user có thể gõ thực tế — trigger rõ ràng]"
3. "[Câu user có thể gõ thực tế — trigger rõ ràng]"
...
8-10. ...

**Kết quả mong đợi:** Dispatcher nhận ra mỗi câu trên và routing sang [agent/skill] (không phải agent khác, không xử lý trực tiếp).
```

### Bước 3 — Viết bộ test should-NOT-trigger (8–10 near-miss query)

Viết 8–10 câu có vẻ tương tự nhưng Dispatcher KHÔNG được gọi agent/skill này — thay vào đó gọi agent khác hoặc xử lý trực tiếp.

```markdown
## Should-NOT-trigger queries (Dispatcher KHÔNG được routing sang [agent]):

1. "[Câu near-miss — trông giống nhưng thực ra không phải]" → nên gọi [agent khác]
2. "[Câu near-miss — trông giống nhưng thực ra không phải]" → nên trả lời trực tiếp
3. ...
8-10. ...

**Kết quả mong đợi:** Dispatcher routing sang agent khác hoặc xử lý trực tiếp — KHÔNG routing sang [agent đang test].
```

### Bước 4 — Chạy test (simulation)

Với mỗi query trong danh sách:

```
Query: "[câu test]"
Đọc description của [agent]: [trích dẫn ngắn phần liên quan]
Kết quả routing dự kiến: [agent được gọi / xử lý trực tiếp]
Thực tế description có trigger rõ không?: [Có / Không — giải thích ngắn]
```

Nếu bước simulation cho thấy description không đủ "pushy" để trigger đúng → ghi rõ vấn đề và đề xuất sửa.

### Bước 5 — Báo cáo kết quả

```
╔══════════════════════════════════════════════════════════════╗
║  SKILL-TRIGGER-TEST — Kết quả                               ║
╠══════════════════════════════════════════════════════════════╣
║  Agent/skill test: [tên]                                    ║
║  Should-trigger  : [X/10 PASS] — [X/10 FAIL]               ║
║  Should-NOT-trig : [X/10 PASS] — [X/10 FAIL]               ║
╠══════════════════════════════════════════════════════════════╣
║  Vấn đề phát hiện:                                          ║
║  - [Near-miss query N gây nhầm lẫn — mô tả vấn đề]         ║
║  - [Should-trigger query M không được nhận ra — lý do]      ║
╠══════════════════════════════════════════════════════════════╣
║  Đề xuất sửa description:                                   ║
║  [Cụ thể — thêm điều kiện X, làm rõ ranh giới Y]           ║
╚══════════════════════════════════════════════════════════════╝
```

## Ví dụ: Test agent `code-migrator`

### Should-trigger (8 query):
1. "Chuyển project WinForms sang Avalonia"
2. "Migrate codebase từ .NET Framework 4.8 lên .NET 8"
3. "Port ứng dụng jQuery sang React"
4. "Chuyển đổi WPF sang MAUI"
5. "Migrate từ Entity Framework 6 lên EF Core"
6. "Port ứng dụng desktop sang web (Blazor)"
7. "Chuyển Flutter app sang native Java/Kotlin"
8. "Migrate từ ASP.NET Web Forms sang ASP.NET Core MVC"

### Should-NOT-trigger (8 near-miss):
1. "Viết tính năng mới bằng Avalonia" → junior-developer / senior-developer
2. "Fix bug trong WinForms hiện tại" → WF-BUGFIX agents
3. "Review code migration PR do dev viết" → senior-developer / tech-lead
4. "Cần dùng EF Core thay EF6 cho feature mới" → senior-developer
5. "Tìm hiểu về Avalonia có gì khác WPF" → trả lời trực tiếp (không cần agent)
6. "Cập nhật package từ version cũ lên version mới" → senior-developer (không phải migration framework)
7. "Sửa UI theo mockup mới trong Avalonia" → senior-developer
8. "Tối ưu performance app WinForms hiện tại" → senior-developer

## Tần suất chạy

- Sau mỗi lần tạo agent/skill mới.
- Sau mỗi lần sửa `description:` frontmatter.
- Khi nhận thấy Dispatcher routing sai lặp lại nhiều lần.
- Không cần chạy định kỳ nếu không có thay đổi.
