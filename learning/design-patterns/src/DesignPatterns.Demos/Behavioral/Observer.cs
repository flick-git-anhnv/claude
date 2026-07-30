namespace DesignPatterns.Demos.Behavioral.Observer;

/// <summary>
/// OBSERVER — 1 object (subject) tự động thông báo cho danh sách object khác (observer) mỗi khi trạng
/// thái của nó thay đổi — observer đăng ký/huỷ đăng ký linh hoạt, subject không cần biết observer là ai.
/// Khi nào dùng: event system, pub/sub nội bộ (UI cập nhật khi data đổi, gửi thông báo khi có sự kiện).
/// Khi KHÔNG nên dùng: chỉ có 1 nơi cần biết kết quả — gọi callback/return value trực tiếp là đủ.
/// </summary>
public interface IOrderObserver
{
    void OnOrderStatusChanged(string orderId, string newStatus);
}

public class OrderSubject
{
    private readonly List<IOrderObserver> _observers = new();
    public void Subscribe(IOrderObserver observer) => _observers.Add(observer);
    public void Unsubscribe(IOrderObserver observer) => _observers.Remove(observer);

    public void ChangeStatus(string orderId, string newStatus)
    {
        foreach (var observer in _observers)
            observer.OnOrderStatusChanged(orderId, newStatus);
    }
}

public class SmsNotifier : IOrderObserver
{
    public void OnOrderStatusChanged(string orderId, string newStatus) => Console.WriteLine($"[SMS] Đơn {orderId} chuyển sang '{newStatus}'");
}

public class WarehouseDashboard : IOrderObserver
{
    public void OnOrderStatusChanged(string orderId, string newStatus) => Console.WriteLine($"[Dashboard kho] Cập nhật đơn {orderId}: {newStatus}");
}

public class ObserverDemo : IPatternDemo
{
    public string Category => "Behavioral";
    public string Name => "Observer";

    public void Run()
    {
        var order = new OrderSubject();
        order.Subscribe(new SmsNotifier());
        order.Subscribe(new WarehouseDashboard());

        // Subject chỉ biết "có ai đó đang lắng nghe" — không biết cụ thể là SMS hay Dashboard.
        order.ChangeStatus("DH-001", "Đang giao hàng");
    }
}
