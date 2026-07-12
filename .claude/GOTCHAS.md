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
| G001 | `scripts/md_to_docx_kztek.py` — PDF export thất bại trên Linux không có LibreOffice | 2026-07-12 |

---

## G001 — PDF export thất bại: thiếu LibreOffice trên Linux

**Ngày phát hiện:** 2026-07-12

**Môi trường:** Linux sandbox (claude.ai / cloud agent), không có GUI

**Vấn đề:**
Chạy `python scripts/md_to_docx_kztek.py <file.md>` thành công tạo DOCX nhưng báo lỗi PDF:

```
⚠  PDF: Không thể xuất PDF (thử cài docx2pdf hoặc LibreOffice)
```

Script cố gắng dùng `docx2pdf` (Windows/macOS) hoặc gọi `libreoffice --headless` (Linux). Cả hai đều thất bại trong môi trường Linux sandbox:
- `docx2pdf` yêu cầu Microsoft Word (chỉ có trên Windows/macOS)
- `libreoffice --headless` không được cài sẵn trong môi trường sandbox

**Nguyên nhân:**
- Môi trường cloud agent không có LibreOffice và không có Microsoft Word
- Script không raise exception — chỉ in cảnh báo và tiếp tục — nên DOCX vẫn được tạo

**Cách xử lý:**
1. Dùng flag `--no-pdf` để chỉ tạo DOCX và bỏ qua PDF:
   ```bash
   python scripts/md_to_docx_kztek.py docs/research/RESEARCH-xyz.md --no-pdf
   ```
2. Ghi rõ trong output agent: "PDF thất bại (thiếu LibreOffice), DOCX OK"
3. KHÔNG coi đây là lỗi blocking — DOCX là artifact chính; PDF là nice-to-have
4. Nếu cần PDF thật: cài LibreOffice trên máy local rồi chạy lại

**Lần đầu gặp:** Bước 1.2 — WF-GITHUB-RESEARCH nghiên cứu affaan-m/ecc (2026-07-12)

**Không cần làm lại:**
- Không cần thử `pip install docx2pdf` — nó phụ thuộc vào Word/LibreOffice, không hoạt động độc lập trên Linux sandbox
- Không cần điều chỉnh script — script đã xử lý đúng, chỉ cần dùng `--no-pdf`

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
