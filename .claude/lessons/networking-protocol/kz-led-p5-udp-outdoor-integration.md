---
category: networking-protocol
tags: [led, udp, outdoor-led, kztek-iparking, protocol]
severity: medium
created: 2026-07-18
updated: 2026-07-18
project-origin: IPGSv1
---

# Thêm loại bảng LED ngoài trời mới (P5 UDP) chỉ cần mở rộng enum + switch, không cần class mới

## Tình huống gặp phải

> Tích hợp bảng LED ma trận ngoài trời loại mới "P5" (giao thức UDP string, xem
> `Tai lieu/outdoor_led/KZ_LED_iParkingLots_P5_Protocol_V1.0.docx`) vào project
> `iParkingPGS` (IPGSv1). Trước khi code, tưởng cần viết class UDP mới song song
> `OutDoorLed.cs`.

## Triệu chứng / Lỗi

Không phải lỗi — là nhận ra sau khi đọc code: `iParkingPGS.OutdoorLeds.OutDoorLed`
+ `UdpTools` + `LedCmd`/`CmdBuilder` đã implement **gần như y hệt** giao thức P5:
`GetFirmwareVersion?/`, `ChangeIP?/...`, `SetScreenResolution?/NumOfLine=.../Row=.../Col=...`,
`GetScreenResolution?/`, `SetLineCurrent?/Line=.../FontSize=.../Text=<Colour=N>...`,
`AutoDetect?`. Response parse dùng chung `EventHelpers.GetEventContent` (split `/` rồi `key=value`).

## Nguyên nhân gốc rễ (Root Cause)

Code cũ được thiết kế generic theo `EM_ModuleType` (enum) chứ không hard-code theo
từng dòng LED — hầu hết command string không phụ thuộc module type
(`LedCmd._Get_Screen_Solution()`, `_Get_Module_Type()`...). Chỉ vài chỗ có
`switch (moduleType)` cần thêm case: `CmdBuilder.getFirmwareVersion`,
`CmdBuilder._Set_Screen_Resolution` + `CheckResolutionCapacity`,
`CmdBuilder._Get_Screen_Solution`, và `OutDoorLed.Check_Color`.

Giao thức P5 **thiếu 2 lệnh** mà codebase cũ chưa có: `ClearScreen?/` và `Reboot?/`
(cần thêm mới vào `CmdBuilder`/`OutDoorLed`). Ngược lại P5 **không hỗ trợ**
`SetModuleType?/`/`GetModuleType?/`/`ChangeMacAddress?/`/`ResetDefault?/` — nhưng
không sao vì UI thực tế (`frmOutDoorLed.btnSave_Click` → `UpdateRealDeviceSetting`)
chỉ gọi `Set_Screen_Resolution`, dòng gọi `Set_Module_Type` đã bị comment sẵn.

Quy tắc Row/Col của P5 **khác** P10: P10 ràng buộc Row×Col theo từng `NumberOfLine`
cụ thể (bảng cứng trong `CheckResolutionCapacity`), còn P5 đơn giản là
Row∈{32,64} × Col∈{64,128} độc lập với NumOfLine (1–3). Nếu tái dùng nhầm switch
case của P10 sẽ luôn báo `WRONG_PARAMETER` cho P5.

## Giải pháp

1. `OutdoorLeds/Enums.cs`: thêm `EM_ModuleType.P5 = 2`; thêm `FontSize_20`, `FontSize_30`
   vào `Fontsize.EM_FontSize` (P5 dùng code 10/20/30, không phải point-size như P10).
   ⚠️ FontSize của P5 là **tập giá trị hoàn toàn khác** P10: P5 chỉ chấp nhận
   10 (native 32×48, chỉ 0-9/-), 20 (scale2 32×48, mặc định), 30 (scale3 48×72,
   chỉ dùng khi Col≥64) — còn P10 dùng thang point-size 7/8/12/13/14/16/23–32.
   Trùng giá trị `10` giữa 2 loại chỉ là trùng số, **khác ý nghĩa**. Phải lọc
   riêng danh sách FontSize hiển thị theo `moduleType` ở UI (`frmLedLineConfig.
   LoadLedFontsizeCapacity`), KHÔNG dùng chung 1 danh sách `Enum.GetValues` cho
   mọi module type — nếu không, user có thể chọn nhầm FontSize point-size (vd 32)
   cho bảng P5, firmware sẽ không hiểu giá trị này.
2. `OutdoorLeds/CMD/CmdBuilder.cs`: thêm `case EM_ModuleType.P5` vào
   `getFirmwareVersion`, `_Set_Screen_Resolution`, `_Get_Screen_Solution`; thêm nhánh
   riêng trong `CheckResolutionCapacity` (không dùng chung `isIpLedv2Version`); thêm
   `_Clear_Screen()` → `"ClearScreen?/"`, `_Reboot()` → `"Reboot?/"`.
3. `OutdoorLeds/OutDoorLed.cs`: thêm `ClearScreen()`, `Reboot()` (dùng
   `UdpTools.ExecuteCommand_Ascii` + `IsSuccess(response,"OK")` như các hàm khác);
   mở rộng `Check_Color` cho `P5` dùng chung rule với `P10FullColorv2` (7 màu).
4. `Forms/DeviceForms/frmOutDoorLed.cs`: `LoadNumberOfLineCapacity` thêm case P5
   (1–3 dòng); `LoadColorCapacity` thêm case P5 (7 màu); `LoadResolution` đổi chữ ký
   nhận thêm `EM_ModuleType` vì P5 sinh danh sách Row×Col khác hẳn logic theo
   `numberOfLine` của P10 — không thể tái dùng switch cũ. Dùng
   `LedLineConfig.CreateDefaultConfigP5()` (FontSize_20) thay vì
   `CreateDefaultConfig()` (FontSize_10, dùng cho P10) khi tạo line config mặc định.
5. `Forms/DeviceForms/frmLedLineConfig.cs`: `LoadLedFontsizeCapacity` đổi chữ ký
   nhận `EM_ModuleType`, lọc riêng {10,20,30} cho P5 thay vì liệt kê toàn bộ
   `EM_FontSize`; thêm case P5 vào `LoadLedColorCapacity` (form này có bản
   `LoadLedColorCapacity` riêng, tách biệt với bản trong `frmOutDoorLed.cs` — dễ
   sửa 1 nơi quên nơi kia).

Không cần sửa DB (`tblOutDoorLed`) vì cột `Type` lưu int của enum, tự tương thích;
không cần class LED mới, không đụng tới `LedFactory`/`ILED`/`EmCategory` (đó là hệ
LED trong nhà — namespace `iParkingPGS.Device`, khác hoàn toàn `iParkingPGS.OutdoorLeds`).

## Áp dụng lại (How to reuse)

- Khi có yêu cầu "thêm loại bảng LED ngoài trời mới" → đọc `OutdoorLeds/OutDoorLed.cs`
  + `Enums.cs` + `CMD/CmdBuilder.cs` trước, đối chiếu với tài liệu giao thức UDP mới —
  rất có thể chỉ cần thêm 1 giá trị `EM_ModuleType` + vài `case` trong switch, không
  cần viết lại tầng UDP.
- Luôn phân biệt "LED ngoài trời" (`iParkingPGS.OutdoorLeds`, UDP string protocol)
  với "LED trong nhà" (`iParkingPGS.Device` + `ILED`/`LedFactory`/`EmCategory`) —
  tên rất dễ nhầm nhưng là 2 hệ thống độc lập hoàn toàn.
- Khi thêm command mới theo tài liệu giao thức, kiểm tra command đó đã tồn tại ở
  `LedCmd`/`CmdBuilder` chưa trước khi viết lại — nhiều lệnh generic không cần
  switch theo module type.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `OutDoorLed.Set_Screen_Current(int, Row[], EM_DisplayMode)` build command có
  khoảng trắng thừa: `"...Line={i+1}/ FontSize=..."` (dư 1 space sau `/`) — vi phạm
  quy tắc "không khoảng trắng trong chuỗi lệnh" của giao thức. Method này có vẻ
  không được gọi trong luồng production thực tế (production dùng
  `DisplayCurrentParkinglot` — không có bug này), nhưng nếu sau này dùng lại
  `Set_Screen_Current` phải sửa bug này trước.
- ⚠️ Quy tắc Row/Col hợp lệ khác nhau theo module type — đừng gộp chung switch case
  P10 và P5 dù cả hai đều dùng lệnh `SetScreenResolution?/` giống hệt cú pháp.
- ⚠️ obj/*.csproj.FileListAbsolute.txt có thể chứa marker conflict `<<<<<<< HEAD`
  sót từ merge cũ (không phải source, nhưng chặn `MSBuild`) — xem lesson
  [[msbuild-obj-filelistabsolute-stale-conflict-marker]].

## Tham chiếu

- Tài liệu giao thức: `Tai lieu/outdoor_led/KZ_LED_iParkingLots_P5_Protocol_V1.0 20260709.docx`
- Project liên quan: IPGSv1 (`PGS_4_number/iParkingPGS/iParkingPGS/OutdoorLeds/`)
