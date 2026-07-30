namespace DesignPatterns.Demos.Creational.Prototype;

/// <summary>
/// PROTOTYPE — tạo object mới bằng cách CLONE 1 object mẫu có sẵn, thay vì tạo mới từ đầu.
/// Khi nào dùng: khởi tạo object tốn kém (load config nặng, gọi DB) nhưng cần nhiều bản gần giống nhau
/// chỉ khác vài field — clone rồi chỉnh sửa nhanh hơn tạo lại từ đầu.
/// Khi KHÔNG nên dùng: object đơn giản, tạo mới rẻ — clone chỉ thêm phức tạp không cần thiết.
/// </summary>
public class DocumentTemplate
{
    public string Title { get; set; } = "";
    public List<string> Sections { get; set; } = new();
    public Dictionary<string, string> Metadata { get; set; } = new();

    // Deep clone thủ công — nếu chỉ MemberwiseClone() thì List/Dictionary sẽ bị CHIA SẺ tham chiếu (lỗi hay gặp).
    public DocumentTemplate Clone() => new()
    {
        Title = Title,
        Sections = new List<string>(Sections),
        Metadata = new Dictionary<string, string>(Metadata)
    };
}

public class PrototypeDemo : IPatternDemo
{
    public string Category => "Creational";
    public string Name => "Prototype";

    public void Run()
    {
        var baseTemplate = new DocumentTemplate
        {
            Title = "Hợp đồng mẫu",
            Sections = { "Điều khoản chung", "Điều khoản thanh toán", "Điều khoản bảo mật" },
            Metadata = { ["Version"] = "1.0" }
        };

        var contractA = baseTemplate.Clone();
        contractA.Title = "Hợp đồng khách hàng A";
        contractA.Sections.Add("Phụ lục riêng cho khách A");

        Console.WriteLine($"Bản gốc: {baseTemplate.Title} — {baseTemplate.Sections.Count} sections");
        Console.WriteLine($"Bản clone: {contractA.Title} — {contractA.Sections.Count} sections");
        Console.WriteLine($"Bản gốc có bị ảnh hưởng không? {(baseTemplate.Sections.Count == 3 ? "Không — clone độc lập" : "Có lỗi!")}");
    }
}
