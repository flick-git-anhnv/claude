namespace DesignPatterns.Demos.Structural.Proxy;

/// <summary>
/// PROXY — tạo 1 object "đại diện" đứng trước object thật, cùng interface, để kiểm soát truy cập
/// (lazy loading, cache, quyền truy cập, logging) mà code gọi không hề biết có proxy ở giữa.
/// Khi nào dùng: cần lazy-load object nặng, thêm access control, hoặc cache kết quả gọi tốn kém.
/// Khi KHÔNG nên dùng: không có nhu cầu kiểm soát truy cập — gọi object thật trực tiếp là đủ.
/// (Khác Decorator: Proxy kiểm soát TRUY CẬP, Decorator thêm HÀNH VI mới.)
/// </summary>
public interface IReportGenerator
{
    string Generate(string reportName);
}

public class HeavyReportGenerator : IReportGenerator // object thật — khởi tạo/chạy rất tốn kém
{
    public HeavyReportGenerator() => Console.WriteLine("  (Khởi tạo HeavyReportGenerator — load dữ liệu nặng...)");

    public string Generate(string reportName)
    {
        Console.WriteLine($"  (Đang tính toán report '{reportName}' — tốn nhiều CPU...)");
        return $"[Nội dung report {reportName}]";
    }
}

public class CachingReportProxy : IReportGenerator
{
    private HeavyReportGenerator? _realGenerator; // lazy — chỉ tạo khi thật sự cần
    private readonly Dictionary<string, string> _cache = new();

    public string Generate(string reportName)
    {
        if (_cache.TryGetValue(reportName, out var cached))
        {
            Console.WriteLine($"[Proxy] Trả từ cache cho '{reportName}' — không gọi object thật");
            return cached;
        }

        _realGenerator ??= new HeavyReportGenerator(); // lazy init
        var result = _realGenerator.Generate(reportName);
        _cache[reportName] = result;
        return result;
    }
}

public class ProxyDemo : IPatternDemo
{
    public string Category => "Structural";
    public string Name => "Proxy";

    public void Run()
    {
        IReportGenerator proxy = new CachingReportProxy();

        Console.WriteLine("Lần gọi 1 (chưa có cache):");
        proxy.Generate("Doanh thu Q1");

        Console.WriteLine("Lần gọi 2 (cùng report — dùng cache):");
        proxy.Generate("Doanh thu Q1");
    }
}
