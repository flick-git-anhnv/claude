using TodoApp.Application;
using TodoApp.ConsoleUI.Components;
using TodoApp.ConsoleUI.Rendering;
using TodoApp.Domain;

namespace TodoApp.ConsoleUI.Screens;

public sealed class CreateScreen
{
    private readonly ITodoService _service;

    public CreateScreen(ITodoService service)
    {
        _service = service;
    }

    public void Show()
    {
        AppHeader.Render("Tạo công việc mới");

        // Bước 1: Tiêu đề
        string title;
        while (true)
        {
            Console.Write("  Tiêu đề (*): ");
            var input = Console.ReadLine()?.Trim() ?? "";
            if (string.IsNullOrEmpty(input))
            {
                AnsiConsole.WriteLine(AnsiColors.Red, $"  {Messages.TitleEmpty}");
                continue;
            }
            if (input.Length > 200)
            {
                AnsiConsole.WriteLine(AnsiColors.Red, $"  {Messages.TitleTooLong}");
                continue;
            }
            title = input;
            break;
        }

        // Bước 2: Mô tả
        Console.Write("  Mô tả (Enter để bỏ qua): ");
        var desc = Console.ReadLine()?.Trim();
        if (string.IsNullOrEmpty(desc)) desc = null;

        // Bước 3: Ưu tiên
        var priority = PickPriority();

        // Bước 4: Ngày hạn
        var dueDate = PickDueDate();

        // Xác nhận
        Console.WriteLine();
        Console.WriteLine(AnsiConsole.Separator());
        AnsiConsole.WriteLine(AnsiColors.White, $"  Tiêu đề : {title}");
        if (desc is not null)   AnsiConsole.WriteLine(AnsiColors.DarkGray, $"  Mô tả   : {desc}");
        AnsiConsole.WriteLine(AnsiColors.DarkGray, $"  Ưu tiên : {PriorityLabel(priority)}");
        if (dueDate.HasValue)   AnsiConsole.WriteLine(AnsiColors.DarkGray, $"  Ngày hạn: {dueDate:yyyy-MM-dd}");
        Console.WriteLine();
        Console.Write("  Xác nhận tạo? (Y/N, mặc định Y): ");

        if (!ConsoleInput.ReadYesNo(defaultYes: true))
        {
            ToastNotification.Show(ToastKind.Info, "Đã hủy.", 600);
            return;
        }

        var result = _service.Create(new CreateTodoRequest(title, desc, priority, dueDate));
        if (result.Success)
            ToastNotification.Show(ToastKind.Success, Messages.TaskCreated);
        else
            ToastNotification.ShowAndWait(ToastKind.Error, result.ErrorMessage ?? Messages.StorageError);
    }

    private static Priority PickPriority()
    {
        AnsiConsole.WriteLine(AnsiColors.Cyan, "  Ưu tiên: [1] Không  [2] Thấp  [3] Trung bình  [4] Cao");
        Console.Write("  Chọn (mặc định 1): ");
        return ConsoleInput.ReadInt(1, 4) switch
        {
            2 => Priority.Low,
            3 => Priority.Medium,
            4 => Priority.High,
            _ => Priority.None
        };
    }

    private static DateOnly? PickDueDate()
    {
        while (true)
        {
            Console.Write("  Ngày hạn yyyy-MM-dd (Enter để bỏ): ");
            var raw = Console.ReadLine()?.Trim();
            if (string.IsNullOrEmpty(raw)) return null;

            if (!DateOnly.TryParseExact(raw, "yyyy-MM-dd",
                System.Globalization.CultureInfo.InvariantCulture,
                System.Globalization.DateTimeStyles.None, out var d))
            {
                AnsiConsole.WriteLine(AnsiColors.Red, $"  {Messages.DateInvalidFormat}");
                continue;
            }

            if (d < DateOnly.FromDateTime(DateTime.Today))
            {
                AnsiConsole.Write(AnsiColors.Yellow, $"  {Messages.DateInPast} ");
                if (!ConsoleInput.ReadYesNo(false)) continue;
            }
            return d;
        }
    }

    private static string PriorityLabel(Priority p) => p switch
    {
        Priority.High   => "Cao [!!!]",
        Priority.Medium => "Trung bình [!]",
        Priority.Low    => "Thấp [·]",
        _               => "Không"
    };
}
