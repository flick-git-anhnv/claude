using TodoApp.Application;
using TodoApp.ConsoleUI.Components;
using TodoApp.ConsoleUI.Rendering;
using TodoApp.Domain;

namespace TodoApp.ConsoleUI.Screens;

public sealed class EditScreen
{
    private readonly ITodoService _service;

    public EditScreen(ITodoService service)
    {
        _service = service;
    }

    public void Show(int displayIndex)
    {
        var item = _service.GetByDisplayIndex(displayIndex, TaskFilter.All);
        if (item is null)
        {
            ToastNotification.ShowAndWait(ToastKind.Error, Messages.TaskNotFound);
            return;
        }

        AppHeader.Render($"Sửa: {item.Title}");
        AnsiConsole.WriteLine(AnsiColors.DarkGray, "  (Enter = giữ nguyên giá trị hiện tại)");
        Console.WriteLine();

        // Tiêu đề
        string newTitle;
        while (true)
        {
            Console.Write($"  Tiêu đề [{item.Title}]: ");
            var input = ConsoleInput.ReadLineWithDefault(item.Title);
            if (string.IsNullOrWhiteSpace(input))
            {
                AnsiConsole.WriteLine(AnsiColors.Red, $"  {Messages.TitleEmpty}");
                continue;
            }
            if (input.Length > 200)
            {
                AnsiConsole.WriteLine(AnsiColors.Red, $"  {Messages.TitleTooLong}");
                continue;
            }
            newTitle = input.Trim();
            break;
        }

        // Mô tả
        Console.Write($"  Mô tả [{item.Description ?? "(trống)"}]: ");
        var descInput = ConsoleInput.ReadLineWithDefault(item.Description ?? "");
        var newDesc = string.IsNullOrEmpty(descInput) ? null : descInput;

        // Ưu tiên
        var priorityLabel = item.Priority switch
        {
            Priority.High   => "4-Cao",
            Priority.Medium => "3-Trung bình",
            Priority.Low    => "2-Thấp",
            _               => "1-Không"
        };
        AnsiConsole.Write(AnsiColors.Cyan, $"  Ưu tiên [{priorityLabel}] [1/2/3/4]: ");
        var newPriority = ConsoleInput.ReadInt(1, 4) switch
        {
            2 => Priority.Low,
            3 => Priority.Medium,
            4 => Priority.High,
            1 => Priority.None,
            _ => item.Priority   // giữ nguyên nếu invalid
        };

        // Ngày hạn
        var dueCurrent = item.DueDate?.ToString("yyyy-MM-dd") ?? "(không)";
        Console.Write($"  Ngày hạn [{dueCurrent}] yyyy-MM-dd (Enter giữ nguyên): ");
        var dueInput = Console.ReadLine()?.Trim();
        DateOnly? newDue = item.DueDate;
        if (!string.IsNullOrEmpty(dueInput))
        {
            if (DateOnly.TryParseExact(dueInput, "yyyy-MM-dd",
                System.Globalization.CultureInfo.InvariantCulture,
                System.Globalization.DateTimeStyles.None, out var d))
                newDue = d;
            else
                AnsiConsole.WriteLine(AnsiColors.Yellow, $"  Ngày không hợp lệ — giữ nguyên [{dueCurrent}].");
        }

        var result = _service.Update(item.Id, new UpdateTodoRequest(newTitle, newDesc, newPriority, newDue));
        if (result.Success)
            ToastNotification.Show(ToastKind.Success, Messages.TaskUpdated);
        else
            ToastNotification.ShowAndWait(ToastKind.Error, result.ErrorMessage ?? Messages.StorageError);
    }
}
