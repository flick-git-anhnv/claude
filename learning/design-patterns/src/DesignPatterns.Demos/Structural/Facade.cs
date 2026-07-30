namespace DesignPatterns.Demos.Structural.Facade;

/// <summary>
/// FACADE — cung cấp 1 interface đơn giản đứng trước 1 hệ thống con phức tạp (nhiều class phải gọi
/// đúng thứ tự), giúp code gọi không cần biết chi tiết bên trong.
/// Khi nào dùng: quy trình nghiệp vụ cần điều phối nhiều service/class theo đúng trình tự cố định.
/// Khi KHÔNG nên dùng: hệ thống con đã đơn giản — thêm facade chỉ là 1 lớp gọi thừa không giá trị.
/// </summary>
public class InventoryService
{
    public bool ReserveStock(string sku, int qty) { Console.WriteLine($"[Inventory] Giữ {qty} x {sku}"); return true; }
}

public class PaymentService
{
    public bool Charge(string customerId, decimal amount) { Console.WriteLine($"[Payment] Thu {amount:N0}đ từ {customerId}"); return true; }
}

public class ShippingService
{
    public string CreateShipment(string sku, int qty) { Console.WriteLine($"[Shipping] Tạo vận đơn cho {qty} x {sku}"); return "SHIP-001"; }
}

public class NotificationService
{
    public void NotifyCustomer(string customerId, string message) => Console.WriteLine($"[Notify] Gửi '{message}' tới {customerId}");
}

/// Facade — điểm vào duy nhất, tự điều phối 4 service con theo đúng thứ tự nghiệp vụ.
public class OrderFacade
{
    private readonly InventoryService _inventory = new();
    private readonly PaymentService _payment = new();
    private readonly ShippingService _shipping = new();
    private readonly NotificationService _notification = new();

    public void PlaceOrder(string customerId, string sku, int qty, decimal amount)
    {
        if (!_inventory.ReserveStock(sku, qty)) return;
        if (!_payment.Charge(customerId, amount)) return;
        var shipmentId = _shipping.CreateShipment(sku, qty);
        _notification.NotifyCustomer(customerId, $"Đơn hàng đã xác nhận, vận đơn {shipmentId}");
    }
}

public class FacadeDemo : IPatternDemo
{
    public string Category => "Structural";
    public string Name => "Facade";

    public void Run()
    {
        // Code gọi chỉ cần biết 1 method duy nhất — không cần biết có 4 service phía sau.
        new OrderFacade().PlaceOrder("KH001", "SKU-XYZ", 2, 450_000m);
    }
}
