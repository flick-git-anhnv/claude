using TodoApp.Domain;

namespace TodoApp.Application;

/// <summary>Dữ liệu đầu vào để tạo task mới (F01 — US-001).</summary>
public sealed record CreateTodoRequest(
    string Title,
    string? Description = null,
    Priority Priority = Priority.None,
    DateOnly? DueDate = null);

/// <summary>Dữ liệu đầu vào để cập nhật task (F03, F09, F10 — US-003/009/010).</summary>
public sealed record UpdateTodoRequest(
    string Title,
    string? Description,
    Priority Priority,
    DateOnly? DueDate);

/// <summary>Số lượng task theo nhóm trạng thái — dùng cho StatusBar và FilterScreen.</summary>
public sealed record TaskCounts(int Total, int Pending, int Completed);
