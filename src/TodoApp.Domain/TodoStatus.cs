namespace TodoApp.Domain;

// Tên TodoStatus thay vì TaskStatus để tránh xung đột với System.Threading.Tasks.TaskStatus (TR5).
/// <summary>Trạng thái của task (BR-GLOBAL-05: mặc định Pending khi tạo).</summary>
public enum TodoStatus
{
    Pending = 0,
    Completed = 1
}
