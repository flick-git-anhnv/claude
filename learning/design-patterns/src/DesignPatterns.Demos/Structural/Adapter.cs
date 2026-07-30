namespace DesignPatterns.Demos.Structural.Adapter;

/// <summary>
/// ADAPTER — "bọc" 1 interface không tương thích thành interface mà code của bạn mong đợi,
/// giống ổ cắm chuyển đổi điện. Không sửa code cũ, chỉ thêm 1 lớp trung gian.
/// Khi nào dùng: tích hợp thư viện/API bên thứ 3 có interface khác với interface nội bộ đang dùng.
/// Khi KHÔNG nên dùng: bạn sở hữu cả 2 phía và có thể sửa trực tiếp cho khớp nhau — adapter là thừa.
/// </summary>
public interface IPaymentGateway
{
    void Pay(decimal amountVnd);
}

// Thư viện bên thứ 3 — code có sẵn, KHÔNG được sửa, interface khác hoàn toàn (đơn vị USD, tên method khác).
public class LegacyStripeClient
{
    public void Charge(double amountUsd) => Console.WriteLine($"[StripeClient legacy] Charged ${amountUsd:F2} USD");
}

public class StripeAdapter : IPaymentGateway
{
    private readonly LegacyStripeClient _stripeClient;
    private const decimal UsdToVnd = 25000m;

    public StripeAdapter(LegacyStripeClient stripeClient) => _stripeClient = stripeClient;

    public void Pay(decimal amountVnd)
    {
        var amountUsd = (double)(amountVnd / UsdToVnd);
        _stripeClient.Charge(amountUsd);
    }
}

public class AdapterDemo : IPatternDemo
{
    public string Category => "Structural";
    public string Name => "Adapter";

    public void Run()
    {
        IPaymentGateway gateway = new StripeAdapter(new LegacyStripeClient());
        gateway.Pay(250_000m); // code nghiệp vụ chỉ biết VND, không cần biết Stripe dùng USD
    }
}
