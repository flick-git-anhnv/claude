# KZTEK Shared Claude Config — Cài đặt cho project mới

Repo này là nguồn dùng chung (single source of truth) cho toàn bộ hệ thống agent/skill/hook KZTEK, phân phối theo 2 cơ chế:

1. **Plugin** (`.claude-plugin/`) — cho `agents/`, `commands/`, `hooks/` ở **root repo** (bản build cho plugin — xem "Cấu trúc & lưu ý kỹ thuật" bên dưới).
2. **Git submodule + symlink** — cho `CLAUDE.md`, `RULES.md`, `WORKFLOW.md`, `Kztek_Logo.png`, `scripts/` (những thứ plugin không đóng gói được).

---

## Cấu trúc & lưu ý kỹ thuật (đọc trước khi sửa nội dung)

> **Xác nhận qua test thực tế 2026-07-22:** Claude Code Plugin **bắt buộc** `agents/`, `commands/`, `hooks/` nằm ngay tại **root của plugin package** — KHÔNG được lồng trong `.claude/`. Lồng trong `.claude/agents/` khiến agent hoàn toàn không load.

Vì vậy repo này có **2 bản song song, cố ý**:

| Thư mục | Vai trò |
|---|---|
| `.claude/agents/`, `.claude/commands/`, `.claude/hooks/` | **Nguồn chỉnh sửa chính** — dùng khi tự bảo trì repo này bằng Claude Code (mở thẳng repo, Claude Code đọc `.claude/` như 1 project bình thường) |
| `agents/`, `commands/`, `hooks/` (root) | **Bản build cho Plugin** — đây là nội dung thực sự được project khác tải về khi cài `kztek-agents` plugin |

**BẮT BUỘC:** Sau khi sửa bất kỳ file nào trong `.claude/agents|commands|hooks`, chạy:

```bash
bash scripts/sync-plugin-content.sh
```

rồi **bump version** trong cả `.claude-plugin/marketplace.json` và `.claude-plugin/plugin.json` (plugin cache của Claude Code lưu theo thư mục tên = version — không bump thì project khác vẫn dùng bản cache cũ dù đã push code mới), sau đó mới commit + push.

**Trước khi bắt user khác test lại**, tự kiểm tra cấu trúc bằng:

```bash
claude plugin validate .
```

---

## Bước 1 — Cài Plugin (agents/skills/hooks)

Chạy 1 lần cho mỗi máy (không cần lặp lại cho từng project trên cùng máy, marketplace là user-level):

```
/plugin marketplace add flick-git-anhnv/claude
```

Sau đó, ở mỗi project muốn dùng:

```
/plugin install kztek-agents@kztek-marketplace
```

> **Lưu ý:** Sau khi cài qua plugin, các skill hiện có (`verify-pr`, `ship`, `scope-check`, `security-audit-stride`, `kztek-brand-info`, `skill-trigger-test`, `writing-agent-skill`) có thể được namespace hóa thành `/kztek-agents:verify-pr` thay vì `/verify-pr` — cần kiểm tra thực tế khi test.

**Cập nhật khi repo có bản mới:**

```
/plugin marketplace update
```

---

## Bước 2 — Lấy CLAUDE.md / RULES.md / WORKFLOW.md / Kztek_Logo.png / scripts/ / templates (qua submodule)

> **Lưu ý phạm vi:** Plugin (Bước 1) CHỈ mang `agents/`, `commands/`, `hooks/`. Mọi thứ khác — kể cả `.claude/templates/`, `.claude/shared/CORE.md`, `.claude/evals/`, `.claude/references/`, `.claude/GOTCHAS.md` — KHÔNG nằm trong plugin vì các agent tham chiếu chúng theo đúng đường dẫn `.claude/...` (ví dụ `task-planner` đọc `.claude/templates/PLAN-MASTER-template.md`). Các file này phải đi qua submodule + symlink dưới đây, symlink đúng vào `.claude/` của project (không phải root).

Ở project đích, chạy 1 lần:

```bash
git submodule add https://github.com/flick-git-anhnv/claude .claude-shared
```

Sau đó tạo symlink vào đúng vị trí project (Windows cần bật Developer Mode hoặc chạy PowerShell với quyền admin để tạo symlink):

```powershell
# Root — tai lieu chinh
New-Item -ItemType SymbolicLink -Path "CLAUDE.md"      -Target ".claude-shared\CLAUDE.md"
New-Item -ItemType SymbolicLink -Path "RULES.md"       -Target ".claude-shared\RULES.md"
New-Item -ItemType SymbolicLink -Path "WORKFLOW.md"    -Target ".claude-shared\WORKFLOW.md"
New-Item -ItemType SymbolicLink -Path "Kztek_Logo.png" -Target ".claude-shared\Kztek_Logo.png"
New-Item -ItemType SymbolicLink -Path "scripts"        -Target ".claude-shared\scripts"

# .claude/ - cac thu muc HO TRO agent (KHONG symlink agents/commands/hooks o day,
# vi 2 thu do da co san qua Plugin (Buoc 1) - symlink chong len se gay trung lap)
New-Item -ItemType Directory -Force ".claude" | Out-Null
New-Item -ItemType SymbolicLink -Path ".claude\templates"  -Target "..\.claude-shared\.claude\templates"
New-Item -ItemType SymbolicLink -Path ".claude\shared"     -Target "..\.claude-shared\.claude\shared"
New-Item -ItemType SymbolicLink -Path ".claude\evals"      -Target "..\.claude-shared\.claude\evals"
New-Item -ItemType SymbolicLink -Path ".claude\references" -Target "..\.claude-shared\.claude\references"
New-Item -ItemType SymbolicLink -Path ".claude\GOTCHAS.md" -Target "..\.claude-shared\.claude\GOTCHAS.md"
```

**Cập nhật khi repo có bản mới:**

```bash
git submodule update --remote .claude-shared
```

(Symlink tự động phản ánh nội dung mới, không cần làm gì thêm.)

---

## Trạng thái xác thực (BẮT BUỘC test trước khi coi là hoàn tất)

- [x] `/plugin marketplace add flick-git-anhnv/claude` — OK (qua GUI panel "Manage Plugins", `/plugin` slash command không chạy được trong VSCode extension, chỉ chạy ở terminal CLI thuần)
- [x] Marketplace add cần source dạng HTTPS (`source: url`), KHÔNG dùng `source: github` mặc định — máy không có SSH key sẽ lỗi `Permission denied (publickey)` dù repo public
- [x] Cấu trúc plugin: agents/commands/hooks PHẢI ở root (không lồng `.claude/`) — đã sửa, `claude plugin validate` pass
- [x] **CRLF làm hỏng YAML frontmatter** — file có `\r\n` khiến parser fail ngầm (metadata rỗng). Đã thêm `.gitattributes` ép LF cho `agents/*.md`, `commands/*.md`, `hooks/*.js`, `hooks/*.json`, `.claude-plugin/*.json`
- [x] **Colon (`:`) trong giá trị `description` phá YAML** (vd: "Do NOT call for: ...", "Output: ...") — YAML hiểu nhầm thành mapping mới → lỗi "mapping values are not allowed here". Đã tìm thấy + sửa 2 file (`agents/cto.md`, `commands/verify-pr.md`) bằng cách bọc description trong `"..."`. **Khi thêm/sửa agent hoặc skill mới, PHẢI kiểm tra: nếu description có dấu `:` theo sau bởi khoảng trắng, bắt buộc bọc value trong dấu ngoặc kép.**
- [x] `/plugin install kztek-agents@kztek-marketplace` cài thành công (bản `1.0.2`) — **confirmed 2026-07-22:** đủ 19 agent KZTEK xuất hiện khi hỏi "bạn có những agents nào"
- [ ] Skill gọi được đúng — kiểm tra có bị namespace hóa thành `/kztek-agents:ship`, `/kztek-agents:verify-pr` thay vì `/ship`, `/verify-pr` không
- [ ] Hook `config-protection.js` vẫn chạy khi Edit/Write vào file bảo vệ (đã thêm `hooks/hooks.json` khai báo PreToolUse — CHƯA test thực tế)
- [ ] Submodule + symlink CLAUDE.md/RULES.md/WORKFLOW.md hoạt động đúng, nội dung khớp
- [ ] Symlink `.claude/templates`, `.claude/shared`, `.claude/evals`, `.claude/references`, `.claude/GOTCHAS.md` — agent (vd `task-planner`) đọc được đúng file qua đường dẫn `.claude/templates/...` như bình thường, không lỗi "file not found"
- [ ] Sửa nội dung ở repo gốc → bump version + refresh marketplace (panel GUI hoặc `/plugin marketplace update` ở terminal) → project đích nhận bản mới
- [ ] `git submodule update --remote .claude-shared` ở project đích thực sự lấy được bản mới nhất, symlink vẫn trỏ đúng sau khi update

**Trước khi push, LUÔN chạy `claude plugin validate .claude-plugin/plugin.json` cục bộ** — bắt được cả lỗi cấu trúc lẫn lỗi YAML frontmatter mà không cần chờ user test trên máy khác.

*Cập nhật checklist này sau khi test thực tế — phần nào fail cần ghi rõ lỗi để fix ở lần commit sau.*
