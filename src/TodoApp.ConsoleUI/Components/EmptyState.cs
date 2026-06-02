using TodoApp.ConsoleUI.Rendering;

namespace TodoApp.ConsoleUI.Components;

public static class EmptyState
{
    public static void Render(string message = "Không có công việc nào.")
    {
        Console.WriteLine();
        AnsiConsole.WriteLine(AnsiColors.DarkGray, $"  (!) {message}");
        Console.WriteLine();
    }
}
