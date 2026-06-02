using TodoApp.Application;
using TodoApp.ConsoleUI.Components;
using TodoApp.ConsoleUI.Rendering;
using TodoApp.ConsoleUI.Screens;
using TodoApp.Domain;
using TodoApp.Infrastructure;

namespace TodoApp.ConsoleUI;

public sealed class AppRunner
{
    private readonly ITodoService _service;
    private readonly JsonFileRepository? _repo;

    public AppRunner(ITodoService service, ITodoRepository repository)
    {
        _service = service;
        _repo = repository as JsonFileRepository;
    }

    public void Run()
    {
        AnsiConsole.Initialize();

        // Initialize — load dữ liệu
        var initResult = _service.Initialize();

        // Hiển thị cảnh báo nếu có vấn đề storage khi khởi động
        if (_repo is not null)
        {
            if (_repo.CorruptionDetected)
                ToastNotification.ShowAndWait(ToastKind.Warning, Messages.DataCorrupt);
            else if (_repo.PermissionErrorOnLoad)
                ToastNotification.ShowAndWait(ToastKind.Warning, Messages.PermissionError);
        }

        var mainScreen   = new MainScreen(_service);
        var createScreen = new CreateScreen(_service);
        var editScreen   = new EditScreen(_service);
        var deleteScreen = new DeleteScreen(_service);
        var toggleScreen = new ToggleScreen(_service);
        var filterScreen = new FilterScreen(_service);

        while (true)
        {
            var action = mainScreen.Show(out var selectedIndex);

            switch (action)
            {
                case "create": createScreen.Show(); break;
                case "edit":   editScreen.Show(selectedIndex); break;
                case "delete": deleteScreen.Show(selectedIndex); break;
                case "toggle": toggleScreen.Show(selectedIndex); break;
                case "filter":
                    var newFilter = filterScreen.Show(mainScreen.CurrentFilter);
                    mainScreen.SetFilter(newFilter);
                    break;
                case "quit":
                    Console.Clear();
                    AnsiConsole.WriteLine(AnsiColors.Green, "  Tạm biệt! Dữ liệu đã được lưu.");
                    Console.WriteLine();
                    return;
            }
        }
    }
}
