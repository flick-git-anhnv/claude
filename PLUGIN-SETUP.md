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

## Bước 2 — Lấy CLAUDE.md / RULES.md / WORKFLOW.md / Kztek_Logo.png / scripts/ (qua submodule)

Ở project đích, chạy 1 lần:

```bash
git submodule add https://github.com/flick-git-anhnv/claude .claude-shared
```

Sau đó tạo symlink/copy các file cần dùng vào đúng vị trí project (Windows cần bật Developer Mode hoặc chạy PowerShell với quyền admin để tạo symlink):

```powershell
New-Item -ItemType SymbolicLink -Path "CLAUDE.md"    -Target ".claude-shared\CLAUDE.md"
New-Item -ItemType SymbolicLink -Path "RULES.md"     -Target ".claude-shared\RULES.md"
New-Item -ItemType SymbolicLink -Path "WORKFLOW.md"  -Target ".claude-shared\WORKFLOW.md"
New-Item -ItemType SymbolicLink -Path "Kztek_Logo.png" -Target ".claude-shared\Kztek_Logo.png"
New-Item -ItemType SymbolicLink -Path "scripts"      -Target ".claude-shared\scripts"
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
- [ ] `/plugin install kztek-agents@kztek-marketplace` cài thành công, agent list xuất hiện đủ agent — **lần test đầu FAIL vì agents/commands lồng trong `.claude/`, đã sửa (xem "Cấu trúc & lưu ý kỹ thuật"), cần test lại bản `1.0.1`**
- [ ] Skill gọi được đúng — kiểm tra có bị namespace hóa thành `/kztek-agents:ship`, `/kztek-agents:verify-pr` thay vì `/ship`, `/verify-pr` không
- [ ] Hook `config-protection.js` vẫn chạy khi Edit/Write vào file bảo vệ (đã thêm `hooks/hooks.json` khai báo PreToolUse — CHƯA test thực tế)
- [ ] Submodule + symlink CLAUDE.md hoạt động đúng, nội dung khớp
- [ ] Sửa nội dung ở repo gốc → bump version + `/plugin marketplace update` (hoặc nút refresh trong panel) → project đích nhận bản mới

*Cập nhật checklist này sau khi test thực tế — phần nào fail cần ghi rõ lỗi để fix ở lần commit sau.*
