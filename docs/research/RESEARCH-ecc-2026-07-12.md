---
title: "Nghiên cứu repo GitHub: affaan-m/ecc (Everything Claude Code)"
repo: https://github.com/affaan-m/ecc
slug: ecc
date: 2026-07-12
researcher: GitHub Repo Researcher
workflow: WF-GITHUB-RESEARCH
status: phase-1-complete
---

# Nghiên cứu repo: affaan-m/ecc — Everything Claude Code (ECC)

---

## PHẦN 1: PHÂN TÍCH REPO

### 1.1 Tổng quan repo

**ECC (Everything Claude Code)** là một *harness-native operator system* — hệ điều hành lớp điều phối agent — được thiết kế để cài vào các AI coding harness (Claude Code, Codex, OpenCode, Cursor, Gemini, Zed, GitHub Copilot). Đây không phải là framework lập trình thông thường; ECC là một hệ thống chính sách, kỹ năng (skills), quy tắc (rules), hook tự động, và agent chuyên biệt hoạt động phía trên các LLM harness.

**Mục đích cốt lõi:** Cung cấp một bộ công cụ sẵn sàng dùng ngay cho engineering team khi làm việc với AI coding agent — bao gồm workflow TDD, kiểm tra bảo mật, kiểm soát governance, quản lý context, và tích hợp multi-harness — thay vì mỗi team phải tự xây từ đầu.

**Đối tượng sử dụng:** Engineering team và individual developer đang dùng Claude Code hoặc các AI coding agent tương đương; muốn áp dụng best practice có hệ thống (TDD, security, code review) mà không phải viết tay toàn bộ prompt/config.

**Vấn đề giải quyết:**
- Thiếu chuẩn hóa: mỗi developer dùng AI agent theo cách riêng, không có shared workflow.
- Không có safety net: AI agent dễ dàng bỏ qua bảo mật, bỏ qua test, commit config sai.
- Context window bị lãng phí: agent nạp toàn bộ skill catalog dù chỉ cần một phần nhỏ.
- Không có feedback loop: agent mắc lỗi lặp đi lặp lại mà không học được.

---

### 1.2 Cấu trúc thư mục chính

```
ecc/
├── agents/                     # 67 agent definitions (role-specialized .md files)
├── skills/                     # 278 skill definitions (catalog chính)
├── commands/                   # 94 legacy command shims
├── hooks/
│   ├── hooks.json              # Hook definitions (PreToolUse/PostToolUse)
│   └── memory-persistence/     # Hook scripts
├── rules/                      # Rules theo ngôn ngữ/framework
├── manifests/                  # Install manifests cho selective install
├── schemas/                    # JSON schemas
├── scripts/
│   ├── ci/                     # CI validation scripts
│   ├── hooks/                  # Hook runner scripts
│   ├── ecc.js                  # CLI entry point
│   ├── plan-canvas.js          # Browser canvas CLI
│   └── setup-package-manager.js
├── .agents/skills/             # Cross-harness skill copies (OpenAI format)
├── .claude/                    # Claude Code-specific config
│   ├── commands/               # Workflow commands
│   ├── enterprise/             # Governance controls
│   ├── homunculus/             # Instinct/continuous-learning files
│   ├── rules/                  # Guardrails
│   └── research/               # Research playbook
├── .claude-plugin/
│   ├── plugin.json             # Claude plugin manifest
│   └── PLUGIN_SCHEMA_NOTES.md  # Documented undocumented constraints
├── .codex/                     # Codex/OpenAI harness config
├── .cursor/                    # Cursor IDE config
├── ecc-tools.json              # Install identity manifest
├── identity.json               # Repo identity baseline
└── package.json                # npm package (ecc-universal v2.0.0)
```

**Thành phần quan trọng:**
- `agents/` — 67 agent chuyên biệt (code-reviewer, architect, security-reviewer, build-error-resolver, etc.)
- `skills/` — 278 skill definitions, mỗi skill là một file `.md` có YAML frontmatter
- `hooks/hooks.json` — Hook tự động (PreToolUse/PostToolUse): security scan, context compact gợi ý, governance capture, continuous learning observation
- `manifests/` — Selective install: cho phép cài chỉ những thành phần cần thiết theo stack thực tế

---

### 1.3 Phân tích kỹ thuật

#### 1.3.1 Kiến trúc tổng thể — Harness Operator Layer

ECC không can thiệp vào LLM inference. Nó hoạt động như một lớp điều phối phía trên harness:

```
User Input → Claude Code / Codex / Cursor
               ↓
         [ECC Hooks — PreToolUse]       ← interceptors
               ↓
         [ECC Skills / Agents]          ← chính sách & workflow
               ↓
         [LLM execution]
               ↓
         [ECC Hooks — PostToolUse]      ← validators
               ↓
         Output + Artifacts
```

Điều này cho phép ECC áp đặt chính sách (security, TDD, governance) mà không cần patch LLM hay harness.

#### 1.3.2 Hook System — Automated Quality Gates

Đây là pattern kỹ thuật nổi bật nhất. `hooks/hooks.json` định nghĩa:

| Hook ID | Trigger | Tác dụng |
|---------|---------|----------|
| `pre:bash:dispatcher` | PreToolUse:Bash | Consolidate nhiều quality checks (tmux, push, GateGuard) vào 1 dispatcher |
| `pre:write:doc-file-warning` | PreToolUse:Write | Cảnh báo khi agent tạo file tài liệu ngoài chuẩn |
| `pre:edit-write:suggest-compact` | PreToolUse:Edit/Write | Gợi ý `/compact` khi context vượt 160K token |
| `pre:observe:continuous-learning` | PreToolUse:* (async) | Capture tool use pattern để học liên tục |
| `pre:governance-capture` | PreToolUse:Bash/Write/Edit | Capture security events, policy violations |
| `pre:config-protection` | PreToolUse:Write/Edit | Block sửa linter/formatter config — ép agent sửa code thay vì yếu hóa config |

Pattern đặc biệt: Hook bootstrap (đoạn `node -e "..."`) tự tìm `CLAUDE_PLUGIN_ROOT` qua nhiều đường dẫn fallback — không hard-code path, chạy được mọi môi trường.

#### 1.3.3 DAILY vs LIBRARY Skill Classification (`agent-sort` skill)

ECC giải quyết vấn đề "full install quá to, quá ồn" bằng cách phân loại:
- **DAILY**: skill load mỗi session (khớp với stack thực tế của repo)
- **LIBRARY**: giữ lại nhưng không load mặc định

Phân loại dựa trên evidence từ repo thực (file extensions, lockfile, framework config) — không dựa trên preference. Mỗi quyết định phải có citation bằng lệnh grep cụ thể.

#### 1.3.4 Plugin Manifest Documentation Pattern

`PLUGIN_SCHEMA_NOTES.md` là một pattern đặc biệt: document hóa các ràng buộc *không có trong docs chính thức* nhưng validator thực sự enforce. Ghi lại lịch sử "flip-flop" (commit nào add, commit nào remove, vì sao) để tránh regression lặp lại.

#### 1.3.5 Eval-Driven Development (EDD) — `eval-harness` skill

Áp dụng tư duy TDD vào AI workflow:
- Định nghĩa eval TRƯỚC khi code
- Chạy eval liên tục (pass@k metric)
- Phân loại: Capability Eval, Regression Eval
- Grader: Code-based (deterministic), Model-based, Human (cho security)

#### 1.3.6 Agent Introspection Debugging — 4-phase loop

Khi agent loop/fail, không retry ngay mà chạy qua 4 phase:
1. **Failure Capture** — ghi lại error, last tool call, context pressure
2. **Root-Cause Diagnosis** — match failure vào known pattern table
3. **Contained Recovery** — action nhỏ nhất, reversible, validate trước
4. **Introspection Report** — output dạng structured, legible cho agent/human tiếp theo

#### 1.3.7 Strategic Compact

Script `suggest-compact.js` đọc session transcript, tính `input_tokens + cache_read + cache_creation`, gợi ý `/compact` tại logical boundaries (không phải arbitrary). Scale threshold theo context window (160K/200K window, 250K/1M window).

#### 1.3.8 Plan Canvas — Browser-based Review Loop

CLI tool (`ecc-plan-canvas`) mở artifact trong browser, nhận annotation và verdict (Approve/Request Changes) qua stdout JSON — không cần thêm dependency, chạy trên loopback 127.0.0.1:4517, harness-agnostic.

#### 1.3.9 Tiered Package Structure

ECC có package graph rõ ràng với dependency resolution:
```
runtime-core → workflow-pack → agentshield-pack
                            → research-pack
runtime-core → team-config-sync → enterprise-controls
```

Cho phép team chọn "profile" (full/minimal/custom) thay vì install all-or-nothing.

#### 1.3.10 Điểm mạnh và điểm yếu

**Điểm mạnh:**
- Hook system làm safety net tự động, không cần nhớ chạy thủ công
- Skill taxonomy rất rộng (278 skills), coverage nhiều language/framework
- PLUGIN_SCHEMA_NOTES.md là mô hình documentation gotchas rất tốt
- Cross-harness: 1 skill catalog, nhiều harness format
- agent-sort cho phép selective install dựa trên evidence thực tế

**Điểm yếu:**
- Hook bootstrap code (node -e "...") rất phức tạp, khó debug nếu bị broken
- 278 skill + 67 agent → context window pollution nếu không filter cẩn thận
- Plugin manifest constraints không documented chính thức → phụ thuộc vào PLUGIN_SCHEMA_NOTES.md

---

### 1.4 Thông tin repo

| Thuộc tính | Giá trị |
|-----------|---------|
| URL | https://github.com/affaan-m/ecc |
| License | MIT |
| Version | 2.0.0 |
| Stars / Forks / Contributors | *Không xác minh được* — README dòng 28 tự khai "211.9K+ stars, 32.5K+ forks, 230+ contributors", nhưng đây là text tĩnh do tác giả viết (không lấy từ GitHub API), và tự mâu thuẫn với dòng khác trong cùng README ("30+ contributors" ở phần changelog release notes). KHÔNG dùng số liệu này làm căn cứ đánh giá độ phổ biến/uy tín repo. |
| npm package | `ecc-universal` |
| Ngôn ngữ chính | TypeScript, JavaScript, Markdown |
| Độ trưởng thành | Chưa xác định độc lập — dựa trên nội dung repo (v2.0.0, changelog chi tiết, cấu trúc code hoàn chỉnh) cho thấy đầu tư nghiêm túc, nhưng số liệu "active community" trong README không được cross-check qua GitHub API thật |
| Website | https://ecc.tools |

---

## PHẦN 2: BẢNG ĐỀ XUẤT CẢI TIẾN

> Trạng thái: ⬜ Chờ user xác nhận. Ghi chú: Không có đề xuất nào đụng auth/payment/DB schema — không cần chạy `security-audit-stride`.

| # | Đề xuất | Học từ đâu trong ECC | Áp dụng vào đâu trong KZTEK | Lợi ích | Rủi ro / Effort | Trạng thái |
|---|---------|----------------------|------------------------------|---------|-----------------|-----------|
| E1 | **Hook tự động bảo vệ config** — PreToolUse hook block agent sửa các file config quan trọng (`.gitignore`, `appsettings.json`, `eslint.config.*`) thay vì weakening chúng | `hooks/hooks.json` → `pre:config-protection` hook; `scripts/hooks/config-protection.js` | `.claude/` hoặc `hooks/hooks.json` của KZTEK — thêm hook PreToolUse:Write/Edit | Ngăn agent vô tình yếu hóa config lint/format khi gặp error; ép fix code thay vì fix config | Thấp — chỉ cần thêm 1 hook entry vào `settings.json`. Effort: 2h | ⬜ |
| E2 | **PLUGIN_SCHEMA_NOTES pattern** — Tạo file riêng document hóa các ràng buộc không có trong docs chính thức của tools đang dùng (CLAUDE.md constraints, Python script quirks, script md_to_docx quirks) kèm lịch sử flip-flop | `.claude-plugin/PLUGIN_SCHEMA_NOTES.md` | Tạo `.claude/GOTCHAS.md` hoặc bổ sung section "Known Constraints" trong `CLAUDE.md` — ghi rõ "lần X thêm Y vì sao, lần Z xóa Y vì sao" | Ngăn regression lặp lại; rút ngắn onboarding cho contributor mới; giảm thời gian debug | Thấp — pure documentation, không đụng code. Effort: 1h | ⬜ |
| E3 | **DAILY vs LIBRARY phân loại skill** — Không load toàn bộ agent/skill catalog vào mỗi session; phân loại rõ cái nào "load mặc định" (liên quan hàng ngày) vs "chỉ gọi khi cần" | `.agents/skills/agent-sort/SKILL.md` — evidence-based DAILY/LIBRARY classification | Rà soát `.claude/agents/*.md` và `.claude/commands/*.md` của KZTEK; đánh tag DAILY/LIBRARY; documentation-writer, code-migrator, github-repo-researcher → LIBRARY (ít dùng); dispatcher, senior-developer → DAILY | Giảm context window waste; session bắt đầu nhanh hơn; agent ít bị distract bởi skill không liên quan | Trung bình — cần rà soát 17+ agents. Effort: 4-6h | ⬜ |
| E4 | **Verification Loop trước mỗi PR** — Sau khi agent hoàn thành code change, chạy check list cố định: build, type-check, lint, test, security scan, diff review — output VERIFICATION REPORT | `.agents/skills/verification-loop/SKILL.md` — 6-phase verification + report format | Tích hợp vào `WF-BUGFIX` và `WF-FEATURE` bước trước TL review: thêm skill `/verify` trong `.claude/commands/`; Tech Lead chỉ review sau khi verification report PASS | Agent không đẩy code broken lên cho Tech Lead review; tiết kiệm thời gian review; giảm back-and-forth | Thấp-Trung — tạo 1 skill command file mới. Effort: 2-3h | ⬜ |
| E5 | **Eval-Driven Development (EDD) cho agent workflow** — Định nghĩa pass/fail criteria trước khi implement agent/skill mới; dùng pass@k để đo reliability thay vì chỉ "chạy được là xong" | `.agents/skills/eval-harness/SKILL.md` — Capability Eval, Regression Eval, pass@k, pass^k | Áp dụng khi tạo agent/skill mới trong KZTEK: tạo `.claude/evals/[agent-name].md` trước khi viết agent, ghi rõ capability eval và regression eval; chạy sau khi implement | Có thước đo khách quan cho agent quality; phát hiện regression sớm khi sửa CLAUDE.md; onboarding dễ hơn | Trung bình — thay đổi mindset + tạo eval files. Effort: 3-4h cho framework, sau đó 30-60 phút/agent | ⬜ |
| E6 | **Agent Introspection Debugging pattern** — Khi agent loop hoặc fail, thay vì retry blindly, thực hiện 4-phase: Capture → Diagnose → Contained Recovery → Report | `.agents/skills/agent-introspection-debugging/SKILL.md` | Bổ sung vào `CLAUDE.md` một mục "Khi agent bị stuck/loop" với 4 bước cụ thể; có thể tạo skill `.claude/commands/debug-loop.md` | Giảm token waste khi agent loop; recovery có hệ thống thay vì heuristic; report giúp session tiếp theo không phải debug lại | Thấp — pure documentation/skill. Effort: 1-2h | ⬜ |
| E7 | **Strategic Compact gợi ý** — Hook đọc token count từ session transcript và gợi ý compact tại logical boundary thay vì để auto-compact xảy ra arbitrary | `.agents/skills/strategic-compact/SKILL.md`; `scripts/hooks/suggest-compact.js` | Thêm ghi chú vào CLAUDE.md §16.5 về khi nào nên compact; hoặc tạo hook script đơn giản cho `.claude/hooks/` | Tránh mất context ở giữa multi-phase task; session chất lượng hơn khi context không bị compact mid-work | Trung bình — cần viết script Node.js hoặc Python đơn giản. Effort: 3-4h | ⬜ |
| E8 | **Tiered package structure** — Chia agent/skill catalog thành package tiers có dependency graph rõ ràng thay vì một monolith CLAUDE.md | `ecc-tools.json` dependency graph: runtime-core → workflow-pack → agentshield-pack, research-pack; `ecc2/` modular structure | Refactor `.claude/agents/` và `.claude/commands/` thành nhóm: `core/` (dispatcher, task-planner), `workflow/` (feature, bugfix, hotfix), `specialist/` (migrator, researcher, doc-writer) | Dễ onboard agent mới; dễ bật/tắt theo project; giảm cognitive load khi maintain | Cao — structural refactor, rủi ro break existing workflows. Effort: 8-12h | ⬜ |

---

## Ghi chú áp dụng

- Đề xuất E1, E2, E4, E6 có effort thấp và impact ngay lập tức — nên ưu tiên.
- Đề xuất E3, E5 có effort trung bình nhưng value cao dài hạn.
- Đề xuất E7 phụ thuộc vào việc KZTEK workspace có Node.js sẵn không.
- Đề xuất E8 là structural change lớn — nên để sau khi E3 xong (phân loại trước, refactor sau).
- Không có đề xuất nào đụng auth/payment/DB schema/dữ liệu nhạy cảm — không cần `security-audit-stride`.

---

## Trạng thái áp dụng

| # | Đề xuất | Trạng thái |
|---|---------|-----------|
| E1 | Hook bảo vệ config | ⬜ Chờ user xác nhận |
| E2 | PLUGIN_SCHEMA_NOTES pattern | ⬜ Chờ user xác nhận |
| E3 | DAILY vs LIBRARY skill classification | ⬜ Chờ user xác nhận |
| E4 | Verification Loop trước PR | ⬜ Chờ user xác nhận |
| E5 | Eval-Driven Development | ⬜ Chờ user xác nhận |
| E6 | Agent Introspection Debugging | ⬜ Chờ user xác nhận |
| E7 | Strategic Compact gợi ý | ⬜ Chờ user xác nhận |
| E8 | Tiered package structure | ⬜ Chờ user xác nhận |
