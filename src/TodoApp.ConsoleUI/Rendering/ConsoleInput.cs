namespace TodoApp.ConsoleUI.Rendering;

public static class ConsoleInput
{
    /// <summary>Đọc chuỗi với placeholder. Esc → trả về null.</summary>
    public static string? ReadLine(string? placeholder = null)
    {
        if (placeholder is not null)
        {
            AnsiConsole.Write(AnsiColors.DarkGray, $"[{placeholder}] ");
        }

        var input = Console.ReadLine();
        return input; // null nếu stream đóng
    }

    /// <summary>Đọc chuỗi, nếu rỗng trả về defaultValue.</summary>
    public static string ReadLineWithDefault(string defaultValue)
    {
        var input = Console.ReadLine()?.Trim();
        return string.IsNullOrEmpty(input) ? defaultValue : input;
    }

    /// <summary>Đọc số nguyên từ 1 đến max. Trả về null nếu không hợp lệ hoặc Esc.</summary>
    public static int? ReadInt(int min, int max)
    {
        var raw = Console.ReadLine()?.Trim();
        if (int.TryParse(raw, out var n) && n >= min && n <= max)
            return n;
        return null;
    }

    /// <summary>Đọc phím Y/N. Mặc định = false (N) nếu nhấn Enter.</summary>
    public static bool ReadYesNo(bool defaultYes = false)
    {
        var key = Console.ReadKey(intercept: true);
        Console.WriteLine();
        return key.Key switch
        {
            ConsoleKey.Y => true,
            ConsoleKey.N => false,
            ConsoleKey.Enter => defaultYes,
            _ => defaultYes
        };
    }

    /// <summary>Đọc chọn menu từ 1..count hoặc 'Q' để thoát. Trả về 0 = thoát.</summary>
    public static int ReadMenuChoice(int count)
    {
        var raw = Console.ReadLine()?.Trim().ToUpperInvariant();
        if (raw == "Q" || raw == "0") return 0;
        if (int.TryParse(raw, out var n) && n >= 1 && n <= count)
            return n;
        return -1; // invalid
    }

    /// <summary>Đọc DateOnly với format yyyy-MM-dd. Trả về null nếu rỗng hoặc không hợp lệ.</summary>
    public static DateOnly? ReadDateOnly()
    {
        var raw = Console.ReadLine()?.Trim();
        if (string.IsNullOrEmpty(raw)) return null;
        if (DateOnly.TryParseExact(raw, "yyyy-MM-dd",
            System.Globalization.CultureInfo.InvariantCulture,
            System.Globalization.DateTimeStyles.None, out var d))
            return d;
        return null;
    }

    public static void WaitKey(string message = "Nhấn phím bất kỳ để tiếp tục...")
    {
        AnsiConsole.Write(AnsiColors.DarkGray, message);
        Console.ReadKey(intercept: true);
        Console.WriteLine();
    }
}
