# Bash heredoc thu gọn `\\` → `\` khiến chuỗi Python chứa đường dẫn Windows bị sai âm thầm

**Category:** windows-tooling
**Ngày:** 2026-07-26
**Loại:** Gotcha
**Project gặp:** iPGSv4 (sửa `.csproj` + `CODE-GRAPH.md` bằng script Python chạy qua Bash tool)

---

## Triệu chứng

Chạy Python inline qua Bash tool để sửa đường dẫn Windows trong `.csproj`:

```python
s = s.replace('..\\..\\..\\5.BaseUI\\X.csproj', '$(Root)\\X.csproj')
```

Script báo thành công (`print('ok')`) nhưng **file không đổi gì**. Regex tương đương cũng không khớp.

Lần thứ hai, cùng nguyên nhân nhưng biểu hiện khác: ghi Markdown có `$(KztekCodeRoot)\5.BaseUI` → file sinh ra chứa **ký tự điều khiển**, `grep` báo `Binary file matches`, và converter DOCX chết với
`All strings must be XML compatible: ... no NULL bytes or control characters`.

## Nguyên nhân

Heredoc của Bash tool **thu gọn `\\` thành `\`** trước khi Python nhận source. Sau đó Python đọc `'\5'` như **escape bát phân** → ký tự `\x05`. Tương tự `\1` → `\x01`, `\0` → `\x00`.

Nghĩa là chuỗi `'..\\5.BaseUI'` viết trong heredoc đến Python thành `'..\5.BaseUI'` = `..` + `\x05` + `.BaseUI`. Không khớp gì cả, và nếu đem ghi ra file thì file nhiễm ký tự điều khiển.

Cách nhận ra nhanh:
- `replace()` "chạy mà không đổi gì" trên chuỗi có `\\`
- `grep` đột nhiên báo `Binary file ... matches` với file text
- `repr()` cho ra `\x05`, `\x01`, `\x00` ở đúng chỗ đáng lẽ là `\`

## Cách xử lý

Không viết backslash literal trong Python source chạy qua heredoc. Dựng từ `chr(92)`:

```python
BS = chr(92)
s = s.replace('..' + BS + '5.BaseUI', '$(Root)' + BS + '5.BaseUI')

# regex:
import re
pat = re.compile(r'(?:\.\.[' + BS + BS + r'/])+5\.BaseUI')
```

Hoặc tránh hẳn: dùng tool `Edit`/`Write` cho file có đường dẫn Windows, chỉ dùng script khi thao tác hàng loạt.

## Kiểm chứng

```python
raw = open(path,'rb').read()
print([hex(b) for b in raw if b < 0x09 or 0x0b <= b <= 0x0c or 0x0e <= b <= 0x1f])
```

Danh sách rỗng = sạch. Chạy ngay sau khi script ghi file, trước khi commit hoặc convert DOCX/PDF.

## Bài học

Với mọi script inline qua heredoc mà nội dung có đường dẫn Windows: **luôn kiểm lại file sau khi ghi**, đừng tin `print('ok')`. Script báo thành công vẫn có thể vừa ghi ký tự rác vào file.

Liên quan: [[powershell-vietnamese-bom-parse-error]]
