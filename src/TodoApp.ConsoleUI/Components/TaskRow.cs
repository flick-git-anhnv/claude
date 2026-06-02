using TodoApp.ConsoleUI.Rendering;
using TodoApp.Domain;

namespace TodoApp.ConsoleUI.Components;

public static class TaskRow
{
    private const int TitleWidth = 38;

    public static void Render(int index, TodoItem item)
    {
        var statusMark = item.Status == TodoStatus.Completed
            ? AnsiConsole.Colorize(AnsiColors.Green, "[✓]")
            : AnsiConsole.Colorize(AnsiColors.Yellow, "[ ]");

        var priorityMark = item.Priority switch
        {
            Priority.High   => AnsiConsole.Colorize(AnsiColors.Red,    "[!!!]"),
            Priority.Medium => AnsiConsole.Colorize(AnsiColors.Yellow, " [!] "),
            Priority.Low    => AnsiConsole.Colorize(AnsiColors.Cyan,   " [·] "),
            _               => "     "
        };

        var title = item.Title.Length > TitleWidth
            ? item.Title[..(TitleWidth - 3)] + "..."
            : item.Title.PadRight(TitleWidth);

        if (item.Status == TodoStatus.Completed)
            title = AnsiConsole.Colorize(AnsiColors.DarkGray + AnsiColors.Strikethrough, title);

        string dueStr = "";
        if (item.DueDate.HasValue)
        {
            if (item.IsOverdue)
                dueStr = AnsiConsole.Colorize(AnsiColors.Red, $"⚠ {item.DueDate:yyyy-MM-dd}");
            else if (item.IsDueToday)
                dueStr = AnsiConsole.Colorize(AnsiColors.Yellow, $"★ {item.DueDate:yyyy-MM-dd}");
            else
                dueStr = AnsiConsole.Colorize(AnsiColors.DarkGray, $"  {item.DueDate:yyyy-MM-dd}");
        }

        var indexStr = AnsiConsole.Colorize(AnsiColors.Cyan, $"{index,2}.");
        Console.WriteLine($"  {indexStr} {statusMark} {priorityMark} {title} {dueStr}");
    }
}
