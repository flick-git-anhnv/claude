namespace DesignPatterns.Demos.Structural.Flyweight;

/// <summary>
/// FLYWEIGHT — chia sẻ phần dữ liệu GIỐNG NHAU (intrinsic state) giữa nhiều object, chỉ lưu riêng
/// phần dữ liệu KHÁC NHAU (extrinsic state) — tiết kiệm bộ nhớ khi có rất nhiều object tương tự.
/// Khi nào dùng: hàng chục nghìn/triệu object nhỏ, phần lớn dữ liệu trùng lặp (icon, glyph font, tile bản đồ).
/// Khi KHÔNG nên dùng: số lượng object ít, hoặc mỗi object đã khác nhau hoàn toàn — không tiết kiệm được gì.
/// </summary>
public class CarModel // intrinsic state — dùng chung, tạo 1 lần, có thể nặng (ảnh 3D, mesh...)
{
    public string Brand { get; }
    public string Model { get; }
    public string MeshData { get; } // giả lập dữ liệu nặng dùng chung

    public CarModel(string brand, string model)
    {
        Brand = brand;
        Model = model;
        MeshData = $"[mesh 3D nặng của {brand} {model}]";
        Console.WriteLine($"  (Tạo mới CarModel dùng chung cho {brand} {model} — tốn kém, chỉ làm 1 lần)");
    }
}

public class CarModelFactory
{
    private readonly Dictionary<string, CarModel> _cache = new();

    public CarModel GetModel(string brand, string model)
    {
        var key = $"{brand}|{model}";
        if (!_cache.TryGetValue(key, out var carModel))
        {
            carModel = new CarModel(brand, model);
            _cache[key] = carModel;
        }
        return carModel;
    }

    public int UniqueModelCount => _cache.Count;
}

public class ParkedCar // extrinsic state — riêng cho từng xe: biển số, vị trí, màu
{
    private readonly CarModel _model; // tham chiếu dùng chung, KHÔNG copy dữ liệu nặng
    public string LicensePlate { get; }
    public string ParkingSlot { get; }

    public ParkedCar(CarModel model, string licensePlate, string parkingSlot)
    {
        _model = model;
        LicensePlate = licensePlate;
        ParkingSlot = parkingSlot;
    }

    public void PrintInfo() => Console.WriteLine($"  {LicensePlate} ({_model.Brand} {_model.Model}) tại chỗ {ParkingSlot}");
}

public class FlyweightDemo : IPatternDemo
{
    public string Category => "Structural";
    public string Name => "Flyweight";

    public void Run()
    {
        var factory = new CarModelFactory();
        var cars = new List<ParkedCar>
        {
            new(factory.GetModel("Toyota", "Vios"), "30A-111.11", "A01"),
            new(factory.GetModel("Toyota", "Vios"), "30A-222.22", "A02"), // dùng lại CarModel đã tạo, không tạo mới
            new(factory.GetModel("Honda", "City"), "30A-333.33", "A03"),
        };

        foreach (var car in cars) car.PrintInfo();
        Console.WriteLine($"Số xe: {cars.Count} — nhưng chỉ {factory.UniqueModelCount} CarModel (mesh nặng) được tạo trong bộ nhớ");
    }
}
