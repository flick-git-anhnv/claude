---
description: >
  UI/UX design intelligence skill — gọi khi cần quyết định về style, màu sắc, typography,
  pattern layout, accessibility, chart type, hay stack-specific guidelines (Avalonia, WPF,
  React, Next.js, Flutter, SwiftUI...). Cung cấp database 84 styles, 192 palettes, 74 font
  pairings, 98 UX guidelines, 161 reasoning rules trên 22 stacks — không suy đoán, query data.
---

# Skill: UI UX Pro Max — Design Intelligence

> Skill được cài từ repo [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (v2.11.0, MIT License).
> Files data + scripts: `.claude/skills/ui-ux-pro-max/`
> Xem workflow đầy đủ: `.claude/skills/ui-ux-pro-max/SKILL.md`

---

## Khi nào gọi skill này

Gọi **bất kỳ khi nào** task liên quan đến:
- Xây dựng UI mới (page, component, form, dashboard, landing page)
- Chọn style / màu / font / spacing cho project
- Review UI về accessibility, UX, consistency
- Implement animation / chart / icon
- Viết code UI theo framework cụ thể (Avalonia, WPF, React, Flutter, SwiftUI...)

**Bỏ qua** khi task chỉ là backend/logic, API design, infra, hoặc non-visual script.

---

## Lệnh cơ bản (chạy từ thư mục gốc project)

### Query domain cụ thể

```bash
# Tìm style phù hợp
python .claude/skills/ui-ux-pro-max/scripts/search.py "saas dashboard modern" --domain style

# Tìm palette theo loại sản phẩm
python .claude/skills/ui-ux-pro-max/scripts/search.py "fintech banking" --domain color

# Tìm font pairing
python .claude/skills/ui-ux-pro-max/scripts/search.py "elegant premium" --domain typography

# Tìm guideline UX / anti-pattern
python .claude/skills/ui-ux-pro-max/scripts/search.py "form validation feedback" --domain ux

# Tìm chart type phù hợp
python .claude/skills/ui-ux-pro-max/scripts/search.py "time series realtime" --domain chart
```

### Stack-specific guidelines (ƯU TIÊN dùng khi code Avalonia / WPF / Desktop)

```bash
# Avalonia — compiled bindings, MVVM, DataGrid, TreeView, DI...
python .claude/skills/ui-ux-pro-max/scripts/search.py "compiled bindings x:DataType" --stack avalonia
python .claude/skills/ui-ux-pro-max/scripts/search.py "DataGrid TreeView" --stack avalonia
python .claude/skills/ui-ux-pro-max/scripts/search.py "MVVM dependency injection" --stack avalonia

# WPF
python .claude/skills/ui-ux-pro-max/scripts/search.py "data binding command" --stack wpf

# React / Next.js
python .claude/skills/ui-ux-pro-max/scripts/search.py "rerender performance" --stack react
python .claude/skills/ui-ux-pro-max/scripts/search.py "server component rsc" --stack nextjs

# JavaFX (nếu cần)
python .claude/skills/ui-ux-pro-max/scripts/search.py "tableview layout" --stack javafx
```

### Design System Generator (dùng khi bắt đầu dự án mới)

```bash
# Sinh design system hoàn chỉnh (pattern + style + color + typography + anti-patterns)
python .claude/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness" --design-system -p "ProjectName"

# Sinh và lưu vào file (persist xuyên session)
python .claude/skills/ui-ux-pro-max/scripts/search.py "saas analytics" --design-system --persist -p "MyApp" --output-dir "."

# Với design dials (variance 1-10, motion 1-10, density 1-10)
python .claude/skills/ui-ux-pro-max/scripts/search.py "dashboard" --design-system --variance 8 --motion 5 --density 7
```

### Domain tham chiếu nhanh

| Cần gì | `--domain` | Ví dụ query |
|--------|-----------|------------|
| Loại UI style | `style` | `"glassmorphism dark premium"` |
| Màu sắc theo ngành | `color` | `"healthcare medical"` |
| Font pairing | `typography` | `"clean modern sans"` |
| Pattern landing page | `landing` | `"saas hero cta"` |
| Best practices UX | `ux` | `"accessibility keyboard nav"` |
| Chart phù hợp | `chart` | `"comparison bar pie"` |
| Icon recommendations | `icons` | `"navigation outline minimal"` |
| GSAP animation | `gsap` | `"scroll reveal stagger"` |
| React performance | `react` | `"memo virtualize"` |
| App/native guidelines | `web` | `"touch safe-area bottom-nav"` |
| Google Fonts | `google-fonts` | `"variable weight popular"` |

---

## Lưu ý khi chạy trên Windows

```bash
# Dùng python thay vì python3
python .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain style

# Nếu encoding lỗi
python -X utf8 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain style
```

---

## Tham chiếu thêm

- Workflow đầy đủ: `.claude/skills/ui-ux-pro-max/SKILL.md`
- Quick reference (98 UX guidelines): `.claude/skills/ui-ux-pro-max/references/quick-reference.md`
- Pro rules + pre-delivery checklist: `.claude/skills/ui-ux-pro-max/references/pro-rules.md`
