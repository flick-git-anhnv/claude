using TodoApp.Domain;

namespace TodoApp.Application;

/// <summary>
/// Contract duy nhất mà Presentation layer được phép gọi.
/// Không throw exception nghiệp vụ — mọi lỗi trả về qua OperationResult.
/// </summary>
public interface ITodoService
{
    /// <summary>
    /// Nạp dữ liệu từ storage khi khởi động (US-007).
    /// UI gọi 1 lần trong Program.cs sau khi wire DI.
    /// Value = số task đã nạp.
    /// </summary>
    OperationResult<int> Initialize();

    /// <summary>F01 — Tạo task mới. Validate title trước khi persist (US-001).</summary>
    OperationResult<TodoItem> Create(CreateTodoRequest request);

    /// <summary>
    /// F02/F08 — Lấy danh sách theo filter, sort CreatedAt DESC (US-002 BR1, US-008).
    /// Không đọc lại đĩa — dùng in-memory.
    /// </summary>
    IReadOnlyList<TodoItem> GetTasks(TaskFilter filter = TaskFilter.All);

    /// <summary>
    /// Lấy 1 task theo số thứ tự hiển thị (1-based) trong filter hiện tại.
    /// Trả null nếu index out-of-range.
    /// </summary>
    TodoItem? GetByDisplayIndex(int index, TaskFilter filter);

    /// <summary>F03 — Sửa title/desc/priority/dueDate (US-003, US-009, US-010).</summary>
    OperationResult<TodoItem> Update(Guid id, UpdateTodoRequest request);

    /// <summary>F04 — Xóa vĩnh viễn task theo Id (US-004).</summary>
    OperationResult<bool> Delete(Guid id);

    /// <summary>
    /// F05 — Toggle Pending ↔ Completed.
    /// Pending → Completed: set CompletedAt = Now (US-005 BR2).
    /// Completed → Pending: clear CompletedAt (US-005 BR3).
    /// </summary>
    OperationResult<TodoItem> ToggleComplete(Guid id);

    /// <summary>Số lượng task theo nhóm cho StatusBar/FilterScreen (DESIGN §9.2).</summary>
    TaskCounts GetCounts();
}
