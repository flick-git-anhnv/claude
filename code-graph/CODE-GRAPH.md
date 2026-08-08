# CODE-GRAPH.md — Bản đồ codebase: KZTEK Multi-Agent Workspace
**Cập nhật lần cuối:** 2026-08-08 | **Bởi:** senior-developer | **Version:** 1.8

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
│   ├── lessons/                 ← Kinh nghiệm/gotcha kỹ thuật theo category (junction: ~/.claude/lessons)
│   ├── plans/                   ← Plan files (docs/plans/PLAN-*.md) — runtime, không commit
│   ├── shared/                  ← CORE.md (context chung), GOTCHAS.md
│   └── templates/               ← PLAN-template.md, EVAL-template.md, CODE-GRAPH-template.md
├── KztekComponent/              ← Thư viện C# WinForms components (xem chi tiết bên dưới)
│   ├── Controls/                ← 28 custom controls (KzButton, KzDataGrid, KzTextBox, ...)
│   ├── Theme/                   ← KzEnums.cs, KzTokens.cs, KzThemeHelper.cs
│   └── Properties/              ← AssemblyInfo.cs
├── code-graph/                  ← Bản đồ codebase (file này)
├── docs/                        ← Tài liệu dự án (agents, research, planning)
│   └── research/                ← Báo cáo nghiên cứu repo ngoài (RESEARCH-*.md)
├── scripts/                     ← Helper scripts (junction: ~/.claude/scripts)
│   ├── md_to_docx_kztek.py     ← Xuất .md → .docx + .pdf với brand KZTEK
│   ├── link-global.ps1          ← Tạo 9 junction ~/.claude → repo (user-level scope)
│   └── review-package.sh        ← Tạo diff handoff cho code review
├── CLAUDE.md                    ← Quy tắc bắt buộc cho Claude Code (agent config gốc)
├── RULES.md                     ← Quy tắc tổ chức, phân cấp, luồng giao việc
└── WORKFLOW.md                  ← Ví dụ workflow mẫu theo từng scenario
├── tools/                       ← Công cụ nội bộ KZTEK
│   └── agent-dashboard/         ← Dashboard web local quản lý Claude Code agents
│       ├── backend/             ← Python/FastAPI: file-watcher, WebSocket, SQLite (port 7770)
│       └── frontend/            ← Vite/React/TS/Tailwind (build tĩnh)
│           └── src/utils/format.ts  ← Tiện ích format: fmtNum, fmtTime, fmtDateTime,
│                                        fmtDateShort, fmtDate, fmtRelative, normalizeIso
```

---

## Module chính

| Module | Path | Mục đích | Files quan trọng |
|--------|------|----------|-----------------|
| Agent Definitions | `.claude/agents/` | Định nghĩa vai trò, model, tools, quy trình cho mỗi agent | `task-planner.md`, `senior-developer.md`, `qa-engineer.md`, `tech-lead.md`, ... |
| Skills/Commands | `.claude/commands/` | Các skill có thể gọi qua slash command | `ship.md`, `verify-pr.md`, `scope-check.md`, `security-audit-stride.md` |
| Eval Files | `.claude/evals/` | Capability Eval theo EDD cho từng agent | `task-planner.md`, `senior-developer.md`, `qa-engineer.md` |
| Shared Context | `.claude/shared/` | Context chung đọc đầu mỗi session | `CORE.md`, `GOTCHAS.md` |
| Lessons Learned | `.claude/lessons/` | Kinh nghiệm/gotcha kỹ thuật theo category, đọc trước khi làm task liên quan | `INDEX.md`, `LESSONS-LOG.md`, `avalonia/`, `camera-integration/`, ... |
| Templates | `.claude/templates/` | Khung mẫu cho plan, eval, code-graph | `PLAN-template.md`, `EVAL-template.md`, `CODE-GRAPH-template.md` |
| KztekComponent | `KztekComponent/` | Thư viện UI C# WinForms — dùng tối đa cho mọi project C# KZTEK | Xem bảng Controls bên dưới |
| Scripts | `scripts/` | Automation scripts hỗ trợ agent | `md_to_docx_kztek.py`, `link-global.ps1`, `review-package.sh` |
| Agent Dashboard Frontend | `tools/agent-dashboard/frontend/src/` | Dashboard web local — 18 components, 4 pages, WebSocket client | `utils/format.ts` (+`fmtTokensCompact` Sprint 4, +`decodeProjectSlug`, `getUsageErrorMsg` Sprint 6), `api/interceptor.ts`, `state/wsReducer.ts`, `types/index.ts` (Sprint 4: thêm `RosterTokens`, `RosterHistoryEntry`, `RosterEntry`, `RosterResponse`; `ChainResponse` deprecated; Sprint 6: kind required), `components/sessions/ContextBadge.tsx` (FR-002), `components/sessions/AgentRosterItem.tsx` (FR-001 Sprint 4 — NEW, thay StepStation), `components/sessions/StepStation.tsx` (FR-001 Sprint 3 — deprecated), `components/sessions/PipelineCard.tsx` (FR-001 Sprint 4 redesign — roster[], history panel), `components/sessions/SessionCard.tsx` (v2 — FR-001/002/003), `hooks/useApi.ts` (+getSessionChain), `components/sessions/AggregatePipelineView.tsx` (Sprint 6 FR-006: segmented control, project group-by, Windows paths decode) |
| Agent Dashboard Backend | `tools/agent-dashboard/backend/` | FastAPI: file-watcher, WebSocket, SQLite ingestion, account mgmt, OAuth session management, usage metering | `main.py` (Sprint 5 BUG-004: broadcast `chain_updated` với `parent_session_id` khi child event; include `pipeline_router`), `state_manager.py`, `db.py` (Sprint 5 FR-004: `get_session_chain` prepend Dispatcher node `{is_dispatcher:True}`; FR-005: `get_pipeline_aggregate` group by attribution_agent; Sprint 6 FR-006: get_pipeline_aggregate support group_by project), `parser.py` (Sprint 3: ai-title → `is_meta=True`; early-return for no-timestamp BUG-003; `first_user_text` extraction), `config.py` (Sprint 3: `MODEL_CONTEXT_WINDOW` dict + `resolve_max_context(model)`), `models.py` (Sprint 3: `ParsedLine` + `ai_title`, `first_user_text`, `is_meta` fields), `watcher.py`, `routes/accounts.py` (Sprint 5: `GET /usage/active` + `GET /{acc_id}/usage` — Bearer token, httpx, oauth-only; Sprint 6: _broadcast_account_change sends kind and key/oauth_masked; BUG-002: POST returns 409 on ACCOUNT_NAME_DUPLICATE for both api_key and oauth_session kinds), `routes/sessions.py` (Sprint 3: `GET /api/sessions/{id}/chain`), `routes/pipeline.py` (NEW Sprint 5 FR-005: `GET /api/pipeline/aggregate?project=&window=`; Sprint 6 FR-006: support group_by query param), `usage_service.py` (NEW Sprint 5: `UsageInfo`, `get_usage()`, `_pct()`, in-memory cache 60s TTL, httpx 5s timeout), `accounts.py` (v2 — kind discriminator, OAuth snapshot; BUG-002: `_name_exists()` + duplicate-name guard in `add_account`/`add_oauth_account` → raises `ValueError("ACCOUNT_NAME_DUPLICATE")`), `oauth_service.py` (activate_oauth_account requires `refresh_lock: asyncio.Lock`, auto-refresh scheduler, subprocess invoke) |

---

## User-level scope — config dùng chung mọi project (từ 2026-07-25)

Repo này là **nguồn duy nhất** của config KZTEK. `~/.claude` chứa 9 junction trỏ vào đây,
nên mọi project trên máy dùng chung một bộ agents/skills/templates/scripts — không copy tay.

| Junction `~/.claude\` | → Nguồn trong repo |
|---|---|
| `agents`, `commands`, `shared`, `templates`, `references`, `evals` | `.claude/<tên>` |
| `hooks-kztek` | `.claude/hooks` (tên khác vì `~/.claude/hooks` đã có hook riêng của máy) |
| `scripts` | `scripts/` (repo root) |

**Quy tắc đường dẫn khi sửa file trong các thư mục trên:**

| Loại path | Cách viết | Ví dụ |
|---|---|---|
| Hạ tầng dùng chung | Tuyệt đối | `C:/Users/nguye/.claude/templates/PRD-template.md` |
| Sản phẩm của project | Tương đối | `docs/plans/`, `src/`, `code-graph/` |

Cài đặt / rollback: `scripts/link-global.ps1` + `docs/SETUP-GLOBAL.md`.
Commit thay đổi config từ project khác: skill `/sync-global`.
`CLAUDE.md` **không** junction — quy trình 17-agent chỉ áp cho project phần mềm.

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
| `vitest` | ^4.1 | `tools/agent-dashboard/frontend/` — unit test runner (format.test.ts) |
| `FastAPI` / `uvicorn` | 0.110+ / 0.27+ | `tools/agent-dashboard/backend/` — HTTP + WebSocket server |
| `aiosqlite` | 0.20+ | `tools/agent-dashboard/backend/` — SQLite async storage |
| `asyncio` (stdlib) | 3.11+ | `tools/agent-dashboard/backend/oauth_service.py` — Lock, background scheduler, run_in_executor for subprocess |
| `subprocess` (stdlib) | 3.11+ | `tools/agent-dashboard/backend/oauth_service.py` — `claude -p ok --model claude-haiku-4-5` swap-and-invoke |

---

## Config / Environment Variables

> Workspace hiện tại không có env variable riêng. Project sản phẩm khi phát triển sẽ bổ sung mục này.

| Key | Default | Bắt buộc | Mô tả |
|-----|---------|---------|-------|
| `OAUTH_REFRESH_INTERVAL_SEC` | `1800` | Không | Khoảng cách (giây) giữa mỗi lần scheduler auto-refresh OAuth (agent-dashboard backend) |
| `OAUTH_REFRESH_AHEAD_RATIO` | `0.20` | Không | Tỉ lệ thời gian còn lại để kích hoạt refresh sớm (20% = refresh khi còn 20% thời gian hết hạn) |
| `OAUTH_REFRESH_MIN_AHEAD_MS` | `1800000` (30 phút) | Không | Ngưỡng tối thiểu (ms) còn lại trước khi hết hạn để kích hoạt refresh |
| `MODEL_CONTEXT_WINDOW` | dict (static) | Không | Giá trị tĩnh context window theo model (Sprint 3): Sonnet5/Opus5/Fable5=1M; Haiku4.5/Sonnet4.6/Opus4.7=200K; fallback 200K |

---

## Thay đổi gần đây

| Ngày | File/Module | Loại | Mô tả ngắn | Agent |
|------|------------|------|------------|-------|
| 2026-07-12 | `.claude/evals/` | Add | Tạo thư mục + 3 eval mẫu (task-planner, senior-developer, qa-engineer) | senior-developer |
| 2026-07-12 | `code-graph/CODE-GRAPH.md` | Add | Tạo bản đồ codebase ban đầu cho workspace | senior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/utils/format.ts` | Update | Thêm `normalizeIso()` + `fmtDateShort()` — fix NaN bug với Python microseconds timestamp; thêm fallback >24h | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/` | Add | Thêm vitest + `format.test.ts` (20 tests) — coverage `fmtRelative`, `normalizeIso`, `fmtDateShort` | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/backend/agent_dashboard/oauth_service.py` | Update | H-1 fix: `activate_oauth_account` thêm param `refresh_lock: asyncio.Lock`, wrap Steps 1-6 với `async with refresh_lock:` — serialise với background refresh scheduler | senior-developer |
| 2026-08-06 | `tools/agent-dashboard/backend/agent_dashboard/main.py` | Update | H-1 fix: expose `_oauth_refresh_lock` lên `app.state.oauth_refresh_lock` trong lifespan | senior-developer |
| 2026-08-06 | `tools/agent-dashboard/backend/agent_dashboard/routes/accounts.py` | Update | H-1 fix: thêm `_get_refresh_lock()` helper, truyền lock vào `activate_oauth_account` call | senior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/types/index.ts` | Update | Sprint 3: thêm `ChainStep`, `ChainResponse`; thêm `title`, `context_pct`, `last_input_total`, `max_context` vào Session; thêm `session_title_changed`, `session_context_updated` DeltaEvent | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/components/sessions/ContextBadge.tsx` | Add | NEW FR-002: progress bar 48×8px + %text, ngưỡng màu navy/warning/danger, ẩn khi context_pct=0/null | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/components/sessions/StepStation.tsx` | Add | NEW FR-001: station done (96px, mờ, hover expand) / active (164px, pulse dot #F05922, border-left cam) | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/components/sessions/PipelineCard.tsx` | Add | NEW FR-001: fetch /chain, scroll ngang + fade gradient (pointer-events:none), auto-scroll active station | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/components/sessions/SessionCard.tsx` | Add | NEW v2 (upgrade AgentCard): tích hợp FR-001/002/003 — title row, ContextBadge, PipelineCard | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/components/agents/AgentStatusPanel.tsx` | Update | Switch AgentCard → SessionCard (Sprint 3 upgrade) | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/state/wsReducer.ts` | Update | Sprint 3: handle session_title_changed + session_context_updated delta events | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/api/mockData.ts` | Update | Sprint 3: thêm title/context_pct/last_input_total/max_context vào MOCK_SESSIONS; thêm getMockChain() | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/api/interceptor.ts` | Update | Sprint 3: thêm handler GET /api/sessions/:id/chain | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/hooks/useApi.ts` | Update | Sprint 3: thêm getSessionChain(sessionId) | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/backend/agent_dashboard/parser.py` | Update | Sprint 3: BUG-003 early-return None khi thiếu timestamp; ai-title → ParsedLine(is_meta=True, ai_title); first_user_text fallback title | senior-developer |
| 2026-08-06 | `tools/agent-dashboard/backend/agent_dashboard/config.py` | Update | Sprint 3: MODEL_CONTEXT_WINDOW dict + resolve_max_context(model) — exact match, fallback 200K | senior-developer |
| 2026-08-06 | `tools/agent-dashboard/backend/agent_dashboard/models.py` | Update | Sprint 3: ParsedLine + 3 fields: ai_title, first_user_text, is_meta | senior-developer |
| 2026-08-06 | `tools/agent-dashboard/backend/agent_dashboard/db.py` | Update | Sprint 3: _migrate_sprint3_columns (5 cột mới + BUG-003 cleanup); update_title/update_title_if_null; upsert_session snapshot last_* (ghi đè); get_session_chain; _compute_step_status; SELECT queries + _row_to_session tính context_pct | senior-developer |
| 2026-08-06 | `tools/agent-dashboard/backend/agent_dashboard/routes/sessions.py` | Update | Sprint 3: endpoint GET /api/sessions/{id}/chain — 404 nếu session không tồn tại | senior-developer |
| 2026-08-06 | `tools/agent-dashboard/backend/agent_dashboard/main.py` | Update | Sprint 3: _process_file handle is_meta, snapshot last_* khi input_tokens>0, WS session_title_changed, WS token_update +context_pct | senior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/utils/format.ts` | Update | Sprint 4: thêm `fmtTokensCompact(n)` — format token compact ("1.5K", "1.2M", null nếu n≤0) | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/types/index.ts` | Update | Sprint 4: thêm `RosterTokens`, `RosterHistoryEntry`, `RosterEntry`, `RosterResponse`; deprecate `ChainResponse.steps` → `roster[]` | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/components/sessions/AgentRosterItem.tsx` | Add | NEW Sprint 4: ô roster 1 vai trò — active (196px cam pulse) / done (148px mờ hover-expand), token compact, "(xN)" badge, nút "Xem lịch sử" | junior-developer |
| 2026-08-06 | `tools/agent-dashboard/frontend/src/components/sessions/PipelineCard.tsx` | Update | Sprint 4 redesign: dùng roster[] thay steps[], AgentRosterItem thay StepStation, history panel inline bên dưới grid | junior-developer |
| 2026-08-07 | `tools/agent-dashboard/backend/agent_dashboard/usage_service.py` | Add | NEW Sprint 5: UsageInfo TypedDict, get_usage() httpx Bearer token, _pct() ratio→%, in-memory cache 60s TTL | senior-developer |
| 2026-08-07 | `tools/agent-dashboard/backend/agent_dashboard/routes/pipeline.py` | Add | NEW Sprint 5 FR-005: GET /api/pipeline/aggregate?project=&window= — group by attribution_agent, call_count DESC | senior-developer |
| 2026-08-07 | `tools/agent-dashboard/backend/agent_dashboard/routes/accounts.py` | Update | Sprint 5: thêm GET /usage/active + GET /{acc_id}/usage (oauth-only, Bearer token, httpx, cache 60s) | senior-developer |
| 2026-08-07 | `tools/agent-dashboard/backend/agent_dashboard/db.py` | Update | Sprint 5 FR-004: get_session_chain prepend Dispatcher node {is_dispatcher:True}; FR-005: get_pipeline_aggregate | senior-developer |
| 2026-08-07 | `tools/agent-dashboard/backend/agent_dashboard/main.py` | Update | Sprint 5 BUG-004: broadcast chain_updated với parent_session_id khi child event processed; include pipeline router | senior-developer |
| 2026-08-08 | `tools/agent-dashboard/backend/agent_dashboard/accounts.py` | Update | BUG-002: thêm `_name_exists()`, duplicate-name guard (case-insensitive) trong `add_account` + `add_oauth_account` → raise ValueError("ACCOUNT_NAME_DUPLICATE") | senior-developer |
| 2026-08-08 | `tools/agent-dashboard/backend/agent_dashboard/routes/accounts.py` | Update | BUG-002: POST /api/accounts trả 409 ACCOUNT_NAME_DUPLICATE cho cả api_key lẫn oauth_session khi tên trùng | senior-developer |
| 2026-08-08 | `tools/agent-dashboard/backend/agent_dashboard/db.py` | Update | FR-006-dispatcher: `get_session_chain` — dispatcher_entry.history giờ populated từ non-Agent tool events (Read/Write/Bash…); call_count = len(history) khi có events (fallback 1); history[last].status='active' khi session Running | senior-developer |
| 2026-08-08 | `tools/agent-dashboard/frontend/src/components/sessions/AgentRosterItem.tsx` | Update | FR-006-dispatcher: DispatcherNode nhận `onShowHistory` prop; hiện nút "Xem lịch sử" khi history.length>0; hasHistory = entry.history.length>0 (bỏ điều kiện !is_dispatcher) | senior-developer |

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
- **Plan files không commit:** `docs/plans/PLAN-*.md` là scratchpad runtime — đã thêm vào `.gitignore` (hoặc cần thêm nếu chưa có).
