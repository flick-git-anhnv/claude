using Anthropic;
using Anthropic.Models.Messages;

namespace MyClaude.Cli;

/// <summary>
/// PHASE 1 — Chat CLI: giữ lịch sử hội thoại, gọi Claude API, stream phản hồi ra console.
/// Đây là cơ chế cốt lõi của mọi chatbot: API không có state — client tự gửi lại toàn bộ
/// lịch sử mỗi lần gọi (xem README "Vì sao API stateless").
/// </summary>
public class ChatSession
{
    private readonly AnthropicClient _client;
    private readonly string _model;
    private readonly string? _systemPrompt;
    private readonly List<MessageParam> _history = new();

    public ChatSession(AnthropicClient client, string model, string? systemPrompt = null)
    {
        _client = client;
        _model = model;
        _systemPrompt = systemPrompt;
    }

    public async Task RunAsync()
    {
        Console.WriteLine($"MyClaude Chat — model: {_model}. Gõ 'exit' để thoát.\n");

        while (true)
        {
            Console.Write("Bạn: ");
            var input = Console.ReadLine();
            if (string.IsNullOrWhiteSpace(input)) continue;
            if (input.Trim().Equals("exit", StringComparison.OrdinalIgnoreCase)) break;

            _history.Add(new MessageParam { Role = Role.User, Content = input });

            Console.Write("Claude: ");
            var assistantText = await StreamAssistantReplyAsync();
            Console.WriteLine("\n");

            _history.Add(new MessageParam { Role = Role.Assistant, Content = assistantText });
        }
    }

    /// <summary>Gọi API với streaming, in text ra console theo thời gian thực, trả về toàn văn để lưu vào lịch sử.</summary>
    private async Task<string> StreamAssistantReplyAsync()
    {
        var parameters = new MessageCreateParams
        {
            Model = _model,
            MaxTokens = 4096,
            System = _systemPrompt,
            // Tắt thinking cho chat CLI đơn giản — giữ output gọn, dễ đọc khi mới học.
            Thinking = new ThinkingConfigDisabled(),
            Messages = _history,
        };

        var fullText = new System.Text.StringBuilder();

        await foreach (var streamEvent in _client.Messages.CreateStreaming(parameters))
        {
            if (streamEvent.TryPickContentBlockDelta(out var delta) &&
                delta.Delta.TryPickText(out var textDelta))
            {
                Console.Write(textDelta.Text);
                fullText.Append(textDelta.Text);
            }
        }

        return fullText.ToString();
    }
}
