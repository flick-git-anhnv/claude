---
category: windows-tooling
tags: [graphify, pip, PATH, claude-code-hooks, windows, PreToolUse]
severity: high
created: 2026-07-29
updated: 2026-07-29
project-origin: App-Access-V2 (KZTEK IACCESS v2)
---

# `graphify claude install` cài hook PreToolUse nhưng chạy im lặng vô hiệu vì `graphify.exe` không có trong PATH (Windows)

## Tình huống gặp phải

> Cài đặt package `graphifyy` (PyPI) qua `pip install graphifyy` trên Windows, rồi chạy `python -m graphify claude install` để tự động chèn section vào `CLAUDE.md` + đăng ký PreToolUse hook vào `.claude/settings.json` cho Claude Code.

## Triệu chứng / Lỗi

- `pip install graphifyy` cảnh báo ngay lúc cài:
  ```
  WARNING: The scripts graphify-mcp.exe and graphify.exe are installed in
  'C:\Users\<user>\AppData\Local\Programs\Python\Python310\Scripts' which is not on PATH.
  ```
- Sau khi `graphify claude install`, `.claude/settings.json` được ghi hook với lệnh **tên trần** `graphify hook-guard read` / `graphify hook-guard search` (không phải đường dẫn tuyệt đối).
- Test thực tế: yêu cầu Claude Code đọc 1 file bằng `Read` "không dùng graphify trước" — `Read` chạy thẳng, KHÔNG có bất kỳ dấu hiệu nào của graphify chen vào. Không có lỗi hiển thị — hook fail hoàn toàn im lặng, tool vẫn chạy bình thường như chưa cài gì.

## Nguyên nhân gốc rễ (Root Cause)

`graphify/install.py::_resolve_graphify_exe()` cố lấy đường dẫn tuyệt đối của exe để hook hoạt động độc lập với PATH:
1. Thử `shutil.which("graphify")` — fail vì `Scripts/` không có trong PATH.
2. Fallback: suy ra từ `Path(sys.executable).parent` (thư mục chứa `python.exe`) rồi tìm `graphify.exe` ở đó — **fail** vì trên Windows, `graphify.exe` nằm ở `Python310/Scripts/graphify.exe`, KHÁC thư mục với `python.exe` (`Python310/python.exe`). Hai thư mục không giống nhau như trên Unix (`bin/`).
3. Cả 2 cách đều fail → rơi về fallback cuối: dùng tên trần `"graphify"`.

Khi Claude Code chạy hook (qua Git Bash trên Windows), PATH của tiến trình con không có `Scripts/` → lệnh `graphify hook-guard ...` báo "command not found" → hook fail. Claude Code không chặn tool khi hook lỗi (không phải infra bug, đây là behavior mong đợi — hook lỗi không nên chặn toàn bộ workflow) → tool gốc (`Read`/`Bash`/`Grep`/`Glob`) vẫn chạy tiếp bình thường, **không có cảnh báo nào hiển thị cho user** — dễ khiến người dùng tưởng hook hoạt động trong khi thực chất vô hiệu hoàn toàn.

## Giải pháp

1. Xác định đường dẫn thật của `graphify.exe`:
   ```bash
   ls "C:\Users\<user>\AppData\Local\Programs\Python\Python310\Scripts\graphify.exe"
   ```
2. Sửa trực tiếp 2 dòng `command` trong `.claude/settings.json` (dùng forward-slash để tương thích cả Git Bash/cmd/PowerShell):
   ```json
   "command": "C:/Users/<user>/AppData/Local/Programs/Python/Python310/Scripts/graphify.exe hook-guard search"
   ```
   ```json
   "command": "C:/Users/<user>/AppData/Local/Programs/Python/Python310/Scripts/graphify.exe hook-guard read"
   ```
3. Verify: chạy thẳng lệnh đó ngoài Claude Code, kiểm tra exit code = 0:
   ```bash
   "/c/Users/<user>/.../Scripts/graphify.exe" hook-guard read; echo "exit:$?"
   ```
4. **Bắt buộc mở session Claude Code MỚI** để settings.json hook được nạp lại — sửa file không áp dụng cho session đang chạy.

## Áp dụng lại (How to reuse)

- Sau **bất kỳ** `pip install <package>` nào trên Windows kèm cảnh báo "Scripts ... not on PATH" mà package đó cài Claude Code hook / CLI hook tự động → PHẢI verify hook thực sự resolve được exe (không chỉ tin log "hooks registered" là xong).
- Verify bằng cách chạy thẳng lệnh trong `hooks[].hooks[].command` ở `.claude/settings.json` ngoài terminal, không chỉ tin log cài đặt.
- Nếu hook dùng tên trần (không phải đường dẫn tuyệt đối) trong `command` sau khi cài trên Windows → nghi ngờ ngay khả năng PATH resolution đã fail lúc install.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Claude Code KHÔNG báo lỗi khi 1 hook fail để chạy — tool gốc vẫn chạy tiếp như bình thường. Test "có hook hay không" bằng cách quan sát tool chạy suôn sẻ KHÔNG đủ để kết luận hook hoạt động — phải verify chủ động (test hook command riêng, hoặc kiểm tra log/side-effect cụ thể của hook).
- ⚠️ Trên Windows, thư mục chứa `python.exe` (`Python3XX/`) và thư mục chứa script/exe do pip cài (`Python3XX/Scripts/`) là 2 thư mục KHÁC NHAU — bất kỳ code nào tự suy luận exe path từ `sys.executable` mà không cộng thêm `/Scripts` sẽ fail trên Windows dù hoạt động đúng trên Unix (`bin/`).
- ⚠️ Sửa `.claude/settings.json` chỉ có hiệu lực cho session Claude Code MỚI — không áp dụng ngay cho session đang chạy.

## Tham chiếu

- Package: `graphifyy` trên PyPI (không phải `graphify` — xem lesson riêng nếu có về tên package)
- File nguồn: `graphify/install.py::_resolve_graphify_exe()` (site-packages, version 0.9.29)
- Project liên quan: App-Access-V2 (KZTEK IACCESS v2, dùng skill `/graphify`)
