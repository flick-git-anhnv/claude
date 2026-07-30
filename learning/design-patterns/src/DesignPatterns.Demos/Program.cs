using DesignPatterns.Demos;
using DesignPatterns.Demos.Creational.Singleton;
using DesignPatterns.Demos.Creational.FactoryMethod;
using DesignPatterns.Demos.Creational.AbstractFactory;
using DesignPatterns.Demos.Creational.Builder;
using DesignPatterns.Demos.Creational.Prototype;
using DesignPatterns.Demos.Structural.Adapter;
using DesignPatterns.Demos.Structural.Bridge;
using DesignPatterns.Demos.Structural.Composite;
using DesignPatterns.Demos.Structural.Decorator;
using DesignPatterns.Demos.Structural.Facade;
using DesignPatterns.Demos.Structural.Flyweight;
using DesignPatterns.Demos.Structural.Proxy;
using DesignPatterns.Demos.Behavioral.ChainOfResponsibility;
using DesignPatterns.Demos.Behavioral.Command;
using DesignPatterns.Demos.Behavioral.Interpreter;
using DesignPatterns.Demos.Behavioral.Iterator;
using DesignPatterns.Demos.Behavioral.Mediator;
using DesignPatterns.Demos.Behavioral.Memento;
using DesignPatterns.Demos.Behavioral.Observer;
using DesignPatterns.Demos.Behavioral.State;
using DesignPatterns.Demos.Behavioral.Strategy;
using DesignPatterns.Demos.Behavioral.TemplateMethod;
using DesignPatterns.Demos.Behavioral.Visitor;

List<IPatternDemo> allDemos = new()
{
    // Creational
    new SingletonDemo(), new FactoryMethodDemo(), new AbstractFactoryDemo(), new BuilderDemo(), new PrototypeDemo(),
    // Structural
    new AdapterDemo(), new BridgeDemo(), new CompositeDemo(), new DecoratorDemo(), new FacadeDemo(), new FlyweightDemo(), new ProxyDemo(),
    // Behavioral
    new ChainOfResponsibilityDemo(), new CommandDemo(), new InterpreterDemo(), new IteratorDemo(), new MediatorDemo(),
    new MementoDemo(), new ObserverDemo(), new StateDemo(), new StrategyDemo(), new TemplateMethodDemo(), new VisitorDemo(),
};

if (args.Length == 0)
{
    PrintMenu(allDemos);
    return 0;
}

if (args[0] == "all")
{
    foreach (var demo in allDemos) RunDemo(demo);
    return 0;
}

var match = allDemos.FirstOrDefault(d => d.Name.Equals(args[0], StringComparison.OrdinalIgnoreCase)
                                          || d.Name.Replace(" ", "").Equals(args[0], StringComparison.OrdinalIgnoreCase));
if (match == null)
{
    Console.WriteLine($"Không tìm thấy pattern '{args[0]}'. Chạy không kèm tham số để xem danh sách.");
    return 1;
}

RunDemo(match);
return 0;

static void RunDemo(IPatternDemo demo)
{
    Console.WriteLine($"\n=== [{demo.Category}] {demo.Name} ===");
    demo.Run();
}

static void PrintMenu(List<IPatternDemo> demos)
{
    Console.WriteLine("MyDesignPatterns — chạy demo cho từng pattern GoF (23 pattern).");
    Console.WriteLine("Usage: dotnet run -- \"<TenPattern>\"   (vd: dotnet run -- Singleton)");
    Console.WriteLine("       dotnet run -- all               (chạy toàn bộ 23 demo)\n");

    foreach (var group in demos.GroupBy(d => d.Category))
    {
        Console.WriteLine($"[{group.Key}]");
        foreach (var demo in group) Console.WriteLine($"  - {demo.Name}");
    }
}
