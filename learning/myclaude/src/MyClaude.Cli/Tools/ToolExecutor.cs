using System.Diagnostics;
using System.Text.Json;

namespace MyClaude.Cli.Tools;

/// <summary>
/// PHASE 2 — Thực thi tool phía client. Đây là phần "harness" — Claude chỉ quyết định GỌI tool
/// nào với input gì; code này mới là bên thật sự đọc/ghi file, chạy lệnh.
///
/// CẢNH BÁO BẢO MẬT (học tập, KHÔNG dùng nguyên bản cho production):
/// - path do model cung cấp PHẢI được resolve về canonical path và xác nhận nằm trong WorkDir
///   trước khi đọc/ghi — chặn path traversal (../, symlink, đường dẫn tuyệt đối ngoài WorkDir).
/// - run_bash ở đây KHÔNG có sandbox thật (không container, không giới hạn tài nguyên) —
///   chỉ nên dùng trong thư mục thử nghiệm riêng, không chạy trên máy có dữ liệu nhạy cảm.
/// </summary>
public class ToolExecutor
{
    private readonly string _workDir;

    public ToolExecutor(string workDir)
    {
        _workDir = Path.GetFullPath(workDir);
        Directory.CreateDirectory(_workDir);
    }

    public string Execute(string toolName, IReadOnlyDictionary<string, JsonElement> input)
    {
        try
        {
            return toolName switch
            {
                "read_file" => ReadFile(input["path"].GetString()!),
                "write_file" => WriteFile(input["path"].GetString()!, input["content"].GetString()!),
                "run_bash" => RunBash(input["command"].GetString()!),
                _ => $"Lỗi: không rõ tool '{toolName}'",
            };
        }
        catch (Exception ex)
        {
            return $"Lỗi khi thực thi {toolName}: {ex.Message}";
        }
    }

    private string ResolveSafePath(string relativePath)
    {
        var full = Path.GetFullPath(Path.Combine(_workDir, relativePath));
        if (!full.StartsWith(_workDir, StringComparison.Ordinal))
            throw new InvalidOperationException($"Path '{relativePath}' nằm ngoài thư mục làm việc — bị chặn.");
        return full;
    }

    private string ReadFile(string relativePath)
    {
        var full = ResolveSafePath(relativePath);
        if (!File.Exists(full)) return $"File không tồn tại: {relativePath}";
        return File.ReadAllText(full);
    }

    private string WriteFile(string relativePath, string content)
    {
        var full = ResolveSafePath(relativePath);
        Directory.CreateDirectory(Path.GetDirectoryName(full)!);
        File.WriteAllText(full, content);
        return $"Đã ghi {content.Length} ký tự vào {relativePath}";
    }

    private string RunBash(string command)
    {
        using var process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = "/bin/bash",
                Arguments = $"-c \"{command.Replace("\"", "\\\"")}\"",
                WorkingDirectory = _workDir,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
            }
        };

        process.Start();
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        if (!process.WaitForExit(10_000))
        {
            process.Kill();
            return "Lỗi: lệnh chạy quá 10 giây, đã bị hủy.";
        }

        return $"exit={process.ExitCode}\nstdout:\n{stdout}\nstderr:\n{stderr}";
    }
}
