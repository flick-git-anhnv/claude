---
title: "Nghiên cứu repo GitHub: obra/superpowers"
repo: https://github.com/obra/superpowers
researcher: GitHub Repo Researcher (L4)
created: 2026-07-12
updated: 2026-07-12
workflow: WF-GITHUB-RESEARCH
branch: research/superpowers-2026-07-12
status: Phân tích hoàn chỉnh — chờ user xác nhận đề xuất (Bước 2.1)
---

# Nghiên cứu repo GitHub: obra/superpowers

---

## Phần 1 — Phân tích repo

### 1.1 Tổng quan

**obra/superpowers** là một thư viện skill hoàn chỉnh dành cho coding agents, được xây dựng bởi Jesse Vincent và team Prime Radiant. Repo cung cấp một *software development methodology* dưới dạng tập hợp các skill có thể tái sử dụng — mỗi skill là một file Markdown có YAML frontmatter, mô tả chính xác khi nào kích hoạt và cách thực thi.

**Mục đích cốt lõi:** Đảm bảo coding agents không nhảy thẳng vào viết code, mà bước qua một chuỗi quy trình có kỷ luật: khảo sát ý tưởng (brainstorming) → lập kế hoạch (writing-plans) → thực thi có review (subagent-driven-development) → hoàn thành có verification (finishing-a-development-branch).

**Đối tượng sử dụng:** Lập trình viên và team muốn đảm bảo AI coding agents (Claude Code, Codex, Cursor, Antigravity, Kimi Code, OpenCode, Pi...) tuân thủ quy trình nhất quán thay vì hành động tự do.

**Vấn đề giải quyết:**
- Agents hay bỏ qua thiết kế → brainstorming bắt buộc trước khi code
- Agents "hoàn thành" mà không verify → verification-before-completion ngăn chặn
- Context window phình to khi nhiều bước → file handoffs thay pasting
- Context mất khi session bị compact → durable progress ledger
- Debug bằng cách đoán → systematic-debugging bắt root cause trước

---

### 1.2 Cấu trúc thư mục

```
obra/superpowers/
├── skills/                        ← Thư viện 14 skill chính
│   ├── using-superpowers/         ← Bootstrap — trigger cơ chế tự động dùng skill
│   ├── brainstorming/             ← Làm rõ spec trước khi code
│   ├── writing-plans/             ← Lập plan chi tiết từng bước
│   ├── subagent-driven-development/ ← Dispatch fresh subagent mỗi task + 2-stage review
│   ├── executing-plans/           ← Thực thi plan theo batch có checkpoint
│   ├── dispatching-parallel-agents/ ← Xử lý N task độc lập song song
│   ├── test-driven-development/   ← RED-GREEN-REFACTOR nghiêm ngặt
│   ├── systematic-debugging/      ← 4-phase root cause trước khi fix
│   ├── verification-before-completion/ ← Bắt chạy lệnh verify trước khi claim done
│   ├── requesting-code-review/    ← Checklist trước khi yêu cầu review
│   ├── receiving-code-review/     ← Cách phản hồi feedback review
│   ├── using-git-worktrees/       ← Tạo workspace cô lập trên nhánh mới
│   ├── finishing-a-development-branch/ ← Quyết định merge/PR/discard khi xong
│   └── writing-skills/            ← Meta-skill để tạo skill mới (TDD cho documentation)
├── hooks/
│   ├── hooks.json                 ← Claude Code: inject using-superpowers khi session start
│   ├── hooks-cursor.json          ← Cursor hook config
│   └── session-start/             ← Shell script inject bootstrap
├── .claude-plugin/plugin.json     ← Manifest cho Claude Code marketplace
├── .cursor-plugin/plugin.json     ← Manifest cho Cursor
├── .codex-plugin/plugin.json      ← Manifest cho Codex (hooks: {})
├── .kimi-plugin/plugin.json       ← Manifest cho Kimi Code
├── .opencode/                     ← Hướng dẫn cài cho OpenCode
├── docs/
│   ├── porting-to-a-new-harness.md ← Hướng dẫn hỗ trợ harness mới
│   └── testing.md                 ← Hướng dẫn kiểm tra skill
├── tests/                         ← Test infrastructure cho từng harness
├── scripts/                       ← Version bump, lint, packaging
├── CLAUDE.md                      ← Contributor guide (cho AI agents)
├── AGENTS.md                      ← (alias CLAUDE.md cho các harness khác)
└── README.md                      ← Quickstart + installation guide
```

**Mô tả thành phần quan trọng:**

| Thành phần | Vai trò |
|---|---|
| `skills/*/SKILL.md` | Định nghĩa skill: YAML frontmatter (name, description), nội dung hướng dẫn step-by-step, Red Flags tables, graphviz flow diagrams |
| `skills/using-superpowers/SKILL.md` | Bootstrap skill — được inject vào mọi session, buộc agent kiểm tra skill trước mọi hành động |
| `hooks/hooks.json` | Claude Code SessionStart hook — chạy shell script inject bootstrap |
| `skills/subagent-driven-development/scripts/` | Scripts phục vụ file handoff: `task-brief` (trích task ra file), `review-package` (tạo diff file), `sdd-workspace` (quản lý workspace) |
| `.claude-plugin/plugin.json` | Metadata cho Anthropic marketplace |
| `docs/porting-to-a-new-harness.md` | Blueprint để thêm harness mới vào ecosystem |

---

### 1.3 Phân tích kỹ thuật

#### 1.3.1 Kiến trúc: Skill-as-Document

Mỗi skill là một file Markdown có YAML frontmatter với trường `description` mô tả *chính xác khi nào invoke skill này*. Đây là design đơn giản nhưng hiệu quả: agent đọc description và tự quyết định có áp dụng hay không, thay vì cần hard-coding trigger logic.

```yaml
---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before
  committing or creating PRs - requires running verification commands and confirming
  output before making any success claims; evidence before assertions always
---
```

**Điểm mạnh:** Zero-dependency, portable sang mọi harness chỉ cần đọc Markdown. **Điểm yếu:** Không có cơ chế enforcement kỹ thuật — phụ thuộc hoàn toàn vào compliance của LLM.

#### 1.3.2 Pattern "Red Flags" để ngăn rationalization

Mọi skill đều có bảng "Red Flags" liệt kê các lý do mà agent thường dùng để *bỏ qua* skill, kèm phản bác trực tiếp:

```markdown
| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "The skill is overkill" | Simple things become complex. Use it. |
```

Pattern này nhận ra rằng LLM có xu hướng hợp lý hóa việc bỏ qua quy trình. Bằng cách liệt kê trước các rationalization phổ biến và phản bác ngay, skill tăng đáng kể tỷ lệ compliance.

#### 1.3.3 File Handoff Protocol để kiểm soát context window

`subagent-driven-development` giải quyết vấn đề context window phình to bằng cách truyền artifact qua file thay vì paste trực tiếp vào prompt:

- **Task briefs:** `scripts/task-brief PLAN_FILE N` — trích nội dung task N ra file riêng, trả về đường dẫn
- **Review packages:** `scripts/review-package BASE HEAD` — tạo file chứa commit list + diff, trả về đường dẫn
- **Report files:** Implementer viết báo cáo vào file, reviewer đọc file (không paste)

Kết quả: Controller session không bị phình to theo số task. Một session thực tế ghi nhận dispatch prompt đạt 42k chars vì paste accumulated history — file handoffs ngăn chặn điều này.

#### 1.3.4 Durable Progress Ledger

SDD skill duy trì file progress ledger tại `.superpowers/sdd/progress.md` (git-ignored, không bị commit) để track task đã hoàn thành. Khi session bị compact hay khởi động lại, agent đọc ledger thay vì đoán từ memory:

```
Task N: complete (commits abc1234..def5678, review clean)
```

**Tại sao cần thiết:** Context compaction xóa memory — controllers đã re-dispatch toàn bộ task đã hoàn thành là failure mode thực tế được ghi nhận.

#### 1.3.5 Model Tier Selection

`subagent-driven-development` có bảng hướng dẫn chọn model theo độ phức tạp task:

| Task type | Model tier |
|---|---|
| Mechanical (1-2 files, complete spec) | Cheap (e.g., Haiku) |
| Integration (multi-file, pattern matching) | Standard (e.g., Sonnet) |
| Architecture/design, final review | Most capable (e.g., Opus) |

Nguyên tắc: **"Turn count beats token price"** — model rẻ hơn thường mất nhiều turns hơn, tổng chi phí có thể cao hơn. Cân nhắc complexity, không chỉ unit price.

#### 1.3.6 Two-Stage Task Review

Sau mỗi task, có 2 vòng review độc lập:
1. **Spec compliance:** Agent đã làm đúng yêu cầu spec chưa? Thiếu hay thừa gì?
2. **Code quality:** Code có đạt tiêu chuẩn chất lượng không?

Cả hai phải pass trước khi chuyển task tiếp theo. Reviewer không được "pre-judge" (bảo reviewer bỏ qua vấn đề X).

#### 1.3.7 Writing-Skills: TDD Applied to Documentation

`writing-skills` skill định nghĩa quy trình tạo skill mới theo TDD:
- **RED:** Chạy subagent không có skill → ghi lại behavior vi phạm
- **GREEN:** Viết skill giải quyết vi phạm đó → verify subagent comply
- **REFACTOR:** Tìm lỗ hổng mới (rationalization mới) → vá → verify lại

Đây là cách đảm bảo skill mới thực sự thay đổi agent behavior, không chỉ là documentation mà agent bỏ qua.

#### 1.3.8 Multi-Harness Plugin Architecture

Repo duy trì manifest riêng cho từng harness (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.kimi-plugin/`, `.opencode/`, `.pi/`) nhưng chia sẻ cùng một thư mục `skills/`. Mỗi manifest chỉ mô tả cách install và điểm khác biệt của harness đó (hooks vs native skill discovery).

Acceptance test chuẩn hóa cho mọi harness: gõ "Let's make a react todo list" → `brainstorming` skill phải auto-trigger trước khi code bất kỳ dòng nào.

---

### 1.4 Điểm mạnh và điểm yếu

**Điểm mạnh:**
- Composable: mỗi skill độc lập, có thể dùng riêng lẻ không cần toàn bộ ecosystem
- Zero-dependency: chỉ là Markdown files, không cần build/compile
- Có eval harness (superpowers-evals) để kiểm tra behavior thực tế với LLM
- Khả năng mở rộng cao: thêm harness mới chỉ cần thêm manifest + test acceptance

**Điểm yếu:**
- Enforcement phụ thuộc compliance của LLM — không có cơ chế kỹ thuật bắt buộc
- Skills được thiết kế cho software development agents, không phải multi-agent orchestration có hierarchy
- Không có cơ chế cho escalation, approval chain, hay two-eyes principle ở tầng tổ chức

---

### 1.5 Thông tin repo

| Mục | Thông tin |
|---|---|
| URL | https://github.com/obra/superpowers |
| License | MIT |
| Version hiện tại | v6.1.1 (2026-07-02) |
| Tác giả | Jesse Vincent, Prime Radiant Inc. |
| Commit gần nhất | d884ae0 — Release v6.1.1 |
| Số skill | 14 skills |
| Harness hỗ trợ | Claude Code, Codex App/CLI, Cursor, Antigravity, Factory Droid, GitHub Copilot CLI, Kimi Code, OpenCode, Pi |
| Marketplace | Anthropic official Claude plugin marketplace |
| Community | Discord (https://discord.gg/35wsABTejz) |
| Độ trưởng thành | Đang active, đã có 6+ major versions, có eval framework, có commercial support |

---

## Phần 2 — Đề xuất cải tiến cho codebase KZTEK

> Phần này tách biệt khỏi phân tích (theo CLAUDE.md §4 WF-GITHUB-RESEARCH Bước 3b). Mỗi đề xuất cần user duyệt trước khi áp dụng.

### Bảng đề xuất

| # | Đề xuất | Học từ đâu (repo nguồn) | Áp dụng vào đâu trong KZTEK | Lợi ích | Rủi ro / Effort |
|---|---------|------------------------|------------------------------|---------|-----------------|
| **P1** | Thêm bảng "Red Flags" (rationalization prevention) vào các skill/agent quan trọng | `skills/using-superpowers/SKILL.md` — bảng "Red Flags" liệt kê lý do agent hay bỏ qua skill kèm phản bác | `.claude/commands/scope-check.md`, `.claude/commands/ship.md`, `.claude/agents/tech-lead.md`, `.claude/agents/qa-lead.md` — thêm mục "Red Flags" vào các agent/skill hay bị bỏ qua | Tăng compliance rate: agent ít có cớ để bỏ qua bước quan trọng (scope-check, security-audit, two-eyes review); tương tự pattern đã áp dụng trong CLAUDE.md §0 cho tư duy Dispatcher | Effort thấp (chỉ thêm bảng vào Markdown), rủi ro thấp — không thay đổi logic, chỉ thêm hướng dẫn |
| **P2** | Áp dụng "verification-before-completion" cho agent hoàn thành task | `skills/verification-before-completion/SKILL.md` — "Iron Law: NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"; agent phải chạy lệnh verify và đọc output trước khi báo cáo Done | Thêm mục "Verification Gate" vào `.claude/agents/senior-developer.md`, `.claude/agents/junior-developer.md`, `.claude/agents/qa-engineer.md` — trước khi agent nào đánh dấu task ✅ hoặc handoff sang agent tiếp | Giảm false completions: agent không tự tin tuyên bố "Done" mà không có bằng chứng thực tế; đặc biệt quan trọng khi QA sign-off và deploy | Effort thấp-trung bình (thêm section vào 3 agent files), rủi ro thấp |
| **P3** | Tạo `scripts/review-package.sh` để chuẩn hóa file handoff khi code review | `skills/subagent-driven-development/scripts/review-package` — script tạo file chứa commit list + git diff + stat cho reviewer đọc 1 lần thay vì paste vào prompt | Tạo `scripts/review-package.sh` mới; tham chiếu trong `.claude/agents/tech-lead.md` và `.claude/agents/senior-developer.md` khi dispatch code review | Giảm context window inflation trong WF-REVIEW-STD/CRIT: reviewer nhận 1 file path thay vì toàn bộ diff được paste vào prompt; consistent review format | Effort trung bình (tạo shell script mới + cập nhật 2 agent files), rủi ro thấp — script không thay đổi behavior hiện tại, chỉ là tooling mới |
| **P4** | Thêm "Durable Progress Ledger" bổ sung cho plan files trong WF-MIGRATE và WF-GITHUB-RESEARCH | `skills/subagent-driven-development/SKILL.md` — progress ledger tại `.superpowers/sdd/progress.md` (git-ignored) track task đã complete với commit hash; phục hồi từ git log khi ledger bị xóa | Thêm quy tắc vào `.claude/agents/code-migrator.md` và `.claude/agents/github-repo-researcher.md`: sau mỗi bước Done, append 1 dòng vào `.claude/workspace/progress.md` (git-ignored); bổ sung CLAUDE.md §16 với hướng dẫn recovery | Tăng resilience khi session bị compact/restart ở WF-MIGRATE (nhiều bước nhất); plan file đã có nhưng ledger nhẹ hơn và không cần edit nhiều fields | Effort trung bình (cập nhật 2 agent files + 1 section CLAUDE.md), rủi ro thấp |
| **P5** | Tách `description` của agent file thành trigger condition rõ ràng theo pattern superpowers | `skills/*/SKILL.md` — frontmatter `description` luôn bắt đầu bằng "Use when..." mô tả điều kiện trigger chính xác, không phải mô tả tổng quát | Chuẩn hóa frontmatter của tất cả `.claude/agents/*.md`: trường `description` phải theo format "Use when [điều kiện cụ thể] — [mô tả ngắn nhiệm vụ]" thay vì chỉ là mô tả agent | Dispatcher routing chính xác hơn khi đọc description; dễ onboard agent mới; nhất quán với best practice | Effort thấp (chỉ edit description strings trong ~15 agent files), rủi ro thấp |
| **P6** | Tạo skill `writing-skills` riêng cho KZTEK để chuẩn hóa quy trình tạo agent/skill mới | `skills/writing-skills/SKILL.md` — "Writing skills IS Test-Driven Development applied to process documentation"; RED: chạy test kịch bản áp lực → GREEN: viết skill giải quyết vi phạm → REFACTOR: vá lỗ hổng | Tạo `.claude/commands/writing-agent-skill.md` mới, mô tả quy trình: (1) viết test scenario, (2) verify agent vi phạm, (3) viết skill, (4) verify agent comply, (5) refactor | Tăng chất lượng agent/skill mới: không viết theo trực giác mà theo evidence thực tế từ test; giảm trường hợp agent mới tạo ra mà không ai dùng | Effort trung bình (tạo file skill mới, không cụ thể thay đổi code), rủi ro thấp |
| **P7** | Áp dụng "Turn count beats token price" vào bảng §13.1b CLAUDE.md khi downshift Haiku | `skills/subagent-driven-development/SKILL.md` — "Turn count beats token price. Wall-clock and context cost scale with how many turns a subagent takes, and the cheapest models routinely take 2-3x the turns on multi-step work — costing more overall" | Cập nhật CLAUDE.md §13.1b và §13.2: thêm cảnh báo "Haiku phù hợp khi task chỉ 1-2 turns (điền template, chạy script). Nếu task yêu cầu ≥3 turns → dùng Sonnet dù task tưởng đơn giản" | Tránh tình huống downshift sang Haiku làm tăng chi phí tổng do nhiều turns; giải thích được quyết định chọn model | Effort rất thấp (edit 2 đoạn trong CLAUDE.md §13), rủi ro thấp |

---

### Ghi chú về an toàn

Các đề xuất P1-P7 không đụng đến auth, payment, DB schema, hay dữ liệu nhạy cảm. Không cần chạy `security-audit-stride` trước khi merge.

---

### Trạng thái áp dụng

| # | Đề xuất | Trạng thái |
|---|---------|-----------|
| P1 | Thêm Red Flags table vào agent/skill | ⬜ Chờ user xác nhận |
| P2 | Verification-before-completion gate | ⬜ Chờ user xác nhận |
| P3 | Script review-package.sh | ⬜ Chờ user xác nhận |
| P4 | Durable Progress Ledger bổ sung | ⬜ Chờ user xác nhận |
| P5 | Chuẩn hóa description trigger condition | ⬜ Chờ user xác nhận |
| P6 | Skill writing-agent-skill mới | ⬜ Chờ user xác nhận |
| P7 | Turn count caution trong §13.1b | ⬜ Chờ user xác nhận |

---

*File này được tạo bởi GitHub Repo Researcher trong workflow WF-GITHUB-RESEARCH.*
*Nhánh: `research/superpowers-2026-07-12` | Plan: `.claude/plans/PLAN-superpowers-research-2026-07-12.md`*
