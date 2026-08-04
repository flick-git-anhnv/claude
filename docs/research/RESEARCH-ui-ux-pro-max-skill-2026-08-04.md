---
title: "Báo cáo nghiên cứu — nextlevelbuilder/ui-ux-pro-max-skill"
repo_url: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
research_date: 2026-08-04
researcher: github-repo-researcher
branch: research/ui-ux-pro-max-skill-2026-08-04
mode: pending — chờ user xác nhận Mode A/B
status: draft — phân tích Bước 3 (chưa có đề xuất)
---

# Nghiên cứu repo: nextlevelbuilder/ui-ux-pro-max-skill

> Bước 3 WF-GITHUB-RESEARCH — Phân tích trung lập. Đề xuất cải tiến KZTEK (Mode A) hoặc giải thích nguyên lý (Mode B) sẽ được thực hiện sau khi user xác nhận mục đích.

---

## 1. Tổng quan repo

**Tên:** UI UX Pro Max  
**URL:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill  
**Phiên bản phân tích:** v2.11.0 (branch main, đang active development)  
**License:** MIT (có thể dùng trong sản phẩm thương mại)  
**Tác giả:** NextLevelBuilder (nextlevelbuilder.io)  
**Độ trưởng thành:** Repository đang active, có npm package `ui-ux-pro-max-cli`, star history tăng đều (badge hiển thị), hỗ trợ 19 AI platform; bản v2.0 giới thiệu Design System Generator là tính năng flagship.

### Mục đích cốt lõi

UI UX Pro Max là một **AI coding skill** cung cấp "design intelligence" — khi AI assistant nhận yêu cầu xây dựng UI/UX, thay vì tự suy đoán style/màu sắc/typography ngẫu nhiên, skill này cung cấp:

1. **Database có cấu trúc** chứa 84 UI styles, 192 color palettes, 74 font pairings, 98 UX guidelines, 25 chart types, 161 reasoning rules — tất cả dưới dạng CSV có thể tìm kiếm.
2. **Search engine BM25** để AI query database theo domain (style, color, typography, chart, landing, ux...) và trả về kết quả ranked — không phải hardcode trong prompt.
3. **Design System Generator** phân tích loại sản phẩm (VD: "beauty spa wellness") và tự động chọn pattern + style + palette + typography + effects phù hợp dựa trên 161 industry-specific reasoning rules.
4. **Stack-specific guidelines** cho 22 framework bao gồm React, Next.js, Avalonia, WPF, WinUI, Flutter, SwiftUI, Angular, Vue, Laravel...

### Vấn đề giải quyết

AI assistant khi xây dựng UI thường mặc định về các lựa chọn ngẫu nhiên: "AI purple gradient", centered hero over dark mesh, Inter font + slate-900, generic glassmorphism. Repo này cung cấp dữ liệu có cấu trúc và reasoning engine để AI agent đưa ra lựa chọn design có căn cứ, phù hợp với loại sản phẩm và ngành, thay vì đoán mò.

---

## 2. Cấu trúc thư mục

```
ui-ux-pro-max-skill/
├── src/ui-ux-pro-max/              # Nguồn gốc (source of truth)
│   ├── data/                       # 14 file CSV chứa database design
│   │   ├── products.csv            # 192 loại sản phẩm + mapping sang style/color
│   │   ├── styles.csv              # 84 UI styles + keywords, effects, framework compat.
│   │   ├── colors.csv              # 192 color palettes theo product type
│   │   ├── typography.csv          # 74 font pairings + Google Fonts import code
│   │   ├── landing.csv             # 34 landing page patterns + CTA strategies
│   │   ├── charts.csv              # 25 chart types + accessibility notes
│   │   ├── ux-guidelines.csv       # 98 UX best practices + anti-patterns
│   │   ├── ui-reasoning.csv        # 161 industry-specific reasoning rules
│   │   ├── motion.csv              # GSAP animation snippets theo intensity tier
│   │   ├── icons.csv               # Icon recommendations + import code
│   │   ├── google-fonts.csv        # Google Fonts lookup với metadata
│   │   ├── react-performance.csv   # React/Next.js performance patterns
│   │   ├── app-interface.csv       # App UI guidelines (iOS/Android/RN/Flutter)
│   │   └── stacks/                 # 22 file CSV mỗi stack cụ thể
│   │       ├── avalonia.csv        # 29 guidelines Avalonia XAML + MVVM
│   │       ├── wpf.csv             # WPF-specific guidelines
│   │       ├── react.csv           # React-specific guidelines
│   │       └── ...                 # 19 stack khác
│   ├── scripts/
│   │   ├── search.py               # CLI entry point — BM25 search + design system CLI
│   │   ├── core.py                 # BM25 + regex hybrid search engine
│   │   └── design_system.py        # Design system generator (5 parallel searches → reasoning)
│   └── templates/
│       ├── base/
│       │   ├── skill-content.md    # Template nội dung skill (platform-agnostic)
│       │   └── quick-reference.md  # Template quick reference cho AI
│       └── platforms/              # Config render template cho từng platform
├── cli/                            # CLI installer (npm package ui-ux-pro-max-cli)
│   ├── src/commands/init.ts        # Install command — generate files từ template
│   └── assets/                     # Bundled copy của src/ (~564KB)
├── skill.json                      # Metadata: version, platforms, install command
├── CLAUDE.md                       # Hướng dẫn cho AI khi làm việc với repo này
└── .claude/skills/ui-ux-pro-max/   # Claude Code skill (SKILL.md + data + scripts)
```

**Quan trọng về Sync Rules:** Không có symlink trong repo (git-on-Windows xử lý symlink không tốt). Mọi bản copy (`cli/assets/`, `.claude/skills/`) đều là file thực sự được sync bởi script `cli/scripts/sync-assets.mjs`, không phải symlink.

---

## 3. Phân tích kỹ thuật

### 3.1 Search Engine: BM25 + Regex Hybrid

**File:** `src/ui-ux-pro-max/scripts/core.py`

Search engine được xây dựng từ đầu (không dùng thư viện BM25 ngoài) bằng Python standard library:
- **BM25** (Best Match 25): thuật toán ranking văn bản probabilistic, ưu tiên document có term xuất hiện nhiều (TF) nhưng giảm ảnh hưởng khi document quá dài (IDF).
- **Regex matching**: kết hợp song song với BM25 để xử lý chính xác exact-match (VD: query "glassmorphism" khớp chính xác keyword).
- **Auto domain detection**: khi không chỉ định `--domain`, engine phân tích query để tự detect domain (VD: "dark mode" → domain `style`), có runner-up domain.
- **No external dependencies**: toàn bộ search logic dùng Python standard library (`csv`, `re`, `math`, `collections`) — chạy được trên mọi môi trường có Python 3.

```python
# CSV_CONFIG trong core.py — định nghĩa domain và column nào để search/output
CSV_CONFIG = {
    "style": {
        "file": "styles.csv",
        "search_cols": ["Style Category", "Keywords", "Best For", "Type", "AI Prompt Keywords"],
        "output_cols": ["Style Category", "Type", "Keywords", ..., "Implementation Checklist"]
    },
    "product": { "file": "products.csv", ... },
    # ... 12 domain khác
}
```

Pattern đáng chú ý: mỗi domain được cấu hình riêng — `search_cols` (cột nào được search), `output_cols` (cột nào được trả về). Điều này cho phép mở rộng thêm domain mà không sửa logic engine.

### 3.2 Design System Generator: Multi-Domain Search + Reasoning

**File:** `src/ui-ux-pro-max/scripts/design_system.py`

Khi gọi `--design-system`, engine thực hiện 5 search song song trên 5 domain (product, style, color, landing, typography), sau đó áp dụng **161 reasoning rules** từ `ui-reasoning.csv` để tổng hợp ra design system hoàn chỉnh:

```
Luồng hoạt động:
1. Query "beauty spa wellness"
2. → Search 5 domain đồng thời (product, style×3, color×2, landing×2, typography×2)
3. → Load ui-reasoning.csv → tìm rule khớp product type "Beauty/Spa"
4. → Merge kết quả: rule + search results → anti-patterns + checklist
5. → Output ASCII table hoặc Markdown với đủ: pattern, style, colors, typography, effects, AVOID list, pre-delivery checklist
```

Điểm nổi bật: **AVOID list** (anti-patterns) trong mỗi rule — ví dụ rule cho banking platform có "AI purple/pink gradients" trong danh sách avoid. Đây là dữ liệu có cấu trúc, không phải heuristic tự sinh của AI.

### 3.3 Design Dials: 3 tham số điều chỉnh kết quả

Repo giới thiệu 3 "design dials" có thể truyền qua CLI:
- `--variance 1-10`: 1 = centered/minimal, 10 = bold/asymmetric (biases style selection)
- `--motion 1-10`: 1 = subtle, 10 = complex (chọn GSAP snippet từ motion.csv)
- `--density 1-10`: 1 = spacious, 10 = dense/dashboard (override spacing-scale tokens)

Khi không set, engine hoạt động như trước (query-based). Khi set, các dial "bias" kết quả bằng cách ưu tiên style có từ khóa phù hợp. Concept này tương đồng với `DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY` trong `design-taste-frontend.md` của KZTEK (skill được thêm vào sau).

### 3.4 Stack-Specific Guidelines: Avalonia CSV đáng chú ý

**File:** `src/ui-ux-pro-max/data/stacks/avalonia.csv`

Repo chứa 29 Avalonia-specific guidelines có cấu trúc đầy đủ (No, Category, Guideline, Description, Do, Don't, Code Good, Code Bad, Severity, Docs URL), bao gồm:
- XAML: compiled bindings với x:DataType, #name shorthand thay ElementName, PHẢI set `AvaloniaUseCompiledBindingsByDefault`
- Styling: CSS-like selectors, pseudoclass selectors (`:pointerover`, `:pressed`), nesting selectors
- Controls: DataGrid yêu cầu NuGet package riêng + StyleInclude trong App.axaml, TreeDataTemplate thay HierarchicalDataTemplate (WPF only)
- Data Binding: INotifyPropertyChanged, ObservableCollection, FuncValueConverter
- Architecture: MVVM với ReactiveUI/CommunityToolkit, ViewLocator, DI với Microsoft.Extensions

Đây là dữ liệu structured, searchable — AI có thể query "TreeView" và nhận Do/Don't code cụ thể thay vì phải nhớ trong context.

### 3.5 Persist Design System: Master + Overrides Pattern

Tính năng v2.0 cho phép lưu design system vào file để tái sử dụng xuyên session:

```bash
python3 scripts/search.py "SaaS dashboard" --design-system --persist -p "MyApp"
# → Tạo design-system/MASTER.md (global source of truth)

python3 scripts/search.py "..." --design-system --persist -p "MyApp" --page "dashboard"
# → Tạo design-system/pages/dashboard.md (page-specific overrides)
```

**Cơ chế hierarchical retrieval:** AI đọc MASTER.md trước, sau đó check page override. Override chỉ ghi chép sự khác biệt so với MASTER. Pattern này tương tự "global config + project override" đã biết trong git.

### 3.6 Cài đặt đa platform: CLI + Claude Marketplace

Repo cung cấp 2 cách cài đặt:
1. **CLI npm** (`npm install -g ui-ux-pro-max-cli` + `uipro init --ai claude`): tạo file skill theo đúng cấu trúc platform. Không dùng symlink.
2. **Claude Marketplace** (`/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill`): cài trực tiếp trong Claude Code.

Skill được cài vào `.claude/skills/ui-ux-pro-max/` (Claude Code), `.cursor/skills/`, `.windsurf/skills/`... tùy platform.

---

## 4. Điểm mạnh / Điểm yếu

### Điểm mạnh

| # | Điểm mạnh | Chi tiết |
|---|-----------|---------|
| 1 | **Database có cấu trúc, searchable** | 14 CSV file = 84 styles + 192 palettes + 74 fonts + 98 UX guidelines... — AI query thay vì đoán. |
| 2 | **Zero external dependencies** | Search engine dùng Python standard library — deploy được mọi môi trường. |
| 3 | **Reasoning rules có AVOID list** | 161 rules với anti-patterns cụ thể cho từng ngành (banking, healthcare, beauty spa...). |
| 4 | **Avalonia support đầy đủ** | 29 guidelines có Do/Don't + code example + docs URL — relevance cao với KZTEK. |
| 5 | **Design dials** | 3 tham số variance/motion/density định lượng hoá lựa chọn design thay vì mô tả mơ hồ. |
| 6 | **Persist design system** | Master + Overrides pattern giữ nhất quán xuyên session. |
| 7 | **Multi-platform** | 19 AI platforms, 22 stacks, npm CLI + Marketplace. |

### Điểm yếu

| # | Điểm yếu | Chi tiết |
|---|----------|---------|
| 1 | **Python required** | Cần Python 3.x — nếu environment không có Python, AI phải fall back vào Quick Reference tĩnh. |
| 2 | **CLI phải chạy thủ công** | Không có watcher/daemon — AI phải chủ động gọi `python3 scripts/search.py` trước mỗi task UI. |
| 3 | **Data chủ yếu cho Web/Mobile** | Dù có Avalonia CSV, phần lớn data (styles, colors, landing...) thiên về web/mobile, ít pattern desktop-native cụ thể. |
| 4 | **Premium tier** | Tính năng Brand Identity, Logo Design, Corporate Identity Program nằm trong premium (trả phí). |
| 5 | **Không có KZTEK brand** | Colors/typography/spacing của KZTEK phải cấu hình riêng, không có trong database sẵn. |

---

## 5. Hiện trạng KZTEK

Khu vực tương ứng trong KZTEK được kiểm tra qua 2 file:

### 5.1 `ui-ux-designer.md` (agent)

**File:** `.claude/agents/ui-ux-designer.md`

Agent UI/UX Designer của KZTEK hiện tại là một agent **quy trình** (process-oriented) — mô tả vai trò, quy trình (wireframe → mockup → hand-off), và format artifact. Không có:
- Database styles/colors/typography
- Reasoning engine cho từng loại sản phẩm
- Anti-pattern library cụ thể
- Stack-specific guidelines

Khi agent này cần đưa ra lựa chọn design, nó phụ thuộc hoàn toàn vào model LLM để suy đoán — không có structured data hỗ trợ.

### 5.2 `design-taste-frontend.md` (skill)

**File:** `.claude/commands/design-taste-frontend.md`

Skill này là **bộ quy tắc prescriptive** phong phú (508+ dòng đã đọc) dành cho landing page, portfolio, redesign với stack React/Next.js/Tailwind. Bao gồm:
- Brief Inference (Section 0): đọc context trước khi code
- Design Dials (Section 1): `DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY`
- Design System Map (Section 2): khi nào dùng Fluent, Carbon, shadcn/ui...
- Nhiều anti-pattern cụ thể: The Lila Rule (no AI purple), Serif Discipline, Eyebrow Restraint...

**Nhận xét:** Skill này đã được xây dựng công phu và bao phủ tốt use-case **web landing page/portfolio**. Tuy nhiên nó là hardcoded rules trong Markdown, không phải searchable database — AI không thể query "typography cho fintech" mà phải đọc toàn bộ file. Ngoài ra, nó **không bao gồm**:
- Desktop UI (WinForms, Avalonia) — KZTEK dùng nhiều
- Non-web contexts (JavaFX, WPF, Uno Platform)
- Industry-specific reasoning (161 rules)

### 5.3 `kztek-brand-info.md` (skill)

**File:** `.claude/commands/kztek-brand-info.md` — chứa màu brand KZTEK (#251C53, #F05922...), logo guidelines, quy tắc áp dụng. Đây là "palette KZTEK" nhưng không kết nối với database styles/typography của bất kỳ tool nào.

---

## 6. So sánh repo nguồn — hiện trạng KZTEK

| Khía cạnh | ui-ux-pro-max-skill | KZTEK hiện tại |
|-----------|-------------------|---------------|
| **Nguồn design decisions** | Database CSV có cấu trúc, searchable (BM25) | Hardcoded rules trong Markdown + LLM suy đoán |
| **Industry reasoning** | 161 rules có AVOID list theo ngành | Không có — agent tự suy |
| **Color palettes** | 192 palettes theo product type | KZTEK brand colors (`kztek-brand-info.md`), không map theo product type |
| **Typography** | 74 font pairings + Google Fonts import | Không có database, LLM chọn tự do |
| **UI styles** | 84 styles với framework compat. table | Liệt kê trong `design-taste-frontend.md` (web-only) |
| **Avalonia guidelines** | 29 Do/Don't có code example + docs URL | Nằm trong lessons (`C:\Users\nguye\.claude\lessons\avalonia\`) — không searchable từ AI |
| **Anti-patterns** | Embedded trong data, searchable | Hardcoded trong `design-taste-frontend.md` (web only) |
| **Design dials** | 3 dials: variance/motion/density CLI params | 3 dials trong `design-taste-frontend.md` nhưng chỉ cho web landing page |
| **Persist design system** | Master + Overrides pattern | Không có — mỗi session bắt đầu lại |
| **Scope** | Web + Mobile + Desktop (Avalonia/WPF/WinUI/JavaFX...) | Web (landing page/portfolio): `design-taste-frontend.md`; Desktop: không có skill tương đương |
| **Stack-specific** | 22 stacks có file CSV riêng | Không có structured guidelines theo stack |

---

## 7. Thông tin repo

| Thông tin | Chi tiết |
|-----------|---------|
| License | MIT — tự do dùng, fork, tích hợp vào project thương mại |
| Version | 2.11.0 (stable) |
| Activity | Active development — commits đều đặn, semantic-release automation |
| Platform support | 19 AI platforms, npm CLI |
| Python requirement | Python 3.x standard library only, no pip install |
| Install | `npm install -g ui-ux-pro-max-cli && uipro init --ai claude` |
| Homepage | https://uupm.cc |
| Premium | Có bản premium (Brand Identity, Logo Design, CIP) — không xác định giá công khai |

---

## 8. Ghi chú tiến độ

- [x] Bước 1: Tạo nhánh `research/ui-ux-pro-max-skill-2026-08-04`
- [x] Bước 2: Clone về scratchpad, đọc README, CLAUDE.md, core.py, design_system.py, avalonia.csv, skill.json, template structure
- [x] Bước 3: Viết phân tích trung lập (file này)
- [ ] Bước 3*: Chờ user xác nhận Mode A (đề xuất áp dụng KZTEK) hay Mode B (học tập/tham khảo)

---

> **Cần user xác nhận:** Bước tiếp theo phụ thuộc vào mục đích nghiên cứu. Xem phần "Bước tiếp theo" ở cuối báo cáo gốc.
