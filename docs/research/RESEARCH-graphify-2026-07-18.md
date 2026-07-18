---
repo: Graphify-Labs/graphify
url: https://github.com/Graphify-Labs/graphify
slug: graphify
researched: 2026-07-18
researcher: github-repo-researcher
branch: research/graphify-2026-07-18
status: draft — awaiting user selection (Bước 3b hoàn thành)
---

# RESEARCH: Graphify-Labs/graphify

> **Mục đích tài liệu:** Phân tích kỹ thuật repo Graphify-Labs/graphify và đề xuất cải tiến áp dụng cho hệ thống KZTEK (agent workflow, KztekComponent, và các dự án iParking/iLocker/SDK).

---

## 1. Tổng quan repo

### Mục đích
Graphify là một **CLI tool / Python library / AI coding assistant skill** biến thư mục bất kỳ (code, docs, PDF, hình ảnh, video) thành một **đồ thị tri thức có thể truy vấn** (`graph.json`). Thay vì grep qua file, người dùng chạy `graphify query "câu hỏi"` để lấy subgraph phù hợp, hoặc `graphify path A B` để tìm đường nối ngắn nhất giữa 2 khái niệm.

### Đối tượng sử dụng
- Lập trình viên cần hiểu codebase lớn nhanh hơn
- AI coding assistants (Claude Code, Cursor, Codex, Gemini CLI, ...) cần context codebase mà không đọc toàn bộ file
- Tech Lead/Senior Dev cần phân tích impact khi đổi module

### Vấn đề giải quyết
| Vấn đề | Giải pháp graphify |
|--------|-------------------|
| AI assistant đọc quá nhiều file để hiểu codebase | Graph pre-built, query trả subgraph nhỏ |
| Không biết module nào bị ảnh hưởng khi sửa file X | `graphify affected X` — BFS trên graph |
| Vector store / embedding tốn tiền, không deterministic | Tree-sitter AST parse, không LLM, không token cost |
| Code graph bị lỗi thời sau mỗi commit | Git hooks tự update sau `git commit` |

### Độ trưởng thành (tại thời điểm nghiên cứu 2026-07-18)
- **PyPI:** `graphifyy` (có dấu `y` thừa — tên package PyPI khác tên repo)
- **Version:** 0.9.19 (pre-1.0, đang phát triển tích cực)
- **Tổ chức:** Graphify-Labs (YC S26 — Y Combinator batch Summer 2026)
- **License:** Xem `LICENSE` — đọc kỹ trước khi dùng trong sản phẩm thương mại
- **CHANGELOG.md:** 1 MB — rất nhiều release, dự án tích cực
- **Test suite:** 200+ file test, coverage rộng

---

## 2. Cấu trúc thư mục

```
graphify/                         ← Repo root
├── graphify/                     ← Python package chính
│   ├── __main__.py               ← Entry point CLI (~169 KB, lớn nhất)
│   ├── cli.py                    ← Lệnh CLI đầy đủ
│   ├── extractors/               ← Extractor riêng theo ngôn ngữ
│   │   ├── engine.py             ← Engine core (~231 KB)
│   │   ├── csharp.py             ← C# cross-file resolution
│   │   ├── go.py, rust.py, ...   ← 20+ ngôn ngữ có extractor riêng
│   │   └── base.py               ← Base class + _make_id()
│   ├── exporters/                ← Xuất đồ thị ra nhiều format
│   │   ├── html.py               ← Interactive graph.html (~25 KB)
│   │   └── graphdb.py            ← Xuất sang Neo4j / FalkorDB
│   ├── always_on/                ← Context snippet inject vào AI assistant
│   │   ├── claude-md.md          ← Inject vào CLAUDE.md
│   │   ├── agents-md.md          ← Inject vào AGENTS.md (Cursor, ...)
│   │   └── antigravity-rules.md  ← Inject vào Google Antigravity
│   ├── skills/                   ← Skill file theo từng platform
│   │   ├── claude/               ← Claude Code skill
│   │   ├── cursor/               ← Cursor skill
│   │   └── ...                   ← 15 platform khác
│   ├── validate.py               ← Schema validator trước build_graph
│   ├── security.py               ← URL guard, path guard, label sanitize
│   ├── affected.py               ← Impact analysis (BFS từ file đổi)
│   ├── hooks.py                  ← Git hooks: post-commit auto-update
│   ├── global_graph.py           ← Đồ thị toàn cục cross-repo
│   ├── cache.py                  ← Semantic + minHash dedup cache
│   ├── watch.py                  ← File system watcher
│   └── serve.py                  ← MCP stdio/HTTP server
├── tools/skillgen/               ← Skill generator: 1 template → 15 platform
│   ├── gen.py                    ← Script sinh skill file
│   └── platforms.toml            ← Cấu hình từng platform
├── tests/                        ← 200+ test file, 1 file / module
├── docs/superpowers/             ← Tài liệu tính năng nâng cao
├── worked/                       ← Ví dụ đã chạy thật (FastAPI, httpx, ...)
├── ARCHITECTURE.md               ← Mô tả pipeline + module responsibilites
└── BENCHMARKS.md                 ← So sánh hiệu suất với mem0, supermemory
```

---

## 3. Phân tích kỹ thuật

### 3.1 Pipeline một chiều, không trạng thái chung

```
detect()  →  extract()  →  build_graph()  →  cluster()  →  analyze()  →  report()  →  export()
```

**Pattern đáng chú ý:** Mỗi stage là **1 hàm thuần túy** trong module riêng, giao tiếp qua Python dict và `nx.Graph`. Không có shared state, không có side effect ngoài thư mục `graphify-out/`. Pattern này từ `ARCHITECTURE.md` — mỗi module dễ test độc lập và dễ thay thế.

### 3.2 Schema extraction chuẩn

Mọi extractor đều trả về cùng schema (`validate.py` enforce trước khi tiếp tục pipeline):

```json
{
  "nodes": [
    {"id": "...", "label": "...", "source_file": "path", "source_location": "L42", "file_type": "code"}
  ],
  "edges": [
    {"source": "id_a", "target": "id_b", "relation": "calls|imports|uses|...", "confidence": "EXTRACTED|INFERRED|AMBIGUOUS", "source_file": "..."}
  ]
}
```

**Pattern đáng chú ý:** `confidence` field phân biệt rõ `EXTRACTED` (mối quan hệ rõ trong source) vs `INFERRED` (suy luận) vs `AMBIGUOUS` (không chắc). Không đánh đồng tất cả mối quan hệ như nhau.

### 3.3 C# extractor với cross-file resolution

File `graphify/extractors/csharp.py` và `graphify/extractors/resolution.py` cung cấp:
- Build index `(namespace, class_name) → node_id` từ toàn bộ `.cs` files
- Resolve cross-file type references (kế thừa, generic constraints, method calls)
- Loại nested type, operator overload khỏi resolution để tránh noise

Đây là **trực tiếp liên quan đến KZTEK** — KztekComponent là thư viện C# WinForms với 28+ custom controls, nhiều kế thừa và cross-file reference.

### 3.4 Affected analysis — impact analysis từ file đổi

File `graphify/affected.py` dùng BFS/DFS trên đồ thị để trả lời: "nếu tôi đổi `KzButton.cs`, file/class nào khác bị ảnh hưởng?"

```python
DEFAULT_AFFECTED_RELATIONS = (
    "calls", "indirect_call", "references", "imports",
    "re_exports", "inherits", "extends", "implements",
    "uses", "mixes_in", "embeds",
)
```

Giao diện CLI: `graphify affected KzButton.cs` → danh sách node bị ảnh hưởng, kèm `depth` và `via_relation`.

### 3.5 Git hooks — auto-update sau commit

`graphify/hooks.py` inject vào `.git/hooks/post-commit` một script Bash:
- **Probe 3-level** để tìm đúng Python interpreter (pinned, từ file `.graphify_python`, từ PATH shebang) — quan trọng vì git GUI clients và CI thường có PATH khác terminal
- Chạy detached (`nohup`) để không block `git commit`
- Dùng `importlib.util.find_spec` thay vì import toàn bộ package khi probe (tránh AV scan gây chậm)

### 3.6 Always-on context injection

Thư mục `graphify/always_on/` chứa snippet Markdown nhỏ được inject vào context của AI assistant:
- `claude-md.md` → inject vào `CLAUDE.md`
- `agents-md.md` → inject vào `AGENTS.md` của Cursor
- Nội dung: hướng dẫn agent "trước khi trả lời câu hỏi về codebase, chạy `graphify query` thay vì đọc source files"

### 3.7 Skill generator (1 template → 15 platform)

`tools/skillgen/gen.py` + `platforms.toml` sinh ra skill file cho 15 platform từ một source template. Mỗi platform có cấu hình riêng (tên lệnh, format file, vị trí cài đặt). Tránh duplicate nội dung khi cần hỗ trợ nhiều AI assistant.

### 3.8 Security module

`graphify/security.py` xử lý mọi external input:
- URL → `validate_url()` (chỉ http/https) + block SSRF (AWS metadata, link-local, CGN)
- Fetched content → size cap 50 MB binary / 10 MB text
- Graph file paths → phải nằm trong `graphify-out/`
- Node labels → strip control chars, HTML-escape, cap 256 chars
- Memory bomb guard → reject `graph.json` > 512 MiB trước khi parse

---

## 4. Hiện trạng KZTEK (Bắt buộc — đối chiếu từng điểm)

### 4.1 Code graph hiện tại — `code-graph/CODE-GRAPH.md`

**Đọc tại:** `/home/user/claude/code-graph/CODE-GRAPH.md` (version 1.0, cập nhật 2026-07-12)

**Thực trạng:**
- Là file Markdown **tĩnh, viết tay** — không tự sinh, không tự cập nhật
- Liệt kê thư mục, module, controls theo dạng bảng và mô tả văn xuôi
- **Không có khả năng truy vấn:** không thể hỏi "class nào kế thừa `KzButton`?" hay "thay đổi `KzDataGrid` ảnh hưởng những đâu?"
- **Phải cập nhật thủ công** mỗi khi thêm/xóa/đổi module, API, schema (theo CLAUDE.md §17.2)
- Quy tắc CLAUDE.md §17: "Cập nhật `.md` mà không xuất lại `.pdf` = CHƯA HOÀN THÀNH" — tạo thêm gánh nặng cho developer
- **Dễ lỗi thời** vì phụ thuộc vào discipline của agent/developer cập nhật sau mỗi thay đổi

**Không có:**
- Query capability
- Affected/impact analysis
- Auto-update sau git commit
- Confidence labels cho mối quan hệ
- Traversal (tìm path giữa 2 khái niệm)

### 4.2 KztekComponent — thư viện C# WinForms

**Đọc tại:** CODE-GRAPH.md mục "KztekComponent — Controls có sẵn"

**Thực trạng:**
- 28 custom controls (`KzButton`, `KzTextBox`, `KzDataGrid`, v.v.)
- Cross-file inheritance (controls kế thừa lẫn nhau), namespace riêng
- **Không có tool tự động phân tích relationship giữa các control**
- Khi một control thay đổi, agent/developer phải đọc từng file để đánh giá impact
- Không có bản đồ dependency giữa 28 controls

### 4.3 Agent skill/command — `.claude/commands/`

**Đọc tại:** `.claude/commands/` (kztek-brand-info.skill, verify-pr.md, scope-check.md, ...)

**Thực trạng:**
- Skill files chỉ dành cho Claude Code — không có cơ chế sinh tự động cho platform khác
- Nếu KZTEK cần hỗ trợ thêm platform (Cursor, Kiro, Gemini CLI), phải viết lại từng skill thủ công
- Không có tool tương tự `skillgen` của graphify

### 4.4 Impact analysis trong PR review

**Đọc tại:** CLAUDE.md §4 WF-FEATURE Bước 10 / WF-BUGFIX Bước 3

**Thực trạng:**
- Tech Lead review PR dựa trên diff — không có tool hỗ trợ phân tích graph-based impact
- Nếu Senior Dev sửa `KzButton.cs`, Tech Lead phải đọc code để biết `KzCombobox.cs` hay form nào dùng nó
- Không có `graphify affected` tương đương

---

## 5. So sánh trực tiếp — Repo nguồn vs Hiện trạng KZTEK

| Chiều so sánh | Graphify (repo nguồn) | KZTEK (hiện tại) |
|---|---|---|
| Code graph | Auto-generated từ AST, queryable `graph.json` | Static Markdown, viết tay |
| Cập nhật graph | Git hook post-commit tự động | Thủ công, dễ lỗi thời |
| Query codebase | `graphify query / path / explain` | Không có — phải đọc file |
| Impact analysis | `graphify affected <file>` — BFS trên graph | Thủ công trong Tech Lead review |
| Confidence của relationship | `EXTRACTED / INFERRED / AMBIGUOUS` | Không phân biệt |
| C# support | Extractor với namespace-aware cross-file resolution | CODE-GRAPH.md static, liệt kê thủ công |
| Multi-platform skill | 1 template → 15 platform qua `skillgen` | Chỉ Claude Code, viết tay |
| Security validation | Module riêng: URL, path, label, size cap | Không áp dụng (agent framework, không xử lý input ngoài) |
| Schema validation | `validate.py` enforce trước pipeline | Không có schema validation cho agent artifact |

---

## 6. Bảng đề xuất cải tiến

> Dựa trên phần So sánh (§5). Mỗi đề xuất PHẢI được user chọn riêng ở Bước 4 trước khi áp dụng.

| # | Đề xuất | Hiện trạng KZTEK | Học từ đâu | Lý do thay đổi | Áp dụng vào đâu trong KZTEK | Đạt được gì | Rủi ro / Effort |
|---|---------|-----------------|-----------|----------------|------------------------------|-------------|----------------|
| **G1** | **Cài graphify vào KztekComponent — thay thế CODE-GRAPH.md tĩnh bằng đồ thị auto-generated** | `code-graph/CODE-GRAPH.md` v1.0 — viết tay, phải update thủ công sau mỗi PR, không query được | `graphify/extractors/csharp.py` + `graphify/extractors/resolution.py` — parse C# AST qua tree-sitter, build đồ thị namespace-aware cross-file | CODE-GRAPH.md đòi hỏi discipline cao: CLAUDE.md §17.2 liệt kê 7 trigger bắt buộc update — trên thực tế agent dễ bỏ sót, dẫn đến bản đồ lỗi thời. Không có cách query "class nào inherit KzButton?" | `KztekComponent/` — chạy `graphify .` một lần, sau đó dùng `graphify query / path / affected` trong workflow review | Agents có thể chạy `graphify query "KzButton inheritance"` thay vì đọc 28 file `.cs`; Tech Lead có thể chạy `graphify affected KzButton.cs` để xem danh sách class/form bị ảnh hưởng ngay trong review session | Effort thấp: `uv tool install graphifyy && graphify .` trong `KztekComponent/`. Rủi ro thấp: chỉ tạo `graphify-out/` mới, không sửa code. Phụ thuộc Python 3.10+. |
| **G2** | **Cài git hook graphify cho KztekComponent — tự động refresh đồ thị sau mỗi commit** | Không có auto-update — CLAUDE.md §17.2 yêu cầu dev tự cập nhật CODE-GRAPH.md + xuất PDF sau mỗi PR | `graphify/hooks.py` — `graphify hook install` chèn script vào `.git/hooks/post-commit`, chạy detached (không block commit), probe 3 level tìm Python | Không có git hook → dev quên cập nhật CODE-GRAPH.md → graph lỗi thời → agent đọc context sai → review thiếu chính xác. Hiện tại mỗi PR phải nhớ update thủ công và xuất PDF thêm | `.git/hooks/` trong `KztekComponent/` (hoặc root workspace nếu áp dụng G1) | CODE-GRAPH (graphify-out/graph.json) tự động cập nhật sau mỗi `git commit` — không cần bước thủ công; loại bỏ 1 nguyên nhân gây drift giữa code và tài liệu | Cần G1 trước. Effort thấp: 1 lệnh `graphify hook install`. Rủi ro rất thấp: hook chạy background, fail silently nếu Python không tìm thấy. |
| **G3** | **Thêm bước `graphify affected` vào checklist Tech Lead review PR** | Tech Lead review thủ công: đọc diff, tự phán đoán impact — không có tool hỗ trợ graph-based impact | `graphify/affected.py` + CLI `graphify affected <file>` — BFS trên graph, trả danh sách node bị ảnh hưởng kèm depth và loại quan hệ | Khi PR sửa `KzDataGrid.cs` hoặc một control base, Tech Lead không biết nhanh có bao nhiêu form/control downstream sử dụng — phải đọc từng file. Bỏ sót → merge code breaking change mà không biết | `.claude/agents/tech-lead.md` — thêm bước checklist: "nếu PR sửa file C# trong KztekComponent, chạy `graphify affected <file>` và ghi kết quả vào PR comment" | Thay vì 15-30 phút đọc code để map impact, Tech Lead chạy 1 lệnh và có danh sách đầy đủ ngay lập tức; giảm rủi ro merge thay đổi breaking không phát hiện ra | Cần G1 (graphify-out/graph.json cần tồn tại). Effort thấp: chỉ cập nhật CLAUDE.md / tech-lead.md thêm 1 bước checklist. |
| **G4** | **Áp dụng confidence labels (EXTRACTED / INFERRED / AMBIGUOUS) vào CODE-GRAPH.md và agent dependency docs** | Bảng trong CODE-GRAPH.md liệt kê relationships ("Agent A gọi Agent B") không phân biệt rõ "khai báo tường minh" vs "suy luận từ workflow" | `graphify/validate.py` fields `confidence: EXTRACTED|INFERRED|AMBIGUOUS` — mỗi edge trong graph đều có nhãn confidence | Không biết mối quan hệ nào là cứng (code/config tường minh) hay suy luận — khi cần debug routing sai hoặc refactor chain, không có cơ sở để quyết định relationship nào an toàn để thay đổi | `code-graph/CODE-GRAPH.md` cột "Ghi chú" / `CLAUDE.md` §1 org chart / `.claude/agents/*.md` mục "Phụ thuộc" — thêm nhãn `[EXTRACTED]` hoặc `[INFERRED]` bên cạnh mỗi mối quan hệ | Khi đọc CODE-GRAPH, developer phân biệt ngay "relationship này từ code/config rõ ràng" vs "relationship này từ suy luận của agent" — giảm thời gian phân tích khi debug routing issue | Không cần G1. Effort thấp: cập nhật văn bản trong CODE-GRAPH.md + một số agent file. Không cần tool mới. |
| **G5** | **Tạo skill generator (tương tự `tools/skillgen`) để sinh skill file KZTEK cho nhiều platform** | `.claude/commands/*.md` viết tay, chỉ target Claude Code. Nếu KZTEK cần hỗ trợ Cursor, Kiro, Gemini CLI thì phải copy-paste và sửa thủ công từng file | `tools/skillgen/gen.py` + `platforms.toml` — 1 template Markdown + config TOML → sinh skill cho 15 platform với naming convention riêng từng platform | Hiện tại KZTEK chỉ phục vụ Claude Code. Nếu mở rộng sang platform khác (Cursor, Kiro, Gemini CLI đang phổ biến), phải duplicate skill definitions — dễ drift khi update một skill mà quên update bản tương ứng | `scripts/` — tạo `scripts/skillgen_kztek.py` + `scripts/platforms-kztek.toml` để sinh từ `.claude/commands/*.md` sang format của platform khác | Khi thêm hoặc cập nhật 1 skill, chỉ sửa 1 file source rồi chạy script — tất cả platform được cập nhật đồng bộ; loại bỏ risk drift giữa các bản skill | Cần xác định KZTEK có kế hoạch mở rộng sang platform khác không. Effort trung bình: viết script Python ~200-300 dòng + platforms.toml. Có thể defer nếu chưa cần. |

---

## 7. Thông tin repo

| Mục | Giá trị |
|-----|---------|
| Tên | `Graphify-Labs/graphify` |
| PyPI | `graphifyy` (0.9.19) |
| License | Xem `LICENSE` (đọc trước khi dùng thương mại) |
| Hoạt động | Tích cực — CHANGELOG.md ~1 MB |
| Tổ chức | Graphify-Labs (YC S26) |
| Stars/Fork | Xem repo trực tiếp — YC-backed, trending |
| Python | >= 3.10 |
| Dep chính | networkx, tree-sitter, rapidfuzz |

---

## 8. Trạng thái áp dụng đề xuất

| # | Đề xuất | Trạng thái |
|---|---------|-----------|
| G1 | Cài graphify vào KztekComponent | ⬜ Chờ user chọn (Bước 4) |
| G2 | Git hook auto-refresh | ⬜ Chờ user chọn (Bước 4) |
| G3 | Thêm `graphify affected` vào Tech Lead checklist | ⬜ Chờ user chọn (Bước 4) |
| G4 | Confidence labels trong CODE-GRAPH + agent docs | ⬜ Chờ user chọn (Bước 4) |
| G5 | Skill generator cho multi-platform | ⬜ Chờ user chọn (Bước 4) |

---

*Nghiên cứu bởi: GitHub Repo Researcher (L4, claude-sonnet-4-6)*
*Nhánh: research/graphify-2026-07-18*
*Ngày: 2026-07-18*
