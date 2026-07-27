# KZTEK — Claude Code Config dùng chung

Repo này là **nguồn duy nhất** cho toàn bộ cấu hình Claude Code của KZTEK: 19+ agent, skill/slash command, template, checklist bảo mật, script hỗ trợ, và kho kinh nghiệm kỹ thuật (`lessons/`) — dùng chung cho **mọi project** trên máy, không copy tay.

---

## 1. Cài đặt trên máy mới (bắt buộc — làm 1 lần)

```powershell
git clone https://github.com/flick-git-anhnv/claude.git C:\Users\<user>\Desktop\Claude-Git\claude
cd C:\Users\<user>\Desktop\Claude-Git\claude
powershell -ExecutionPolicy Bypass -File scripts\link-global.ps1
```

Không cần quyền admin. Script tạo **9 junction** ở `~/.claude/` trỏ vào đúng thư mục trong repo này (`agents`, `commands`, `shared`, `templates`, `references`, `evals`, `hooks-kztek`, `scripts`, `lessons`) — sửa qua `~/.claude/...` cũng chính là sửa file trong repo, git thấy ngay, không có bản sao nào để lệch phiên bản.

Sau đó merge (không copy đè) `.claude/templates/settings-global.json` vào `~/.claude/settings.json`.

Kiểm tra:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\link-global.ps1 -WhatIf
```

**Chi tiết đầy đủ + rollback:** [`docs/SETUP-GLOBAL.md`](docs/SETUP-GLOBAL.md)

---

## 2. Dùng trong 1 project sản phẩm cụ thể

Nếu project đó muốn áp dụng quy trình 17-agent Dispatcher (PM → BA → Tech Lead → Dev → QA → DevOps...) của KZTEK, tạo `CLAUDE.md` ở gốc project với đúng 3 dòng:

```
@C:/Users/<user>/Desktop/Claude-Git/claude/CLAUDE.md
@C:/Users/<user>/Desktop/Claude-Git/claude/RULES.md
@C:/Users/<user>/Desktop/Claude-Git/claude/WORKFLOW.md
```

Claude Code nạp lại nội dung thật từ 3 file này mỗi session — sửa 1 lần trong repo, mọi project tự động dùng bản mới, không cần đồng bộ tay. Project không cần quy trình Dispatcher thì bỏ qua bước này.

> Không nên tạo junction thẳng cho 3 file trên (khác 9 mục ở §1): mỗi project có thể cần ghi thêm nội dung riêng (tên project, stack công nghệ...) phía dưới 3 dòng `@import` — junction sẽ khiến mọi project bắt buộc dùng chung 1 file y hệt, không chèn thêm được.

---

## 3. Cấu trúc repo

```
.claude/
├── agents/        19+ agent (CTO, Tech Lead, Senior/Junior Dev, QA, DevOps, ...)
├── commands/       Skill / slash command (/ship, /verify-pr, /run-plan-step, ...)
├── shared/         Context đọc đầu mỗi session — CORE.md, GOTCHAS.md
├── templates/       Khung mẫu PRD/TDD/PLAN/EVAL/CODE-GRAPH...
├── references/      Checklist bảo mật (OWASP/STRIDE), Definition of Done
├── evals/          Capability Eval theo EDD cho từng agent/skill
├── hooks/          Hook bảo vệ config (config-protection.js)
└── lessons/         Kinh nghiệm/gotcha kỹ thuật theo category (avalonia, camera-integration,
                     csharp-winforms, dotnet-general, database, networking-protocol, ...)
scripts/
├── link-global.ps1               Tạo 9 junction ~/.claude → repo
├── md_to_docx_kztek.py           Xuất .md → .docx + .pdf theo brand KZTEK
├── windows-tools/                GUI tool cho Windows (ClaudeConfigAudit, KioskDeployTool)
└── linux-kiosk/, linux-deb/      Script triển khai kiosk/deb Linux
docs/                Tài liệu dự án khi có project sản phẩm thực tế (PRD, TDD, plan...)
code-graph/          Bản đồ codebase (đọc trước khi sửa code)
CLAUDE.md            Quy tắc bắt buộc — chain of command, workflow, routing table
RULES.md             Quy tắc tổ chức, phân cấp, luồng giao việc
WORKFLOW.md          Ví dụ workflow mẫu theo từng scenario
```

---

## 4. Kiểm tra project cũ còn copy tay hạ tầng không

Nếu bạn có project từ trước khi cơ chế junction ra đời, chúng có thể còn giữ **bản copy tay cũ** của `agents/commands/shared/templates/references/evals/hooks` — nay đã dư thừa (bị `~/.claude` junction che khuất, không nhận bản cập nhật mới). Dùng GUI có sẵn để quét và dọn an toàn (đưa vào Thùng rác, không xóa vĩnh viễn):

```powershell
powershell -sta -File scripts\windows-tools\ClaudeConfigAudit.ps1
```

Xem hướng dẫn thông số trong chính giao diện tool (banner trạng thái junction, độ sâu quét, nút "Xem chi tiết khác biệt").

---

## 5. Đóng góp lesson / gotcha mới

Gặp lỗi ngầm (không có trong docs chính thức) khi phát triển sản phẩm? Ghi vào `.claude/lessons/<category>/` theo `_TEMPLATE.md`, cập nhật `INDEX.md` + `LESSONS-LOG.md`, xuất DOCX/PDF bằng `md_to_docx_kztek.py` — quy trình đầy đủ nằm trong phần "BẮT BUỘC: Hệ Thống Lessons Learned" của CLAUDE.md global (`~/.claude/CLAUDE.md`). Vì `lessons/` giờ đã nằm trong repo (junction thứ 9), lesson mới ghi ở bất kỳ project nào cũng cần `git commit` + `push` lại repo này để chia sẻ cho toàn bộ máy khác.

---

## 6. Tài liệu liên quan

| File | Nội dung |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Quy tắc bắt buộc cho Claude Code — chain of command, workflow, routing |
| [`RULES.md`](RULES.md) | Quy tắc tổ chức, phân cấp, luồng giao việc |
| [`WORKFLOW.md`](WORKFLOW.md) | Ví dụ workflow mẫu theo từng scenario |
| [`docs/SETUP-GLOBAL.md`](docs/SETUP-GLOBAL.md) | Chi tiết cơ chế junction, cài đặt máy mới, rollback |
| [`.claude/shared/GOTCHAS.md`](.claude/shared/GOTCHAS.md) | Lỗi ngầm của chính hệ thống agent/tooling (không phải lesson sản phẩm) |
| [`.claude/lessons/INDEX.md`](.claude/lessons/INDEX.md) | Mục lục kinh nghiệm kỹ thuật theo category |
