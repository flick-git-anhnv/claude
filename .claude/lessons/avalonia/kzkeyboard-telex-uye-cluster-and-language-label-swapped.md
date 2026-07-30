---
category: avalonia
tags: [keyboard, telex, vietnamese, ime, virtual-keyboard, kzkeyboard]
severity: high
created: 2026-07-30
updated: 2026-07-30
project-origin: MolexAPP (MolexKioskApp)
---

# KzKeyboard: label ngôn ngữ bị đảo ngược + KzTelexEngine đặt sai dấu thanh cho cụm "uyê" và "ao/eo"

## Tình huống gặp phải

Thêm 1 view nhập tên (`RegistrationNameView`) dùng `KzKeyboard` (component dùng chung `KztekComponentAvalonia`) để gõ tên khách bằng Telex tiếng Việt. User test gõ "Nguyễn" trên bàn phím ảo, phát hiện 2 lỗi trực quan.

## Triệu chứng / Lỗi

1. Nút toggle ngôn ngữ đang tô đậm (nền navy — tức là đang ở trạng thái active theo cách vẽ của `SHIFT`/`TELEX`) nhưng lại hiện chữ "ENG" trong khi bàn phím đang thực sự ở chế độ gõ tiếng Việt (Telex bật) — gây hiểu lầm "đang chọn tiếng Việt nhưng sao nút EN lại sáng".
2. Gõ "nguyeenx" (Telex cho "Nguyễn") ra kết quả sai: "Nguỹên" (dấu ngã nằm trên "y") thay vì đúng "Nguyễn" (dấu ngã trên "ê").
3. Gõ "vaof" (Telex cho "vào") ra kết quả sai: "vaò" (dấu huyền nằm trên "o") thay vì đúng "vào" (dấu huyền trên "a"). Tương tự với mọi từ có cụm "ao"/"eo" (báo, kéo, leo, sáo...).

## Nguyên nhân gốc rễ (Root Cause)

**Lỗi 1 — `KzKeyboard.cs` (`DrawKey`):** label hiển thị cho phím TELEX bị viết ngược so với biến trạng thái:
```csharp
string lbl = val == "TELEX" ? (_telexEnabled ? "ENG" : "VIE") : ...
```
Trong khi highlight (`telexActive = val == "TELEX" && _telexEnabled`) tô nền đậm đúng khi `_telexEnabled == true`. Kết quả: khi Telex bật (đang gõ tiếng Việt) → nút sáng đậm NHƯNG label lại in "ENG" (cái sẽ chuyển TỚI nếu bấm), ngược với quy ước UX của cả nút SHIFT ngay cạnh (label luôn phản ánh trạng thái HIỆN TẠI, không phải trạng thái sẽ chuyển tới).

**Lỗi 2 — `KzTelexEngine.FindTonePos` (đặt dấu thanh, cụm "uyê"):** quy tắc chung "cụm ≥3 nguyên âm → đặt dấu ở giữa (index 1)" đúng cho các cụm như "yêu", "hiếu", "chiều" (i/y-ê-u, nhân âm tiết ê nằm ở giữa cụm) nhưng SAI cho cụm "uyê" (u-y-ê, như trong "nguyễn", "chuyện", "khuyến") — ở cụm này nhân âm tiết là "ê" nằm CUỐI cụm, không phải giữa. Code đã có sẵn xử lý đặc biệt cho "qu" (bỏ "u" ra khỏi cụm vì là âm đệm) nhưng KHÔNG có xử lý cho "uyê" đứng sau phụ âm thường (ng, ch, kh...) — trường hợp này "u" vẫn được tính là 1 nguyên âm đầy đủ trong cụm nên rơi vào nhánh "3+ vowel → middle" và đặt nhầm dấu lên "y".

**Lỗi 3 — `KzTelexEngine.FindTonePos` (đặt dấu thanh, cụm "ao"/"eo"):** với cụm 2 nguyên âm, "Rule A" (bán nguyên âm cuối i/y/u → đặt dấu lên nguyên âm ĐẦU, ví dụ ai/ay/âu/ôi/ui) chỉ liệt kê `lastBase` thuộc `{i, y, u}` mà thiếu `o` — trong khi "ao" và "eo" về mặt ngữ âm cũng là song âm khép (closing diphthong) giống hệt nhóm i/y/u, chỉ khác chữ cái cuối. Do thiếu case này, "ao"/"eo" rơi xuống "Rule C" (mặc định "đặt cuối cụm", vốn chủ ý dùng cho oa/oe kiểu cũ) và đặt nhầm dấu lên "o" thay vì nguyên âm đầu (a hoặc e).

## Giải pháp

1. `KzKeyboard.cs` — đảo lại label cho khớp trạng thái:
```csharp
string lbl = val == "TELEX"
    ? (_telexEnabled ? "VIE" : "ENG")   // VIE sáng khi Telex bật, ENG khi tắt
    : ...
```

2. `KzTelexEngine.cs` — thêm ngoại lệ cho cụm "uyê" TRƯỚC khi áp quy tắc "middle":
```csharp
if (len == 3)
{
    GetVowelInfo(char.ToLowerInvariant(word[clusterStart]),     out char b0, out _);
    GetVowelInfo(char.ToLowerInvariant(word[clusterStart + 1]), out char b1, out _);
    GetVowelInfo(char.ToLowerInvariant(word[clusterStart + 2]), out char b2, out _);
    if (b0 == 'u' && b1 == 'y' && b2 == 'ê') return clusterEnd; // nguyễn, chuyện, khuyến...
}
if (len >= 3) return clusterStart + 1;

// Rule A: coda i/y/u → FIRST (ai, ay, âu, ôi, ui...)
if (lastBase == 'i' || lastBase == 'y' || lastBase == 'u') return clusterStart;

// Rule A2 (bổ sung): coda 'o' cùng nhóm bán nguyên âm khép như trên → FIRST
if (lastBase == 'o' && (startBase == 'a' || startBase == 'e')) return clusterStart; // báo, kéo, vào, leo
```

## Áp dụng lại (How to reuse)

- Khi thêm/sửa bất kỳ nút toggle 2 trạng thái nào có cả highlight (nền đậm) VÀ label text (SHIFT, TELEX, hoặc tương tự) → luôn kiểm tra label phải mô tả trạng thái HIỆN TẠI đang active, khớp với điều kiện tô nền — không mô tả trạng thái sẽ chuyển tới, dễ gây nhầm lẫn ngược.
- Khi sửa/mở rộng `KzTelexEngine` (hoặc viết engine Telex tương tự) — đừng chỉ test các từ dùng nguyên âm rời rạc (a, e, o...) mà PHẢI test riêng:
  - Cụm "uyê" (nguyễn, chuyện, khuyến, tuyết, quyết) — dễ bị quy tắc tổng quát "đặt dấu giữa cụm 3 nguyên âm" xử lý sai.
  - Cụm "ao"/"eo" (báo, kéo, vào, leo, sáo) — dễ bị bỏ sót khỏi nhóm "bán nguyên âm cuối → đặt đầu" nếu chỉ liệt kê i/y/u mà quên o.
  - Khi thêm 1 rule mới cho 1 cụm nguyên âm cụ thể, luôn tự hỏi: "còn ký tự nào tương đương về ngữ âm (glide/nucleus) nhưng bị bỏ sót trong cùng điều kiện if không?" — cả 2 bug trên đều là dạng "liệt kê thiếu 1 phần tử trong tập hợp cùng vai trò ngữ âm".
- Cụm "qu" + "yê" (quyết, quyền) đã đúng sẵn nhờ logic skip-glide cho "qu" — không cần sửa, chỉ "uyê" đứng sau phụ âm thường mới thiếu xử lý.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Build vẫn PASS 0 lỗi cho cả 2 bug — đây là lỗi hành vi/UX thuần túy, chỉ phát hiện được khi gõ thử bằng tay trên app thật (đúng như CLAUDE.md yêu cầu chạy app thật trước khi báo hoàn thành UI).
- ⚠️ Đây là component DÙNG CHUNG (`KztekComponentAvalonia`, qua `ProjectReference`) — sửa ở đây ảnh hưởng MỌI project tham chiếu tới, không chỉ MolexAPP. Nhớ rebuild/kiểm tra các project khác đang dùng `KzKeyboard`/Telex nếu cần.
- ⚠️ Đừng mở rộng ngoại lệ "uyê" thành tổng quát hóa quá tay (VD áp nhầm cho "yêu"/"iêu") — chỉ đúng 3 base-vowel theo thứ tự chính xác u→y→ê mới được đặt dấu cuối cụm.

## Tham chiếu

- File: `KztekComponentAvalonia/Controls/KzKeyboard.cs` (DrawKey, dòng label TELEX), `KztekComponentAvalonia/Controls/KzTelexEngine.cs` (FindTonePos)
- Project liên quan: MolexAPP (MolexKioskApp) — phát hiện khi thêm `RegistrationNameView`; component dùng chung `E:\KZTEK\Code_Git\5.BaseUI\KztekComponentAvalonia`
