namespace DesignPatterns.Demos.Behavioral.TemplateMethod;

/// <summary>
/// TEMPLATE METHOD — định nghĩa BỘ KHUNG (thứ tự các bước) của 1 thuật toán trong lớp cha, để lớp con
/// chỉ override các bước cụ thể cần khác biệt — thứ tự tổng thể không đổi.
/// Khi nào dùng: nhiều quy trình có CÙNG các bước tổng quát nhưng khác nhau ở vài bước cụ thể
/// (import dữ liệu từ CSV/JSON/XML: đọc file khác nhau, nhưng validate + save giống nhau).
/// Khi KHÔNG nên dùng: các bước không có phần chung thật sự — ép vào template method sẽ gượng ép.
/// </summary>
public abstract class DataImporter
{
    // Template method — "đóng khung" (sealed) để lớp con KHÔNG được đổi thứ tự các bước.
    public void Import(string filePath)
    {
        var rawData = ReadFile(filePath);
        var records = Parse(rawData);
        Validate(records);
        Save(records);
        Console.WriteLine($"  Import xong {records.Count} bản ghi từ {filePath}");
    }

    protected abstract string ReadFile(string filePath);
    protected abstract List<string> Parse(string rawData);

    protected virtual void Validate(List<string> records) // có default, lớp con có thể override thêm
    {
        if (records.Count == 0) throw new InvalidOperationException("File rỗng!");
    }

    private void Save(List<string> records) => Console.WriteLine($"  Đã lưu {records.Count} bản ghi vào DB");
}

public class CsvImporter : DataImporter
{
    protected override string ReadFile(string filePath) => "name,age\nAn,25\nBinh,30"; // giả lập đọc file
    protected override List<string> Parse(string rawData) => rawData.Split('\n').Skip(1).ToList();
}

public class JsonImporter : DataImporter
{
    protected override string ReadFile(string filePath) => "[{\"name\":\"An\"},{\"name\":\"Binh\"}]";
    protected override List<string> Parse(string rawData) => new() { "{\"name\":\"An\"}", "{\"name\":\"Binh\"}" };
}

public class TemplateMethodDemo : IPatternDemo
{
    public string Category => "Behavioral";
    public string Name => "Template Method";

    public void Run()
    {
        Console.WriteLine("Import CSV:");
        new CsvImporter().Import("users.csv");

        Console.WriteLine("Import JSON:");
        new JsonImporter().Import("users.json");
    }
}
