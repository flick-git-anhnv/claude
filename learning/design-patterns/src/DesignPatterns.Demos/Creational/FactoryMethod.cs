namespace DesignPatterns.Demos.Creational.FactoryMethod;

/// <summary>
/// FACTORY METHOD — định nghĩa 1 method để tạo object, nhưng để lớp con quyết định tạo loại cụ thể nào.
/// Khi nào dùng: code gọi hàm tạo object không nên biết chính xác class cụ thể nào sẽ được tạo ra
/// (vd: tạo Notification theo kênh gửi mà không cần "if channel == email then new EmailNotification").
/// Khi KHÔNG nên dùng: chỉ có 1-2 loại object cố định, không có kế hoạch mở rộng — dùng constructor thường.
/// </summary>
public interface INotification
{
    void Send(string message);
}

public class EmailNotification : INotification
{
    public void Send(string message) => Console.WriteLine($"[Email] {message}");
}

public class SmsNotification : INotification
{
    public void Send(string message) => Console.WriteLine($"[SMS] {message}");
}

public abstract class NotificationCreator
{
    // Factory method — lớp con override để quyết định tạo loại notification nào.
    protected abstract INotification CreateNotification();

    public void Notify(string message) => CreateNotification().Send(message);
}

public class EmailNotificationCreator : NotificationCreator
{
    protected override INotification CreateNotification() => new EmailNotification();
}

public class SmsNotificationCreator : NotificationCreator
{
    protected override INotification CreateNotification() => new SmsNotification();
}

public class FactoryMethodDemo : IPatternDemo
{
    public string Category => "Creational";
    public string Name => "Factory Method";

    public void Run()
    {
        NotificationCreator creator = new EmailNotificationCreator();
        creator.Notify("Đơn hàng đã được xác nhận");

        creator = new SmsNotificationCreator();
        creator.Notify("Mã OTP của bạn là 123456");
    }
}
