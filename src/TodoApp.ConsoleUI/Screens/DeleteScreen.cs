using TodoApp.Application;
using TodoApp.ConsoleUI.Components;
using TodoApp.ConsoleUI.Rendering;

namespace TodoApp.ConsoleUI.Screens;

public sealed class DeleteScreen
{
    private readonly ITodoService _service;

    public DeleteScreen(ITodoService service)
    {
        _service = service;
    }

    public void Show(Guid id)
    {
        var item = _service.GetTasks(TaskFilter.All).FirstOrDefault(t => t.Id == id);
        if (item is null)
        {
            ToastNotification.ShowAndWait(ToastKind.Error, Messages.TaskNotFound);
            return;
        }

        AppHeader.Render("Xóa công việc");
        AnsiConsole.WriteLine(AnsiColors.Red, $"  Sắp xóa: \"{item.Title}\"");
        Console.WriteLine();
        // Enter mặc định = N (an toàn, TDD §8 BR7)
        Console.Write(Messages.ConfirmDelete);

        if (!ConsoleInput.ReadYesNo(defaultYes: false))
        {
            ToastNotification.Show(ToastKind.Info, "Đã hủy.", 600);
            return;
        }

        var result = _service.Delete(item.Id);
        if (result.Success)
            ToastNotification.Show(ToastKind.Success, Messages.TaskDeleted);
        else
            ToastNotification.ShowAndWait(ToastKind.Error, result.ErrorMessage ?? Messages.StorageError);
    }
}
