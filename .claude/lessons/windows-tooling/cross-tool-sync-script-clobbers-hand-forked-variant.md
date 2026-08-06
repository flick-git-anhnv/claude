---
category: windows-tooling
tags: [sync-script, powershell, cross-tool, config-drift]
severity: high
created: 2026-08-05
updated: 2026-08-05
project-origin: claude (Claude-Git — sync-to-gemini.py)
---

# Script đồng bộ cấu hình theo tên file giống nhau sẽ ghi đè mất bản đã hand-fork riêng

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Viết `scripts/sync-to-gemini.py` để tự động đồng bộ agents/commands/lessons/scripts
từ repo Claude-Git sang repo GeminiGit (thay việc copy tay). Cơ chế: với mọi file
không phải `.md`, script copy nguyên văn (verbatim) theo đúng đường dẫn tương đối
— giả định "cùng tên file ở 2 bên = cùng nội dung, chỉ cần đồng bộ".

## Triệu chứng / Lỗi

Dry-run báo `scripts/windows-tools/GeminiConfigAudit.ps1` là "orphan" (không còn
tương ứng ở nguồn) — nhưng vào kiểm tra thì file này **có tồn tại thật và đang
được dùng**, chỉ là tên khác `ClaudeConfigAudit.ps1` ở phía nguồn. Nếu chạy
`--apply` mà không phát hiện sớm, `ClaudeConfigAudit.ps1` (bản Claude) sẽ được
copy đè vào `scripts/windows-tools/` bên Gemini, tồn tại song song với
`GeminiConfigAudit.ps1` — không mất dữ liệu ngay, nhưng để lâu sẽ gây nhầm lẫn
2 file cùng chức năng khác tên.

## Nguyên nhân gốc rễ (Root Cause)

Không phải mọi cặp file "tương đương chức năng" giữa 2 tool đều cùng TÊN file.
2 GUI tool `ClaudeConfigAudit.ps1` / `GeminiConfigAudit.ps1` đã được **hand-fork
thật** — đổi tên file, đổi biến (`$RepoClaude`/`$HomeClaude` vs
`$RepoGemini`/`$HomeGemini`), đổi text hiển thị trong GUI — không phải bản
mirror 1:1. Script sync coi "đồng bộ theo path tương đối giống nhau" là đúng
mặc định, nhưng giả định đó chỉ đúng với phần lớn file (agents/commands/lessons),
không đúng với các GUI tool đã được customize riêng theo từng tool đích.

## Giải pháp

```python
EXCLUDE_DIR_NAMES = {"__pycache__", ".git", "windows-tools"}
```

Loại trừ hẳn thư mục `scripts/windows-tools/` khỏi phạm vi tự động đồng bộ —
coi nó cùng nhóm với `README.md` (nội dung bespoke riêng từng bên, không mirror).

1. Trước khi thêm 1 thư mục vào danh sách "verbatim copy" của sync script, kiểm
   tra xem 2 bên có cùng TÊN file cho cùng chức năng không (không chỉ nhìn nội
   dung — nhìn cả filename).
2. Nếu phát hiện tên file khác nhau cho cùng 1 chức năng ở 2 bên → đó là dấu hiệu
   đã hand-fork, loại khỏi phạm vi tự động, để agent/con người tự sửa tay 2 bên
   riêng biệt.
3. Chạy dry-run trước, luôn đọc kỹ mục "ORPHAN" — orphan không có nghĩa là "file
   thừa cần xoá", có thể là "file đã hand-fork, sync tool không biết map nó với
   gì ở nguồn".

## Lần gặp lại (2026-08-06)

Ngay sau khi loại `windows-tools/` và commit, chạy `sync-to-gemini.py --apply` lần
tiếp theo (đồng bộ đợt merge Agent Dashboard) **vẫn ghi đè mất** bản fix đúng của
`.gemini/templates/settings-global.json` (schema Antigravity thật, commit `15bac7f`)
bằng bản gốc `.claude/templates/settings-global.json` (schema Claude Code
`permissions.allow`/`hooks.PreToolUse`) — vì file này KHÔNG phải `.md` nên bị copy
verbatim, không qua transform, và không nằm trong danh sách loại trừ ban đầu (chỉ
mới loại `windows-tools/`, quên rằng `templates/settings-global.json` cũng đã
hand-fork tương tự). Fix: thêm `"settings-global.json"` vào `EXCLUDE_FILE_NAMES`.

→ **Bài học tổng quát:** loại trừ 1 file/thư mục hand-fork không đủ — phải rà lại
TOÀN BỘ các file non-`.md` trong phạm vi sync (không chỉ nơi vừa phát hiện lỗi) để
tìm các cặp đã hand-fork tương tự, vì chúng có xu hướng xuất hiện thành cụm (mọi
file "hướng dẫn/cấu hình cho người dùng cuối" — README, settings mẫu, GUI tool —
đều có khả năng bị viết lại riêng cho từng bên, khác với agents/lessons/code
thường mirror 1:1 được).

## Áp dụng lại (How to reuse)

- Khi viết bất kỳ script đồng bộ nào giữa 2 hệ thống (Claude ↔ Gemini, hay
  sau này thêm bên thứ 3) → luôn có bước dry-run + review danh sách "orphan"
  bằng mắt TRƯỚC khi cho phép ghi đè/xoá.
- Không giả định "cùng path tương đối = cùng nội dung nên đồng bộ được" cho
  thư mục chứa GUI tool hoặc bất kỳ nơi nào tên biến/tên file có thể đã được
  đổi theo tên sản phẩm (Claude/Gemini, ...).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ "Orphan" trong báo cáo dry-run của sync script KHÔNG đồng nghĩa với "xoá
  được an toàn" — luôn kiểm tra xem có phải bản hand-fork trước khi dùng `--prune`.
- ⚠️ Verbatim-copy an toàn cho nội dung tool-agnostic (lessons, code snippet,
  data script) nhưng KHÔNG an toàn cho bất kỳ file có khả năng đã được
  rebrand/hand-tune riêng theo từng tool đích.
- ⚠️ **Mở rộng từ phiên làm việc thực tế:** cơ chế cấu hình permission thật của
  Antigravity/Gemini KHÔNG nằm ở `settings.json` (VS Code style) hay
  `~/.gemini/settings.json` — mà ở `~/.gemini/config/config.json` →
  `userSettings.globalPermissionGrants.allow`, dạng mảng string phẳng
  (`command(<text>)`, `write_file(<path>)`, `read_file(<path>)`), KHÔNG phải
  object `{match, pattern}` như 1 số blog/docs bên thứ 3 mô tả. App tự động
  loại bỏ (không lỗi, chỉ im lặng bỏ qua) mọi field không đúng schema khi
  regenerate file — dấu hiệu nhận biết: field mình thêm "biến mất" sau khi
  app restart mà không có thông báo lỗi nào. Ngoài ra: dấu `*` cuối 1 pattern
  trong `allow` list **không đảm bảo hoạt động như wildcard/prefix-match** —
  nhiều lệnh biến thể (`node -c...`, `node -e...`, `node script.js`,
  `powershell -Command "..."`) vẫn bị hỏi lại dù đã có `node*` trong allow list.
  Cách chắc chắn duy nhất đã xác nhận: bấm "Yes, and always allow '<câu lệnh
  chính xác>' in this project" ngay trên dialog — lưu literal string, exact
  match, không phụ thuộc wildcard.

## Tham chiếu

- Project liên quan: `scripts/sync-to-gemini.py` (Claude-Git ↔ GeminiGit)
- File minh chứng: `scripts/windows-tools/ClaudeConfigAudit.ps1` vs
  `scripts/windows-tools/GeminiConfigAudit.ps1`
- File cấu hình permission thật của Antigravity: `~/.gemini/config/config.json`
