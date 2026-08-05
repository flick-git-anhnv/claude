# Nghiên cứu Repo: mattpocock/skills

**Ngày nghiên cứu:** 2026-08-05
**Researcher:** GitHub Repo Researcher (WF-GITHUB-RESEARCH)
**Nhánh:** research/skills-2026-08-05
**Trạng thái:** Bước 3 hoàn thành — chờ user chọn Mode A / Mode B

---

## 1. Tổng quan repo

| Mục | Chi tiết |
|-----|---------|
| Repo | [mattpocock/skills](https://github.com/mattpocock/skills) |
| Tác giả | Matt Pocock — người tạo Total TypeScript, ts-reset, và newsletter AI Hero (~60,000 đăng ký) |
| Mô tả gốc | "My agent skills that I use every day to do real engineering — not vibe coding" |
| Version | 1.2.1 (plugin.json) / 1.2.0 (package.json) |
| License | MIT — tự do sử dụng, chỉnh sửa, phân phối |
| Stars | 204,447 (cực kỳ phổ biến) |
| Forks | 17,652 |
| Hoạt động gần nhất | 2026-08-05 (hôm nay — đang được phát triển tích cực) |
| Open Issues | 280 |

**Mục đích cốt lõi:** Bộ skills (slash commands + behaviors) cho Claude Code và Codex được thiết kế theo tư duy kỹ thuật phần mềm thực sự — không phải "vibe coding". Thay vì kiểm soát toàn bộ quy trình như GSD/BMAD, các skill này nhỏ, có thể hack, và composable. Chúng đối phó với 4 failure mode phổ biến khi dùng AI coding agents:

1. Agent không làm đúng ý → Giải pháp: grilling session trước khi code
2. Agent quá verbose → Giải pháp: shared domain vocabulary (CONTEXT.md)
3. Code không chạy → Giải pháp: TDD + feedback loop + debug discipline
4. Codebase thành ball of mud → Giải pháp: codebase design vocabulary + architecture improvement

---

## 2. Cấu trúc repo

```
mattpocock/skills/
├── skills/                          ← Tất cả skill definitions
│   ├── engineering/                 ← 18 skills (được promote — ship trong plugin)
│   │   ├── ask-matt/                ← Router: chỉ user gọi, map sang các skill khác
│   │   ├── grill-with-docs/         ← Grilling + domain model building (stateful)
│   │   ├── triage/                  ← Issue state machine
│   │   ├── improve-codebase-architecture/
│   │   ├── setup-matt-pocock-skills/← Setup 1 lần/repo (issue tracker, labels, doc layout)
│   │   ├── to-spec/                 ← Conversation → spec → issue tracker
│   │   ├── to-tickets/              ← Plan → tracer-bullet tickets với blocking edges
│   │   ├── implement/               ← Build theo spec/tickets (drives /tdd + /code-review)
│   │   ├── wayfinder/               ← Map huge foggy work as decision tickets
│   │   ├── prototype/               ← Throwaway HTML prototype để answer design question
│   │   ├── diagnosing-bugs/         ← 6-phase disciplined debug loop
│   │   ├── research/                ← Background agent investigates từ primary sources
│   │   ├── tdd/                     ← Red-green-refactor TDD loop
│   │   ├── domain-modeling/         ← Sharpen project domain language → CONTEXT.md + ADRs
│   │   ├── codebase-design/         ← Deep module vocabulary (module/interface/depth/seam)
│   │   ├── code-review/             ← 2-axis parallel sub-agents review (Standards + Spec)
│   │   ├── resolving-merge-conflicts/
│   │   └── wizard/                  ← Tạo bash wizard cho bước chỉ human làm được
│   ├── productivity/                ← 7 skills (được promote — ship trong plugin)
│   │   ├── grill-me/                ← User-invoked grilling (stateless, không có repo)
│   │   ├── grilling/                ← Reusable interview primitive (model-invoked)
│   │   ├── handoff/                 ← Compact session → file để agent mới tiếp tục
│   │   ├── teach/                   ← Multi-session teaching workspace
│   │   ├── to-questionnaire/        ← Decision → questionnaire gửi người khác
│   │   ├── wait-what/               ← Re-explain message không hiểu, dùng vocab CONTEXT.md
│   │   └── writing-for-agents/      ← Meta-skill: viết docs cho agents
│   ├── misc/                        ← 4 skills (giữ lại, không promote, không ship)
│   ├── in-progress/                 ← 6 skills (beta, public để nhận feedback, không ship)
│   └── deprecated/                  ← Skills không còn dùng
├── docs/                            ← Human-facing docs (mirrors engineering/ + productivity/)
│   ├── engineering/                 ← 1 page/skill với 4 sections chuẩn
│   └── productivity/
├── .agents/                         ← Documentation cho agent/maintainer của repo này
│   ├── adr/                         ← Architectural decisions về system skills
│   ├── install-block.md             ← Cú pháp install cho readme
│   ├── invocation.md                ← Model-invoked vs user-invoked rules
│   └── writing-docs.md              ← Template viết docs page cho skill
├── .claude-plugin/                  ← Claude Code plugin manifest
│   ├── plugin.json                  ← Danh sách skills ship trong plugin, version
│   └── marketplace.json             ← Self-hosted marketplace fallback
├── .out-of-scope/                   ← ADR-style docs: những gì đã từ chối và tại sao
├── scripts/
│   ├── link-skills.sh               ← Symlink skills vào ~/.claude/skills, ~/.agents/skills
│   └── list-skills.sh
├── CONTEXT.md                       ← Shared domain glossary của chính repo skills này
├── CLAUDE.md                        ← Repo instructions cho Claude Code agents
└── AGENTS.md                        ← Symlink → CLAUDE.md (để Codex đọc cùng instructions)
```

**Mỗi skill trong `engineering/` và `productivity/` có:**
- `SKILL.md` — nội dung skill, frontmatter YAML (name, description, disable-model-invocation)
- `agents/openai.yaml` — Codex metadata (display_name, short_description, policy.allow_implicit_invocation)
- File companion tùy chọn: `DEEPENING.md`, `DESIGN-IT-TWICE.md`, `PHASE-BOUNDARIES.md`, `tests.md`, `mocking.md`

---

## 3. Phân tích kỹ thuật

### 3.1 User-invoked vs Model-invoked — Phân tách tường minh

Đây là pattern nổi bật nhất của repo. Mỗi skill thuộc đúng 1 trong 2 loại:

**User-invoked** (chỉ human gọi, không agent tự gọi):
```yaml
# SKILL.md frontmatter
disable-model-invocation: true

# agents/openai.yaml  
policy:
  allow_implicit_invocation: false
```
Ví dụ: `ask-matt`, `grill-with-docs`, `grill-me`, `handoff`, `implement`, `wayfinder`, `to-spec`, `to-tickets`

**Model-invoked** (agent hoặc human đều có thể gọi):
```yaml
# Không có disable-model-invocation, description dùng trigger phrasing
description: "Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases."
```
Ví dụ: `grilling`, `tdd`, `diagnosing-bugs`, `codebase-design`, `domain-modeling`, `code-review`, `research`

**Quy tắc thành phần:** User-invoked skill có thể gọi model-invoked skill, nhưng KHÔNG BAO GIỜ gọi user-invoked skill khác. Model-invoked skill hoàn toàn độc lập.

**Lý do thiết kế:** Ngăn agent tự ý khởi động orchestration flow (như `grill-with-docs` hoặc `implement`) — những flow này chỉ có ý nghĩa khi human chủ động muốn. Model-invoked skills là "primitive" được tái dùng bởi nhiều user-invoked skills.

### 3.2 Grilling — Reusable Interview Primitive

`grilling` (model-invoked) là primitive được dùng bởi ít nhất 5 skills:
- `grill-me` (wrapper stateless)
- `grill-with-docs` (wrapper với CONTEXT.md + ADRs)
- `triage` (internal)
- `wayfinder` (internal)
- `improve-codebase-architecture` (internal)

**Cơ chế:** (`skills/productivity/grilling/SKILL.md`)
- Map decisions như **design tree**: mỗi quyết định branch thành các quyết định phụ thuộc
- Làm việc theo **rounds**: frontier = tất cả quyết định chưa settled có đủ prerequisite
- Mỗi round: hỏi toàn bộ frontier cùng lúc (đánh số + kèm recommended answer), chờ trả lời
- Agent tự tìm **facts** từ environment (sub-agent nếu cần) — không hỏi user về thứ agent tra được
- Session kết thúc khi frontier rỗng: mọi branch của design tree đã resolved

**Format câu hỏi chuẩn:**
```
Q1 - <question title>: <question body>
➡️ <your recommended answer>
```

### 3.3 CONTEXT.md — Shared Domain Glossary

Pattern: mỗi repo dùng skills này nên có `CONTEXT.md` riêng, do `/grill-with-docs` và `/domain-modeling` sinh ra và maintain.

`CONTEXT.md` trong repo `mattpocock/skills` chính là ví dụ minh họa (`CONTEXT.md` tại root):
```markdown
## Language
**Issue tracker**: The tool that hosts a repo's issues...
  _Avoid_: backlog manager, backlog backend, issue host

**Issue**: A single tracked unit of work...
  _Avoid_: ticket (chỉ dùng khi quote external system)
```

**Mục đích:**
- Tất cả agents cùng dùng vocabulary này thay vì phải "suy đoán jargon"
- Giảm verbosity: "problem with materialization cascade" thay vì "problem when a lesson inside a section is made real"
- File này được đọc bởi `tdd`, `diagnosing-bugs`, `code-review` để dùng vocabulary đúng
- `domain-modeling` skill chủ động challenge và update file này

### 3.4 Diagnosing-bugs — 6-Phase Disciplined Debug Loop

(`skills/engineering/diagnosing-bugs/SKILL.md`)

Phase 1 — Build a feedback loop (critical, tốn effort nhiều nhất):
- Phải có **tight feedback loop** trước: 1 command có thể go red on this bug
- 10 cách build: failing test, curl script, CLI invocation, headless browser, trace replay, throwaway harness, property/fuzz, bisection, differential, HITL bash script
- **Completion criterion:** "No Phase 2 if no tight loop." Nếu bắt đầu đọc code để suy ra hypothesis trước khi có loop → STOP.

Phase 2 — Reproduce + minimise
Phase 3 — Hypothesise (3-5 ranked hypotheses, falsifiable predictions)
Phase 4 — Instrument (1 variable at a time, tagged debug logs `[DEBUG-a4f2]`)
Phase 5 — Fix + regression test (write test BEFORE fix, chỉ khi có correct seam)
Phase 6 — Cleanup + post-mortem (grep debug tags, thêm architectural finding)

### 3.5 Code-review — 2-Axis Parallel Sub-agents

(`skills/engineering/code-review/SKILL.md`)

Hai trục hoàn toàn độc lập, chạy song song:
- **Standards**: code có theo documented coding standards không? + Fowler code smells baseline
- **Spec**: code có faithfully implement originating issue/spec không?

```
Spawn cả 2 sub-agents cùng 1 lúc với Agent tool →
collect reports → aggregate dưới 2 headings riêng biệt → KHÔNG merge/rerank
```

**Lý do 2 trục riêng biệt:** Code có thể pass Standards nhưng fail Spec (đúng convention, sai yêu cầu), hoặc ngược lại. Trộn 2 trục khiến 1 trục mask trục kia.

**Fowler smell baseline cố định** (12 smells, luôn áp dụng dù repo không có coding standards): Mysterious Name, Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent Change, Speculative Generality, Message Chains, Middle Man, Refused Bequest.

### 3.6 Codebase-design — Deep Module Vocabulary

(`skills/engineering/codebase-design/SKILL.md`)

Định nghĩa chính xác 6 khái niệm (dùng đúng từ, không thay thế bằng "component/API/boundary"):
- **Module**: anything with interface + implementation (scale-agnostic: function, class, package, tier-slice)
- **Interface**: type signature + invariants + ordering constraints + error modes + config + perf characteristics
- **Depth**: leverage-as-interface — amount of behavior per unit of interface learned
- **Seam** (Michael Feathers): where you can alter behavior without editing in that place
- **Adapter**: concrete thing satisfying an interface at a seam (role, not substance)
- **Leverage/Locality**: what callers/maintainers get from depth

**Test thực dụng:**
- Deletion test: xóa module đi thì complexity biến mất (pass-through) hay xuất hiện khắp N callers (earning keep)?
- One adapter = hypothetical seam. Two adapters = real seam. Không tạo seam khi chưa cần.

### 3.7 Wayfinder — Map Huge Work as Decision Tickets

(`skills/engineering/wayfinder/SKILL.md`)

Dành cho work quá lớn cho 1 session, chưa rõ đường đi (foggy). Tạo **shared map** trên issue tracker.

**Key distinctions:**
- Decision tickets = questions, NOT implementation tasks
- 1 ticket/session maximum (trừ research tickets)
- Fog of war: chỉ chart những gì đã có thể specify — "Not yet specified" section cho fuzzy areas
- Out of scope: explicit section, không bao giờ graduate thành ticket

**4 ticket types:** Research (AFK, /research subagent), Prototype (HITL, /prototype), Grilling (HITL, default), Task (HITL hoặc AFK, unblocks a decision)

### 3.8 Writing-for-agents — Meta-skill về Document Design

(`skills/productivity/writing-for-agents/SKILL.md`)

Rất quan trọng: meta-skill viết skills/CLAUDE.md/AGENTS.md. Các concept chính:

**Context pointers:** Wording quyết định khi nào agent reach tài liệu — pointer yếu = variance bug.

**Information hierarchy (4 tầng):**
1. In-file step (primary tier — what agent does, in order)
2. In-file reference (consulted on demand — rules, facts)
3. Disclosed reference (separate file, reached by pointer, loaded only when pointer fires)

**Leading words:** Compact concepts từ pretraining: "tight" (loop), "red" (test state), "fog of war", "tracer bullets". Dùng token duy nhất thay vì 20 từ giải thích. Anchor: nếu word cùng xuất hiện trong prompts, docs, và codebase → agent link được.

**Pruning disciplines:** Single source of truth, environment là source (đừng restate), relevance check từng dòng, tránh sediment (stale layers không ai dám xóa).

**Completion criteria:** Phải checkable (agent tự biết done/not-done) + exhaustive (drives enough legwork).

### 3.9 Bucket Lifecycle + ADR trong .agents/

Skills có vòng đời rõ ràng: `in-progress/` → `engineering/` hoặc `productivity/` → có thể → `deprecated/`. Skills trong `misc/` tồn tại song song nhưng không promote.

`.agents/adr/` chứa ADR của chính hệ thống skills (không phải sản phẩm):
- `0001-explicit-setup-pointer-only-for-hard-dependencies.md` — hard vs soft dependency distinction
- `0002-ship-as-a-claude-code-plugin.md` — lý do chọn Claude plugin, roadmap Codex plugin

`.out-of-scope/` — pattern rất hiếm: docs tường minh ghi lại những gì đã từ chối:
- `question-limits.md` — tại sao không giới hạn số câu grilling (mọi request liên quan đã được từ chối)
- `mainstream-issue-trackers-only.md`
- `setup-skill-verify-mode.md`

---

## 4. Điểm mạnh và điểm yếu

### Điểm mạnh

| Điểm mạnh | Mô tả |
|-----------|-------|
| **Composable, không monolithic** | Mỗi skill nhỏ, tự chứa. Có thể chạy riêng hoặc kết hợp (implement gọi tdd + code-review) |
| **User-invoked vs Model-invoked tường minh** | Ngăn agent tự khởi động orchestration flows — chỉ human mới trigger |
| **CONTEXT.md như shared language** | Giải quyết vấn đề "agent không biết jargon" theo cách có thể persist qua session |
| **Grilling làm primitive tái dùng** | 1 implementation, 5+ consumers — không duplicate logic |
| **Phase-gated debug loop** | Diagnosing-bugs không cho phép nhảy phase, có completion criteria rõ ràng |
| **Parallel sub-agents trong code-review** | 2 trục không "làm bẩn" context của nhau — kết quả chính xác hơn |
| **Writing-for-agents meta-skill** | Systematic framework viết docs cho agent: leading words, information hierarchy, pruning |
| **Lifecycle skills rõ ràng** | Bucket system + .out-of-scope/ + ADRs = biết tại sao mọi quyết định được đưa ra |
| **MIT license + 204K+ stars** | Rất trưởng thành, cộng đồng lớn, active maintenance |

### Điểm yếu / Giới hạn

| Điểm yếu | Mô tả |
|-----------|-------|
| **Phụ thuộc vào issue tracker** | Nhiều skills (to-tickets, triage, wayfinder) cần setup issue tracker trước — overhead với project nhỏ |
| **Không có role-based agents** | Không có khái niệm PM, TL, QA — skills thiên về "how to do", không về "who does what" |
| **Setup 1 lần per repo** | `/setup-matt-pocock-skills` phải chạy trước các engineering skills mới hoạt động đúng |
| **Chưa có Codex native plugin** | Đang là roadmap (xem ADR-0002) — hiện chỉ Claude Code plugin officially |
| **In-progress skills không ship** | 6 skills beta chưa available trong plugin — phải cài manual qua npx |

---

## 5. Hiện trạng KZTEK

### 5.1 Hệ thống Commands/Skills hiện có

**`.claude/commands/` — 17 skills/commands:**
- `scope-check.md` — chốt workflow/priority/P0-P3 (hỏi tối đa 5 câu)
- `security-audit-stride.md` — OWASP + STRIDE audit
- `ship.md` — GO/NO-GO gate trước deploy
- `verify-pr.md` — automated PR verification
- `detect-impact.md` — phân tích blast radius khi thay đổi code
- `pre-coding-check.md` — đọc CODE-GRAPH + lessons + GOTCHAS trước khi code
- `writing-agent-skill.md` — viết skill/agent mới
- `kztek-brand-info.md` — brand guidelines
- `ui-ux-pro-max.md`, `design-taste-frontend.md` — UI/UX skills
- `graphify.md`, `run-plan-step.md`, `sync-global.md`, v.v.

**`.claude/agents/` — 19 agents theo vai trò:**
CTO, Engineering Manager, Product Manager, Business Analyst, Tech Lead, Senior Developer, Junior Developer, QA Lead, QA Engineer, DevOps Lead, DevOps Engineer, Project Manager, Documentation Writer, UI/UX Designer, UX/UI Reviewer, Code Migrator, GitHub Repo Researcher, Task Planner, MD Optimizer.

### 5.2 So sánh trực tiếp theo từng pattern

| Pattern | mattpocock/skills | KZTEK hiện tại |
|---------|------------------|----------------|
| **Phân tách user-invoked vs model-invoked** | Tường minh qua `disable-model-invocation: true` + openai.yaml policy | Không có — tất cả commands có thể bị agent tự kéo vào |
| **Shared domain glossary** | `CONTEXT.md` per repo, được `domain-modeling` skill maintain | Không có — KZTEK dùng các term trong CLAUDE.md nhưng không có glossary tập trung per-project |
| **Grilling/interview primitive** | `grilling` skill tái dùng bởi 5+ skills, có frontier/round/design-tree model | `scope-check.md` hỏi tối đa 5 câu cứng nhắc, không có design tree, không tái dùng được |
| **Disciplined debug loop** | `diagnosing-bugs` với 6 phases, completion criteria rõ ràng, không cho nhảy phase | §9a Agent Introspection (loop detection) — khác hoàn toàn về mục đích: phát hiện agent stuck, không phải debug app |
| **TDD skill** | `tdd` — red-green-refactor, seam-based, anti-patterns rõ | Không có |
| **Code review skill** | `code-review` — 2 trục (Standards + Spec), parallel sub-agents | `verify-pr.md` — kiểm tra automated, không phải 2-axis review |
| **Session handoff** | `handoff` — compact session → portable markdown | Plan files (`PLAN-MASTER.md` + step files + Handoff Payload 3-key) — khác: plan-centric thay vì session-centric |
| **Domain vocabulary** | `codebase-design` — module/interface/depth/seam/adapter (6 terms chính xác) | `detect-impact.md` — tập trung blast radius, không có vocabulary layer |
| **Huge work planning** | `wayfinder` — decision tickets, fog of war, frontier model | `task-planner` + Plan file — tập trung vào task breakdown, không phải decision tree |
| **Writing docs for agents** | `writing-for-agents` — context pointers, information hierarchy, leading words, pruning | `writing-agent-skill.md` — hướng dẫn format, ít framework lý thuyết hơn |
| **Skill lifecycle** | Bucket system: in-progress → engineering/productivity → deprecated | Không có lifecycle — commands ở flat level, không có trạng thái "in-progress" hay "deprecated" |
| **ADRs về system** | `.agents/adr/` — lý do thiết kế hệ thống skill | `CHANGELOG-AGENTS.md` + `docs/CHANGELOG-AGENTS.md` — ghi lịch sử thay đổi nhưng không phải ADR format |
| **Out-of-scope docs** | `.out-of-scope/` — explicit rejection records | Không có |
| **Plugin distribution** | Claude Code plugin marketplace | Không applicable — repo cấu hình private |
| **Prototype skill** | `prototype` — throwaway HTML để trả lời design question | Không có |
| **Router skill** | `ask-matt` — map toàn bộ skills với reasoning về khi nào dùng cái gì | Không có — người dùng phải tự biết từng command |
| **Research skill** | `research` — background agent, primary sources, cited markdown | `github-repo-researcher` — tập trung vào external repos, không phải research question tổng quát |

---

## 6. Thông tin repo

| Mục | Chi tiết |
|-----|---------|
| URL | https://github.com/mattpocock/skills |
| License | MIT |
| Version | 1.2.1 |
| Stars | 204,447 |
| Forks | 17,652 |
| Hoạt động | Cực kỳ active — push mới nhất ngay hôm nay (2026-08-05) |
| Cài đặt | `claude plugins install mattpocock-skills` (Claude Code) hoặc `npx skills@latest add mattpocock/skills` (Codex/other) |
| Cộng đồng | ~60,000 đăng ký newsletter AI Hero của tác giả |
| Language | Markdown (SKILL.md) + YAML (openai.yaml frontmatter) — không có code runtime |
| Dependencies | Không có runtime dependencies — chỉ là text files |

---

*Tài liệu này chỉ phân tích, không kèm đề xuất áp dụng. Xem Bước 3b để đọc đề xuất cải tiến (Mode A) hoặc Bước 3c/3d/3e để đi sâu học nguyên lý (Mode B).*
