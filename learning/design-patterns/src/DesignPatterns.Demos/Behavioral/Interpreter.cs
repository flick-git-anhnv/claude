namespace DesignPatterns.Demos.Behavioral.Interpreter;

/// <summary>
/// INTERPRETER — định nghĩa ngữ pháp cho 1 ngôn ngữ đơn giản, mỗi luật ngữ pháp là 1 class có thể
/// "Interpret" (đánh giá) 1 câu viết theo ngôn ngữ đó — dùng để build cây biểu thức và tính giá trị.
/// Khi nào dùng: cần parse/tính biểu thức đơn giản lặp lại (công thức tính giá, rule engine, filter query).
/// Khi KHÔNG nên dùng: ngôn ngữ phức tạp (SQL, DSL lớn) — nên dùng parser generator (ANTLR) thay vì tự viết.
/// </summary>
public interface IExpression
{
    int Interpret();
}

public class NumberExpression : IExpression
{
    private readonly int _value;
    public NumberExpression(int value) => _value = value;
    public int Interpret() => _value;
}

public class AddExpression : IExpression
{
    private readonly IExpression _left, _right;
    public AddExpression(IExpression left, IExpression right) { _left = left; _right = right; }
    public int Interpret() => _left.Interpret() + _right.Interpret();
}

public class MultiplyExpression : IExpression
{
    private readonly IExpression _left, _right;
    public MultiplyExpression(IExpression left, IExpression right) { _left = left; _right = right; }
    public int Interpret() => _left.Interpret() * _right.Interpret();
}

public class InterpreterDemo : IPatternDemo
{
    public string Category => "Behavioral";
    public string Name => "Interpreter";

    public void Run()
    {
        // Biểu diễn cây cho biểu thức: (2 + 3) * 4
        IExpression expression = new MultiplyExpression(
            new AddExpression(new NumberExpression(2), new NumberExpression(3)),
            new NumberExpression(4)
        );

        Console.WriteLine($"(2 + 3) * 4 = {expression.Interpret()}");
    }
}
