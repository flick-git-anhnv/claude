# GOTCHAS.md — Ràng buộc ngầm & Lỗi đã gặp

> **Mục đích:** Ghi lại các lỗi "ngầm" — không có trong docs chính thức, nhưng thực tế đã gặp và mất thời gian debug. Học từ pattern `PLUGIN_SCHEMA_NOTES.md` của affaan-m/ecc.
>
> **Quy tắc:** Agent fix xong 1 lỗi ngầm (không có trong CLAUDE.md hay README) PHẢI thêm 1 entry vào file này trước khi đánh dấu task hoàn thành.
>
> **Đọc file này khi:** bắt đầu session mới, hoặc gặp lỗi lạ chưa rõ nguyên nhân — tra ở đây trước khi debug từ đầu.

---

## Quy tắc Archive (áp dụng khi file này phình to)

> File này bị đọc **toàn bộ, mọi session** (§KHỞI ĐỘNG CLAUDE.md) — khác với `lessons/` (chỉ đọc 1-2 file theo Simple Query Rule). Vì vậy giữ file chính GỌN là ưu tiên; entry cũ/không còn liên quan phải chuyển ra ngoài, không tích lũy vô hạn ở đây.

**Khi nào tách sang `GOTCHAS-ARCHIVE.md`:**
- File chính vượt quá **15 entry active**, HOẶC
- Entry đã > 90 ngày kể từ `Ngày phát hiện` VÀ nguyên nhân gốc đã được fix tận gốc trong code/script (không còn khả năng lặp lại, chỉ còn giá trị lịch sử).

**Cách tách:** Di chuyển entry đó (nguyên khối `## G00N — ...` đến hết trước `---`) sang `.claude/shared/GOTCHAS-ARCHIVE.md` (tạo file khi có entry đầu tiên cần chuyển), xóa dòng tương ứng khỏi bảng "Mục lục nhanh" ở trên.

**Khi nào mới đọc `GOTCHAS-ARCHIVE.md`:** CHỈ trong Phase 2 — Diagnose (§9a CLAUDE.md), và CHỈ khi lỗi đang gặp **không khớp** entry nào trong file chính này. Archive KHÔNG thuộc danh sách "đọc khi bắt đầu session" — không đọc mặc định mỗi lần, tránh việc tách archive lại thành thêm 1 file phải đọc đều.

---

## Mục lục nhanh + Bảng lọc theo Category

> **Cách dùng:** Khi gặp lỗi, xác định category loại lỗi → lọc cột Category → chỉ đọc entries thuộc category đó. Không cần đọc tuần tự toàn bộ file.

| # | Vấn đề | Category | Ngày |
|---|--------|----------|------|
| G001 | `md_to_docx_kztek.py` — thiếu `python-docx`/`Pillow`; PDF không cần trên cloud/sandbox | `[SCRIPT]` | 2026-07-12 |
| G002 | File `.ps1` có chữ Việt mà **không có BOM** → PowerShell 5.1 parse lỗi vô nghĩa | `[ENCODING]` | 2026-07-25 |
| G003 | `find_logo()` chỉ tìm theo CWD → xuất tài liệu từ project khác **mất logo mà không báo lỗi** | `[SCRIPT]` | 2026-07-25 |
| G004 | `KzPasswordTextBox`: binding `Text` mặc định OneWay → VM **không nhận giá trị gõ vào, không báo lỗi** | `[UI-BINDING]` | 2026-07-26 |
| G005 | `md_to_docx_kztek.py` báo `✗ PDF thất bại` (RPC failed) nhưng PDF **vẫn được tạo hợp lệ** | `[SCRIPT]` | 2026-07-27 |
| G006 | Tool "graphify" tên package PyPI thật là `graphifyy` (2 chữ y) — `pip install graphify` báo lỗi | `[CONFIG]` | 2026-07-29 |
| G007 | Edit tool báo "updated successfully" nhưng **không ghi vào disk** trên Windows trong 1 số branch context | `[AGENT-LOOP]` | 2026-08-04 |

**Category hiện có:** `[SCRIPT]` (lỗi Python script/tool) · `[ENCODING]` (lỗi mã hóa ký tự) · `[UI-BINDING]` (lỗi Avalonia/WinForms binding) · `[CONFIG]` (cài đặt sai, tên package sai) · `[GIT]` (git workflow) · `[AGENT-LOOP]` (agent bị stuck/loop)

---

## G004 — `KzPasswordTextBox`: binding `Text` phải `Mode=TwoWay` tường minh, Watermark có default, CornerRadius/FontSize không forward
**Category:** `[UI-BINDING]`

**Ngày phát hiện:** 2026-07-26
**Môi trường:** KztekComponentAvalonia (Avalonia 12.1.0), Windows 11
**Vấn đề:** Bind `Text="{Binding Password}"` trên `KzPasswordTextBox` → UI hiển thị giá trị ban đầu đúng nhưng VM KHÔNG nhận giá trị user gõ vào — save ra rỗng, không có lỗi binding nào. Ngoài ra placeholder tự hiện "Nhập mật khẩu" dù không set, và `CornerRadius`/`FontSize` set trong XAML không có tác dụng.
**Nguyên nhân:** `KzPasswordTextBox` là **UserControl** (không phải TextBox): `TextProperty` tự đăng ký bằng `AvaloniaProperty.Register` KHÔNG có `defaultBindingMode: TwoWay` → binding ngoài mặc định OneWay (khác `TextBox.Text` vốn default TwoWay như `KzTextBox : TextBox`). `WatermarkProperty` có default value `"Nhập mật khẩu"`. `CornerRadius`/`FontSize` của UserControl không được forward vào `PART_Border`/`PART_Input` (ApplySize ghi đè FontSize theo KzSize).
**Cách xử lý:** Luôn viết `Text="{Binding X, Mode=TwoWay}"`; set `Watermark=""` khi nguồn không có placeholder; điều chỉnh kích thước qua `KzSize`/`Height`, không set CornerRadius/FontSize trực tiếp.
**Lần đầu gặp:** STEP-3.2 PLAN-migrate-avalonia (migrate ucServerConfig — field RabbitMQ password)
**Không cần làm lại:** Không cần sửa library 5.BaseUI (workaround XAML đủ dùng); `KzTextBox` KHÔNG bị vấn đề này (kế thừa TextBox — TwoWay mặc định, nhận CornerRadius/FontSize/Height bình thường).

---

## G005 — `md_to_docx_kztek.py` báo "PDF thất bại" nhưng file PDF vẫn được tạo hợp lệ
**Category:** `[SCRIPT]`

**Ngày phát hiện:** 2026-07-27
**Môi trường:** Windows 11, `docx2pdf` + Microsoft Word COM Automation

**Vấn đề:**
Script in ra:
```
[docx2pdf] Lỗi: (-2147023170, 'The remote procedure call failed.', None, None)
[WARNING] Không thể xuất PDF. Cài thêm: docx2pdf | LibreOffice | pypandoc+pandoc
✗ PDF  thất bại (xem hướng dẫn ở trên)
```
Nhưng kiểm tra đĩa thì **file `.pdf` CÓ, kích thước bình thường, timestamp mới hơn `.docx` vài giây,
và hợp lệ** (header `%PDF-`, trailer `%%EOF`). Đã xác nhận lặp lại trên nhiều file khác nhau
(≥ 2 project độc lập, iPGSv4 và DoorAlarm v3), luôn cùng mã lỗi COM `-2147023170`.

**Nguyên nhân:**
`-2147023170` = `RPC_E_SERVER_DIED`. `docx2pdf` điều khiển Word qua COM; Word **xuất PDF xong rồi
mới** làm hỏng/ngắt kết nối RPC ở bước dọn dẹp/đóng instance, nên `docx2pdf` nhận exception ở bước
cleanup và báo thất bại — dù công việc chính (ghi file PDF) đã hoàn tất. Hay xảy ra khi Word bị gọi
liên tiếp nhiều lần trong thời gian ngắn (nhiều file `.md` chuyển đổi liên tục trong 1 phiên).

**Cách xử lý:**
1. **Luôn kiểm tra đĩa trước khi tin thông báo lỗi:**
   ```bash
   ls -la <file>.pdf   # có file + timestamp mới hơn .docx = đã xuất xong
   ```
   Kiểm hợp lệ nhanh: 5 byte đầu = `%PDF-`, vài byte cuối chứa `%%EOF`.
2. Nếu file có và hợp lệ → **coi như xong**, KHÔNG chạy lại script.
3. Chỉ khi file thật sự thiếu mới retry, và **tối đa 1–2 lần** (§9a: đừng retry vòng).

**Lần đầu gặp:** WF-MIGRATE DoorAlarmv3 → Avalonia (STEP-1.2/1.3, 2026-07-26); tái xác nhận khi xuất
UX-REVIEW payment-flow (iPGSv4, 2026-07-27).

**Không cần làm lại:**
- KHÔNG cài thêm LibreOffice/pypandoc theo gợi ý của script — `docx2pdf` vốn đã hoạt động.
- KHÔNG chạy lại script nhiều lần: mỗi lần lại mở/đóng Word, càng dễ gây lại lỗi RPC, trong khi
  PDF của lần trước đã đúng.

---

## G003 — `md_to_docx_kztek.py`: logo tìm theo CWD nên mất logo khi chạy từ project khác
**Category:** `[SCRIPT]`

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
**Category:** `[ENCODING]`

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

## G007 — Edit tool báo "updated successfully" nhưng không ghi vào disk (Windows)
**Category:** `[AGENT-LOOP]`

**Ngày phát hiện:** 2026-08-04
**Môi trường:** Windows 11, Git Bash (POSIX shell), nhánh git không phải main

**Vấn đề:**
Dùng Edit tool để patch file (VD: `.claude/templates/CODE-GRAPH-template.md`, `CLAUDE.md`) — tool báo "File updated successfully" nhưng `grep` sau đó trả về 0 kết quả. Thay đổi **không được ghi vào disk** mặc dù không có thông báo lỗi nào.

**Môi trường tái hiện:**
- Đang ở trên nhánh feature (`research/gitnexus-2026-08-04`) thay vì `main`
- File target là file lớn (CLAUDE.md > 500 dòng, CODE-GRAPH-template.md)
- Edit có nhiều lần thay thế liên tiếp trong cùng 1 lệnh

**Cách phát hiện:**
```bash
grep -n "keyword_from_edit" <file>   # trả về rỗng sau khi Edit tool báo thành công
# HOẶC
python3 -c "open('<file>').read().count('new_string')"  # trả về 0
```

**Cách xử lý (ĐÃ XÁC NHẬN):**
Viết nội dung patch vào file `.py` riêng rồi chạy bằng Bash:
```python
# patch_file.py
with open(r'path/to/file.md', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('OLD_STRING', 'NEW_STRING')
with open(r'path/to/file.md', 'w', encoding='utf-8') as f:
    f.write(content)
```
```bash
PYTHONIOENCODING=utf-8 python3 patch_file.py
```

**Lần đầu gặp:** WF-GITHUB-RESEARCH Mode A Bước 4b — áp dụng GX-1 đến GX-6 (2026-08-04)

**Không cần làm lại:**
- KHÔNG retry Edit tool nhiều lần — nó sẽ tiếp tục báo "updated successfully" mà không ghi disk
- KHÔNG dùng Write tool để ghi lại toàn bộ file lớn (rủi ro mất nội dung nếu format sai)
- Dùng Python `str.replace()` — đơn giản, idempotent, và verifiable ngay sau khi chạy


## G001 — `md_to_docx_kztek.py`: thiếu `python-docx`/`Pillow`; PDF là optional trên cloud/sandbox
**Category:** `[SCRIPT]`

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

## G006 — Tool "graphify": tên package PyPI thật là `graphifyy` (2 chữ y), không phải `graphify`
**Category:** `[CONFIG]`

**Ngày phát hiện:** 2026-07-29

**Môi trường:** Windows 11, Python 3.10.11, pip 23.0.1

**Vấn đề:**
Chạy theo trực giác từ tên tool "graphify" (Graphify-Labs/graphify trên GitHub):
```bash
pip install graphify
```
→ `ERROR: No matching distribution found for graphify`. Package `graphify` trên PyPI không tồn tại
hoặc không phải package này — dễ khiến agent nghĩ tool chưa release, hoặc bịa cách cài khác.

**Nguyên nhân:**
Tên repo GitHub (`Graphify-Labs/graphify`) và tên package publish lên PyPI **không trùng nhau**.
Theo `docs/research/RESEARCH-graphify-2026-07-29.md` §1 (đã research từ README repo gốc), package
thật là `graphifyy` — xác nhận bằng `pip index versions graphifyy` (trả về danh sách version từ
0.1.1 đến 0.9.29, active development).

**Cách xử lý:**
Luôn dùng:
```bash
python -m pip install graphifyy
```
Nếu nghi ngờ tên package của bất kỳ tool GitHub nào không khớp tên repo, xác nhận trước bằng:
```bash
python -m pip index versions <tên-nghi-ngờ>
```
thay vì đoán và cài nhầm.

**Lần đầu gặp:** Trả lời user hỏi cách dùng graphify cho project `App-Access-V2` (2026-07-29);
tạo skill `.claude/commands/graphify.md` ngay sau đó có ghi lại gotcha này trong bảng Red Flags.

**Không cần làm lại:** Không cần thử biến thể tên khác (`graphify-cli`, `pygraphify`, ...) —
`graphifyy` là tên chính thức duy nhất, đã xác nhận qua `pip index versions`.

---

<!-- Thêm entry mới theo format:

## G00N — [Tên vấn đề ngắn gọn]
**Category:** `[SCRIPT]` | `[ENCODING]` | `[UI-BINDING]` | `[CONFIG]` | `[GIT]` | `[AGENT-LOOP]` | (hoặc thêm category mới nếu không khớp)

**Ngày phát hiện:** YYYY-MM-DD
**Môi trường:** [OS / platform / version]
**Vấn đề:** [Mô tả triệu chứng cụ thể]
**Nguyên nhân:** [Root cause đã xác định]
**Cách xử lý:** [Giải pháp, workaround, hoặc cách tránh]
**Lần đầu gặp:** [Context task / session]
**Không cần làm lại:** [Những gì đã thử mà KHÔNG hoạt động — để tránh lặp lại]

BẮT BUỘC: Sau khi thêm entry mới → cập nhật bảng "Mục lục nhanh + Bảng lọc theo Category" ở đầu file.

-->
