# KZTEK Shared Claude Config — Cài đặt cho project mới

Repo này là nguồn dùng chung (single source of truth) cho toàn bộ hệ thống agent/skill/hook KZTEK, phân phối theo 2 cơ chế:

1. **Plugin** (`.claude-plugin/`) — cho `agents/`, `commands/` (skills), `hooks/` bên trong `.claude/`.
2. **Git submodule + symlink** — cho `CLAUDE.md`, `RULES.md`, `WORKFLOW.md`, `Kztek_Logo.png`, `scripts/` (những thứ plugin không đóng gói được).

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

- [ ] `/plugin marketplace add flick-git-anhnv/claude` chạy được không lỗi
- [ ] `/plugin install kztek-agents@kztek-marketplace` cài thành công, agent list xuất hiện đủ 17 agent
- [ ] Skill (`/verify-pr`, `/ship`...) gọi được đúng (có/không namespace prefix)
- [ ] Hook `config-protection.js` vẫn chạy khi Edit/Write vào file bảo vệ
- [ ] Submodule + symlink CLAUDE.md hoạt động đúng, nội dung khớp
- [ ] Sửa nội dung ở repo gốc → `/plugin marketplace update` + `git submodule update --remote` → project đích nhận bản mới

*Cập nhật checklist này sau khi test thực tế — phần nào fail cần ghi rõ lỗi để fix ở lần commit sau.*
