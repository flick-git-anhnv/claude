namespace DesignPatterns.Demos.Behavioral.Visitor;

/// <summary>
/// VISITOR — thêm 1 THAO TÁC MỚI vào 1 nhóm class có sẵn mà KHÔNG cần sửa code của các class đó —
/// bằng cách tách logic thao tác ra thành 1 "visitor" riêng, mỗi class chấp nhận (Accept) visitor.
/// Khi nào dùng: có 1 cây/nhóm class cấu trúc ổn định, nhưng cần thêm nhiều thao tác mới lên chúng
/// theo thời gian (tính thuế, xuất báo cáo, export XML cho nhiều loại sản phẩm khác nhau).
/// Khi KHÔNG nên dùng: cấu trúc class hay thay đổi (thêm loại mới thường xuyên) — visitor sẽ phải sửa
/// ở MỌI nơi mỗi khi thêm 1 class mới, ngược lại với mục đích "mở rộng không sửa code cũ".
/// </summary>
public interface IProductVisitor
{
    void Visit(Electronics item);
    void Visit(Groceries item);
}

public interface IProduct
{
    void Accept(IProductVisitor visitor);
}

public class Electronics : IProduct
{
    public decimal Price { get; init; }
    public void Accept(IProductVisitor visitor) => visitor.Visit(this);
}

public class Groceries : IProduct
{
    public decimal Price { get; init; }
    public bool IsPerishable { get; init; }
    public void Accept(IProductVisitor visitor) => visitor.Visit(this);
}

// Thêm thao tác "tính thuế" mới — không sửa gì trong Electronics/Groceries.
public class TaxCalculatorVisitor : IProductVisitor
{
    public decimal TotalTax { get; private set; }
    public void Visit(Electronics item) => TotalTax += item.Price * 0.10m;  // điện tử thuế 10%
    public void Visit(Groceries item) => TotalTax += item.IsPerishable ? 0m : item.Price * 0.05m; // thực phẩm tươi miễn thuế
}

public class VisitorDemo : IPatternDemo
{
    public string Category => "Behavioral";
    public string Name => "Visitor";

    public void Run()
    {
        var cart = new List<IProduct>
        {
            new Electronics { Price = 5_000_000m },
            new Groceries { Price = 200_000m, IsPerishable = false },
            new Groceries { Price = 100_000m, IsPerishable = true },
        };

        var taxVisitor = new TaxCalculatorVisitor();
        foreach (var product in cart) product.Accept(taxVisitor);

        Console.WriteLine($"Tổng thuế phải trả: {taxVisitor.TotalTax:N0}đ");
    }
}
