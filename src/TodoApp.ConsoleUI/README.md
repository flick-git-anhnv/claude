# TodoApp.ConsoleUI — Ứng dụng Quản lý Công việc

Ứng dụng console đơn giản để quản lý công việc cá nhân (To-Do), viết bằng C# / .NET 8.
Lưu trữ cục bộ bằng file JSON, không cần cài đặt database hay server.

---

## Yêu cầu hệ thống

| Thành phần | Yêu cầu |
|-----------|---------|
| Hệ điều hành | Windows 10 (64-bit) trở lên |
| .NET Runtime | .NET 8 Runtime (nếu dùng framework-dependent) |
| Bản self-contained | Không cần cài .NET — chạy trực tiếp từ `.exe` |
| Bộ nhớ RAM | Tối thiểu 64 MB |
| Dung lượng đĩa | ~70 MB (bản self-contained) / ~1 MB (framework-dependent) |
| Màn hình | Terminal hỗ trợ UTF-8 (Windows Terminal, PowerShell 5+, cmd) |

---

## Hướng dẫn chạy

### Cách 1: Chạy bằng .exe (self-contained — không cần cài .NET)

```
publish\win-x64\TodoApp.ConsoleUI.exe
```

Hoặc double-click file `TodoApp.ConsoleUI.exe` trong thư mục `publish\win-x64\`.

### Cách 2: Chạy bằng `dotnet run` (yêu cầu .NET 8 SDK)

```powershell
dotnet run --project src/TodoApp.ConsoleUI
```

### Cách 3: Build Debug và chạy

```powershell
dotnet build src/TodoApp.ConsoleUI
dotnet src/TodoApp.ConsoleUI/bin/Debug/net8.0/TodoApp.ConsoleUI.exe
```

### Cách 4: Chạy từ Release build

```powershell
dotnet build src/TodoApp.ConsoleUI -c Release
src/TodoApp.ConsoleUI/bin/Release/net8.0/TodoApp.ConsoleUI.exe
```

---

## Phím tắt / Lựa chọn menu

Ứng dụng điều hướng bằng bàn phím. Nhập số tương ứng rồi nhấn **Enter**.

### Menu chính

| Phím | Chức năng |
|------|-----------|
| `1` | Tạo công việc mới |
| `2` | Sửa công việc (nhập số thứ tự) |
| `3` | Xóa công việc (nhập số thứ tự) |
| `4` | Toggle hoàn thành / mở lại (nhập số thứ tự) |
| `5` | Lọc danh sách (Tất cả / Đang chờ / Đã hoàn thành) |
| `Q` hoặc `0` | Thoát ứng dụng |

### Tạo công việc mới

| Trường | Bắt buộc | Mô tả |
|--------|----------|-------|
| Tiêu đề | Có | Tối đa 200 ký tự |
| Mô tả | Không | Tối đa 1000 ký tự; Enter để bỏ qua |
| Ưu tiên | Không | `1` Không / `2` Thấp / `3` Trung bình / `4` Cao |
| Ngày hạn | Không | Định dạng `yyyy-MM-dd`; Enter để bỏ qua |

### Xác nhận và hủy thao tác

| Phím | Ý nghĩa |
|------|---------|
| `Y` + Enter | Xác nhận |
| `N` + Enter (hoặc Enter) | Hủy |

---

## Vị trí file dữ liệu

Dữ liệu được lưu tự động tại:

```
%LOCALAPPDATA%\KZTEK\TodoApp\todos.json
```

Ví dụ trên Windows 10/11:
```
C:\Users\<TênNgườiDùng>\AppData\Local\KZTEK\TodoApp\todos.json
```

| File | Mô tả |
|------|-------|
| `todos.json` | File dữ liệu chính (tạo tự động khi khởi động lần đầu) |
| `todos.bak.json` | Bản sao lưu tự động khi file dữ liệu bị hỏng |
| `todos.tmp` | File tạm trong quá trình ghi (tự xóa sau khi ghi xong) |

Để thay đổi thư mục lưu dữ liệu (ví dụ cho test), đặt biến môi trường:
```powershell
$env:TODOAPP_DATA_DIR = "C:\MyData\TodoApp"
```

---

## Gỡ cài đặt

Xóa thư mục `publish\win-x64\` (hoặc thư mục chứa `.exe`) và thư mục dữ liệu:
```
%LOCALAPPDATA%\KZTEK\TodoApp\
```

---

## Thông tin phiên bản

| Thông tin | Giá trị |
|-----------|---------|
| Phiên bản | 1.0.0 |
| Framework | .NET 8 |
| Kiến trúc | Layered (Domain → Application → Infrastructure → ConsoleUI) |
| Lưu trữ | JSON file (atomic write) |
| Ngày build | 2026-06-02 |

---

*Phát triển bởi KZTEK — kztek.net*
