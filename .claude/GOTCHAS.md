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
| G001 | `scripts/md_to_docx_kztek.py` — thiếu `python-docx`/`Pillow`; PDF không cần trên cloud/sandbox | 2026-07-12 |

---

## G001 — `scripts/md_to_docx_kztek.py`: thiếu `python-docx`/`Pillow`; PDF là optional trên cloud/sandbox

**Ngày phát hiện:** 2026-07-12

**Môi trường:** Linux sandbox (claude.ai / cloud agent)

**Vấn đề ban đầu:**
Chạy `python scripts/md_to_docx_kztek.py <file.md>` báo `ModuleNotFoundError: No module named 'docx'` vì thiếu package `python-docx` và `Pillow`.

**Khắc phục (ĐÃ XÁC NHẬN HOẠT ĐỘNG):**
```bash
pip install python-docx Pillow
```
Sau khi cài, DOCX tạo thành công. Đây là fix dứt điểm cho lỗi ModuleNotFoundError.

**Về PDF export trên cloud/sandbox:**
LibreOffice đã cài tại `/usr/bin/soffice`, nhưng `soffice --headless --convert-to pdf` báo lỗi "source file could not be loaded" trong môi trường sandbox — đây là hiện tượng đã biết, KHÔNG cần debug thêm.

Theo chỉ đạo: **trên cloud/sandbox, PDF không cần thiết**. Dùng `--no-pdf` làm mặc định:
```bash
python scripts/md_to_docx_kztek.py <file.md> --no-pdf
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
