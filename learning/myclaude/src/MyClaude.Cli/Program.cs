using Anthropic;
using MyClaude.Cli;

var model = Environment.GetEnvironmentVariable("MYCLAUDE_MODEL") ?? "claude-opus-5";
var client = new AnthropicClient(); // đọc API key từ biến môi trường ANTHROPIC_API_KEY

if (args.Length == 0 || args[0] == "chat")
{
    // Phase 1 — chat CLI đơn giản
    var systemPrompt = Environment.GetEnvironmentVariable("MYCLAUDE_SYSTEM_PROMPT");
    await new ChatSession(client, model, systemPrompt).RunAsync();
}
else if (args[0] == "agent")
{
    // Phase 2 — agentic loop có tool-use, chạy trong thư mục chỉ định (mặc định: ./workspace)
    var workDir = args.Length > 1 ? args[1] : "./workspace";
    await new AgentLoop(client, model, workDir).RunAsync();
}
else
{
    Console.WriteLine("""
        MyClaude — tự viết lại 1 phiên bản mini của Claude, gọi Claude API thật.
        Usage:
          dotnet run -- chat              Phase 1: chat CLI đơn giản
          dotnet run -- agent [workdir]    Phase 2: agentic loop có tool-use (mặc định workdir=./workspace)
        """);
}
