using System.Runtime.InteropServices;

namespace TodoApp.ConsoleUI.Rendering;

/// <summary>Helper bật ANSI VT trên Windows + fallback no-color nếu không hỗ trợ (DESIGN §12.3).</summary>
public static class AnsiConsole
{
    private const uint ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004;
    private const int  STD_OUTPUT_HANDLE                  = -11;

    public static bool AnsiSupported { get; private set; }

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GetStdHandle(int nStdHandle);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetConsoleMode(IntPtr hConsoleHandle, out uint lpMode);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetConsoleMode(IntPtr hConsoleHandle, uint dwMode);

    public static void Initialize()
    {
        try
        {
            if (!RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                // Linux/Mac: ANSI natively supported
                AnsiSupported = true;
                return;
            }

            var handle = GetStdHandle(STD_OUTPUT_HANDLE);
            if (GetConsoleMode(handle, out var mode))
            {
                AnsiSupported = SetConsoleMode(handle, mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING);
            }
        }
        catch
        {
            AnsiSupported = false;
        }
    }

    public static string Colorize(string ansiCode, string text)
        => AnsiSupported ? $"{ansiCode}{text}{AnsiColors.Reset}" : text;

    public static void Write(string ansiCode, string text)
        => Console.Write(Colorize(ansiCode, text));

    public static void WriteLine(string ansiCode, string text)
        => Console.WriteLine(Colorize(ansiCode, text));

    public static string Separator(int width = 60)
        => new string('─', width);

    public static string DoubleSeparator(int width = 60)
        => new string('═', width);
}
