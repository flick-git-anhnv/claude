# GOTCHAS.md — Ràng buộc ngầm & Lỗi đã gặp

> **Mục đích:** Ghi lại các lỗi "ngầm" — không có trong docs chính thức, nhưng thực tế đã gặp và mất thời gian debug. Học từ pattern `PLUGIN_SCHEMA_NOTES.md` của affaan-m/ecc.
>
> **Quy tắc:** Agent fix xong 1 lỗi ngầm (không có trong CLAUDE.md hay README) PHẢI thêm 1 entry vào file này trước khi đánh dấu task hoàn thành.
>
> **Đọc file này khi:** bắt đầu session mới, hoặc gặp lỗi lạ chưa rõ nguyên nhân — tra ở đây trước khi debug từ đầu.

---

## Mục lục nhanh

| # | Vấn đề | Ngày |
|---|--------|------|
| G001 | `C:/Users/nguye/.claude/scripts/md_to_docx_kztek.py` — thiếu `python-docx`/`Pillow`; PDF không cần trên cloud/sandbox | 2026-07-12 |
| G002 | File `.ps1` có chữ Việt mà **không có BOM** → PowerShell 5.1 parse lỗi `Missing '=' operator` | 2026-07-25 |
| G003 | `find_logo()` chỉ tìm theo CWD → xuất tài liệu từ project khác **mất logo mà không báo lỗi** | 2026-07-25 |

---

## G003 — `md_to_docx_kztek.py`: logo tìm theo CWD nên mất logo khi chạy từ project khác

**Ngày phát hiện:** 2026-07-25
**Môi trường:** Windows 11, mọi project không phải repo config KZTEK

**Vấn đề:**
Xuất DOCX từ project khác (sau khi script được dùng chung qua junction `~/.claude/scripts`)
thì tài liệu **không có logo KZTEK**, nhưng script vẫn báo `✓ DOCX hoàn thành` — **không có
warning nào**. Vi phạm quy định thương hiệu mà không ai phát hiện.

**Nguyên nhân:**
`LOGO_CANDIDATES` toàn là đường dẫn **tương đối theo CWD** (`"Kztek_Logo.png"`,
`".claude/commands/Kztek_Logo.jpg"`). Chạy ở project khác → CWD không phải repo config
→ `os.path.exists()` fail hết → `find_logo()` trả `None` → `build_doc_header()` bỏ qua logo im lặng.

**Cách xử lý (ĐÃ XÁC NHẬN):**
Thêm tầng fallback tuyệt đối theo vị trí thật của script:
```python
_SCRIPT_ROOT = Path(__file__).resolve().parent.parent   # .resolve() đi xuyên junction
LOGO_CANDIDATES_ABS = [_SCRIPT_ROOT / "Kztek_Logo.png", ...]
```
Thứ tự tìm: CWD trước (cho phép project override logo riêng) → repo config sau (luôn có).

`.resolve()` là mấu chốt: script được gọi qua junction `~/.claude/scripts/...` nhưng
`__file__` sau resolve ra đường dẫn thật trong repo, nên tìm được `Kztek_Logo.png` ở repo root.

**Kiểm chứng:** `cd` ra thư mục lạ → xuất DOCX → `zipfile` xác nhận có `word/media/image1.png`
đúng 352.425 bytes (= kích thước `Kztek_Logo.png`).

**Lần đầu gặp:** Chuyển config sang user-level scope (2026-07-25)

**Không cần làm lại:** Không cần copy `Kztek_Logo.png` sang từng project — fallback đã xử lý.

---

## G002 — File `.ps1` chứa chữ Việt không có BOM → PowerShell 5.1 parse lỗi vô nghĩa

**Ngày phát hiện:** 2026-07-25
**Môi trường:** Windows PowerShell 5.1 (`powershell.exe`), Windows 11

**Vấn đề:**
Ghi file `.ps1` bằng tool `Write` (UTF-8 không BOM) có chữ Việt trong key hashtable
(`Trạng_thái = $status`) → chạy báo hàng loạt lỗi parser **hoàn toàn không liên quan**:
```
Missing '=' operator after key in hash literal.
The string is missing the terminator: ".
Missing closing '}' in statement block or type definition.
```
Nhìn thông báo sẽ tưởng thiếu ngoặc/dấu bằng và đi sửa cú pháp — sai hướng hoàn toàn.

**Nguyên nhân:**
PowerShell 5.1 mặc định đọc `.ps1` **không có BOM** theo **codepage ANSI (Windows-1252)**,
không phải UTF-8. Chữ Việt nhiều byte bị giải mã sai thành ký tự rác
(`Trạng_thái` → `Tráº¡ng_thÃ¡i`), phá vỡ token của parser. PowerShell 7+ không bị (mặc định UTF-8).

**Cách xử lý (cả 2, không chỉ 1):**
1. **Không dùng chữ Việt trong identifier** (tên biến, key hashtable, tên property) — chỉ dùng
   trong comment và chuỗi hiển thị.
2. **Lưu `.ps1` có UTF-8 BOM** để comment/chuỗi tiếng Việt hiển thị đúng:
   ```python
   raw = open(p,'rb').read()
   if not raw.startswith(b'\xef\xbb\xbf'):
       open(p,'wb').write(b'\xef\xbb\xbf' + raw)
   ```
   Hoặc trong PowerShell: `Out-File -Encoding utf8` (5.1 mặc định ghi BOM).

**Lần đầu gặp:** Viết `scripts/link-global.ps1` (2026-07-25)

**Không cần làm lại:**
- Không đi sửa cú pháp hashtable/ngoặc — cú pháp vốn đã đúng, lỗi nằm ở encoding.
- Không dùng `Set-Content` mặc định để ghi lại (5.1 ghi ANSI, làm hỏng tiếp).

---

## G001 — `C:/Users/nguye/.claude/scripts/md_to_docx_kztek.py`: thiếu `python-docx`/`Pillow`; PDF là optional trên cloud/sandbox

**Ngày phát hiện:** 2026-07-12

**Môi trường:** Linux sandbox (claude.ai / cloud agent)

**Vấn đề ban đầu:**
Chạy `python C:/Users/nguye/.claude/scripts/md_to_docx_kztek.py <file.md>` báo `ModuleNotFoundError: No module named 'docx'` vì thiếu package `python-docx` và `Pillow`.

**Khắc phục (ĐÃ XÁC NHẬN HOẠT ĐỘNG):**
```bash
pip install python-docx Pillow
```
Sau khi cài, DOCX tạo thành công. Đây là fix dứt điểm cho lỗi ModuleNotFoundError.

**Về PDF export trên cloud/sandbox:**
LibreOffice đã cài tại `/usr/bin/soffice`, nhưng `soffice --headless --convert-to pdf` báo lỗi "source file could not be loaded" trong môi trường sandbox — đây là hiện tượng đã biết, KHÔNG cần debug thêm.

Theo chỉ đạo: **trên cloud/sandbox, PDF không cần thiết**. Dùng `--no-pdf` làm mặc định:
```bash
python C:/Users/nguye/.claude/scripts/md_to_docx_kztek.py <file.md> --no-pdf
```

PDF chỉ cần khi chạy trên máy local có LibreOffice GUI đầy đủ — không phải môi trường sandbox.

**Không cần làm lại:**
- Không cần điều tra tại sao soffice lỗi trên sandbox — không blocking, không cần fix
- Không cần thử `pip install docx2pdf` — phụ thuộc vào Word/LibreOffice GUI, không hoạt động trên Linux sandbox
- DOCX là artifact chính; PDF là optional và chỉ cần ở môi trường local

**Lần đầu gặp:** Bước 1.1-1.2 — WF-REFACTOR optimize-framework (2026-07-12)

---

<!-- Thêm entry mới theo format:

## G00N — [Tên vấn đề ngắn gọn]

**Ngày phát hiện:** YYYY-MM-DD
**Môi trường:** [OS / platform / version]
**Vấn đề:** [Mô tả triệu chứng cụ thể]
**Nguyên nhân:** [Root cause đã xác định]
**Cách xử lý:** [Giải pháp, workaround, hoặc cách tránh]
**Lần đầu gặp:** [Context task / session]
**Không cần làm lại:** [Những gì đã thử mà KHÔNG hoạt động — để tránh lặp lại]

-->
