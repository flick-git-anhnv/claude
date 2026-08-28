---
category: dotnet-general
tags: [itextsharp, pdf, LocationTextExtractionStrategy, PdfTextExtractor, multi-page]
severity: high
created: 2026-08-13
updated: 2026-08-13
project-origin: ExcelTool (5.Friends/Trang)
---

# iTextSharp: dùng chung 1 `LocationTextExtractionStrategy` cho nhiều trang → dữ liệu trang sau bị cắt/sai, không lỗi rõ ràng

## Tình huống gặp phải

> Đọc hóa đơn PDF 3 trang (bảng hàng hóa 80 dòng chia 26/41/13 dòng qua 3 trang) bằng
> `PdfTextExtractor.GetTextFromPage(pdfReader, pageNumber, strategy)` trong vòng lặp
> `for (pageNumber = 1..NumberOfPages)`. Code gốc còn có thêm bug khác (chỉ đọc cứng
> trang 1), sau khi sửa để loop qua tất cả trang thì tưởng đã xong.

## Triệu chứng / Lỗi

> Sau khi sửa lỗi "chỉ đọc trang 1" bằng cách thêm vòng lặp qua `NumberOfPages`, kết
> quả vẫn SAI nhưng theo kiểu tinh vi hơn: parse ra **41 dòng** thay vì 80 — không
> phải 0, không crash, không exception — dễ nhầm tưởng đã fix đúng nếu chỉ nhìn qua
> "có ra kết quả là được". Debug từng trang cho thấy: trang 1 đúng 26 dòng, trang 2
> chỉ ra 15/41 dòng (thiếu), trang 3 ra 0/13 dòng.

## Nguyên nhân gốc rễ (Root Cause)

`ITextExtractionStrategy strategy = new LocationTextExtractionStrategy();` được khai
báo **1 lần bên ngoài vòng lặp trang**, rồi truyền cùng 1 instance vào
`GetTextFromPage()` cho MỌI trang. `LocationTextExtractionStrategy` là stateful —
nó tích lũy vị trí/text đã render nội bộ qua các lần gọi `RenderText()`. Dùng lại
cùng instance cho trang tiếp theo khiến state cũ từ trang trước lẫn vào, làm text
trả về cho các trang sau bị cắt xén/lệch — không phải lỗi rõ ràng như exception hay
0 kết quả, nên rất dễ bỏ sót khi chỉ test qua loa.

## Giải pháp

```csharp
for (int pageNumber = 1; pageNumber <= pdfReader.NumberOfPages; pageNumber++)
{
    // PHẢI tạo strategy MỚI cho MỖI trang — không được khai báo ngoài vòng lặp
    ITextExtractionStrategy strategy = new LocationTextExtractionStrategy();
    string textFromPage = PdfTextExtractor.GetTextFromPage(pdfReader, pageNumber, strategy);
    // ... xử lý textFromPage ...
}
```

1. Di chuyển `new LocationTextExtractionStrategy()` (hoặc bất kỳ
   `ITextExtractionStrategy` nào khác — `SimpleTextExtractionStrategy` cũng có nguy
   cơ tương tự) vào BÊN TRONG vòng lặp trang.
2. Không tin tưởng "có ra kết quả, không exception" là bằng chứng đủ khi verify fix
   đa trang — phải đếm số dòng/số item thực tế parse được TỪNG TRANG và so với số
   lượng kỳ vọng thực tế trong file mẫu.

## Áp dụng lại (How to reuse)

- Khi thấy code lặp qua nhiều trang PDF bằng `PdfTextExtractor.GetTextFromPage` mà
  tái sử dụng 1 biến `strategy` khai báo bên ngoài vòng lặp → sửa ngay, đây là bug
  tiềm ẩn dù chưa report.
- Khi verify 1 bug "chỉ đọc được 1 phần dữ liệu nhiều trang", đừng dừng lại ở "build
  pass + không crash" — viết 1 harness console nhỏ độc lập chạy đúng logic đã sửa
  trên file mẫu THẬT, in ra số dòng/kết quả từng trang để so khớp con số kỳ vọng
  (ví dụ tổng dòng hàng hóa phải khớp số trang × số dòng mỗi trang theo file gốc).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Bug này KHÔNG lộ ra ở trang đầu tiên (trang 1 luôn đúng vì chưa có state cũ để
  lẫn vào) — chỉ lộ ra từ trang 2 trở đi, và mức độ sai (thiếu bao nhiêu dòng) không
  cố định, phụ thuộc lượng text đã render trước đó — dễ đánh lừa là "PDF trang đó bị
  lỗi định dạng" chứ không nghĩ do code dùng lại strategy.
- ⚠️ Đây là bug THỨ HAI chồng lên bug ban đầu ("chỉ đọc trang 1 vì code hardcode page
  1") — sau khi sửa bug đầu (thêm vòng lặp qua các trang) tưởng xong, nhưng vẫn cần
  verify bằng số liệu thật vì bug thứ hai (state) chỉ lộ ra khi thực sự có ≥2 trang
  chứa dữ liệu bảng.

## Tham chiếu

- Thư viện: iTextSharp 5.5.13.3 (`iTextSharp.text.pdf.parser.LocationTextExtractionStrategy`)
- Project liên quan: ExcelTool (i:\5.Friends\Trang\ExcelTool) — `Test\Form1.cs`, hàm `btnImport_Click`
