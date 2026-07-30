namespace DesignPatterns.Demos.Behavioral.State;

/// <summary>
/// STATE — cho phép object thay đổi HÀNH VI khi trạng thái nội bộ thay đổi, như thể object đã đổi class
/// — thay vì viết 1 đống if/switch(state) rải khắp mọi method.
/// Khi nào dùng: object có nhiều trạng thái, mỗi trạng thái hành xử khác hẳn (đơn hàng: Pending/Paid/Shipped),
/// và logic chuyển trạng thái phức tạp dần theo thời gian.
/// Khi KHÔNG nên dùng: chỉ 2-3 trạng thái đơn giản, hành vi ít khác biệt — 1 switch-case là đủ, không cần pattern.
/// </summary>
public interface IOrderState
{
    void Pay(OrderContext context);
    void Ship(OrderContext context);
    string Name { get; }
}

public class OrderContext
{
    public IOrderState State { get; set; } = new PendingState();
    public void Pay() => State.Pay(this);
    public void Ship() => State.Ship(this);
}

public class PendingState : IOrderState
{
    public string Name => "Pending";
    public void Pay(OrderContext context)
    {
        Console.WriteLine("  Thanh toán thành công -> chuyển sang Paid");
        context.State = new PaidState();
    }
    public void Ship(OrderContext context) => Console.WriteLine("  Không thể giao hàng — đơn chưa thanh toán!");
}

public class PaidState : IOrderState
{
    public string Name => "Paid";
    public void Pay(OrderContext context) => Console.WriteLine("  Đơn đã thanh toán rồi, không thể thanh toán lại");
    public void Ship(OrderContext context)
    {
        Console.WriteLine("  Đang giao hàng -> chuyển sang Shipped");
        context.State = new ShippedState();
    }
}

public class ShippedState : IOrderState
{
    public string Name => "Shipped";
    public void Pay(OrderContext context) => Console.WriteLine("  Đơn đã giao, không thể thanh toán");
    public void Ship(OrderContext context) => Console.WriteLine("  Đơn đã giao rồi, không thể giao lại");
}

public class StateDemo : IPatternDemo
{
    public string Category => "Behavioral";
    public string Name => "State";

    public void Run()
    {
        var order = new OrderContext();
        Console.WriteLine($"Trạng thái ban đầu: {order.State.Name}");

        order.Ship(); // thử giao khi chưa thanh toán -> bị chặn bởi đúng state
        order.Pay();
        order.Ship();
        Console.WriteLine($"Trạng thái cuối: {order.State.Name}");
    }
}
