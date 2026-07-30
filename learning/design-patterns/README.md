# Design Patterns — tự tay implement 23 pattern GoF (C#/.NET)

Dự án học tập cá nhân (không phải sản phẩm KZTEK), đặt trong `learning/` để tách biệt khỏi source
chính thức. Mỗi pattern được viết thành 1 file độc lập, có ví dụ chạy được + giải thích khi nào nên/
không nên dùng — không chỉ chép lại lý thuyết suông.

## Yêu cầu

.NET 8 SDK trở lên. Sandbox hiện tại không có sẵn .NET nên bạn cần chạy trên máy local.

## Build & chạy

```bash
cd learning/design-patterns
dotnet build

# Xem danh sách 23 pattern
dotnet run --project src/DesignPatterns.Demos

# Chạy demo 1 pattern cụ thể
dotnet run --project src/DesignPatterns.Demos -- Singleton
dotnet run --project src/DesignPatterns.Demos -- "Factory Method"

# Chạy toàn bộ 23 demo liên tiếp
dotnet run --project src/DesignPatterns.Demos -- all
```

## Danh sách 23 pattern

| Nhóm | Pattern | File | Ý tưởng cốt lõi (1 câu) |
|---|---|---|---|
| Creational | Singleton | `Creational/Singleton.cs` | Đảm bảo chỉ có đúng 1 instance toàn cục |
| Creational | Factory Method | `Creational/FactoryMethod.cs` | Lớp con quyết định tạo loại object nào |
| Creational | Abstract Factory | `Creational/AbstractFactory.cs` | Tạo cả 1 họ object tương thích nhau |
| Creational | Builder | `Creational/Builder.cs` | Xây object phức tạp từng bước, tách khỏi object đó |
| Creational | Prototype | `Creational/Prototype.cs` | Tạo object mới bằng clone object mẫu |
| Structural | Adapter | `Structural/Adapter.cs` | Bọc interface không tương thích thành interface mong muốn |
| Structural | Bridge | `Structural/Bridge.cs` | Tách abstraction khỏi implementation thành 2 cây độc lập |
| Structural | Composite | `Structural/Composite.cs` | Gộp object đơn lẻ và object chứa nhiều object vào chung interface |
| Structural | Decorator | `Structural/Decorator.cs` | Bọc thêm hành vi mới tại runtime, không cần lớp con |
| Structural | Facade | `Structural/Facade.cs` | 1 interface đơn giản đứng trước hệ thống con phức tạp |
| Structural | Flyweight | `Structural/Flyweight.cs` | Chia sẻ dữ liệu giống nhau để tiết kiệm bộ nhớ |
| Structural | Proxy | `Structural/Proxy.cs` | Object đại diện kiểm soát truy cập tới object thật |
| Behavioral | Chain of Responsibility | `Behavioral/ChainOfResponsibility.cs` | Chuyển request qua chuỗi handler, ai xử lý được thì nhận |
| Behavioral | Command | `Behavioral/Command.cs` | Biến hành động thành object — hỗ trợ undo/queue/log |
| Behavioral | Interpreter | `Behavioral/Interpreter.cs` | Xây cây biểu thức cho 1 ngôn ngữ đơn giản, tự đánh giá |
| Behavioral | Iterator | `Behavioral/Iterator.cs` | Duyệt collection mà không lộ cấu trúc bên trong |
| Behavioral | Mediator | `Behavioral/Mediator.cs` | Mọi object giao tiếp qua 1 trung gian thay vì gọi thẳng nhau |
| Behavioral | Memento | `Behavioral/Memento.cs` | Snapshot trạng thái để khôi phục sau, không vi phạm encapsulation |
| Behavioral | Observer | `Behavioral/Observer.cs` | Subject tự thông báo cho danh sách observer khi có thay đổi |
| Behavioral | State | `Behavioral/State.cs` | Hành vi object thay đổi theo trạng thái nội bộ, không cần if/switch |
| Behavioral | Strategy | `Behavioral/Strategy.cs` | Đóng gói họ thuật toán, hoán đổi được tại runtime |
| Behavioral | Template Method | `Behavioral/TemplateMethod.cs` | Khung thuật toán cố định ở lớp cha, lớp con override từng bước |
| Behavioral | Visitor | `Behavioral/Visitor.cs` | Thêm thao tác mới lên nhóm class có sẵn mà không sửa class đó |

## Cách đọc mỗi file

Mỗi file theo đúng 1 cấu trúc:
1. Comment đầu file: pattern là gì, **khi nào dùng**, **khi nào KHÔNG nên dùng** (quan trọng — pattern
   dùng sai chỗ gây over-engineering, không phải cứ dùng nhiều pattern là code tốt).
2. Interface/class implement pattern, ví dụ generic dễ hiểu (không lẫn business logic thật).
3. 1 class `XxxDemo : IPatternDemo` — chạy thử để thấy pattern hoạt động thế nào, không chỉ đọc lý thuyết.

## Việc tiếp theo (đề xuất, chưa làm)

- Thêm ví dụ "before/after" cho vài pattern hay bị lạm dụng (Singleton, Factory) — so sánh code
  không dùng pattern vs có dùng pattern, để thấy rõ vấn đề pattern thật sự giải quyết.
- Áp dụng vào bối cảnh KZTEK thật (iParking/iLocker) sau khi đã nắm chắc bản chất generic — ví dụ
  Strategy cho tính phí gửi xe theo loại thẻ, State cho vòng đời phiên gửi xe (Vào bãi → Đang gửi →
  Ra bãi), Observer cho sự kiện camera LPR nhận diện biển số.
