using TodoApp.Application.Validation;
using TodoApp.Domain;

namespace TodoApp.Application;

public sealed class TodoService : ITodoService
{
    private readonly ITodoRepository _repository;

    public TodoService(ITodoRepository repository)
    {
        _repository = repository;
    }

    public OperationResult<int> Initialize()
    {
        try
        {
            var items = _repository.Load();
            return OperationResult<int>.Ok(items.Count);
        }
        catch (StorageException ex)
        {
            return OperationResult<int>.Fail(OperationErrorKind.Storage,
                $"MSG-014: Không thể tải dữ liệu. {ex.Message}");
        }
    }

    public OperationResult<TodoItem> Create(CreateTodoRequest request)
    {
        var title = request.Title?.Trim() ?? string.Empty;

        var (titleValid, titleError) = TitleValidator.Validate(title);
        if (!titleValid)
            return OperationResult<TodoItem>.Fail(OperationErrorKind.Validation, titleError!);

        var (descValid, descError) = TitleValidator.ValidateDescription(request.Description);
        if (!descValid)
            return OperationResult<TodoItem>.Fail(OperationErrorKind.Validation, descError!);

        var item = new TodoItem
        {
            Id = Guid.NewGuid(),
            Title = title,
            Description = request.Description,
            Status = TodoStatus.Pending,
            Priority = request.Priority,
            DueDate = request.DueDate,
            CreatedAt = DateTime.Now,
            UpdatedAt = null,
            CompletedAt = null
        };

        try
        {
            _repository.Add(item);
            return OperationResult<TodoItem>.Ok(item);
        }
        catch (StorageException ex)
        {
            return OperationResult<TodoItem>.Fail(OperationErrorKind.Storage,
                $"MSG-012: Không thể lưu dữ liệu. {ex.Message}");
        }
    }

    public IReadOnlyList<TodoItem> GetTasks(TaskFilter filter = TaskFilter.All)
    {
        var all = _repository.GetAll();

        IEnumerable<TodoItem> filtered = filter switch
        {
            TaskFilter.Pending   => all.Where(i => i.Status == TodoStatus.Pending),
            TaskFilter.Completed => all.Where(i => i.Status == TodoStatus.Completed),
            _                    => all
        };

        return filtered.OrderByDescending(i => i.CreatedAt).ToList().AsReadOnly();
    }

    public TodoItem? GetByDisplayIndex(int index, TaskFilter filter)
    {
        var list = GetTasks(filter);
        if (index < 1 || index > list.Count) return null;
        return list[index - 1];
    }

    public OperationResult<TodoItem> Update(Guid id, UpdateTodoRequest request)
    {
        var item = _repository.GetById(id);
        if (item is null)
            return OperationResult<TodoItem>.Fail(OperationErrorKind.NotFound,
                "MSG-006: Không tìm thấy công việc.");

        var title = request.Title?.Trim() ?? string.Empty;

        var (titleValid, titleError) = TitleValidator.Validate(title);
        if (!titleValid)
            return OperationResult<TodoItem>.Fail(OperationErrorKind.Validation, titleError!);

        var (descValid, descError) = TitleValidator.ValidateDescription(request.Description);
        if (!descValid)
            return OperationResult<TodoItem>.Fail(OperationErrorKind.Validation, descError!);

        // Snapshot để rollback
        var oldTitle       = item.Title;
        var oldDescription = item.Description;
        var oldPriority    = item.Priority;
        var oldDueDate     = item.DueDate;
        var oldUpdatedAt   = item.UpdatedAt;

        item.Title       = title;
        item.Description = request.Description;
        item.Priority    = request.Priority;
        item.DueDate     = request.DueDate;
        item.UpdatedAt   = DateTime.Now;

        try
        {
            _repository.Update(item);
            return OperationResult<TodoItem>.Ok(item);
        }
        catch (StorageException ex)
        {
            item.Title       = oldTitle;
            item.Description = oldDescription;
            item.Priority    = oldPriority;
            item.DueDate     = oldDueDate;
            item.UpdatedAt   = oldUpdatedAt;
            return OperationResult<TodoItem>.Fail(OperationErrorKind.Storage,
                $"MSG-012: Không thể lưu dữ liệu. {ex.Message}");
        }
    }

    public OperationResult<bool> Delete(Guid id)
    {
        var item = _repository.GetById(id);
        if (item is null)
            return OperationResult<bool>.Fail(OperationErrorKind.NotFound,
                "MSG-006: Không tìm thấy công việc.");

        try
        {
            _repository.Delete(id);
            return OperationResult<bool>.Ok(true);
        }
        catch (StorageException ex)
        {
            return OperationResult<bool>.Fail(OperationErrorKind.Storage,
                $"MSG-012: Không thể lưu dữ liệu. {ex.Message}");
        }
    }

    public OperationResult<TodoItem> ToggleComplete(Guid id)
    {
        var item = _repository.GetById(id);
        if (item is null)
            return OperationResult<TodoItem>.Fail(OperationErrorKind.NotFound,
                "MSG-006: Không tìm thấy công việc.");

        var oldStatus      = item.Status;
        var oldCompletedAt = item.CompletedAt;

        if (item.Status == TodoStatus.Pending)
        {
            item.Status      = TodoStatus.Completed;
            item.CompletedAt = DateTime.Now;
        }
        else
        {
            item.Status      = TodoStatus.Pending;
            item.CompletedAt = null;
        }

        try
        {
            _repository.Update(item);
            return OperationResult<TodoItem>.Ok(item);
        }
        catch (StorageException ex)
        {
            item.Status      = oldStatus;
            item.CompletedAt = oldCompletedAt;
            return OperationResult<TodoItem>.Fail(OperationErrorKind.Storage,
                $"MSG-012: Không thể lưu dữ liệu. {ex.Message}");
        }
    }

    public TaskCounts GetCounts()
    {
        var all       = _repository.GetAll();
        var pending   = all.Count(i => i.Status == TodoStatus.Pending);
        var completed = all.Count(i => i.Status == TodoStatus.Completed);
        return new TaskCounts(all.Count, pending, completed);
    }
}
