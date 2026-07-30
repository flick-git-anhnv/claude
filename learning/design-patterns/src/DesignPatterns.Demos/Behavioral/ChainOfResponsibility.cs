namespace DesignPatterns.Demos.Behavioral.ChainOfResponsibility;

/// <summary>
/// CHAIN OF RESPONSIBILITY — chuyển request qua 1 chuỗi handler, mỗi handler tự quyết định xử lý
/// hay đẩy tiếp cho handler sau — người gửi request không cần biết ai sẽ xử lý.
/// Khi nào dùng: pipeline duyệt request qua nhiều bước kiểm tra (auth -> validate -> rate-limit -> log),
/// hoặc hệ thống approval nhiều cấp (duyệt chi phí theo hạn mức).
/// Khi KHÔNG nên dùng: chỉ có 1 bước xử lý cố định — if/else đơn giản đủ dùng, không cần chuỗi.
/// </summary>
public abstract class ExpenseApprovalHandler
{
    protected ExpenseApprovalHandler? Next;
    public ExpenseApprovalHandler SetNext(ExpenseApprovalHandler next) { Next = next; return next; }

    public abstract void Approve(decimal amount);
}

public class TeamLeadApprover : ExpenseApprovalHandler
{
    public override void Approve(decimal amount)
    {
        if (amount <= 2_000_000m) Console.WriteLine($"[Team Lead] Duyệt {amount:N0}đ");
        else Next?.Approve(amount);
    }
}

public class ManagerApprover : ExpenseApprovalHandler
{
    public override void Approve(decimal amount)
    {
        if (amount <= 20_000_000m) Console.WriteLine($"[Manager] Duyệt {amount:N0}đ");
        else Next?.Approve(amount);
    }
}

public class CtoApprover : ExpenseApprovalHandler
{
    public override void Approve(decimal amount) => Console.WriteLine($"[CTO] Duyệt {amount:N0}đ (vượt hạn mức Manager)");
}

public class ChainOfResponsibilityDemo : IPatternDemo
{
    public string Category => "Behavioral";
    public string Name => "Chain of Responsibility";

    public void Run()
    {
        var teamLead = new TeamLeadApprover();
        teamLead.SetNext(new ManagerApprover()).SetNext(new CtoApprover());

        teamLead.Approve(1_500_000m);   // Team Lead tự duyệt
        teamLead.Approve(10_000_000m);  // đẩy lên Manager
        teamLead.Approve(50_000_000m);  // đẩy lên tận CTO
    }
}
