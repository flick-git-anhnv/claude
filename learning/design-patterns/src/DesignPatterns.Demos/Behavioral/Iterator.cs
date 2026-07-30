namespace DesignPatterns.Demos.Behavioral.Iterator;

/// <summary>
/// ITERATOR — cung cấp cách duyệt tuần tự qua các phần tử của 1 collection mà không cần lộ ra cấu trúc
/// bên trong (array, linked list, tree...). C# đã có sẵn qua IEnumerable/yield — đây là cách nó hoạt động.
/// Khi nào dùng: cần duyệt collection với logic đặc biệt (duyệt ngược, duyệt theo tầng cây, phân trang).
/// Khi KHÔNG nên dùng: chỉ cần duyệt danh sách phẳng đơn giản — dùng foreach/LINQ có sẵn của .NET.
/// </summary>
public class PriorityQueue // collection tuỳ chỉnh — có logic duyệt riêng (theo priority giảm dần)
{
    private readonly List<(string Task, int Priority)> _items = new();
    public void Add(string task, int priority) => _items.Add((task, priority));

    // Tự viết iterator bằng "yield return" — giấu chi tiết sắp xếp bên trong khỏi code gọi.
    public IEnumerable<string> IterateByPriority()
    {
        foreach (var item in _items.OrderByDescending(i => i.Priority))
            yield return $"{item.Task} (ưu tiên {item.Priority})";
    }
}

public class IteratorDemo : IPatternDemo
{
    public string Category => "Behavioral";
    public string Name => "Iterator";

    public void Run()
    {
        var queue = new PriorityQueue();
        queue.Add("Fix bug P3", 1);
        queue.Add("Fix production incident", 10);
        queue.Add("Code review PR", 5);

        // Code gọi chỉ cần foreach — không biết/không cần biết bên trong đang OrderByDescending.
        foreach (var task in queue.IterateByPriority())
            Console.WriteLine(task);
    }
}
