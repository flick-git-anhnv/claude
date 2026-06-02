using TodoApp.Domain;

namespace TodoApp.Infrastructure;

/// <summary>
/// Wrapper JSON cho file todos.json.
/// schemaVersion cho phép migrate format trong tương lai (US-009/010 EC dữ liệu cũ).
/// </summary>
internal sealed class StorageFileDto
{
    public int SchemaVersion { get; set; } = 1;
    public List<TodoItem> Items { get; set; } = new();
}
