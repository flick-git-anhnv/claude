using System.Text.Json;
using Anthropic.Models.Messages;

namespace MyClaude.Cli.Tools;

/// <summary>
/// PHASE 2 — Định nghĩa 3 tool cơ bản cho agentic loop: read_file, write_file, run_bash.
/// Đây là tập con rất thu nhỏ của bộ tool thật trong Claude Code (Read/Write/Bash).
/// </summary>
public static class ToolDefinitions
{
    public static List<Tool> All => new()
    {
        new Tool
        {
            Name = "read_file",
            Description = "Đọc nội dung 1 file trong thư mục làm việc của agent.",
            InputSchema = new()
            {
                Properties = new Dictionary<string, JsonElement>
                {
                    ["path"] = JsonSerializer.SerializeToElement(new { type = "string", description = "Đường dẫn tương đối tới file cần đọc" }),
                },
                Required = ["path"],
            },
        },
        new Tool
        {
            Name = "write_file",
            Description = "Ghi (tạo mới hoặc ghi đè) nội dung vào 1 file trong thư mục làm việc của agent.",
            InputSchema = new()
            {
                Properties = new Dictionary<string, JsonElement>
                {
                    ["path"] = JsonSerializer.SerializeToElement(new { type = "string", description = "Đường dẫn tương đối tới file cần ghi" }),
                    ["content"] = JsonSerializer.SerializeToElement(new { type = "string", description = "Nội dung sẽ ghi vào file" }),
                },
                Required = ["path", "content"],
            },
        },
        new Tool
        {
            Name = "run_bash",
            Description = "Chạy 1 lệnh shell trong thư mục làm việc của agent. Chỉ dùng cho lệnh đọc/kiểm tra đơn giản (ls, cat, git status...).",
            InputSchema = new()
            {
                Properties = new Dictionary<string, JsonElement>
                {
                    ["command"] = JsonSerializer.SerializeToElement(new { type = "string", description = "Lệnh shell cần chạy" }),
                },
                Required = ["command"],
            },
        },
    };
}
