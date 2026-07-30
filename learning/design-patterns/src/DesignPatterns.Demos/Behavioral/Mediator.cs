namespace DesignPatterns.Demos.Behavioral.Mediator;

/// <summary>
/// MEDIATOR — thay vì để nhiều object gọi thẳng lẫn nhau (N×N liên kết chằng chịt), tất cả giao tiếp
/// qua 1 "trung gian" (mediator) — giảm coupling giữa các object với nhau.
/// Khi nào dùng: nhiều UI control phải phối hợp phức tạp (form với nhiều field phụ thuộc nhau),
/// hoặc nhiều service phải phối hợp nhưng không nên biết trực tiếp về nhau.
/// Khi KHÔNG nên dùng: chỉ 2 object giao tiếp đơn giản — gọi trực tiếp rõ ràng hơn qua trung gian.
/// </summary>
public interface IChatMediator
{
    void SendMessage(string message, ChatUser sender);
    void Register(ChatUser user);
}

public class ChatRoomMediator : IChatMediator
{
    private readonly List<ChatUser> _users = new();
    public void Register(ChatUser user) => _users.Add(user);

    public void SendMessage(string message, ChatUser sender)
    {
        foreach (var user in _users.Where(u => u != sender))
            user.Receive(message, sender.Name);
    }
}

public class ChatUser
{
    public string Name { get; }
    private readonly IChatMediator _mediator;

    public ChatUser(string name, IChatMediator mediator)
    {
        Name = name;
        _mediator = mediator;
        _mediator.Register(this);
    }

    public void Send(string message) => _mediator.SendMessage(message, this);
    public void Receive(string message, string fromName) => Console.WriteLine($"  [{Name} nhận] {fromName}: {message}");
}

public class MediatorDemo : IPatternDemo
{
    public string Category => "Behavioral";
    public string Name => "Mediator";

    public void Run()
    {
        var chatRoom = new ChatRoomMediator();
        var alice = new ChatUser("Alice", chatRoom);
        var bob = new ChatUser("Bob", chatRoom);
        var charlie = new ChatUser("Charlie", chatRoom);

        // Alice không cần biết Bob/Charlie tồn tại — chỉ nói chuyện qua mediator.
        alice.Send("Chào mọi người!");
    }
}
