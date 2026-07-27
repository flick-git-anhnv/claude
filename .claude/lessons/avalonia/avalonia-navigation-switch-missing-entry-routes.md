---
category: avalonia
tags: [navigation, migration, parallel-agents, integration-testing]
severity: critical
created: 2026-07-20
updated: 2026-07-20
project-origin: iPGSv4 (migrate-ipgs-kiosk-avalonia)
---

# Navigation switch-case thiếu route "entry point" khi nhiều task migrate song song tự thêm route riêng lẻ

## Tình huống gặp phải

Migrate `IPGS.Kiosk` (WinForms) sang Avalonia, dùng pattern `INavigationService.NavigateTo(string viewKey, ...)` với 1 switch-case lớn trong `WindowNavigationService` (`MainWindow.axaml.cs`). Nhiều task migrate (2.B3, 2.B4, 2.C1-C4, 2.D1-D6, 2.E1-E2) chạy SONG SONG qua nhiều subagent, mỗi task tự thêm `case` cho route MÀN HÌNH ĐÍCH của chính nó, và tự thêm hằng số route key vào `AppRoutes.cs`.

## Triệu chứng / Lỗi

User test thực tế: chọn ngôn ngữ ở màn hình đầu xong, bấm không chuyển sang màn chọn loại xe — đứng yên, không lỗi, không crash. Build "PASS 0 error" hoàn toàn bình thường.

## Nguyên nhân gốc rễ (Root Cause)

`SelectLanguageViewModel` gọi `_navigation.NavigateTo("SelectVehicleType", ...)` — route key này ĐÃ được định nghĩa trong `AppRoutes.SelectVehicleType` (task 2.B4 tạo), nhưng **không task nào từng thêm `case AppRoutes.SelectVehicleType:` vào switch trong `MainWindow.axaml.cs`** — vì task 2.B4 (tạo SelectVehicleTypeView) chỉ chịu trách nhiệm màn hình ĐÍCH của chính route đó (2.C-nhóm/2.D-nhóm), không phải route DẪN VÀO nó. Tương tự thiếu cả `AppRoutes.CarBranch` và `AppRoutes.MotorBranch` (entry point vào nhánh Ô tô/Xe máy) — mỗi task chỉ thêm case cho đích ĐẾN, quên rằng route DẪN VÀO cũng cần 1 case riêng, và không ai được giao trách nhiệm "wire toàn bộ chuỗi entry point" ở cuối.

Switch có `default:` chỉ log "Unknown route" rồi im lặng giữ nguyên màn hình — không throw, không crash, nên KHÔNG bị phát hiện qua build hay chạy nhanh test khác không đi đúng luồng đó.

## Giải pháp

1. Đọc toàn bộ `AppRoutes.cs` — liệt kê MỌI hằng số route key đã định nghĩa.
2. Grep toàn bộ `case AppRoutes\.` trong file switch — liệt kê route đã có case xử lý.
3. Đối chiếu 2 danh sách — route nào có hằng số nhưng KHÔNG có case là gap; route nào được `NavigateTo(string_literal, ...)` gọi trực tiếp (không qua hằng số `AppRoutes.X`) cũng phải grep riêng bằng chuỗi để không bỏ sót (VD `"SelectVehicleType"` được gọi trực tiếp bằng string literal ở `SelectLanguageViewModel`, không qua `AppRoutes.SelectVehicleType`, dễ bị bỏ sót nếu chỉ grep `AppRoutes\.`).
4. Thêm case còn thiếu, chú ý namespace/using cần thiết cho ViewModel/View đích (kiểm tra ctor signature chính xác trước khi gọi `new`).

## Áp dụng lại (How to reuse)

- Khi kiến trúc navigation dùng pattern "string route key + switch-case tập trung 1 chỗ" VÀ nhiều agent/task làm song song, PHẢI có 1 bước cuối cùng (sau khi tất cả task hoàn thành, hoặc định kỳ giữa chừng) đối chiếu TOÀN BỘ route key đã định nghĩa (constants + string literal gọi trực tiếp) với TOÀN BỘ case đã implement — không giả định "mỗi agent tự lo route của mình" là đủ, vì route ĐI VÀO 1 màn hình thường không thuộc trách nhiệm rõ ràng của agent nào.
- Khi audit visual/parity (lesson `avalonia-migration-theme-drift-not-caught-by-build-pass.md`), NÊN kết hợp luôn bước audit "route coverage" này — cùng nguyên tắc: build PASS không đảm bảo hành vi đúng.
- `default:` case chỉ log mà không throw là con dao 2 lưỡi: an toàn (không crash) nhưng che giấu bug hoàn toàn — cân nhắc thêm assert/warning box hiển thị NGAY trên UI trong môi trường Debug khi gặp route lạ, thay vì chỉ ghi log file (dễ bỏ qua khi test nhanh).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Route gọi bằng string literal trực tiếp (không qua hằng số `AppRoutes.X`) dễ lọt lưới khi grep chỉ tìm `AppRoutes\.` — phải grep cả `NavigateTo\("` để bắt string literal.
- ⚠️ "Entry point route" (route DẪN VÀO 1 nhóm màn hình mới, VD `CarBranch`/`MotorBranch`) khác với "route đích cụ thể bên trong nhóm" (VD `CarLocation`, `MotoCash`) — khi giao task theo từng cụm Form, dễ quên rằng bản thân "cửa vào" cụm đó cũng cần người phụ trách.

## Tham chiếu

- Project liên quan: `iPGSv4` — `IPGS.Kiosk.Avalonia/Views/MainWindow.axaml.cs`, plan `PLAN-migrate-ipgs-kiosk-avalonia-2026-07-20`
- Liên quan: `avalonia-migration-theme-drift-not-caught-by-build-pass.md` (cùng nguyên tắc: build PASS ≠ hành vi đúng)
