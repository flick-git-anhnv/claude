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

        _service.Initialize();

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
                case "create":
                    createScreen.Show();
                    break;

                case "edit":
                case "delete":
                case "toggle":
                    // Resolve Guid dùng filter hiện tại — tránh BUG-002
                    var targetItem = _service.GetByDisplayIndex(selectedIndex, mainScreen.CurrentFilter);
                    if (targetItem is null)
                    {
                        ToastNotification.ShowAndWait(ToastKind.Error, Messages.TaskNotFound);
                        break;
                    }
                    if (action == "edit")   editScreen.Show(targetItem.Id);
                    if (action == "delete") deleteScreen.Show(targetItem.Id);
                    if (action == "toggle") toggleScreen.Show(targetItem.Id);
                    break;

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
