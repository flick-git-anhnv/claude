using TodoApp.Application;
using TodoApp.ConsoleUI.Components;
using TodoApp.ConsoleUI.Rendering;

namespace TodoApp.ConsoleUI.Screens;

public sealed class FilterScreen
{
    private readonly ITodoService _service;

    public FilterScreen(ITodoService service)
    {
        _service = service;
    }

    /// <summary>Cho user chọn filter, trả về filter mới.</summary>
    public TaskFilter Show(TaskFilter current)
    {
        AppHeader.Render("Lọc danh sách");
        var counts = _service.GetCounts();

        Console.WriteLine();
        AnsiConsole.WriteLine(AnsiColors.Cyan, $"  [1] Tất cả        ({counts.Total})");
        AnsiConsole.WriteLine(AnsiColors.Yellow, $"  [2] Đang chờ      ({counts.Pending})");
        AnsiConsole.WriteLine(AnsiColors.Green,  $"  [3] Đã hoàn thành ({counts.Completed})");
        Console.WriteLine();

        var currentLabel = current switch
        {
            TaskFilter.Pending   => "Đang chờ",
            TaskFilter.Completed => "Đã hoàn thành",
            _                    => "Tất cả"
        };
        AnsiConsole.WriteLine(AnsiColors.DarkGray, $"  Hiện tại: {currentLabel}");
        Console.Write("  Chọn (Enter = giữ nguyên): ");

        return ConsoleInput.ReadInt(1, 3) switch
        {
            1 => TaskFilter.All,
            2 => TaskFilter.Pending,
            3 => TaskFilter.Completed,
            _ => current
        };
    }
}
