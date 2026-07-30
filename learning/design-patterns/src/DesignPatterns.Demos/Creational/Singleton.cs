namespace DesignPatterns.Demos.Creational.Singleton;

/// <summary>
/// SINGLETON — đảm bảo 1 class chỉ có đúng 1 instance trong toàn bộ ứng dụng, truy cập qua 1 điểm chung.
/// Khi nào dùng: config/logger/connection-pool dùng chung toàn app, tạo lại tốn kém hoặc cần trạng thái duy nhất.
/// Khi KHÔNG nên dùng: che giấu global state làm code khó test (không mock được) — ưu tiên Dependency Injection
/// với lifetime "Singleton" thay vì tự viết class này trong code hiện đại.
/// </summary>
public sealed class AppLogger
{
    private static readonly Lazy<AppLogger> _instance = new(() => new AppLogger());
    public static AppLogger Instance => _instance.Value;

    private readonly List<string> _logs = new();
    private AppLogger() { } // constructor private — không ai new() được từ bên ngoài

    public void Log(string message)
    {
        _logs.Add(message);
        Console.WriteLine($"[LOG] {message}");
    }

    public int LogCount => _logs.Count;
}

public class SingletonDemo : IPatternDemo
{
    public string Category => "Creational";
    public string Name => "Singleton";

    public void Run()
    {
        AppLogger.Instance.Log("Ứng dụng khởi động");
        var loggerRefKhac = AppLogger.Instance;
        loggerRefKhac.Log("Ghi log từ 1 chỗ khác trong code");

        Console.WriteLine($"Cùng 1 instance? {ReferenceEquals(AppLogger.Instance, loggerRefKhac)}");
        Console.WriteLine($"Tổng số log đã ghi: {AppLogger.Instance.LogCount}");
    }
}
