namespace DesignPatterns.Demos.Creational.AbstractFactory;

/// <summary>
/// ABSTRACT FACTORY — tạo ra 1 HỌ các object liên quan với nhau, đảm bảo chúng tương thích nhau,
/// mà không cần biết class cụ thể (khác Factory Method: đây là factory tạo NHIỀU loại object cùng lúc).
/// Khi nào dùng: cần switch cả 1 bộ UI theo theme (Light/Dark), hoặc 1 bộ driver theo hệ điều hành.
/// Khi KHÔNG nên dùng: chỉ có 1 họ sản phẩm, không có biến thể — over-engineering không cần thiết.
/// </summary>
public interface IButton { void Render(); }
public interface ICheckbox { void Render(); }

public class LightButton : IButton { public void Render() => Console.WriteLine("[Light] Button trắng, viền mảnh"); }
public class LightCheckbox : ICheckbox { public void Render() => Console.WriteLine("[Light] Checkbox trắng"); }

public class DarkButton : IButton { public void Render() => Console.WriteLine("[Dark] Button đen, viền neon"); }
public class DarkCheckbox : ICheckbox { public void Render() => Console.WriteLine("[Dark] Checkbox đen"); }

public interface IUiFactory
{
    IButton CreateButton();
    ICheckbox CreateCheckbox();
}

public class LightThemeFactory : IUiFactory
{
    public IButton CreateButton() => new LightButton();
    public ICheckbox CreateCheckbox() => new LightCheckbox();
}

public class DarkThemeFactory : IUiFactory
{
    public IButton CreateButton() => new DarkButton();
    public ICheckbox CreateCheckbox() => new DarkCheckbox();
}

public class AbstractFactoryDemo : IPatternDemo
{
    public string Category => "Creational";
    public string Name => "Abstract Factory";

    public void Run()
    {
        RenderForm(new LightThemeFactory());
        RenderForm(new DarkThemeFactory());
    }

    private static void RenderForm(IUiFactory factory)
    {
        // Code này không cần biết theme nào — factory đảm bảo Button và Checkbox luôn "đồng bộ" cùng 1 theme.
        factory.CreateButton().Render();
        factory.CreateCheckbox().Render();
    }
}
