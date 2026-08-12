---
category: windows-tooling
tags: [python, encoding, utf-8, cp1252, surrogateescape, windows, jsonl, mojibake]
severity: high
created: 2026-08-08
updated: 2026-08-08
project-origin: tools/agent-dashboard
---

# Python trên Windows: open() không encoding → cp1252 → lone surrogates trong UTF-8 text

## Tình huống gặp phải

Đang audit bug mojibake trong Agent Dashboard: text tiếng Việt trong
`history[].description` của Dispatcher (endpoint `/api/sessions/{id}/chain`)
bị garbled, ví dụ: `"gi\udc9d"` thay vì `"giờ"`, `"v\xa0"` thay vì `"và"`.
Backend là FastAPI + aiosqlite, đọc Claude JSONL từ `~/.claude/projects/`.

## Triệu chứng / Lỗi

```
# Ví dụ dữ liệu bị lỗi trong API response:
"description": "kiểm tra, v\xa0 ho\xa0n thiện các t\xadnh nang dang gi\udc9d"

# Thay vì:
"description": "kiểm tra, và hoàn thiện các tính năng đang dở"

# Các ký tự lỗi thường gặp:
# \xa0  = U+00A0 (non-breaking space) — do cp1252 đọc byte 0xA0 thành Unicode point trực tiếp
# \xad  = U+00AD (soft hyphen) — byte 0xAD trong UTF-8 là 1/2 của ký tự 2-byte, bị đọc sai
# \udc9d = lone surrogate (U+DC9D) — do errors='surrogateescape' map byte 0x9D
# \udc90 = lone surrogate (U+DC90) — do errors='surrogateescape' map byte 0x90
```

## Nguyên nhân gốc rễ (Root Cause)

### Cơ chế sinh lỗi trên Windows

Python 3.10 trên Windows có:
```python
import locale
locale.getpreferredencoding()  # → 'cp1252'  (KHÔNG phải 'UTF-8')
```

Bất kỳ `open(path)` KHÔNG chỉ định `encoding=` sẽ mặc định dùng `cp1252`.
File JSONL chứa UTF-8 bytes sẽ bị decode sai:

```
# Ví dụ: "ờ" trong UTF-8 = bytes 0xE1 0xBB 0x9D
# cp1252 đọc từng byte độc lập:
#   0xE1 → 'á' (U+00E1)
#   0xBB → '»' (U+00BB)
#   0x9D → lone surrogate U+DC9D (errors='surrogateescape' khi byte > 0x7F không ánh xạ được)
```

### Hai loại lỗi encoding khác nhau

| Loại | Ký tự | Nguồn gốc | Cách phát hiện |
|------|--------|-----------|----------------|
| Mojibake | `\xa0`, `\xad`, `NgÃ\xa0y` | cp1252 decode UTF-8 byte thành Latin-1 codepoint | Ký tự Latin-1/Windows-1252 lạ xen trong text Việt |
| Lone surrogate | `\udc9d`, `\udc90` | `errors='surrogateescape'`: byte 0x80-0xFF → U+DC80-U+DCFF | `0xD800 <= ord(c) <= 0xDFFF` |

### Khác biệt `surrogateescape` vs `replace`

```python
# Cách 1 — tạo LONE SURROGATE (nguy hiểm, JSON không serialize được):
b"\x9d".decode("utf-8", errors="surrogateescape")  # → '\udc9d'

# Cách 2 — thay bằng replacement char (an toàn):
b"\x9d".decode("utf-8", errors="replace")  # → '??' (U+FFFD)
```

### Trường hợp KHÔNG phải lỗi code (quan trọng)

- Claude Code CLI tự ghi tool_result (output của Bash/Read) vào JSONL bằng encoding
  của process LLM — nếu LLM process dùng cp1252, tool output đã bị garbled từ trước
  khi agent dashboard đọc. Đây là upstream issue, không thể fix ở reader.

## Giải pháp

### 1. Audit tất cả `open()` call trong code đọc JSONL

```bash
# Tìm open() không có encoding= (có thể bỏ sót)
grep -rn "open(" tools/agent-dashboard/backend/ | grep -v "encoding="
```

Các pattern ĐÚNG trong agent-dashboard:
```python
# Pattern 1 — Binary mode (KHÔNG phụ thuộc locale):
with open(path, "rb") as f:
    data = f.read()
    text = data.decode("utf-8", errors="replace")  # explicit, safe

# Pattern 2 — Text mode với encoding tường minh:
with open(path, encoding="utf-8", errors="replace") as f:
    text = f.read()
```

### 2. Thêm hàm `_sanitize_text()` để làm sạch dữ liệu cũ

```python
def _sanitize_text(text: str) -> str:
    """Làm sạch lone surrogates từ encoding cũ bị lỗi.
    
    Lone surrogates (U+DC80..U+DCFF) xuất hiện khi bytes đọc sai encoding
    rồi Python áp errors='surrogateescape'. Hàm encode lại về bytes gốc
    qua surrogateescape, sau đó decode UTF-8 với errors='replace'.
    """
    # Fast path: không có surrogate → không cần xử lý
    if not any(0xD800 <= ord(c) <= 0xDFFF for c in text):
        return text
    try:
        return text.encode("utf-8", "surrogateescape").decode("utf-8", "replace")
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Fallback: xóa thủ công các surrogate
        return "".join(c for c in text if not (0xD800 <= ord(c) <= 0xDFFF))
```

Gọi trong `_extract_user_turn_text()` và bất kỳ hàm nào trả text từ payload:
```python
sanitized = _sanitize_text(raw_text)
return sanitized[:120] if sanitized else None
```

### 3. Script re-ingest để fix dữ liệu cũ

Tạo `scripts/reingest_recent_sessions.py` với cờ `--days N --dry-run --all`:
```python
raw_text = p.read_text(encoding="utf-8", errors="replace")  # key fix
```
Dry-run trước để kiểm tra có bao nhiêu event cần update, rồi chạy thật.

## Áp dụng lại (How to reuse)

- Khi thấy `\udc9d`, `\udc90`, `\udcXX` trong string Python → đây là lone surrogate
  từ `errors='surrogateescape'`; dùng `_sanitize_text()` pattern ở trên để làm sạch.
- Khi thấy `\xa0`, `\xad` xen trong text Việt → mojibake cp1252; kiểm tra ngay xem
  đoạn code đọc file có `encoding=` không.
- Khi bắt đầu project Python trên Windows đọc file UTF-8 → LUÔN chỉ định
  `encoding="utf-8"` hoặc dùng binary mode + `.decode("utf-8", errors="replace")`.
- Set `PYTHONUTF8=1` (env var) hoặc `python -X utf8` để force UTF-8 toàn process
  (nhưng đừng dựa vào đây, vẫn nên ghi tường minh trong code).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `open(path, "rb")` rồi `.decode("utf-8", errors="surrogateescape")` sẽ TẠO lone
  surrogates cho byte không hợp lệ. Dùng `errors="replace"` thay vì `surrogateescape`
  nếu không cần round-trip về bytes gốc.
- ⚠️ Lone surrogate KHÔNG serialize được thành JSON chuẩn (`json.dumps` throw
  `UnicodeEncodeError` trên Python 3.12+, hoặc tạo invalid JSON trên 3.10).
- ⚠️ Mojibake trong tool_result (Bash/Read output được Claude tự ghi vào JSONL) là
  upstream issue — `_sanitize_text()` không thể phục hồi được nếu byte gốc đã mất.
- ⚠️ `locale.getpreferredencoding()` trả `cp1252` (Windows) hoặc `UTF-8` (Linux/Mac) —
  code chạy đúng trên dev Mac có thể lỗi trên prod Windows nếu không tường minh encoding.
- ⚠️ `PYTHONUTF8=1` không có hiệu lực nếu set sau khi Python process đã khởi động
  (env var phải set trước khi launch interpreter).

## Tham chiếu

- Python docs: [open() encoding parameter](https://docs.python.org/3/library/functions.html#open)
- Python docs: [codecs error handlers — surrogateescape](https://docs.python.org/3/library/codecs.html#error-handlers)
- PEP 383: [Non-decodable Bytes in System Character Interfaces](https://peps.python.org/pep-0383/)
- Project liên quan: tools/agent-dashboard (Senior Developer, 2026-08-08)
