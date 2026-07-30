namespace DesignPatterns.Demos;

/// <summary>Mỗi pattern implement interface này để Program.cs liệt kê và chạy demo thống nhất.</summary>
public interface IPatternDemo
{
    string Category { get; }
    string Name { get; }
    void Run();
}
