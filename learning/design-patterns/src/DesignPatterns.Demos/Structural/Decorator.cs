namespace DesignPatterns.Demos.Structural.Decorator;

/// <summary>
/// DECORATOR — "bọc" thêm hành vi mới cho 1 object tại runtime, bằng cách wrap nó trong 1 object khác
/// cùng interface — thay vì tạo lớp con cho từng tổ hợp tính năng.
/// Khi nào dùng: cần thêm/bớt tính năng linh hoạt (nén, mã hoá, logging) mà không sinh ra hàng chục lớp con.
/// Khi KHÔNG nên dùng: tổ hợp tính năng cố định, ít thay đổi — kế thừa đơn giản dễ đọc hơn.
/// </summary>
public interface IDataSource
{
    void Write(string data);
    string Read();
}

public class FileDataSource : IDataSource
{
    private string _storage = "";
    public void Write(string data) => _storage = data;
    public string Read() => _storage;
}

// Decorator gốc — implement lại interface, giữ tham chiếu tới object được bọc.
public abstract class DataSourceDecorator : IDataSource
{
    protected readonly IDataSource Wrapped;
    protected DataSourceDecorator(IDataSource wrapped) => Wrapped = wrapped;
    public virtual void Write(string data) => Wrapped.Write(data);
    public virtual string Read() => Wrapped.Read();
}

public class Base64EncodingDecorator : DataSourceDecorator
{
    public Base64EncodingDecorator(IDataSource wrapped) : base(wrapped) { }
    public override void Write(string data) => Wrapped.Write(Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(data)));
    public override string Read() => System.Text.Encoding.UTF8.GetString(Convert.FromBase64String(Wrapped.Read()));
}

public class LoggingDecorator : DataSourceDecorator
{
    public LoggingDecorator(IDataSource wrapped) : base(wrapped) { }
    public override void Write(string data)
    {
        Console.WriteLine($"[Log] Writing {data.Length} ký tự");
        Wrapped.Write(data);
    }
}

public class DecoratorDemo : IPatternDemo
{
    public string Category => "Structural";
    public string Name => "Decorator";

    public void Run()
    {
        // Xếp chồng decorator: log -> encode base64 -> file thật. Thứ tự bọc quyết định thứ tự thực thi.
        IDataSource source = new LoggingDecorator(new Base64EncodingDecorator(new FileDataSource()));

        source.Write("dữ liệu nhạy cảm");
        Console.WriteLine($"Đọc lại (đã tự động decode): {source.Read()}");
    }
}
