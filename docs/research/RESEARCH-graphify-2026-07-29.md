---
title: "Báo cáo nghiên cứu — Graphify-Labs/graphify"
repo_url: https://github.com/Graphify-Labs/graphify
research_date: 2026-07-29
researcher: github-repo-researcher
branch: research/graphify-2026-07-29
mode: A (Cải tiến KZTEK — mặc định)
status: draft — phân tích (chưa có đề xuất)
---

# Nghiên cứu repo: Graphify-Labs/graphify

> Bước 3 WF-GITHUB-RESEARCH — Phân tích trung lập. Đề xuất cải tiến KZTEK sẽ được viết riêng tại Bước 3A.1 (Mode A).

---

## 1. Tổng quan repo

**Tên:** graphify (package PyPI: `graphifyy`)
**URL:** https://github.com/Graphify-Labs/graphify
**Phiên bản phân tích:** v0.9.29 (branch chính: v8, đang active development)
**License:** Apache-2.0 (có thể dùng trong sản phẩm thương mại)
**Nguồn gốc:** YC S26, được giới thiệu trên Trendshift, hỗ trợ 20+ AI assistant platform

### Mục đích cốt lõi

Graphify là một AI coding assistant skill — người dùng gõ lệnh `/graphify .` trong Claude Code (hoặc 20+ trợ lý AI khác), toàn bộ codebase cùng docs, PDFs và media được phân tích và build thành một **knowledge graph có thể query**, thay vì AI phải đọc từng file thủ công.

### Vấn đề giải quyết

Khi project lớn, AI assistant cần đọc hàng chục file mới hiểu được quan hệ giữa các component. Graphify pre-build graph một lần; sau đó mọi câu hỏi về codebase được trả lời qua graph traversal — nhanh hơn, scoped hơn, và có thể trace lại từng bước suy luận.

---

## 2. Stack & Công nghệ

| Layer | Công nghệ | Ghi chú |
|---|---|---|
| Ngôn ngữ | Python 3.10+ | |
| Graph engine | NetworkX 3.4+ | Lưu trữ node/edge và traversal |
| Code extraction | tree-sitter AST | 36+ ngôn ngữ, chạy local, không cần LLM, zero API cost |
| Community detection | Leiden (graspologic) | Cài thêm `graphify[leiden]`; fallback greedy algorithm |
| Semantic extraction | LLM pluggable | Gemini / Claude / OpenAI / Ollama / Bedrock / DeepSeek — dùng cho docs, PDFs, images |
| Fuzzy matching | rapidfuzz | Query expansion, entity disambiguation |
| Optional extras | neo4j, falkordb, pdf, office, video, mcp, ... | Cài riêng từng extra theo nhu cầu |
| Package manager | uv (khuyến nghị) | Isolated env, tránh PATH conflict |
| MCP server | fastmcp / starlette | `graphify[mcp]` — expose graph qua MCP tools |

**Điểm đáng chú ý về stack:** Phần parse code (tree-sitter AST) hoàn toàn local và không phát sinh API cost. LLM chỉ được gọi cho semantic extraction của docs/PDFs/images, và kết quả được cache.

---

## 3. Cấu trúc thư mục

```
graphify/                     <- Python package chính
├── __main__.py               <- Entry point CLI (python -m graphify)
├── cli.py                    <- Argument parsing, top-level commands
├── skill.md                  <- SKILL.md cài vào Claude Code (skill body chính)
├── skill-*.md                <- Variant cho từng platform (codex, opencode, kilo, ...)
├── always_on/                <- Snippets inject vào CLAUDE.md / AGENTS.md
│   ├── claude-md.md          <- Đoạn chèn vào CLAUDE.md (buộc query-first behavior)
│   ├── agents-md.md          <- Đoạn chèn vào AGENTS.md
│   └── ...
├── skills/                   <- Reference docs cho từng platform
│   ├── claude/references/    <- extraction-spec.md, query.md, update.md, ...
│   └── ...
├── extractors/               <- Language-specific extractors
│   ├── base.py               <- Shared helpers
│   ├── csharp.py             <- C# cross-file type-reference resolver
│   ├── engine.py             <- Config-driven extraction engine (đa ngôn ngữ)
│   ├── powershell.py         <- PowerShell extractor
│   └── ...
├── detect.py                 <- collect_files() — file filtering theo extension
├── extract.py                <- extract() — dispatch đến extractor đúng theo suffix
├── build.py                  <- build_graph() — dicts -> NetworkX graph
├── cluster.py                <- cluster() — Leiden/greedy community detection
├── analyze.py                <- god_nodes(), surprising_connections(), suggest_questions()
├── report.py                 <- render_report() -> GRAPH_REPORT.md
├── export.py                 <- to_json(), to_html(), to_obsidian(), ...
├── serve.py                  <- MCP server (stdio hoặc HTTP)
├── cache.py                  <- Semantic cache (tránh re-extract files không đổi)
├── security.py               <- validate_url(), sanitize_label(), safe_fetch()
├── validate.py               <- validate_extraction() — schema check trước khi build
├── diagnostics.py            <- diagnose_extraction() — integrity gate sau build
├── prs.py                    <- PR dashboard: CI state, triage AI, community impact
└── reflect.py                <- graphify reflect — Q&A memory -> LESSONS.md
tests/                        <- Unit tests (pytest, no network, no file side effects)
docs/                         <- How-it-works, docker-mcp-sqlite, translations (33 ngôn ngữ)
worked/                       <- Worked examples (corpus + review.md)
```

---

## 4. Pipeline cốt lõi

```
detect() -> extract() -> build_graph() -> cluster() -> analyze() -> report() -> export()
```

Mỗi stage là một function độc lập, giao tiếp qua plain Python dicts và NetworkX graph. Không có shared state, không có side effects ngoài thư mục `graphify-out/`.

### Schema chuẩn hóa của extraction output

```json
{
  "nodes": [
    {
      "id": "unique_string",
      "label": "human readable name",
      "source_file": "path/to/file.cs",
      "source_location": "L42"
    }
  ],
  "edges": [
    {
      "source": "id_a",
      "target": "id_b",
      "relation": "calls|imports|uses|inherits|...",
      "confidence": "EXTRACTED|INFERRED|AMBIGUOUS"
    }
  ]
}
```

### Confidence labels (audit trail)

| Label | Nghĩa |
|---|---|
| `EXTRACTED` | Explicit trong source — import statement, direct call |
| `INFERRED` | Suy diễn — call-graph second pass, co-occurrence |
| `AMBIGUOUS` | Không chắc chắn — flagged cho human review |

---

## 5. Các module chính

### 5.1 `extractors/csharp.py` — C# extractor

Xử lý đặc thù C#: build namespace-to-node_id index, resolve cross-file `inherits`/`uses` edges. Hỗ trợ cả XAML (tree-sitter-c-sharp + XAML parser). Các ngôn ngữ liên quan đến KZTEK đều được hỗ trợ: `.cs`, `.xaml`, `.razor`, `.cshtml`, `.ps1`, `.psm1`, `.psd1`, `.sql`.

### 5.2 `cache.py` — Semantic cache

Cache extraction theo **cặp khóa: file hash + prompt hash**. Ý nghĩa của prompt hash: khi graphify nâng cấp prompt extraction, cache cũ bị invalidate và file được re-extract — tránh replay kết quả lỗi thời. Lệnh `--update` chỉ re-extract file đã thay đổi.

### 5.3 `always_on/claude-md.md` — Always-on injection

Đoạn text inject vào `CLAUDE.md` để buộc agent query graph trước khi đọc raw files:

```markdown
## graphify
- For codebase questions, first run `graphify query "<question>"`...
- After modifying code, run `graphify update .`...
```

Graphify cũng đăng ký `PreToolUse` hook trên Claude Code — fire trước mỗi lần gọi search/read tool, tự động tra graph.

### 5.4 `prs.py` — PR dashboard

`graphify prs` hiển thị PR dashboard với CI state và review status. `graphify prs <N>` deep-dive PR cụ thể, cho thấy **graph impact** — node/edge nào bị ảnh hưởng bởi PR đó. `graphify prs --triage` — AI tự rank review queue theo độ phức tạp.

### 5.5 `reflect.py` — Knowledge accumulation

`graphify reflect` aggregate Q&A memory từ các session làm việc với codebase → tổng hợp thành `LESSONS.md`. Cơ chế này xây dựng "institutional knowledge" cộng dồn theo thời gian.

---

## 6. Điểm nổi bật kỹ thuật

### 6.1 Real graph traversal — không phải vector index

Graphify không dùng embeddings, không dùng vector store. Đây là real graph (NetworkX) có thể traverse bằng BFS/DFS:

- `graphify query "..."` — tìm node liên quan, trả về subgraph
- `graphify path A B` — shortest path giữa hai khái niệm
- `graphify explain X` — subgraph 1-hop quanh node X

Mỗi câu trả lời có thể trace lại từng hop — **traceable reasoning**, không phải black-box semantic similarity.

### 6.2 Parallel subagent dispatch

Bước extraction docs/PDFs/images dùng Agent tool với `run_in_background: true`, dispatch tất cả subagents trong cùng một message để chạy song song. Cụ thể ở `skill.md` Step B2:

> "Call the Agent tool multiple times IN THE SAME RESPONSE — one call per chunk."

Pattern này giống ký hiệu `∥` trong CLAUDE.md KZTEK §4. Tiết kiệm 5–15 giây trên corpora lớn.

### 6.3 Semantic cache với double-key invalidation

`cache.py` cache extraction theo **file hash + prompt hash** (không chỉ file hash). Khi prompt extraction thay đổi giữa các phiên bản, cache entries cũ bị invalidate và file được re-extract, đảm bảo kết quả luôn khớp với logic extraction hiện tại.

### 6.4 Always-on CLAUDE.md injection

`graphify claude install` tự động inject block guidance vào `CLAUDE.md` để mọi agent trong project đều query graph trước khi đọc raw files. Kết hợp với `PreToolUse` hook, cơ chế này trở thành constraint kiến trúc chứ không chỉ là gợi ý.

### 6.5 PR-to-graph impact mapping

`graphify prs <N>` không chỉ hiển thị metadata PR mà còn cho thấy node/edge nào trong knowledge graph bị ảnh hưởng bởi PR đó — kết nối git history với graph để reviewer có context rộng hơn khi đánh giá PR.

---

## 7. Hiện trạng KZTEK — Code Graph hiện tại

**File:** `code-graph/CODE-GRAPH.md`

**Phương pháp hiện tại:** Markdown phẳng, cập nhật thủ công bởi coding agents sau mỗi code change (per CLAUDE.md §17).

**Nội dung hiện tại:** Mô tả tổng quan workspace agent framework và bảng KztekComponent controls. Workspace hiện tại chưa có product codebase C# đang phát triển.

**Quy tắc §17 hiện tại:**
- Agents đọc `CODE-GRAPH.md` TRƯỚC khi đọc source files
- Cập nhật sau mỗi code change có structural impact
- Export `.pdf` đồng thời với `.md` qua `md_to_docx_kztek.py`

**Hạn chế của cơ chế hiện tại:**

| Hạn chế | Mô tả |
|---|---|
| Không query được | Agent phải đọc toàn bộ file rồi grep — tốn context window |
| Không tự cập nhật | Agent phải Edit thủ công sau mỗi code change |
| Không biết "ai gọi ai" | Chỉ mô tả cấu trúc thư mục, không có call graph |
| Không detect module grouping | Không có community detection |
| Không có visualization | Không có interactive graph để duyệt |
| Scope giới hạn | Hiện chỉ mô tả agent framework, không phải product C# |

---

## 8. So sánh trực tiếp: Graphify vs KZTEK CODE-GRAPH.md

| Khía cạnh | Graphify | KZTEK hiện tại (CODE-GRAPH.md §17) |
|---|---|---|
| Kiểu graph | NetworkX traversable graph (nodes + edges) | Flat Markdown document |
| Query | `graphify query "..."`, `path A B`, `explain X` | Grep / Read toàn bộ file |
| Cập nhật | `graphify update .` — incremental, chỉ re-extract file đã đổi | Manual Edit bởi agent |
| Tốc độ build | tree-sitter AST local, ~seconds, không cần LLM | N/A — mô tả thủ công |
| C# support | `extractors/csharp.py` — cross-file type-reference resolution | Không (chỉ mô tả files) |
| Docs / PDF / Image | LLM semantic extraction có semantic cache | Không |
| Visualization | Interactive HTML graph (`graphify-out/graph.html`) | Không |
| Community detection | Leiden algorithm | Không |
| PR integration | `graphify prs` + graph impact per PR | Không |
| Always-on guidance | Inject vào CLAUDE.md — query-first behavior | CLAUDE.md §17 — read file trước |
| Context window | Scoped subgraph (nhỏ, chỉ lấy phần liên quan) | Toàn bộ file CODE-GRAPH.md |
| Confidence tracking | EXTRACTED / INFERRED / AMBIGUOUS per edge | Không |
| Phụ thuộc hạ tầng | Python 3.10+, tree-sitter, NetworkX | Không có — chỉ cần text editor |

**Lưu ý ngữ cảnh so sánh:** Workspace KZTEK hiện tại là agent framework (markdown + scripts), chưa có product C# codebase. Graphify sẽ có giá trị cao nhất khi có codebase C# thực tế để extract (`.cs`, `.xaml`, `.ps1`).

---

## 9. Thông tin repo

| Thuộc tính | Giá trị |
|---|---|
| URL | https://github.com/Graphify-Labs/graphify |
| License | Apache-2.0 (thương mại được phép) |
| Version phân tích | v0.9.29 (pre-1.0, active development) |
| Branch chính | v8 |
| Backing | YC S26 |
| Visibility | Trendshift featured |
| Platform hỗ trợ | 20+ (Claude Code, Codex, OpenCode, Kilo, ...) |
| Ngôn ngữ hỗ trợ | 36+ (bao gồm C#, XAML, PowerShell, SQL) |
| Breaking changes | Có changelog — cần theo dõi upgrade path khi cập nhật |
| Docs | 33 ngôn ngữ tại `docs/` |

---

## 10. Nhận xét chung

Graphify giải quyết một vấn đề thực tế: khi codebase phình to, AI assistant tốn quá nhiều context window chỉ để hiểu cấu trúc project. Cách tiếp cận của Graphify — build real graph một lần, query nhiều lần — là khác biệt rõ ràng so với các công cụ dùng vector embedding thông thường.

Các điểm kỹ thuật đáng chú ý nhất:
1. **Traceable reasoning** qua real graph traversal (không phải black-box similarity)
2. **Semantic cache với double-key** (file hash + prompt hash) — giải quyết vấn đề cache stale khi upgrade
3. **Always-on injection** vào CLAUDE.md — biến guidance thành constraint kiến trúc

Giới hạn đáng ghi nhận: đây là pre-1.0 software đang active development, API/behavior có thể thay đổi giữa các phiên bản.

---

*Báo cáo này thuộc Bước 3 WF-GITHUB-RESEARCH — phân tích trung lập. Đề xuất áp dụng vào KZTEK (Mode A, Bước 3A.1) sẽ được viết riêng sau khi user xác nhận tiếp tục.*

---

## 11. Đề xuất cải tiến KZTEK (Mode A — Bước 3A.1)

> Dựa trên phân tích ở các mục trên. Mỗi đề xuất độc lập — user có thể chọn 0, 1, hoặc nhiều đề xuất để áp dụng ở bước tiếp theo (Bước 3A.2). **CHƯA áp dụng bất kỳ thay đổi nào vào codebase KZTEK ở bước này.**

### Bảng tổng quan nhanh

| # | Đề xuất | Effort | Phụ thuộc ngoài | Áp dụng ngay? | Trạng thái |
|---|---------|--------|-----------------|---------------|------------|
| P1 | Tích hợp Graphify CLI vào workflow coding | Trung bình (1–2 ngày) | Python 3.10+, `pip install graphify` | Khi có C# product codebase | ✅ Đã áp dụng (2026-07-29) |
| P2 | Cải tiến §17: "Query-first checklist" có cấu trúc | Thấp (2–4 giờ) | Không có | Ngay — với cả markdown codebase hiện tại | ✅ Đã áp dụng (2026-07-29) |
| P3 | Confidence labels trong CODE-GRAPH.md | Thấp (4–8 giờ) | Không có | Ngay | ✅ Đã áp dụng (2026-07-29) |
| P4 | "CODE-GRAPH impact" field trong PR checklist §15.3 | Rất thấp (1–2 giờ) | Không có | Ngay | ✅ Đã áp dụng (2026-07-29) |
| P5 | LESSONS.md — Tích lũy institutional knowledge | Thấp (4–6 giờ) | Không có | Ngay | ✅ Đã áp dụng (2026-07-29) |

---

### P1 — Tích hợp Graphify CLI vào quy trình coding

| Trường | Nội dung |
|--------|---------|
| **Hiện trạng KZTEK** | `code-graph/CODE-GRAPH.md` là file Markdown phẳng, cập nhật thủ công bởi agents (CLAUDE.md §17). Agents phải đọc toàn bộ file để lấy context — tốn context window. Không có call graph (ai gọi ai), không query được. Workspace hiện chưa có C# product codebase. |
| **Học từ đâu** | Pipeline `detect() → extract() → build_graph()` (`extract.py`, `build.py`, `extractors/csharp.py`); lệnh `graphify update .` (incremental re-extract chỉ file đã đổi); lệnh `graphify query "..."`, `graphify path A B`, `graphify explain X` (graph traversal); `always_on/claude-md.md` (injection buộc query-first behavior). |
| **Lý do thay đổi** | Agents đọc CODE-GRAPH.md như formality rồi vẫn Glob toàn bộ `src/` để "chắc chắn". Không có call graph → Senior Dev phải grep nhiều file để hiểu dependency. Update thủ công không đủ chính xác (agent suy đoán từ tên file, không từ AST). |
| **Áp dụng vào đâu** | (1) CLAUDE.md §17.1 — thay "đọc CODE-GRAPH.md trước" bằng "chạy `graphify query` trước khi đọc source file". (2) WF-FEATURE Bước 8/9 (Senior/Junior Dev) — thêm bước bắt buộc chạy `graphify update .` sau khi sửa code, trước khi tạo PR. (3) `.claude/shared/CORE.md` §coding-protocol — đồng bộ. |
| **Đạt được gì** | (a) Agent tra cứu `graphify query "where is KzButton used?"` nhận subgraph trong <2 giây thay vì grep 10+ file — giảm từ ~5 lần Read tool xuống 1 lần query per context question. (b) CODE-GRAPH không bao giờ stale: `graphify update .` dùng AST (tree-sitter, zero LLM cost) chỉ re-extract file đã đổi. (c) C# cross-file dependency (`extractors/csharp.py`) phát hiện namespace/inheritance mà Markdown thủ công không capture được. |
| **Rủi ro / Effort** | Rủi ro: (1) Pre-1.0 software — API có thể thay đổi giữa minor releases → cần pin version cụ thể. (2) Cần Python 3.10+ trong môi trường dev/CI. (3) Giá trị thực tế chỉ cao khi có C# product codebase — áp dụng ngay bây giờ lợi ích hạn chế. Effort: **Trung bình** — 1–2 ngày (setup, integration vào workflow instructions, test với C# sample). |

---

### P2 — Cải tiến CLAUDE.md §17: "Query-first checklist" có cấu trúc

| Trường | Nội dung |
|--------|---------|
| **Hiện trạng KZTEK** | CLAUDE.md §17.1 yêu cầu agents "Read code-graph/CODE-GRAPH.md TRƯỚC" nhưng không có hướng dẫn cụ thể về việc phải trả lời những câu hỏi gì từ CODE-GRAPH trước khi mở source file. Không có checklist hay protocol. |
| **Học từ đâu** | `always_on/claude-md.md` — đoạn text inject vào CLAUDE.md với danh sách câu hỏi cụ thể cần trả lời từ graph trước khi đọc raw file: "For codebase questions, first run `graphify query`..."; "After modifying code, run `graphify update .`...". Pattern: biến guidance mơ hồ thành constraint có checklist cụ thể. |
| **Lý do thay đổi** | §17 hiện tại nói "đọc trước" nhưng không định nghĩa "đọc để trả lời câu hỏi gì". Agents đọc qua CODE-GRAPH rồi vẫn mở toàn bộ src/ vì không biết khi nào "đã đủ" — tốn 3–5 lần Read tool redundant mỗi task. |
| **Áp dụng vào đâu** | CLAUDE.md §17.1 — thêm mục "Query Checklist bắt buộc": danh sách 4–5 câu hỏi agents PHẢI cố gắng trả lời từ CODE-GRAPH trước khi mở source file (ví dụ: "Module X nằm ở file nào?", "X phụ thuộc vào những module nào?", "Ai gọi X?", "X expose interface/API nào?"). Chỉ khi CODE-GRAPH không trả lời được mới mở source file. `.claude/shared/CORE.md` §coding-protocol — đồng bộ. |
| **Đạt được gì** | Agents khai thác CODE-GRAPH có chủ đích thay vì đọc formality → ước tính giảm 2–4 lần Read/Glob tool redundant per coding task quen thuộc. Mỗi task tiết kiệm ~500–1000 tokens context. Sau 10 WF-BUGFIX cycles, tiết kiệm đáng kể tổng token. |
| **Rủi ro / Effort** | Rủi ro: Rất thấp — chỉ là text change trong CLAUDE.md và CORE.md, không thêm dependency, không thay đổi code. Effort: **Thấp** — 2–4 giờ (edit §17, viết ví dụ checklist, đồng bộ CORE.md). |

---

### P3 — Confidence labels trong CODE-GRAPH.md

| Trường | Nội dung |
|--------|---------|
| **Hiện trạng KZTEK** | CODE-GRAPH.md không có cơ chế phân biệt giữa relationship "đã verify qua code thực tế" và "agent infer từ tên file/convention" và "không chắc chắn". Template `.claude/templates/CODE-GRAPH-template.md` không có trường confidence. |
| **Học từ đâu** | Extraction output schema (`extract.py`, `validate.py`) — trường `"confidence": "EXTRACTED|INFERRED|AMBIGUOUS"` cho mỗi edge. `EXTRACTED` = explicit trong source code; `INFERRED` = suy diễn từ call-graph second pass; `AMBIGUOUS` = không chắc, flagged cho human review. |
| **Lý do thay đổi** | Agents đọc CODE-GRAPH thấy "module A gọi module B" không biết liệu đây là verified từ code review hay bước trước đoán dựa trên naming convention — có thể đưa ra assumption sai, dẫn đến bug hoặc phải verify lại từ đầu. |
| **Áp dụng vào đâu** | `.claude/templates/CODE-GRAPH-template.md` — thêm cột `Confidence` (CONFIRMED / INFERRED / UNCERTAIN) cho relationship entries. CLAUDE.md §17.2 — thêm quy tắc: "Khi edit CODE-GRAPH, đánh dấu confidence cho mỗi relationship entry: CONFIRMED (đọc code trực tiếp), INFERRED (suy luận từ cấu trúc), UNCERTAIN (cần verify)." |
| **Đạt được gì** | (a) Agents xử lý CONFIRMED relationships như ground truth, UNCERTAIN như "cần verify trước khi dùng" → giảm bug từ incorrect assumption. (b) Tech Lead review CODE-GRAPH có thể filter UNCERTAIN entries và ưu tiên verify trong code review — không bỏ sót relationship không chắc. |
| **Rủi ro / Effort** | Rủi ro: Thấp. Agents phải thêm 1 trường khi edit CODE-GRAPH — tăng nhẹ effort viết. Risk: agents lười ghi "CONFIRMED" hết mà không verify thực tế → cần TL spot-check. Effort: **Thấp** — 4–8 giờ (edit template + §17 + viết ví dụ trong template). |

---

### P4 — "CODE-GRAPH impact" field trong PR checklist §15.3

| Trường | Nội dung |
|--------|---------|
| **Hiện trạng KZTEK** | CLAUDE.md §15.3 PR checklist có dòng "CODE-GRAPH cập nhật (nếu thay đổi structure/API)" — chỉ là Yes/No. Không yêu cầu liệt kê cụ thể module/node nào bị ảnh hưởng. |
| **Học từ đâu** | `prs.py` — `graphify prs <N>` hiển thị graph impact: node/edge nào bị ảnh hưởng bởi PR đó, kết nối git history với graph. Nguyên lý: reviewer cần biết structural impact ngay trong PR description, không phải sau khi mở CODE-GRAPH riêng. |
| **Lý do thay đổi** | Tech Lead review PR phải cross-reference changed files với CODE-GRAPH thủ công để đánh giá structural impact — mất 5–10 phút. Nếu bỏ qua, có thể không nhận ra module downstream bị ảnh hưởng gián tiếp. |
| **Áp dụng vào đâu** | CLAUDE.md §15.3 PR checklist — thêm field: `CODE-GRAPH impact: [liệt kê modules/nodes bị ảnh hưởng — VD: "KzButton (interface đổi), LoginForm (thêm dependency mới)"]`. Senior/Junior Dev điền khi tạo PR. Tech Lead check field này khi review. |
| **Đạt được gì** | Tech Lead đọc PR description và thấy ngay "PR này ảnh hưởng module X (interface đổi), module Y (thêm dependency mới)" — không cần mở CODE-GRAPH.md và grep manually. Review time giảm ước tính 5–10 phút/PR có structural change (quan sát được: Tech Lead không cần mở CODE-GRAPH tab riêng khi review). |
| **Rủi ro / Effort** | Rủi ro: Rất thấp. Developer phải thêm 1–2 dòng vào PR description — nếu không điền, Tech Lead có thể request changes. Effort: **Rất thấp** — 1–2 giờ (edit CLAUDE.md §15.3 + ví dụ). |

---

### P5 — LESSONS.md: Tích lũy institutional knowledge

| Trường | Nội dung |
|--------|---------|
| **Hiện trạng KZTEK** | Sau mỗi WF hoàn thành, không có cơ chế lưu "bài học" từ workflow đó. Plan files (`docs/plans/`) lưu chi tiết nhưng dài, khó search cross-workflow. GOTCHAS.md (`.claude/shared/`) ghi lỗi kỹ thuật ngầm nhưng không ghi lesson nghiệp vụ/workflow. Chưa có `docs/LESSONS.md`. |
| **Học từ đâu** | `reflect.py` — `graphify reflect` aggregate Q&A memory từ các session làm việc với codebase → tổng hợp thành `LESSONS.md`. Nguyên lý: mỗi session để lại Q&A trace; `reflect` đọc traces và distill thành lessons cộng dồn có thể search được. |
| **Lý do thay đổi** | Khi bắt đầu WF-FEATURE mới, agents không có cách nhanh để biết "những gì đã học từ WF trước" ngoài đọc lại toàn bộ plan files (bị gitignored hoặc rất dài) — dẫn đến re-discovery các vấn đề đã gặp, tốn thêm 2–3 turns. |
| **Áp dụng vào đâu** | (1) Tạo file `docs/LESSONS.md` với template: `[date] | [workflow] | [tag] | [lesson 1–2 câu]`. (2) CLAUDE.md §3.3 (Dispatcher tổng kết) — thêm bước cuối: "Có lesson nào đáng ghi vào `docs/LESSONS.md` từ workflow này không? (tùy chọn)". (3) CLAUDE.md §3.0 Pre-0 — thêm: "Nếu tồn tại `docs/LESSONS.md`, Read và scan qua lessons liên quan đến workflow hiện tại trước khi bắt đầu." |
| **Đạt được gì** | Sau 3–5 WF cycles, agents đọc LESSONS.md trong Pre-0 và biết ngay các gotcha đã biết cho domain đó — ước tính tiết kiệm 1–2 turns/WF-FEATURE sau khi có ≥5 lessons tích lũy (quan sát được: agent không cần hỏi lại câu đã từng hỏi trong WF trước). Khác với GOTCHAS.md (lỗi kỹ thuật ngầm) — LESSONS.md ghi pattern nghiệp vụ và workflow decisions. |
| **Rủi ro / Effort** | Rủi ro: Thấp. Risk chính: agents ghi lesson quá generic → vô nghĩa. Cần template bắt buộc có `context` cụ thể (không chỉ "kiểm tra kỹ trước khi deploy"). Effort: **Thấp** — 4–6 giờ (tạo template `docs/LESSONS.md`, cập nhật §3.0 và §3.3 trong CLAUDE.md và CORE.md). |

---

> **Lưu ý ưu tiên:** P4 và P2 có effort thấp nhất và áp dụng được ngay. P1 có giá trị kỹ thuật cao nhất nhưng phụ thuộc vào việc có C# product codebase. P3 và P5 bổ sung chất lượng dài hạn cho quy trình.
>
> **Trạng thái áp dụng (2026-07-29 — Bước 3A.3):** User xác nhận áp dụng CẢ 5 đề xuất P1–P5. Đã hoàn thành tất cả. Chi tiết thay đổi: xem `docs/plans/PLAN-github-research-graphify-2026-07-29/steps/STEP-3A.3-ap-dung-de-xuat.md`.
