namespace DesignPatterns.Demos.Behavioral.Command;

/// <summary>
/// COMMAND — biến 1 yêu cầu/hành động thành 1 object độc lập, cho phép queue, log, undo/redo, hoặc
/// truyền hành động đi như tham số (thay vì gọi method trực tiếp).
/// Khi nào dùng: cần undo/redo, hàng đợi tác vụ (job queue), macro ghi lại thao tác để chạy lại.
/// Khi KHÔNG nên dùng: hành động gọi 1 lần, không cần undo/queue/log — gọi method trực tiếp là đủ.
/// </summary>
public interface ICommand
{
    void Execute();
    void Undo();
}

public class TextDocument
{
    public string Content { get; private set; } = "";
    public void Append(string text) => Content += text;
    public void RemoveFromEnd(int length) => Content = Content[..^length];
}

public class AppendTextCommand : ICommand
{
    private readonly TextDocument _document;
    private readonly string _text;

    public AppendTextCommand(TextDocument document, string text) { _document = document; _text = text; }

    public void Execute() => _document.Append(_text);
    public void Undo() => _document.RemoveFromEnd(_text.Length);
}

public class CommandHistory
{
    private readonly Stack<ICommand> _history = new();

    public void ExecuteAndTrack(ICommand command)
    {
        command.Execute();
        _history.Push(command);
    }

    public void UndoLast()
    {
        if (_history.TryPop(out var command)) command.Undo();
    }
}

public class CommandDemo : IPatternDemo
{
    public string Category => "Behavioral";
    public string Name => "Command";

    public void Run()
    {
        var document = new TextDocument();
        var history = new CommandHistory();

        history.ExecuteAndTrack(new AppendTextCommand(document, "Xin chào"));
        history.ExecuteAndTrack(new AppendTextCommand(document, ", KZTEK!"));
        Console.WriteLine($"Sau 2 lệnh: '{document.Content}'");

        history.UndoLast();
        Console.WriteLine($"Sau khi undo: '{document.Content}'");
    }
}
