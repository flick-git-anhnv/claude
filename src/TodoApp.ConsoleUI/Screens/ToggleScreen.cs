using TodoApp.Application;
using TodoApp.ConsoleUI.Components;
using TodoApp.Domain;

namespace TodoApp.ConsoleUI.Screens;

public sealed class ToggleScreen
{
    private readonly ITodoService _service;

    public ToggleScreen(ITodoService service)
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

        var result = _service.ToggleComplete(item.Id);
        if (result.Success)
        {
            var msg = result.Value!.Status == TodoStatus.Completed
                ? Messages.TaskCompleted
                : Messages.TaskReopened;
            ToastNotification.Show(ToastKind.Success, msg);
        }
        else
        {
            ToastNotification.ShowAndWait(ToastKind.Error, result.ErrorMessage ?? Messages.StorageError);
        }
    }
}
