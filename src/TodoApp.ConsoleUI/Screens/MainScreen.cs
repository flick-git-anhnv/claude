using TodoApp.Application;
using TodoApp.ConsoleUI.Components;
using TodoApp.ConsoleUI.Rendering;

namespace TodoApp.ConsoleUI.Screens;

public sealed class MainScreen
{
    private readonly ITodoService _service;
    private TaskFilter _currentFilter = TaskFilter.All;

    public MainScreen(ITodoService service)
    {
        _service = service;
    }

    /// <summary>Trả về action tiếp theo: "create","edit","delete","toggle","filter","quit"</summary>
    public string Show(out int selectedIndex)
    {
        selectedIndex = 0;

        while (true)
        {
            AppHeader.Render(FilterLabel());
            var counts = _service.GetCounts();
            StatusBar.Render(counts);

            var tasks = _service.GetTasks(_currentFilter);
            if (tasks.Count == 0)
            {
                EmptyState.Render(EmptyMessage());
            }
            else
            {
                for (int i = 0; i < tasks.Count; i++)
                    TaskRow.Render(i + 1, tasks[i]);
                Console.WriteLine();
            }

            Console.WriteLine(AnsiConsole.Separator());
            AnsiConsole.WriteLine(AnsiColors.Cyan,
                "  [1] Tạo mới  [2] Sửa  [3] Xóa  [4] Toggle  [5] Lọc  [Q] Thoát");
            Console.Write("  Chọn: ");

            var choice = Console.ReadLine()?.Trim().ToUpperInvariant();
            switch (choice)
            {
                case "1": return "create";
                case "2":
                    selectedIndex = PickTaskIndex(tasks.Count, "sửa");
                    if (selectedIndex > 0) return "edit";
                    break;
                case "3":
                    selectedIndex = PickTaskIndex(tasks.Count, "xóa");
                    if (selectedIndex > 0) return "delete";
                    break;
                case "4":
                    selectedIndex = PickTaskIndex(tasks.Count, "toggle");
                    if (selectedIndex > 0) return "toggle";
                    break;
                case "5": return "filter";
                case "Q": case "0": return "quit";
                default:
                    ToastNotification.Show(ToastKind.Warning, Messages.InvalidChoice, 800);
                    break;
            }
        }
    }

    public TaskFilter CurrentFilter => _currentFilter;
    public void SetFilter(TaskFilter f) => _currentFilter = f;

    private int PickTaskIndex(int count, string action)
    {
        if (count == 0)
        {
            ToastNotification.Show(ToastKind.Warning, "Không có công việc để " + action + ".", 1000);
            return 0;
        }
        Console.Write($"  Số thứ tự cần {action} (1-{count}): ");
        return ConsoleInput.ReadInt(1, count) ?? 0;
    }

    private string FilterLabel() => _currentFilter switch
    {
        TaskFilter.Pending   => "Đang chờ",
        TaskFilter.Completed => "Đã hoàn thành",
        _                    => "Tất cả"
    };

    private string EmptyMessage() => _currentFilter switch
    {
        TaskFilter.Pending   => "Không có công việc nào đang chờ.",
        TaskFilter.Completed => "Chưa có công việc nào hoàn thành.",
        _                    => "Danh sách trống. Nhấn [1] để tạo công việc đầu tiên."
    };
}
