---
title: "Nghiên cứu repo GitHub: affaan-m/ecc (Everything Claude Code)"
repo: https://github.com/affaan-m/ecc
slug: ecc
date: 2026-07-12
researcher: GitHub Repo Researcher
workflow: WF-GITHUB-RESEARCH
status: phase-2-complete
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

> Trạng thái: ✅ E1-E7 đã áp dụng (2026-07-12). E8 không áp dụng (user không chọn). Ghi chú: Không có đề xuất nào đụng auth/payment/DB schema — không cần chạy `security-audit-stride`.

| # | Đề xuất | Học từ đâu trong ECC | Áp dụng vào đâu trong KZTEK | Tác dụng cụ thể (trước → sau khi áp dụng) | Rủi ro / Effort | Trạng thái |
|---|---------|----------------------|------------------------------|---------------------------------------------|-----------------|-----------|
| E1 | **Hook tự động bảo vệ config** — PreToolUse hook block agent sửa các file config quan trọng (`.gitignore`, `appsettings.json`, `eslint.config.*`) thay vì weakening chúng | `hooks/hooks.json` → `pre:config-protection` hook; `scripts/hooks/config-protection.js` | `.claude/` hoặc `hooks/hooks.json` của KZTEK — thêm hook PreToolUse:Write/Edit | **Trước:** khi agent gặp lỗi lint/build do rule config quá strict, agent có thể tự sửa `.eslintrc`/`appsettings.json` để "cho qua" lỗi mà không ai để ý. **Sau:** hook chặn ngay lệnh Edit/Write nhắm vào file nằm trong danh sách bảo vệ — lệnh bị exit non-zero, agent buộc phải quay lại sửa code nguồn hoặc giải thích rõ lý do cho user trước khi tiếp tục. Đo được bằng: thử cho agent sửa 1 rule ESLint để test → phải bị block. | Thấp — chỉ cần thêm 1 hook entry vào `settings.json`. Effort: 2h | ⬜ |
| E2 | **PLUGIN_SCHEMA_NOTES pattern** — Tạo file riêng document hóa các ràng buộc không có trong docs chính thức của tools đang dùng (CLAUDE.md constraints, Python script quirks, script md_to_docx quirks) kèm lịch sử flip-flop | `.claude-plugin/PLUGIN_SCHEMA_NOTES.md` | Tạo `.claude/GOTCHAS.md` hoặc bổ sung section "Known Constraints" trong `CLAUDE.md` — ghi rõ "lần X thêm Y vì sao, lần Z xóa Y vì sao" | **Trước:** lỗi "ngầm" đã gặp và fix 1 lần (VD: PDF export lỗi vì thiếu LibreOffice — vừa gặp trong task này) không được ghi ở đâu cả, agent/session sau lặp lại đúng lỗi đó, tốn thời gian debug lại từ đầu. **Sau:** mỗi lần fix xong 1 lỗi ngầm, agent PHẢI thêm 1 dòng vào GOTCHAS.md; agent sau khi gặp lỗi tương tự chỉ cần đọc file này 30 giây thay vì debug lại 30 phút. Đo được bằng: đếm số lần cùng 1 lỗi ngầm lặp lại qua các session trước/sau khi có file. | Thấp — pure documentation, không đụng code. Effort: 1h | ⬜ |
| E3 | **DAILY vs LIBRARY phân loại skill** — Không load toàn bộ agent/skill catalog vào mỗi session; phân loại rõ cái nào "load mặc định" (liên quan hàng ngày) vs "chỉ gọi khi cần" | `.agents/skills/agent-sort/SKILL.md` — evidence-based DAILY/LIBRARY classification | Rà soát `.claude/agents/*.md` và `.claude/commands/*.md` của KZTEK; đánh tag DAILY/LIBRARY; documentation-writer, code-migrator, github-repo-researcher → LIBRARY (ít dùng); dispatcher, senior-developer → DAILY | **Trước:** mỗi turn, system-reminder liệt kê description đầy đủ của TẤT CẢ 17 agent (kể cả code-migrator, github-repo-researcher — chỉ dùng vài lần/tháng) — tốn token cố định mỗi lượt chat dù không dùng đến. **Sau:** chỉ agent DAILY xuất hiện mặc định; agent LIBRARY được load qua ToolSearch/kích hoạt rõ ràng khi match trigger từ khóa. Đo được bằng: so sánh số token trong system-reminder trước/sau (ước tính giảm ~30-40% phần liệt kê agent). | Trung bình — cần rà soát 17+ agents, rủi ro: phân loại sai khiến 1 agent cần dùng nhưng không hiện ra khi Dispatcher routing. Effort: 4-6h | ⬜ |
| E4 | **Verification Loop trước mỗi PR** — Sau khi agent hoàn thành code change, chạy check list cố định: build, type-check, lint, test, security scan, diff review — output VERIFICATION REPORT | `.agents/skills/verification-loop/SKILL.md` — 6-phase verification + report format | Tích hợp vào `WF-BUGFIX` và `WF-FEATURE` bước trước TL review: thêm skill `/verify` trong `.claude/commands/`; Tech Lead chỉ review sau khi verification report PASS | **Trước:** Senior/Junior Dev báo "xong" và đẩy thẳng cho Tech Lead review — TL tự chạy build/test, phát hiện lỗi cơ bản (build fail, test fail) mới trả lại, mất 1 vòng review vô ích. **Sau:** Dev PHẢI đính kèm VERIFICATION REPORT (build/lint/test: pass/fail) vào PR description; nếu có mục FAIL, PR không được coi là sẵn sàng review — TL chỉ mở review khi report toàn PASS. Đo được bằng: số PR bị TL trả về do lỗi build/test cơ bản giảm về 0. | Thấp-Trung — tạo 1 skill command file mới. Effort: 2-3h | ⬜ |
| E5 | **Eval-Driven Development (EDD) cho agent workflow** — Định nghĩa pass/fail criteria trước khi implement agent/skill mới; dùng pass@k để đo reliability thay vì chỉ "chạy được là xong" | `.agents/skills/eval-harness/SKILL.md` — Capability Eval, Regression Eval, pass@k, pass^k | Áp dụng khi tạo agent/skill mới trong KZTEK: tạo `.claude/evals/[agent-name].md` trước khi viết agent, ghi rõ capability eval và regression eval; chạy sau khi implement | **Trước:** agent mới (VD: agent đề xuất ở §18 CLAUDE.md) được coi "xong" chỉ vì chạy 1 lần không lỗi cú pháp — không ai kiểm tra agent có thực sự làm đúng domain của nó ở nhiều tình huống khác nhau. **Sau:** trước khi merge agent mới, phải có ≥3 ví dụ input/output mong đợi và agent phải pass hầu hết trong số đó mới được coi hoàn thành; khi sửa CLAUDE.md sau này, chạy lại các eval cũ để phát hiện agent có bị regression không. Đo được bằng: agent mới có file eval kèm log pass/fail trước khi được thêm vào routing table. | Trung bình — thay đổi mindset + tạo eval files. Effort: 3-4h cho framework, sau đó 30-60 phút/agent | ⬜ |
| E6 | **Agent Introspection Debugging pattern** — Khi agent loop hoặc fail, thay vì retry blindly, thực hiện 4-phase: Capture → Diagnose → Contained Recovery → Report | `.agents/skills/agent-introspection-debugging/SKILL.md` | Bổ sung vào `CLAUDE.md` một mục "Khi agent bị stuck/loop" với 4 bước cụ thể; có thể tạo skill `.claude/commands/debug-loop.md` | **Trước:** khi 1 agent gọi lặp cùng 1 tool nhiều lần không tiến triển (VD: build fail liên tục vì thiếu dependency), Dispatcher/agent hoặc tự retry mù hoặc phải tự suy luận lại từ đầu — tốn token, có thể lặp vô hạn. **Sau:** phát hiện loop → dừng ngay, ghi lại lỗi cụ thể + tool call cuối, tra bảng pattern lỗi đã biết, thử 1 hành động nhỏ có thể rollback, rồi báo cáo user thay vì im lặng retry. Đo được bằng: số turn agent bị "loop" trước khi có người/cơ chế can thiệp giảm từ nhiều chục xuống 1-2. | Thấp — pure documentation/skill. Effort: 1-2h | ⬜ |
| E7 | **Strategic Compact gợi ý** — Hook đọc token count từ session transcript và gợi ý compact tại logical boundary thay vì để auto-compact xảy ra arbitrary | `.agents/skills/strategic-compact/SKILL.md`; `scripts/hooks/suggest-compact.js` | Thêm ghi chú vào CLAUDE.md §16.5 về khi nào nên compact; hoặc tạo hook script đơn giản cho `.claude/hooks/` | **Trước:** context window tự bị nén (auto-compact) tại thời điểm bất kỳ, có thể đúng giữa lúc agent đang thực hiện 1 bước nhiều-turn (VD: đang debug 1 lỗi phức tạp) — mất chi tiết quan trọng giữa việc. **Sau:** hệ thống chủ động cảnh báo "nên compact ngay" tại điểm vừa hoàn thành 1 bước/1 phase rõ ràng (logical boundary), trước khi context đầy — tránh mất ngữ cảnh giữa việc dở dang. Đo được bằng: giảm số lần agent phải "đọc lại" cùng 1 file/quyết định sau một lần auto-compact bất ngờ. | Trung bình — cần viết script Node.js hoặc Python đơn giản; phụ thuộc việc KZTEK có Node.js sẵn. Effort: 3-4h | ⬜ |
| E8 | **Tiered package structure** — Chia agent/skill catalog thành package tiers có dependency graph rõ ràng thay vì một monolith CLAUDE.md | `ecc-tools.json` dependency graph: runtime-core → workflow-pack → agentshield-pack, research-pack | Refactor `.claude/agents/` và `.claude/commands/` thành nhóm: `core/` (dispatcher, task-planner), `workflow/` (feature, bugfix, hotfix), `specialist/` (migrator, researcher, doc-writer) | **Trước:** khi 1 project con của KZTEK không cần DevOps/Migrate, toàn bộ agent vẫn nằm chung 1 danh sách phẳng trong `.claude/agents/` — không có cách "tắt" nhóm agent không liên quan theo project. **Sau:** có thể bật/tắt cả 1 tier (VD: tắt `specialist/` cho project nội bộ không cần migrate/research) bằng 1 thay đổi cấu hình, không phải sửa từng agent riêng lẻ. Đo được bằng: thời gian setup agent set cho 1 project mới giảm từ "chọn lọc thủ công 17 agent" xuống "chọn 2-3 tier". **Cảnh báo:** nếu phân loại tier sai, 1 workflow đang hoạt động (VD: WF-FEATURE cần ux-ui-reviewer) có thể "mất" agent cần dùng vì nó bị gán nhầm tier bị tắt. | Cao — structural refactor, rủi ro break existing workflows đang chạy ổn định. Effort: 8-12h | ⬜ |

---

## Ghi chú áp dụng

- Đề xuất E1, E2, E4, E6 có effort thấp và impact ngay lập tức — nên ưu tiên.
- Đề xuất E3, E5 có effort trung bình nhưng value cao dài hạn.
- Đề xuất E7 phụ thuộc vào việc KZTEK workspace có Node.js sẵn không.
- Đề xuất E8 là structural change lớn — nên để sau khi E3 xong (phân loại trước, refactor sau).
- Không có đề xuất nào đụng auth/payment/DB schema/dữ liệu nhạy cảm — không cần `security-audit-stride`.

---

## Trạng thái áp dụng

| # | Đề xuất | Trạng thái | File áp dụng |
|---|---------|-----------|-------------|
| E1 | Hook bảo vệ config | ✅ Đã áp dụng | `.claude/hooks/config-protection.js`, `.claude/settings.json` |
| E2 | PLUGIN_SCHEMA_NOTES pattern (GOTCHAS.md) | ✅ Đã áp dụng | `.claude/GOTCHAS.md`, `CLAUDE.md` §KHỞI ĐỘNG |
| E3 | DAILY vs LIBRARY skill classification | ✅ Đã áp dụng | `.claude/shared/CORE.md` §6b |
| E4 | Verification Loop trước PR | ✅ Đã áp dụng | `.claude/commands/verify-pr.md`, `CLAUDE.md` §WF-FEATURE Bước 10, §WF-BUGFIX Bước 3 |
| E5 | Eval-Driven Development | ✅ Đã áp dụng | `.claude/templates/EVAL-template.md`, `CLAUDE.md` §18.5 |
| E6 | Agent Introspection Debugging | ✅ Đã áp dụng | `CLAUDE.md` §9a |
| E7 | Strategic Compact gợi ý | ✅ Đã áp dụng | `CLAUDE.md` §16.5 |
| E8 | Tiered package structure | ⏭️ Không áp dụng | User không chọn — structural refactor rủi ro cao, bỏ qua |
