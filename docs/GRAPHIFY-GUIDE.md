---
title: Hướng dẫn sử dụng Graphify tại KZTEK
created: 2026-07-29
updated: 2026-07-29
---

# Graphify — Hướng dẫn cài đặt & sử dụng

> **Graphify là gì:** Công cụ Python (package PyPI: `graphifyy`) phân tích codebase bằng
> tree-sitter/AST, dựng thành knowledge graph có thể query — thay vì AI phải Grep/Read
> thủ công từng file. Xem phân tích đầy đủ tại `docs/research/RESEARCH-graphify-2026-07-29.md`.
>
> **Trong hệ thống KZTEK:** Graphify là công cụ **tùy chọn**, bổ sung cho `code-graph/CODE-GRAPH.md`
> (§17 CLAUDE.md) — không thay thế. Có giá trị cao nhất với project >50 file code.

---

## 1. ⚠️ Gotcha quan trọng nhất: tên package

**Tên repo GitHub** (`Graphify-Labs/graphify`) và **tên package PyPI** (`graphifyy` — 2 chữ `y`)
**KHÔNG giống nhau**.

```bash
pip install graphify      # ❌ SAI — "No matching distribution found for graphify"
pip install graphifyy     # ✅ ĐÚNG
```

Chi tiết: `.claude/shared/GOTCHAS.md` mục **G006**.

---

## 2. Cách dùng nhanh nhất: skill `/graphify`

Thay vì tự gõ từng lệnh, dùng skill đã đóng gói sẵn toàn bộ quy trình (detect trạng thái project,
cài đặt đúng tên package, build/update, đối chiếu `CODE-GRAPH.md` không ghi đè):

```
/graphify E:\đường\dẫn\tới\project
```

Không có path → skill dùng thư mục hiện tại (sẽ xác nhận lại với bạn trước khi cài đặt).

Định nghĩa đầy đủ: `.claude/commands/graphify.md`. Eval/test đã pass: `.claude/evals/graphify.md`.

---

## 3. Cài đặt thủ công (nếu không dùng skill)

### 3.1 Điều kiện tiên quyết

- Python **>= 3.10**
- Project nên có **>50 file** ở ngôn ngữ graphify hỗ trợ tốt (`.cs`, `.xaml`, `.razor`, `.cshtml`,
  `.ps1`, `.psm1`, `.psd1`, `.sql`, ...) — project nhỏ hơn thì giá trị thấp, cân nhắc bỏ qua.

### 3.2 Cài đặt + build lần đầu

```bash
python -m pip install graphifyy
cd <project-root>
python -m graphify .
```

Sinh ra thư mục `graphify-out/`:

| File | Nội dung |
|---|---|
| `graph.json` | Dữ liệu graph thô (nodes/edges) |
| `GRAPH_REPORT.md` | Báo cáo dạng đọc được — dùng để đối chiếu với `CODE-GRAPH.md` |
| `graph.html` | Visualization tương tác (mở bằng browser) |

### 3.3 Đối chiếu với `code-graph/CODE-GRAPH.md`

- **Đã có file:** đọc `GRAPH_REPORT.md`, bổ sung phần graphify phát hiện mà file thủ công chưa có
  — dùng **Edit**, **KHÔNG Write đè** (mất nội dung mô tả nghiệp vụ đã viết tay).
- **Chưa có file:** tạo mới từ `.claude/templates/CODE-GRAPH-template.md`, điền dữ liệu nền từ
  `GRAPH_REPORT.md` rồi bổ sung thủ công phần nghiệp vụ.
- Luôn gắn Confidence label (§17.2 CLAUDE.md), map từ nhãn của graphify:

  | Graphify | KZTEK CODE-GRAPH.md |
  |---|---|
  | `EXTRACTED` | `CONFIRMED` |
  | `INFERRED` | `INFERRED` |
  | `AMBIGUOUS` | `UNCERTAIN` |

- Xuất lại `CODE-GRAPH.pdf` sau khi `.md` đổi (§17.4 CLAUDE.md):
  ```bash
  python C:/Users/nguye/.claude/scripts/md_to_docx_kztek.py code-graph/CODE-GRAPH.md --no-docx
  ```

---

## 4. Bảng lệnh tham khảo (project đã cài graphify)

| Ngữ cảnh | Lệnh |
|---|---|
| Tra cứu trước khi đọc/sửa code (VD: "ai gọi hàm X") | `python -m graphify query "<câu hỏi>"` |
| Vừa sửa code xong, chuẩn bị `/verify-pr` | `python -m graphify update --diff` |
| Đường đi giữa 2 khái niệm | `python -m graphify path A B` |
| Subgraph 1-hop quanh 1 node | `python -m graphify explain X` |
| PR dashboard / graph impact của 1 PR | `python -m graphify prs` / `graphify prs <N>` |
| Tích lũy Q&A memory thành lessons | `python -m graphify reflect` |
| Cài always-on injection vào `CLAUDE.md` của project | `python -m graphify claude install` |

> **Sau `update --diff`:** graphify **không tự viết** mô tả nghiệp vụ + Confidence label — luôn phải
> bổ sung thủ công vào `CODE-GRAPH.md` sau đó (§17.3 CLAUDE.md). Chạy xong `update --diff` KHÔNG
> coi là hoàn thành nghĩa vụ cập nhật CODE-GRAPH.

---

## 5. Hook tích hợp vào Claude Code — 2 tầng khác nhau

Graphify có thể tích hợp vào Claude Code qua `hooks` trong `settings.json`, theo **2 tầng độc lập**:

### 5.1 Tầng User (global) — chỉ NHẮC, mọi project

`~/.claude/settings.json` → hook `PostToolUse` (matcher `Write|Edit`):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "node \"C:/Users/nguye/.claude/hooks/code-graph-lesson-reminder.js\"",
            "shell": "bash",
            "timeout": 10,
            "statusMessage": "Kiểm tra code-graph / lesson reminder..."
          }
        ]
      }
    ]
  }
}
```

Sau mỗi lần Edit/Write file source, hook bơm `additionalContext` nhắc cập nhật `CODE-GRAPH.md`
(nếu đổi structure/API) + ghi lesson (nếu vừa fix bug/gotcha). **Chỉ nhắc, không tự chạy graphify,
không bao giờ block.**

> ⚠️ File `~/.claude/hooks/code-graph-lesson-reminder.js` là **hook riêng của máy này, cố ý KHÔNG
> đưa vào repo** (xem `docs/SETUP-GLOBAL.md` §3) — để phân biệt với `hooks-kztek/` (junction dùng
> chung). Đổi máy phải tự tạo lại file này thủ công nếu muốn giữ hành vi nhắc nhở tương tự.

### 5.2 Tầng Project — CHẶN query + TỰ ĐỘNG update thật, chỉ project đã cài graphify

Đây là "always-on injection" thật sự của graphify (§17.6 CLAUDE.md, mục "Always-on CLAUDE.md
injection") — gồm **2 loại hook khác nhau**, cùng nằm trong `.claude/settings.json` của project:

**(a) `PreToolUse` — chặn TRƯỚC mỗi lần Grep/Read/Bash để ép ưu tiên tra graph:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Grep",
        "hooks": [
          { "type": "command", "command": "<path-tới>/graphify.exe hook-guard search" }
        ]
      },
      {
        "matcher": "Read|Glob",
        "hooks": [
          { "type": "command", "command": "<path-tới>/graphify.exe hook-guard read" }
        ]
      }
    ]
  }
}
```

**(b) `PostToolUse` — TỰ ĐỘNG chạy `graphify update` thật sau mỗi lần Edit/Write (không chỉ nhắc):**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "<path-tới>/graphify.exe update . --no-cluster",
            "async": true,
            "timeout": 120,
            "statusMessage": "Đồng bộ graphify graph..."
          }
        ]
      }
    ]
  }
}
```
`async: true` — không chặn luồng chính chờ update xong; `--no-cluster` — bỏ qua bước community
detection (Leiden) để chạy nhanh hơn, phù hợp chạy sau MỖI lần sửa file. Đây chính là câu trả lời
đầy đủ cho câu hỏi "graphify đã tự động cập nhật khi code thay đổi chưa" — **có**, ở project nào đã
thêm block này. Vẫn phải làm thêm việc thủ công ở mục 3.3 (Confidence label + mô tả nghiệp vụ) vì
`update` không tự viết phần đó.

Cả 2 loại hook trên được thêm bằng lệnh `python -m graphify claude install` (Bước 3A.4 trong skill
`/graphify`) — **PHẢI xác nhận với user trước khi chạy**, vì thao tác này sửa `.claude/settings.json`
của project.

Đường dẫn `<path-tới>/graphify.exe` là nơi `pip install graphifyy` đặt executable — trên Windows
thường là `%LOCALAPPDATA%\Programs\Python\Python3XX\Scripts\graphify.exe`. Kiểm tra bằng:

```bash
python -m pip show -f graphifyy | grep graphify.exe
```

**File này thuộc project, KHÔNG thuộc repo config KZTEK** — commit vào git của chính project đó
(xem §6 bên dưới).

---

## 6. Có nên đẩy lên git không? — theo đúng repo của từng file

| File | Thuộc repo nào | Khuyến nghị |
|---|---|---|
| `.claude/commands/graphify.md`, `.claude/evals/graphify.md` | Repo config KZTEK (`Claude-Git/claude`) | ✅ Đã commit + push — dùng chung mọi project qua junction |
| `<project>/.claude/settings.json` (hook-guard sau `graphify claude install`) | **Repo của project đó** (VD: App-Access-V2) | ✅ Nên commit — nếu không, đổi máy/clone lại sẽ mất hook-guard, phải chạy lại `graphify claude install` thủ công |
| `<project>/.claude/settings.json.graphify-bak` (backup tự sinh khi cài) | Repo của project đó | ❌ KHÔNG commit — thêm vào `.gitignore` của project, đây là file backup tạm, không phải cấu hình cần giữ |
| `~/.claude/settings.json` (toàn bộ file) | Không thuộc repo nào — máy cá nhân | ⚠️ Không thể "push" trực tiếp (không phải git repo). Phần KZTEK cần dùng chung nên phản ánh vào `.claude/templates/settings-global.json` (đã có trong repo) để máy mới merge theo hướng dẫn `docs/SETUP-GLOBAL.md` |
| `~/.claude/hooks/code-graph-lesson-reminder.js` | Không thuộc repo nào — cố ý (xem §5.1) | ⚠️ Giữ nguyên thiết kế cũ trừ khi bạn muốn đổi — nếu muốn đồng bộ, cần dời vào `.claude/hooks/` của repo config rồi cập nhật `settings-global.json` |

**Tóm tắt quy tắc:** graphify sinh ra 2 loại config khác nhau — cấu hình **dùng chung** (skill/eval)
đã nằm đúng trong repo KZTEK; cấu hình **riêng từng project** (`hook-guard` sau `claude install`)
phải commit vào **git của chính project đó**, không phải repo KZTEK.

---

## 7. Checklist thiết lập graphify cho 1 project mới (tóm tắt)

```
1. Kiểm tra Python >= 3.10
2. /graphify <path-project>   (hoặc pip install graphifyy + python -m graphify . thủ công)
3. Đối chiếu GRAPH_REPORT.md với code-graph/CODE-GRAPH.md — bổ sung, không ghi đè
4. Xuất lại CODE-GRAPH.pdf
5. [Tùy chọn] python -m graphify claude install — xác nhận trước khi chạy
6. Commit .claude/settings.json (nếu bước 5 có chạy) vào git CỦA PROJECT ĐÓ
7. Thêm .claude/settings.json.graphify-bak vào .gitignore của project đó
```

---

## Tài liệu liên quan

- `.claude/commands/graphify.md` — skill thực thi
- `.claude/evals/graphify.md` — eval/test đã pass
- `.claude/shared/GOTCHAS.md` — G006 (tên package)
- `docs/research/RESEARCH-graphify-2026-07-29.md` — phân tích gốc từ GitHub repo
- `docs/SETUP-GLOBAL.md` — cơ chế junction dùng chung, phân biệt `hooks` vs `hooks-kztek`
- CLAUDE.md §17.3, §17.6

---

## Lịch sử cập nhật

| Ngày | Nội dung | Người |
|---|---|---|
| 2026-07-29 | Tạo mới — hướng dẫn đầy đủ sau khi phát hiện gotcha tên package và thiết lập hook 2 tầng (global reminder + project enforcement) | Claude Code |
