namespace DesignPatterns.Demos.Structural.Composite;

/// <summary>
/// COMPOSITE — gộp object đơn lẻ (leaf) và object chứa nhiều object khác (composite) vào chung 1
/// interface, để code gọi giống hệt nhau dù đang thao tác 1 phần tử hay cả 1 cây (VD: hệ thống file).
/// Khi nào dùng: dữ liệu có cấu trúc cây (thư mục/file, tổ chức nhân sự, UI component lồng nhau).
/// Khi KHÔNG nên dùng: dữ liệu phẳng, không có quan hệ chứa-trong — thêm interface là thừa.
/// </summary>
public interface IFileSystemItem
{
    string Name { get; }
    long GetSizeBytes();
    void Print(int indent = 0);
}

public class FileItem : IFileSystemItem
{
    public string Name { get; }
    private readonly long _sizeBytes;

    public FileItem(string name, long sizeBytes) { Name = name; _sizeBytes = sizeBytes; }

    public long GetSizeBytes() => _sizeBytes;
    public void Print(int indent = 0) => Console.WriteLine($"{new string(' ', indent)}📄 {Name} ({_sizeBytes} bytes)");
}

public class FolderItem : IFileSystemItem
{
    public string Name { get; }
    private readonly List<IFileSystemItem> _children = new();

    public FolderItem(string name) => Name = name;
    public void Add(IFileSystemItem item) => _children.Add(item);

    // Đệ quy: tổng size = tổng size của mọi item con, dù con đó là file hay lại là 1 folder khác.
    public long GetSizeBytes() => _children.Sum(c => c.GetSizeBytes());

    public void Print(int indent = 0)
    {
        Console.WriteLine($"{new string(' ', indent)}📁 {Name}/ ({GetSizeBytes()} bytes)");
        foreach (var child in _children) child.Print(indent + 2);
    }
}

public class CompositeDemo : IPatternDemo
{
    public string Category => "Structural";
    public string Name => "Composite";

    public void Run()
    {
        var root = new FolderItem("project");
        var src = new FolderItem("src");
        src.Add(new FileItem("Program.cs", 1200));
        src.Add(new FileItem("Utils.cs", 800));
        root.Add(src);
        root.Add(new FileItem("README.md", 300));

        root.Print(); // gọi Print() 1 lần trên root — không cần biết bên trong có bao nhiêu cấp
    }
}
