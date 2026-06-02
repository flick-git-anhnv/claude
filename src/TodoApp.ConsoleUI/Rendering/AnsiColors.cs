namespace TodoApp.ConsoleUI.Rendering;

/// <summary>Bảng màu ANSI theo DESIGN §3.1. Fallback tự động nếu terminal không hỗ trợ.</summary>
public static class AnsiColors
{
    // ANSI escape codes
    public const string Reset       = "\x1b[0m";
    public const string Bold        = "\x1b[1m";
    public const string Dim         = "\x1b[2m";
    public const string Strikethrough = "\x1b[9m";

    public const string White       = "\x1b[97m";
    public const string Cyan        = "\x1b[96m";
    public const string Green       = "\x1b[92m";
    public const string Yellow      = "\x1b[93m";
    public const string Red         = "\x1b[91m";
    public const string DarkGray    = "\x1b[90m";
    public const string Blue        = "\x1b[94m";

    public const string BgNavy      = "\x1b[48;2;37;28;83m";   // KZTEK Navy #251C53
    public const string BgOrange    = "\x1b[48;2;240;89;34m";  // KZTEK Orange #F05922
    public const string FgNavy      = "\x1b[38;2;37;28;83m";
    public const string FgOrange    = "\x1b[38;2;240;89;34m";
}
