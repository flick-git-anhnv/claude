---
category: avalonia
tags: [datagrid, column-width, auto-sizing, kzbadge]
severity: medium
created: 2026-07-27
updated: 2026-08-06
project-origin: iPGSv4
---

# DataGrid cột Width="Auto" không đo lại khi thêm dòng mới nội dung dài hơn

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Avalonia `DataGrid`, khai báo `DataGridTemplateColumn Width="Auto" MinWidth="140"`, cell
template chứa `KzBadge` hiển thị trạng thái dạng text (VD "Không xác định").

## Triệu chứng / Lỗi

Cùng một cột, các dòng cũ hiện đủ chữ "Không xác định" nhưng dòng MỚI được thêm vào (thêm
item vào collection sau khi grid đã render) lại hiện cụt "Không xá...". Nới `MinWidth` từ
140 lên 175 vẫn không hết — bề rộng cột không đổi theo MinWidth mới.

```
Không có exception. Chỉ là text bị cắt ở dòng mới thêm, dòng cũ vẫn đúng.
```

## Nguyên nhân gốc rễ (Root Cause)

`Width="Auto"` tính bề rộng cột dựa trên nội dung tại thời điểm dòng được **materialize**
(lần đầu render). Khi thêm dòng mới có nội dung dài hơn vào collection đang hiển thị, cột
KHÔNG được đo lại — Avalonia DataGrid không tự re-measure `Auto` column khi có item mới,
chỉ đo tại lần đầu build layout. `MinWidth` không cứu được vì vấn đề không nằm ở giá trị
tối thiểu — cột đã "chốt" một bề rộng cụ thể (do Auto), không phải đang bị giới hạn bởi
MinWidth quá nhỏ.

## Giải pháp

Đặt bề rộng **cố định** đủ chứa nội dung dài nhất có thể xuất hiện:

```xml
<!-- Trước (lỗi — không đo lại khi thêm dòng mới) -->
<DataGridTemplateColumn Width="Auto" MinWidth="140"> ... </DataGridTemplateColumn>

<!-- Sau (fix) -->
<DataGridTemplateColumn Width="175"> ... </DataGridTemplateColumn>
```

1. Xác định nội dung dài nhất có thể xuất hiện trong cột (kể cả case chưa từng thấy lúc
   design, VD text trạng thái dài).
2. Đặt `Width` là con số cố định đủ chứa nội dung đó — không dùng `Auto`.
3. Nếu cần co giãn theo không gian còn lại của grid → dùng `Width="*"` (tỷ lệ), không phải
   `Auto`.

## Áp dụng lại (How to reuse)

- Khi thấy CÙNG một cột mà dòng này hiện đủ chữ, dòng khác (đặc biệt dòng mới thêm) hiện
  cụt → nghi ngay cột đang dùng `Width="Auto"`, không phải lỗi MinWidth.
- Với cột chứa nội dung độ dài thay đổi theo dòng (badge trạng thái, tên tùy biến...),
  KHÔNG dùng `Auto` — luôn đặt `Width` cố định hoặc `*`.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đừng cố fix bằng cách tăng `MinWidth` — không giải quyết được gốc rễ vì cột đã chốt
  bề rộng từ lần materialize đầu, MinWidth chỉ có tác dụng nếu Auto-width tính ra nhỏ hơn nó.
- ⚠️ Dấu hiệu nhận biết đặc trưng: lỗi chỉ xuất hiện ở dòng được thêm SAU khi grid đã
  render lần đầu — nếu test bằng cách seed toàn bộ dữ liệu rồi mới mở màn hình, bug này rất
  dễ không lộ ra (vì tất cả dòng cùng materialize 1 lượt).

## Tham chiếu

- Commit tham chiếu: `f2ea635` (repo iPGSv4), phát hiện 2026-07-27.
- Project liên quan: `iPGSv4`.

## Lần gặp lại (App-Access-V2, 2026-08-06)

Cùng root cause, biến thể khác: KHÔNG cần thêm dòng mới — chỉ cần Status/Result của MỘT dòng
đã tồn tại đổi qua INPC (VD "Đang thực hiện" → "Xong", "Đang xử lý" → "Đã xử lý") là badge đã
bị kẹt bề rộng cũ, hiện cụt không dấu "..." (VD "Thành công" hiện "Th", "Xong" hiện "Xo") —
KHÔNG cần đợi tới lúc user thêm dòng ở cuối list. Kèm thêm effect phụ: đổi
`ObservableCollection.Add` → `Insert(0, ...)` (newest-on-top) làm container DataGrid bị tái sử
dụng dồn dập hơn (đặc biệt khi code-behind có tầng filter riêng — `_filteredRows.Clear()` +
`Add()` lại toàn bộ mỗi lần `CollectionChanged`), khiến bug lộ ra RÕ và THƯỜNG XUYÊN hơn hẳn so
với trước (trước đó Add ở cuối, dòng top ít đổi nên ít khi lộ). Đã thử `DataGrid.InvalidateMeasure()`
sau khi rebuild ItemsSource trước — KHÔNG fix được (cột Auto tự "chốt" bề rộng nội bộ, không phải
do view chưa remeasure) — đúng như ghi chú "Đừng cố fix bằng MinWidth" ở trên, InvalidateMeasure
cũng vô ích vì lý do tương tự. Fix cuối cùng: đổi `Width="Auto" MinWidth="..."` → `Width="<số cố
định>"` cho đúng 3 cột (`RegisterStatusPanelView.axaml` "Trạng thái", `RegisterStatusTabView.axaml`
"Trạng thái", `ServerDataChangeCardView.axaml` "Kết quả") — khớp 100% giải pháp gốc ở trên.
