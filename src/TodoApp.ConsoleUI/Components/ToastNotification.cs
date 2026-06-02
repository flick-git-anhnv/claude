using TodoApp.ConsoleUI.Rendering;

namespace TodoApp.ConsoleUI.Components;

public enum ToastKind { Success, Error, Warning, Info }

public static class ToastNotification
{
    public static void Show(ToastKind kind, string message, int delayMs = 1500)
    {
        Console.WriteLine();
        var (color, icon) = kind switch
        {
            ToastKind.Success => (AnsiColors.Green,  "✓"),
            ToastKind.Error   => (AnsiColors.Red,    "✗"),
            ToastKind.Warning => (AnsiColors.Yellow, "⚠"),
            _                 => (AnsiColors.Cyan,   "i")
        };
        AnsiConsole.WriteLine(color, $"  {icon} {message}");

        if (delayMs > 0)
            Thread.Sleep(delayMs);
    }

    public static void ShowAndWait(ToastKind kind, string message)
    {
        Show(kind, message, 0);
        ConsoleInput.WaitKey();
    }
}
