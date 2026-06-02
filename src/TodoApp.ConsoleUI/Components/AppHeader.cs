using TodoApp.ConsoleUI.Rendering;

namespace TodoApp.ConsoleUI.Components;

public static class AppHeader
{
    public static void Render(string? subtitle = null)
    {
        Console.Clear();
        Console.WriteLine();
        AnsiConsole.WriteLine(AnsiColors.Bold + AnsiColors.BgNavy + AnsiColors.White,
            "  ✓ TO-DO APP  —  KZTEK  ");
        if (subtitle is not null)
        {
            AnsiConsole.WriteLine(AnsiColors.Cyan, $"  {subtitle}");
        }
        Console.WriteLine(AnsiConsole.Separator());
    }
}
