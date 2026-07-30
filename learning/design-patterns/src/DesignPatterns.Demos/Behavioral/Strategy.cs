namespace DesignPatterns.Demos.Behavioral.Strategy;

/// <summary>
/// STRATEGY — định nghĩa 1 họ thuật toán, đóng gói mỗi thuật toán vào 1 class riêng, cho phép hoán đổi
/// thuật toán tại runtime mà không cần sửa code dùng nó.
/// Khi nào dùng: cùng 1 bước xử lý nhưng có nhiều cách làm khác nhau, chọn cách nào tuỳ ngữ cảnh
/// (tính phí ship theo nhà vận chuyển, tính giảm giá theo loại khách hàng).
/// Khi KHÔNG nên dùng: chỉ có 1 thuật toán cố định, không có kế hoạch thêm biến thể — dùng method thường.
/// </summary>
public interface IShippingFeeStrategy
{
    decimal CalculateFee(decimal weightKg, decimal distanceKm);
}

public class StandardShipping : IShippingFeeStrategy
{
    public decimal CalculateFee(decimal weightKg, decimal distanceKm) => weightKg * 5_000m + distanceKm * 1_000m;
}

public class ExpressShipping : IShippingFeeStrategy
{
    public decimal CalculateFee(decimal weightKg, decimal distanceKm) => weightKg * 8_000m + distanceKm * 2_500m;
}

public class FreeShippingOverThreshold : IShippingFeeStrategy
{
    public decimal CalculateFee(decimal weightKg, decimal distanceKm) => 0m;
}

public class ShippingCalculator
{
    private readonly IShippingFeeStrategy _strategy;
    public ShippingCalculator(IShippingFeeStrategy strategy) => _strategy = strategy;
    public decimal Calculate(decimal weightKg, decimal distanceKm) => _strategy.CalculateFee(weightKg, distanceKm);
}

public class StrategyDemo : IPatternDemo
{
    public string Category => "Behavioral";
    public string Name => "Strategy";

    public void Run()
    {
        var weight = 2.5m; var distance = 15m;

        foreach (var (label, strategy) in new (string, IShippingFeeStrategy)[]
        {
            ("Giao thường", new StandardShipping()),
            ("Giao nhanh", new ExpressShipping()),
            ("Freeship (đơn > 500k)", new FreeShippingOverThreshold())
        })
        {
            var fee = new ShippingCalculator(strategy).Calculate(weight, distance);
            Console.WriteLine($"{label}: {fee:N0}đ");
        }
    }
}
