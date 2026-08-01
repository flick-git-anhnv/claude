using Anthropic;
using Anthropic.Models.Messages;
using MyClaude.Cli.Tools;

namespace MyClaude.Cli;

/// <summary>
/// PHASE 2 — Agentic loop: mini Claude Code. Khác Phase 1 ở chỗ model có thể GỌI TOOL
/// (đọc/ghi file, chạy lệnh) thay vì chỉ trả lời text — vòng lặp tự động thực thi tool
/// và gửi kết quả lại cho model cho đến khi model không cần gọi tool nữa (stop_reason = end_turn).
/// </summary>
public class AgentLoop
{
    private readonly AnthropicClient _client;
    private readonly string _model;
    private readonly ToolExecutor _executor;
    private readonly List<MessageParam> _history = new();

    public AgentLoop(AnthropicClient client, string model, string workDir)
    {
        _client = client;
        _model = model;
        _executor = new ToolExecutor(workDir);
    }

    public async Task RunAsync()
    {
        Console.WriteLine($"MyClaude Agent — model: {_model}. Gõ 'exit' để thoát.");
        Console.WriteLine("Ví dụ: 'Đọc file README.md và tóm tắt', 'Tạo file hello.txt với nội dung Xin chào'\n");

        while (true)
        {
            Console.Write("Bạn: ");
            var input = Console.ReadLine();
            if (string.IsNullOrWhiteSpace(input)) continue;
            if (input.Trim().Equals("exit", StringComparison.OrdinalIgnoreCase)) break;

            _history.Add(new MessageParam { Role = Role.User, Content = input });
            await RunTurnAsync();
            Console.WriteLine();
        }
    }

    /// <summary>Chạy 1 "turn": gọi API, nếu model yêu cầu tool thì thực thi và lặp lại, đến khi model trả lời xong.</summary>
    private async Task RunTurnAsync()
    {
        while (true)
        {
            var parameters = new MessageCreateParams
            {
                Model = _model,
                MaxTokens = 4096,
                System = "Bạn là 1 coding agent nhỏ, có quyền đọc/ghi file và chạy lệnh bash trong thư mục làm việc hiện tại. "
                       + "Luôn giải thích ngắn gọn trước khi gọi tool.",
                Tools = ToolDefinitions.All.Select(t => (ToolUnion)t).ToArray(),
                Messages = _history,
            };

            var response = await _client.Messages.Create(parameters);

            var assistantContent = new List<ContentBlockParam>();
            var toolResults = new List<ContentBlockParam>();

            foreach (var block in response.Content)
            {
                if (block.TryPickText(out TextBlock? text))
                {
                    Console.WriteLine($"Claude: {text.Text}");
                    assistantContent.Add(new TextBlockParam { Text = text.Text });
                }
                else if (block.TryPickToolUse(out ToolUseBlock? toolUse))
                {
                    Console.WriteLine($"  [gọi tool: {toolUse.Name}]");
                    assistantContent.Add(new ToolUseBlockParam
                    {
                        ID = toolUse.ID,
                        Name = toolUse.Name,
                        Input = toolUse.Input,
                    });

                    var result = _executor.Execute(toolUse.Name, toolUse.Input);
                    toolResults.Add(new ToolResultBlockParam
                    {
                        ToolUseID = toolUse.ID,
                        Content = result,
                    });
                }
            }

            _history.Add(new MessageParam { Role = Role.Assistant, Content = assistantContent });

            // Nếu compiler báo lỗi so sánh string ở dòng dưới (StopReason là enum riêng của SDK),
            // đổi thành: response.StopReason != StopReason.ToolUse
            if (response.StopReason != "tool_use")
                return; // model đã trả lời xong, không cần gọi tool nữa

            _history.Add(new MessageParam { Role = Role.User, Content = toolResults });
            // lặp lại: gửi tool_result lên, chờ model phản hồi tiếp
        }
    }
}
