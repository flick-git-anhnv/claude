# CODE-GRAPH.md — Bản đồ codebase: KZTEK Multi-Agent Workspace
**Cập nhật lần cuối:** 2026-07-12 | **Bởi:** senior-developer | **Version:** 1.0

> File này được duy trì tự động bởi coding agents.
> **Đọc file này TRƯỚC khi đọc source code** để hiểu cấu trúc dự án mà không cần mở từng file.

> **LƯU Ý QUAN TRỌNG:** Đây là AI Agent Framework workspace, KHÔNG phải codebase sản phẩm. Thư mục `src/` không tồn tại. File này mô tả cấu trúc framework agent orchestration + thư viện UI C# WinForms. **File này sẽ được điền đầy đủ chi tiết khi có project sản phẩm thực tế bắt đầu phát triển trong workspace này.**

---

## Tổng quan dự án

Workspace điều phối AI agents cho KZTEK — Multi-Agent Orchestration Framework. Định nghĩa chain of command, routing table, và workflow cho 17+ agents. Không có backend/frontend sản phẩm riêng tại workspace này — chỉ có định nghĩa agent, templates, scripts hỗ trợ, và thư viện UI C# WinForms dùng chung.

**Tech stack:**
- Agent framework: Claude Code (`.claude/` config, CLAUDE.md, RULES.md, WORKFLOW.md)
- UI Component Library: C# WinForms (`KztekComponent/` — .NET, dùng cho các project sản phẩm C# KZTEK)
- Scripting: Python 3 (`scripts/md_to_docx_kztek.py`), Bash (`scripts/review-package.sh`)

**Deploy:** N/A — workspace agent configuration, không deploy độc lập

**Môi trường:** Cloud sandbox (claude.ai) hoặc Local (VSCode Extension)

---

## Cấu trúc thư mục

```
/home/user/claude/               ← Workspace root
├── .claude/                     ← Agent framework configuration
│   ├── agents/                  ← Định nghĩa 17+ agents (task-planner, senior-developer, ...)
│   ├── commands/                ← Skills/commands (/ship, /verify-pr, scope-check, ...)
│   ├── evals/                   ← Eval files theo EDD (task-planner, senior-developer, qa-engineer)
│   ├── hooks/                   ← Hook bảo vệ config (config-protection.js)
│   ├── plans/                   ← Plan files (.claude/plans/PLAN-*.md) — runtime, không commit
│   ├── shared/                  ← CORE.md (context chung), GOTCHAS.md
│   └── templates/               ← PLAN-template.md, EVAL-template.md, CODE-GRAPH-template.md
├── KztekComponent/              ← Thư viện C# WinForms components (xem chi tiết bên dưới)
│   ├── Controls/                ← 28 custom controls (KzButton, KzDataGrid, KzTextBox, ...)
│   ├── Theme/                   ← KzEnums.cs, KzTokens.cs, KzThemeHelper.cs
│   └── Properties/              ← AssemblyInfo.cs
├── code-graph/                  ← Bản đồ codebase (file này)
├── docs/                        ← Tài liệu dự án (agents, research, planning)
│   └── research/                ← Báo cáo nghiên cứu repo ngoài (RESEARCH-*.md)
├── scripts/                     ← Helper scripts
│   ├── md_to_docx_kztek.py     ← Xuất .md → .docx + .pdf với brand KZTEK
│   └── review-package.sh        ← Tạo diff handoff cho code review
├── CLAUDE.md                    ← Quy tắc bắt buộc cho Claude Code (agent config gốc)
├── RULES.md                     ← Quy tắc tổ chức, phân cấp, luồng giao việc
└── WORKFLOW.md                  ← Ví dụ workflow mẫu theo từng scenario
```

---

## Module chính

| Module | Path | Mục đích | Files quan trọng |
|--------|------|----------|-----------------|
| Agent Definitions | `.claude/agents/` | Định nghĩa vai trò, model, tools, quy trình cho mỗi agent | `task-planner.md`, `senior-developer.md`, `qa-engineer.md`, `tech-lead.md`, ... |
| Skills/Commands | `.claude/commands/` | Các skill có thể gọi qua slash command | `ship.md`, `verify-pr.md`, `scope-check.md`, `security-audit-stride.md` |
| Eval Files | `.claude/evals/` | Capability Eval theo EDD cho từng agent | `task-planner.md`, `senior-developer.md`, `qa-engineer.md` |
| Shared Context | `.claude/shared/` | Context chung đọc đầu mỗi session | `CORE.md`, `GOTCHAS.md` |
| Templates | `.claude/templates/` | Khung mẫu cho plan, eval, code-graph | `PLAN-template.md`, `EVAL-template.md`, `CODE-GRAPH-template.md` |
| KztekComponent | `KztekComponent/` | Thư viện UI C# WinForms — dùng tối đa cho mọi project C# KZTEK | Xem bảng Controls bên dưới |
| Scripts | `scripts/` | Automation scripts hỗ trợ agent | `md_to_docx_kztek.py`, `review-package.sh` |

---

## KztekComponent — Controls có sẵn (C# WinForms)

> **Coding agents BẮT BUỘC dùng các control này thay vì control .NET gốc** khi làm project C# WinForms (§20 CLAUDE.md).

| Control | Path | Tương đương .NET gốc | Ghi chú |
|---------|------|---------------------|---------|
| `KzButton` | `Controls/KzButton.cs` | `Button` | Button theo brand KZTEK |
| `KzTextBox` | `Controls/KzTextBox.cs` | `TextBox` | TextBox với validation |
| `KzPasswordTextBox` | `Controls/KzPasswordTextBox.cs` | `TextBox (PasswordChar)` | Input mật khẩu |
| `KzIPTextbox` | `Controls/KzIPTextbox.cs` | `TextBox` (custom) | Input địa chỉ IP |
| `KzDataGrid` | `Controls/KzDataGrid.cs` | `DataGridView` | Grid với virtualization |
| `KzCombobox` | `Controls/KzCombobox.cs` | `ComboBox` | Dropdown theo brand |
| `KzCheckBox` | `Controls/KzCheckBox.cs` | `CheckBox` | Checkbox theo brand |
| `KzCheckedListBox` | `Controls/KzCheckedListBox.cs` | `CheckedListBox` | Multi-select list |
| `KzRadioButton` | `Controls/KzRadioButton.cs` | `RadioButton` | Radio theo brand |
| `KzLabel` | `Controls/KzLabel.cs` | `Label` | Label theo brand |
| `KzNumericUpDown` | `Controls/KzNumericUpDown.cs` | `NumericUpDown` | Numeric input |
| `KzDateTimePicker` | `Controls/KzDateTimePicker.cs` | `DateTimePicker` | Date/time picker |
| `KzPanel` | `Controls/KzPanel.cs` | `Panel` | Panel container |
| `KzGroupBox` | `Controls/KzGroupBox.cs` | `GroupBox` | Group container |
| `KzTabControl` | `Controls/KzTabControl.cs` | `TabControl` | Tab navigation |
| `KzMenuStrip` | `Controls/KzMenuStrip.cs` | `MenuStrip` | Top menu |
| `KzContextMenuStrip` | `Controls/KzContextMenuStrip.cs` | `ContextMenuStrip` | Right-click menu |
| `KzProgressBar` | `Controls/KzProgressBar.cs` | `ProgressBar` | Progress indicator |
| `KzToggleSwitch` | `Controls/KzToggleSwitch.cs` | (không có tương đương) | Toggle on/off |
| `KzBadge` | `Controls/KzBadge.cs` | (không có tương đương) | Badge/tag hiển thị |
| `KzCard` | `Controls/KzCard.cs` | (không có tương đương) | Card layout |
| `KzKpiCard` | `Controls/KzKpiCard.cs` | (không có tương đương) | KPI metric card |
| `KzPictureBox` | `Controls/KzPictureBox.cs` | `PictureBox` | Image display |
| `KzNavigation` | `Controls/KzNavigation.cs` | (không có tương đương) | Navigation bar |
| `KzSidebar` | `Controls/KzSidebar.cs` | (không có tương đương) | Sidebar layout |
| `KzSidebarItem` | `Controls/KzSidebarItem.cs` | (không có tương đương) | Sidebar menu item |
| `KzDeviceTreeview` | `Controls/KzDeviceTreeview.cs` | `TreeView` | Device tree KZTEK |
| `KzKeyboard` | `Controls/KzKeyboard.cs` | (không có tương đương) | Soft keyboard |
| `KzCountDown` | `Controls/KzCountDown.cs` | (không có tương đương) | Countdown timer |
| `KzRoundCountdown` | `Controls/KzRoundCountdown.cs` | (không có tương đương) | Circular countdown |
| `KzTelexEngine` | `Controls/KzTelexEngine.cs` | (không có tương đương) | Telex input engine |

**Theme files:**
| File | Mục đích |
|------|---------|
| `Theme/KzEnums.cs` | Enums dùng chung trong library (ThemeMode, ButtonStyle, ...) |
| `Theme/KzTokens.cs` | Design tokens: màu brand (#251C53, #F05922, ...), spacing, font |
| `Theme/KzThemeHelper.cs` | Helper methods áp dụng theme lên controls |

---

## Entry Points

| Tên | File | Mô tả |
|-----|------|-------|
| Agent config gốc | `CLAUDE.md` | Toàn bộ quy tắc bắt buộc cho Claude Code |
| Shared context | `.claude/shared/CORE.md` | Context ngắn gọn đọc đầu session |
| Export script | `scripts/md_to_docx_kztek.py` | `python scripts/md_to_docx_kztek.py <file.md>` |
| Review script | `scripts/review-package.sh` | `scripts/review-package.sh <BASE> <HEAD>` |

---

## API / Interface chính

> Workspace này là agent configuration — không có HTTP API. Interface chính là các agent definitions và skill commands.

| Interface | File | Mô tả |
|-----------|------|-------|
| `task-planner` agent | `.claude/agents/task-planner.md` | Quản lý plan file, điều phối workflow |
| `senior-developer` agent | `.claude/agents/senior-developer.md` | Code phức tạp, review Junior PR |
| `qa-engineer` agent | `.claude/agents/qa-engineer.md` | Viết test case, reproduce bug |
| `/ship` skill | `.claude/commands/ship.md` | Gate GO/NO-GO trước deploy |
| `/verify-pr` skill | `.claude/commands/verify-pr.md` | Pre-PR verification checklist |
| `scope-check` skill | `.claude/commands/scope-check.md` | Làm rõ scope trước khi tạo plan |
| `security-audit-stride` skill | `.claude/commands/security-audit-stride.md` | OWASP + STRIDE audit |

---

## Dependencies quan trọng

| Package | Version | Dùng cho |
|---------|---------|---------|
| `python-docx` | latest | `md_to_docx_kztek.py` — xuất DOCX từ Markdown |
| `Pillow` | latest | `md_to_docx_kztek.py` — xử lý ảnh/logo trong DOCX |
| `.NET` (WinForms) | compatible | `KztekComponent/` — thư viện UI C# |

---

## Config / Environment Variables

> Workspace hiện tại không có env variable riêng. Project sản phẩm khi phát triển sẽ bổ sung mục này.

| Key | Default | Bắt buộc | Mô tả |
|-----|---------|---------|-------|
| (Chưa có) | — | — | Điền khi có project sản phẩm thực tế |

---

## Thay đổi gần đây

| Ngày | File/Module | Loại | Mô tả ngắn | Agent |
|------|------------|------|------------|-------|
| 2026-07-12 | `.claude/evals/` | Add | Tạo thư mục + 3 eval mẫu (task-planner, senior-developer, qa-engineer) | senior-developer |
| 2026-07-12 | `code-graph/CODE-GRAPH.md` | Add | Tạo bản đồ codebase ban đầu cho workspace | senior-developer |

---

## Lessons & Quyết định quan trọng

| Ngày | Quyết định / Bài học | Lý do (WHY) | Agent ghi nhận |
|------|----------------------|--------------|-----------------|
| 2026-07-12 | Dùng `--no-pdf` làm mặc định khi chạy `md_to_docx_kztek.py` trên môi trường cloud/sandbox | PDF export yêu cầu LibreOffice/docx2pdf không có sẵn trong sandbox — DOCX đủ dùng; PDF optional | senior-developer |
| 2026-07-12 | `src/` không tạo cho workspace agent — không có codebase sản phẩm tại đây | Workspace này chỉ là framework orchestration; codebase sản phẩm sẽ có project riêng khi bắt đầu | senior-developer |

---

## Ghi chú đặc biệt

- **Không có codebase sản phẩm:** `src/`, `tests/` không tồn tại trong workspace này. Tất cả code sản phẩm nằm trong project riêng được quản lý bởi workspace này.
- **KztekComponent là shared library thật:** Các controls trong `KztekComponent/Controls/` là C# WinForms components thực tế, dùng chung cho tất cả project C# KZTEK. Mọi coding agent PHẢI tra cứu trước khi tự viết control mới.
- **PDF export là optional trong sandbox:** Môi trường cloud không có LibreOffice — chỉ xuất DOCX; PDF có thể xuất ở môi trường local với `docx2pdf` hoặc LibreOffice.
- **Plan files không commit:** `.claude/plans/PLAN-*.md` là scratchpad runtime — đã thêm vào `.gitignore` (hoặc cần thêm nếu chưa có).
