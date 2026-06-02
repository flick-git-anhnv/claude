using TodoApp.Application;
using TodoApp.ConsoleUI.Rendering;

namespace TodoApp.ConsoleUI.Components;

public static class StatusBar
{
    public static void Render(TaskCounts counts)
    {
        Console.Write("  ");
        AnsiConsole.Write(AnsiColors.DarkGray, $"Tổng: {counts.Total}  |  ");
        AnsiConsole.Write(AnsiColors.Yellow,   $"Chờ: {counts.Pending}  ");
        AnsiConsole.Write(AnsiColors.Green,    $"Xong: {counts.Completed}");
        Console.WriteLine();
        Console.WriteLine(AnsiConsole.Separator());
    }
}
