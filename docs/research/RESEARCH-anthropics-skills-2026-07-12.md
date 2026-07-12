---
repo: https://github.com/anthropics/skills
slug: anthropics-skills
date: 2026-07-12
researcher: github-repo-researcher
branch: research/anthropics-skills-2026-07-12
status: step-3b-complete
---

# RESEARCH: anthropics/skills — Repo chính thức của Anthropic về Agent Skills

---

## PHẦN 1 — PHÂN TÍCH REPO (Bước 3)

### 1.1 Tổng quan repo

**Mục đích:** `anthropics/skills` là repo chính thức của Anthropic chứa định nghĩa và ví dụ mẫu cho hệ thống "Agent Skills" — cơ chế cho phép Claude nhận thêm khả năng chuyên biệt thông qua các file hướng dẫn có cấu trúc. Skills dạy Claude cách hoàn thành các tác vụ lặp lại theo cách nhất quán và có thể tái sử dụng.

**Đối tượng sử dụng:** Developer, tổ chức, cá nhân muốn tạo workflow tùy chỉnh cho Claude (Claude Code, Claude.ai, API). Repo phục vụ hai mục đích đồng thời: (a) reference implementation cho các skill chính thức của Anthropic, và (b) bộ mẫu/hướng dẫn để cộng đồng tạo skill riêng.

**Vấn đề giải quyết:** Khi không có skill, agent phải tự suy luận lại từ đầu mỗi lần gặp cùng một loại tác vụ → tốn token, kết quả không nhất quán, "reinventing the wheel". Skills encapsulate knowledge, scripts, và references để agent invocation sau hiệu quả hơn invocation trước.

**License:** Apache 2.0 cho example skills; Proprietary (source-available) cho document skills (docx, pptx, pdf, xlsx).

---

### 1.2 Cấu trúc repo

```
anthropics/skills/
├── README.md                          ← Overview + quickstart
├── THIRD_PARTY_NOTICES.md
├── .gitignore
├── .claude-plugin/
│   └── marketplace.json               ← Plugin grouping config
├── spec/
│   └── agent-skills-spec.md           ← Trỏ đến agentskills.io/specification
├── template/
│   └── SKILL.md                       ← Template tối giản (chỉ 3 dòng)
└── skills/
    ├── algorithmic-art/               ← SKILL.md + templates/
    ├── brand-guidelines/              ← SKILL.md
    ├── canvas-design/                 ← SKILL.md + fonts/
    ├── claude-api/                    ← SKILL.md + references/ + shared/
    ├── doc-coauthoring/               ← SKILL.md
    ├── docx/                          ← SKILL.md + scripts/office/
    ├── frontend-design/               ← SKILL.md
    ├── internal-comms/                ← SKILL.md + examples/
    ├── mcp-builder/                   ← SKILL.md
    ├── pdf/                           ← SKILL.md + scripts/ + references/
    ├── pptx/                          ← SKILL.md + scripts/ + references/
    ├── skill-creator/                 ← SKILL.md + agents/ + scripts/ + references/ + assets/
    ├── slack-gif-creator/             ← SKILL.md + requirements.txt
    ├── theme-factory/                 ← SKILL.md + PDF showcase
    ├── web-artifacts-builder/         ← SKILL.md
    ├── webapp-testing/                ← SKILL.md + scripts/ + examples/
    └── xlsx/                          ← SKILL.md + scripts/ + references/
```

**Mô tả từng thành phần chính:**

| Thành phần | Mô tả |
|-----------|-------|
| `skills/<name>/SKILL.md` | File bắt buộc duy nhất; YAML frontmatter + Markdown instructions |
| `skills/<name>/scripts/` | Python/shell scripts thực thi cho tác vụ có tính lặp lại, xác định (unpack docx, validate, pack) |
| `skills/<name>/references/` | Tài liệu tham chiếu lớn — được load vào context khi cần, không phải lúc nào cũng load |
| `skills/<name>/assets/` | Files dùng trong output: HTML template, font TTF, icon |
| `skills/<name>/examples/` | File mẫu để agent hiểu định dạng đầu ra |
| `spec/agent-skills-spec.md` | Pointer đến spec chính thức tại agentskills.io/specification |
| `template/SKILL.md` | Template tối giản: 3 dòng YAML + 1 dòng placeholder |
| `.claude-plugin/marketplace.json` | Nhóm skills thành "plugins" để cài đặt theo batch |

---

### 1.3 Phân tích kỹ thuật chi tiết

#### 1.3.1 Format SKILL.md — Frontmatter bắt buộc

Template tối giản (`template/SKILL.md`):
```yaml
---
name: template-skill
description: Replace with description of the skill and when Claude should use it.
---

# Insert instructions below
```

Chỉ 2 fields bắt buộc: `name` (kebab-case, unique identifier) và `description` (what + when). Các fields tùy chọn: `license`, `compatibility` (khai báo tools/dependencies đặc biệt, hiếm khi cần).

**Khác biệt quan trọng so với pattern KZTEK:** Anthropic yêu cầu `name:` luôn phải có vì đây là unique identifier cho routing và marketplace. KZTEK hiện chỉ có `description:` trong frontmatter.

#### 1.3.2 Progressive Disclosure — 3-level loading system

Từ `skills/skill-creator/SKILL.md` mục "Progressive Disclosure":

```
Level 1: Metadata (name + description) — ~100 words
         → Luôn trong context; dùng để trigger skill
         
Level 2: SKILL.md body — ideally <500 lines
         → Loaded vào context khi skill trigger
         
Level 3: Bundled resources (scripts/, references/, assets/)
         → Loaded AS NEEDED; scripts có thể execute mà không load vào context
```

**Key insight:** Scripts trong `scripts/` được gọi như black-box executables — agent chạy `python scripts/validate.py file.docx` mà không cần đọc toàn bộ source code. Giúp giữ context window nhỏ ngay cả với skill phức tạp như `docx` (~600 lines SKILL.md + 4 scripts Python).

**Quy tắc từ skill-creator:** "If approaching 500 lines, add an additional layer of hierarchy along with clear pointers about where the model should go next."

#### 1.3.3 Description Strategy — "Pushy" triggering

Từ `skills/skill-creator/SKILL.md` mục "Write the SKILL.md":

> "Note: currently Claude has a tendency to 'undertrigger' skills — to not use them when they'd be useful. To combat this, please make the skill descriptions a little bit 'pushy'. So for instance, instead of 'How to build a simple fast dashboard', you might write '...Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics...'"

**Pattern thực tế trong repo:**

`docx/SKILL.md` description (trích):
> "Use this skill whenever the user wants to create, read, edit, or manipulate Word documents. Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents... Also use when extracting or reorganizing content from .docx files... If the user asks for a 'report', 'memo', 'letter', 'template'... Do NOT use for PDFs, spreadsheets, Google Docs..."

`claude-api/SKILL.md` description: Liệt kê tường minh 15+ trigger conditions, bao gồm model names cụ thể (`Claude`, `Anthropic`, `Opus`, `Sonnet`, `Haiku`, `anthropic`, `claude-*`).

**Quy tắc cứng từ skill-creator:** "All 'when to use' info goes in description, not in the body."

#### 1.3.4 Bundled Resources Pattern — "Don't reinvent the wheel"

Từ `skills/skill-creator/SKILL.md` mục "How to think about improvements":

> "Look for repeated work across test cases. Read the transcripts from the test runs and notice if the subagents all independently wrote similar helper scripts... If all 3 test cases resulted in the subagent writing a `create_docx.py`, that's a strong signal the skill should bundle that script. Write it once, put it in `scripts/`, and tell the skill to use it."

**Ví dụ thực tế:**
- `skills/docx/scripts/office/`: `unpack.py`, `validate.py`, `pack.py`, `soffice.py`, `accept_changes.py`
- `skills/docx/SKILL.md`: "Use `python scripts/office/unpack.py`..." — agent chạy script, không tự viết logic
- `skills/webapp-testing/SKILL.md`: "**Always run scripts with `--help` first** to see usage. DO NOT read the source until... Scripts exist to be called directly as black-box scripts rather than ingested into your context window."

**Domain organization** (từ skill-creator):
```
cloud-deploy/
├── SKILL.md (workflow + selection logic)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md    ← Claude reads ONLY the relevant file
```

#### 1.3.5 Keywords Section

Một số skills thêm keywords vào body để hỗ trợ routing:

`brand-guidelines/SKILL.md`: `**Keywords**: branding, corporate identity, visual identity, post-processing, styling, brand colors, typography, Anthropic brand, visual formatting, visual design`

`internal-comms/SKILL.md`: `## Keywords` section cuối file: `3P updates, company newsletter, company comms, weekly update, faqs, common questions, updates, internal comms`

**Mục đích:** Cung cấp từ đồng nghĩa/từ liên quan cho trigger mechanism khi description chính không cover hết mọi cách user diễn đạt nhu cầu.

#### 1.3.6 Eval-Driven Description Optimization

Từ `skills/skill-creator/SKILL.md` mục "Description Optimization":

1. Tạo 20 eval queries: 10 should-trigger (realistic, có backstory, details cụ thể) + 10 should-NOT-trigger (near-miss — chia sẻ keywords nhưng không nên trigger)
2. Split 60% train / 40% test để tránh overfitting
3. Chạy `scripts/run_loop.py` — automated optimization loop (max 5 iterations)
4. Pick `best_description` theo test score, không train score
5. Apply vào frontmatter

**Yêu cầu đặc biệt cho queries:** "Not abstract requests, but requests that are concrete and specific... file paths, personal context, column names, company names, URLs. A little bit of backstory." Ví dụ tốt: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column..."` — không phải `"Format this data"`.

#### 1.3.7 Reader Testing Pattern (doc-coauthoring)

`skills/doc-coauthoring/SKILL.md` Stage 3 "Reader Testing":

1. Predict 5-10 câu hỏi mà người đọc sẽ đặt ra khi tìm kiếm document này
2. Invoke subagent với CHỈ nội dung document (không có context của session tạo ra) — fresh Claude
3. Kiểm tra: subagent có trả lời đúng không? Có gì ambiguous không?
4. Fix blind spots → loop lại

**Điều kiện dừng:** Khi Reader Claude consistently trả lời đúng và không surface thêm gap mới.

**Mục đích cốt lõi:** "A document (hoặc instruction set) được tạo trong context của session ban đầu có thể chứa assumptions về context mà người đọc/agent mới không có."

#### 1.3.8 Marketplace / Plugin Grouping

`.claude-plugin/marketplace.json` nhóm skills thành 3 plugins:
- `document-skills`: docx, pptx, pdf, xlsx
- `example-skills`: 12 skills sáng tạo/kỹ thuật  
- `claude-api`: 1 skill

Install tất cả bằng: `/plugin install document-skills@anthropic-agent-skills`

**Ý nghĩa:** Skills được tổ chức theo use case, không phải theo category kỹ thuật — giúp user "install all what I need" mà không cần biết từng skill riêng lẻ.

#### 1.3.9 Writing Principles

Từ `skills/skill-creator/SKILL.md` mục "Writing Style":

> "Try to explain to the model **why** things are important in lieu of heavy-handed musty MUSTs. Use theory of mind... If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid structures, that's a yellow flag — if possible, reframe and explain the reasoning so that the model understands why the thing you're asking for is important. That's a more humane, powerful, and effective approach."

> "Try to make the skill general and not super-narrow to specific examples."

#### 1.3.10 Environment Adaptation

`skill-creator/SKILL.md` có sections riêng biệt:
- "Claude.ai-specific instructions" — không có subagents, không chạy browser viewer
- "Cowork-specific instructions" — có subagents, không có browser, dùng `--static` flag
- Main flow — Claude Code với subagents và browser

---

### 1.4 Hiện trạng KZTEK (BẮT BUỘC — khu vực tương ứng)

Khu vực tương ứng trong KZTEK: `.claude/commands/*.md` (skill definitions) và `.claude/agents/*.md` (agent definitions).

**Tổng quan 7 file skill hiện có trong `.claude/commands/`:**

| File | Có frontmatter? | Có `name:`? | Có `description:`? | Keywords section? | Bundled resources? |
|------|-----------------|-------------|---------------------|-------------------|--------------------|
| `kztek-brand-info.md` | KHÔNG | KHÔNG | KHÔNG | KHÔNG | KHÔNG |
| `scope-check.md` | Có | KHÔNG | Có | KHÔNG | KHÔNG |
| `security-audit-stride.md` | Có | KHÔNG | Có | KHÔNG | KHÔNG |
| `ship.md` | Có | KHÔNG | Có | KHÔNG | KHÔNG |
| `skill-trigger-test.md` | Có | KHÔNG | Có | KHÔNG | KHÔNG |
| `verify-pr.md` | Có | KHÔNG | Có | KHÔNG | KHÔNG |
| `writing-agent-skill.md` | Có | KHÔNG | Có | KHÔNG | KHÔNG |

**Nhận xét chi tiết:**

**`kztek-brand-info.md`** — Không có frontmatter gì cả. File chỉ là nội dung tĩnh bắt đầu bằng `# KZTEK Brand Info`. Không có `name:`, `description:` hay bất kỳ trigger condition nào. Agent muốn dùng phải gọi bằng tên file cứng.

**`scope-check.md`** — Description: `"Chạy TRƯỚC Bước Pre-0 (task-planner) khi yêu cầu của user còn mơ hồ về phạm vi/priority..."` — mô tả thời điểm dùng nhưng không "pushy"; không có near-miss exclusions tường minh trong description.

**`ship.md`** — Description dài, tương đối đầy đủ; đã có "KHÔNG thay thế đầy đủ WF-FEATURE" trong body (không phải description).

**`writing-agent-skill.md`** — Có RED→GREEN→REFACTOR process, tương tự skill-creator's eval loop nhưng manual. Không có "Reader Testing" step để verify fresh-agent invocation.

**`skill-trigger-test.md`** — Tương tự Description Optimization của Anthropic nhưng thủ công (manual simulation). Ví dụ queries là tốt nhưng chưa theo guidance "concrete + backstory" của Anthropic.

**Về Progressive Disclosure:** Tất cả 7 skills đều là single-file. KZTEK có `scripts/md_to_docx_kztek.py` là external script được skills/agents reference bằng đường dẫn — đây là pattern gần với bundled resources nhưng script không được "bundled" vào skill directory cụ thể.

**Về Reader Testing:** Không có bước nào trong `writing-agent-skill.md` yêu cầu test definition với fresh subagent. EDD (`EVAL-template.md`) yêu cầu test scenarios nhưng test bằng simulation, không phải fresh agent invocation thực tế.

---

### 1.5 So sánh trực tiếp KZTEK vs repo nguồn

| Khía cạnh | anthropics/skills | KZTEK hiện tại |
|-----------|------------------|----------------|
| **Frontmatter `name:`** | Bắt buộc — là unique identifier | Không có trong bất kỳ command file nào |
| **Frontmatter `description:`** | Bắt buộc — primary trigger mechanism | Có trong 6/7 files; 1 file không có frontmatter gì |
| **Description "pushy"** | Tường minh 10+ trigger conditions; có near-miss exclusions ("Do NOT use for...") | Passive hơn; ít trigger conditions tường minh |
| **Keywords section** | Một số skills có (`brand-guidelines`, `internal-comms`) | Chưa có skill nào |
| **Progressive Disclosure** | 3-level (metadata / SKILL.md body / bundled resources) | Tất cả nội dung trong 1 file (chưa có concept) |
| **Bundled scripts** | Scripts đóng gói trong `scripts/` — run as black-box | External script `scripts/md_to_docx_kztek.py` — referenced bằng path, không bundled |
| **Eval-driven optimization** | `evals.json` + `run_loop.py` automated; should-trigger/NOT-trigger với backstory cụ thể | `EVAL-template.md` + manual simulation; ít "backstory" trong queries |
| **Reader Testing** | Stage 3 của doc-coauthoring — fresh subagent test | Không có |
| **Meta-skill (tạo skill)** | `skill-creator/SKILL.md` — đầy đủ với eval viewer, grader agents, blind comparison | `writing-agent-skill.md` — TDD approach tốt nhưng thiếu fresh-agent test |
| **Trigger test** | `run_loop.py` automated; description optimization với train/test split | `skill-trigger-test.md` — manual simulation tốt |
| **Marketplace grouping** | `.claude-plugin/marketplace.json` — install theo batch | Chưa có |
| **Writing style** | "Why" over "MUST"; theory of mind; general not narrow | Tốt; có "Lý do hay bỏ qua" (Red Flags) — tương đương |
| **Environment adaptation** | Explicit per-environment sections | Không có |

---

### 1.6 Thông tin repo

| Thông tin | Giá trị |
|-----------|---------|
| URL | https://github.com/anthropics/skills |
| Owner | Anthropic |
| License | Apache 2.0 (example skills); Proprietary/source-available (document skills) |
| Commit gần nhất | `9d2f1ae` — "Update claude-api skill: Claude Sonnet 5 and Managed Agents July updates" |
| Cập nhật | Tháng 7/2026 (repo đang active) |
| Số skills | 15+ skills trong 3 plugin groups |
| Độ trưởng thành | Rất cao — chính thức của Anthropic, đang dùng trong production Claude |
| Spec đầy đủ | https://agentskills.io/specification |

---

## PHẦN 2 — BẢNG ĐỀ XUẤT CẢI TIẾN (Bước 3b)

> Dựa trên phần So sánh (§1.5). Mỗi đề xuất được kiểm tra: "Lý do thay đổi" trả lời được "tại sao không giữ nguyên hiện trạng?"; "Đạt được gì" là kết quả cụ thể quan sát/đo được.

| # | Đề xuất | Hiện trạng KZTEK | Học từ đâu | Lý do thay đổi | Áp dụng vào đâu | Đạt được gì | Rủi ro / Effort |
|---|---------|-----------------|------------|----------------|-----------------|-------------|-----------------|
| **S1** | Thêm `name:` field vào frontmatter của tất cả `.claude/commands/*.md` | Tất cả 7 files chỉ có `description:`; không có unique identifier | `template/SKILL.md` — `name` là required field; `skill-creator/SKILL.md` mục "Anatomy of a Skill" | Không có `name:` → Dispatcher nhận dạng skill chỉ qua description text; khi nhiều skills có description tương tự, không có fallback identifier để phân biệt; không phục vụ được marketplace/plugin grouping sau này | Tất cả 7 files trong `.claude/commands/*.md`: thêm `name: <kebab-case>` vào YAML frontmatter | Mỗi skill có unique identifier rõ ràng; Dispatcher routing chính xác hơn khi description có ambiguity; nền tảng cho marketplace grouping; nhất quán với Anthropic spec | Rủi ro: None. Effort: Rất thấp — 7 file, mỗi file thêm 1 dòng |
| **S2** | Thêm frontmatter đầy đủ (`name:` + `description:`) cho `kztek-brand-info.md` | File không có frontmatter gì; chỉ là static content bắt đầu bằng `# KZTEK Brand Info` | `template/SKILL.md` — cả `name` và `description` đều REQUIRED; `skill-creator/SKILL.md` — "All 'when to use' info goes in description" | Không có frontmatter → Dispatcher không thể auto-trigger skill này dựa trên context; Documentation Writer phải được instruct bằng tên file cứng (`.claude/commands/kztek-brand-info.md`) thay vì trigger tự nhiên khi cần brand info | `.claude/commands/kztek-brand-info.md` — thêm YAML frontmatter với `name: kztek-brand-info` và `description:` mô tả khi nào cần load brand info | Bất kỳ agent nào cần brand colors, logo rules, typography có thể trigger skill tự động dựa trên context ("tạo tài liệu cho KZTEK", "áp dụng brand KZTEK") mà không cần gọi file cứng | Rủi ro: Thấp — chỉ thêm frontmatter, không đổi nội dung. Effort: Rất thấp |
| **S3** | Cập nhật description của `scope-check.md` và `writing-agent-skill.md` theo pattern "pushy" | `scope-check.md` description: mô tả thời điểm dùng nhưng chưa liệt kê tường minh các trigger context; `writing-agent-skill.md` description tốt nhưng near-miss exclusions ở body, không phải description | `skill-creator/SKILL.md` — "Claude has a tendency to 'undertrigger' skills... make descriptions a little bit 'pushy'"; docx description với 10+ explicit trigger conditions và "Do NOT use for..." exclusions | Passive description → Dispatcher bỏ qua scope-check khi yêu cầu mơ hồ; theo nghiên cứu Anthropic đây là lỗi phổ biến nhất với skill system | `.claude/commands/scope-check.md` — thêm near-miss exclusions vào description; `.claude/commands/writing-agent-skill.md` — chuyển "KHÔNG dùng khi" từ body vào description | Giảm tần suất Dispatcher bỏ qua scope-check với yêu cầu mơ hồ; cụ thể: scope-check trigger đúng khi user mô tả tính năng chỉ 1-2 câu mà không nêu workflow rõ | Rủi ro: Thấp. Effort: Thấp — chỉ edit description field |
| **S4** | Thêm `## Keywords` section vào `kztek-brand-info.md`, `writing-agent-skill.md`, `skill-trigger-test.md` | Không có keywords section trong bất kỳ command file nào | `skills/brand-guidelines/SKILL.md` — `**Keywords**: branding, corporate identity...`; `skills/internal-comms/SKILL.md` — `## Keywords` section | Keywords cung cấp synonyms/related terms làm backup cho description trigger; không phải user nào cũng dùng cùng một từ khi cần cùng một skill; description không thể cover tất cả cách diễn đạt | `.claude/commands/kztek-brand-info.md`, `.claude/commands/writing-agent-skill.md`, `.claude/commands/skill-trigger-test.md` — thêm `## Keywords` section cuối file | Routing accuracy tốt hơn cho 3 skills trên; khi user dùng synonym ("màu sắc KZTEK" thay vì "brand", "tạo skill mới" thay vì "viết agent"), Dispatcher vẫn nhận dạng đúng | Rủi ro: None. Effort: Rất thấp |
| **S5** | Thêm Bước "Agent Definition Testing" (Reader Testing) vào `writing-agent-skill.md` | `writing-agent-skill.md` có TDD approach (RED→GREEN→REFACTOR) tốt nhưng không có bước test definition với fresh agent invocation; EDD chỉ test bằng simulation | `skills/doc-coauthoring/SKILL.md` Stage 3 "Reader Testing" — test document với fresh Claude (no context bleed) via subagents để verify instructions work for readers; "A document may contain assumptions about context that readers don't have" | Agent definitions được tạo trong context session hiện tại — người tạo có đầy đủ context nhưng fresh agent invocation sau đó không có; KZTEK không có bước kiểm tra "does this definition work when an agent reads it cold?" trước khi deploy | `.claude/commands/writing-agent-skill.md` — thêm Bước 4b "Agent Definition Testing" sau bước REFACTOR hiện tại: invoke subagent với ONLY agent definition file (không có context session), test các CE scenarios | Mỗi agent/skill mới được verify bằng fresh invocation trước khi thêm vào routing; phát hiện "blind spots" — instructions assume context mà fresh agent không có; giảm tỉ lệ agent mới routing sai trong session đầu tiên | Rủi ro: Thấp. Effort: Trung bình — cần thêm ~1 bước quy trình vào skill |
| **S6** | Thêm "Bundled Resources" guidance vào `writing-agent-skill.md` | Không có hướng dẫn khi nào nên tách external references/scripts vs nhúng vào file; tất cả skills là single-file; skills phức tạp như `security-audit-stride.md` (~100 lines) hoặc `writing-agent-skill.md` (~170 lines) đang nhúng toàn bộ nội dung | `skill-creator/SKILL.md` mục "Anatomy of a Skill" — `scripts/`, `references/`, `assets/` architecture; "Look for repeated work across test cases... that's a signal to bundle the script"; webapp-testing — "Scripts exist to be called directly as black-box scripts rather than ingested into your context window" | Single-file skills → khi skill trigger, TOÀN BỘ nội dung load vào context dù agent chỉ cần 20-30% nội dung cho task cụ thể; không có framework để scale khi skills trở nên phức tạp hơn | `.claude/commands/writing-agent-skill.md` — thêm mục "Khi nào nên dùng bundled resources" với 3 signal cụ thể: (1) file >300 lines, (2) nội dung chỉ cần trong specific contexts, (3) scripts lặp lại trong test runs | Skills phức tạp trong tương lai có cấu trúc rõ ràng để scale; agent chỉ load reference content khi thực sự cần (ước tính giảm context từ ~500 words/skill xuống ~100 words khi không cần references) | Rủi ro: Thấp — không thay đổi skills hiện tại, chỉ thêm guidance cho skills mới. Effort: Thấp |

---

## PHẦN 3 — TRẠNG THÁI ÁP DỤNG

| # | Đề xuất | Trạng thái | Ghi chú |
|---|---------|-----------|---------|
| S1 | Thêm `name:` field vào commands/*.md | Chờ user xác nhận | — |
| S2 | Thêm frontmatter cho kztek-brand-info.md | Chờ user xác nhận | — |
| S3 | Cập nhật description "pushy" | Chờ user xác nhận | — |
| S4 | Thêm Keywords section | Chờ user xác nhận | — |
| S5 | Thêm Agent Definition Testing step | Chờ user xác nhận | — |
| S6 | Thêm Bundled Resources guidance | Chờ user xác nhận | — |

---

*Tài liệu này được tạo bởi GitHub Repo Researcher (L4) — Bước 1.3 và 1.3b của WF-GITHUB-RESEARCH.*
*Nhánh: `research/anthropics-skills-2026-07-12` | Plan: `.claude/plans/PLAN-anthropics-skills-research-2026-07-12.md`*
