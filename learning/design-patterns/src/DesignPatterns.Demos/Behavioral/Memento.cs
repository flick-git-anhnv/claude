namespace DesignPatterns.Demos.Behavioral.Memento;

/// <summary>
/// MEMENTO — chụp lại (snapshot) trạng thái nội bộ của 1 object tại 1 thời điểm, để có thể khôi phục
/// lại sau này, MÀ KHÔNG vi phạm encapsulation (object khác không được đọc trực tiếp trạng thái riêng tư).
/// Khi nào dùng: cần undo nhiều bước (editor), checkpoint/rollback trong 1 quy trình dài.
/// Khi KHÔNG nên dùng: chỉ cần undo 1 bước đơn giản — Command pattern (Undo trực tiếp) gọn hơn.
/// </summary>
public class EditorMemento // snapshot bất biến — chỉ Editor mới đọc được nội dung bên trong
{
    internal string Content { get; }
    internal EditorMemento(string content) => Content = content;
}

public class TextEditor
{
    public string Content { get; private set; } = "";

    public void Type(string text) => Content += text;
    public EditorMemento Save() => new(Content);
    public void Restore(EditorMemento memento) => Content = memento.Content;
}

public class EditorHistory // caretaker — giữ danh sách memento, KHÔNG đọc nội dung bên trong chúng
{
    private readonly Stack<EditorMemento> _snapshots = new();
    public void Push(EditorMemento memento) => _snapshots.Push(memento);
    public EditorMemento Pop() => _snapshots.Pop();
}

public class MementoDemo : IPatternDemo
{
    public string Category => "Behavioral";
    public string Name => "Memento";

    public void Run()
    {
        var editor = new TextEditor();
        var history = new EditorHistory();

        editor.Type("Dòng 1. ");
        history.Push(editor.Save()); // checkpoint sau dòng 1

        editor.Type("Dòng 2 (sẽ bị undo). ");
        Console.WriteLine($"Trước khi undo: '{editor.Content}'");

        editor.Restore(history.Pop());
        Console.WriteLine($"Sau khi undo: '{editor.Content}'");
    }
}
