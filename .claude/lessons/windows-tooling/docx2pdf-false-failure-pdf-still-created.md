# docx2pdf báo lỗi "Word.Application.Quit / RPC failed" nhưng PDF vẫn được tạo đúng

**Category:** windows-tooling
**Ngày:** 2026-07-26
**Môi trường:** Windows 11 Pro, MS Word (COM), Python + `docx2pdf`, script `md_to_docx_kztek.py`

---

## Triệu chứng

Xuất hàng loạt file `.md` sang DOCX + PDF:

```
✓ DOCX hoàn thành
[docx2pdf] Lỗi: (-2147023170, 'The remote procedure call failed.', None, None)
[docx2pdf] Lỗi: Word.Application.Quit
[WARNING] Không thể xuất PDF. Cài thêm: docx2pdf | LibreOffice | pypandoc+pandoc
✗ PDF  thất bại
```

7/8 file báo thất bại. Chạy lại **từng file một** vẫn báo lỗi y hệt → tưởng môi trường hỏng,
định đi cài LibreOffice/pypandoc.

## Nguyên nhân thật

`docx2pdf` điều khiển MS Word qua COM automation. Word **đã convert xong và ghi file PDF ra đĩa**;
ngoại lệ chỉ phát sinh ở bước **đóng/giải phóng instance Word** (`Quit`) khi nhiều tiến trình Word
được mở–đóng liên tiếp trong thời gian ngắn. Vì ngoại lệ ném ra **sau** khi PDF đã ghi, thông báo
lỗi hoàn toàn không phản ánh kết quả thật.

## Cách xử lý

Đừng tin thông báo lỗi — **kiểm tra file trên đĩa** trước khi kết luận:

```powershell
Get-ChildItem -Path .\docs -Recurse -Include *.pdf |
  Select-Object Name, @{n='KB';e={[math]::Round($_.Length/1KB)}}, LastWriteTime
```

PDF tồn tại + kích thước hợp lý + `LastWriteTime` khớp lần chạy ⇒ **thành công**, bỏ qua cảnh báo.

## Không cần làm lại

- Không cần cài LibreOffice / pypandoc + pandoc — Word vẫn hoạt động bình thường.
- Không cần retry từng file: retry cho ra đúng thông báo lỗi giả y hệt, tốn thời gian vô ích.
- Không cần sửa `md_to_docx_kztek.py` (có thể cải tiến sau: kiểm `os.path.exists(pdf)` trước khi
  báo thất bại), workflow không bị chặn.
