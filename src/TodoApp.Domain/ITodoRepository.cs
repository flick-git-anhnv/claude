namespace TodoApp.Domain;

/// <summary>
/// Port định nghĩa hợp đồng lưu trữ — implement ở Infrastructure.
/// In-memory list được nạp 1 lần lúc khởi động; persist sau mỗi thay đổi.
/// </summary>
public interface ITodoRepository
{
    /// <summary>
    /// Nạp toàn bộ task từ storage. Gọi 1 lần lúc khởi động (US-007).
    /// - File không tồn tại → trả list rỗng (Sc.2).
    /// - File corrupt → backup .bak + trả list rỗng, không throw (Sc.3).
    /// - Permission denied → trả list rỗng, không throw (Sc.4).
    /// </summary>
    IReadOnlyList<TodoItem> Load();

    /// <summary>Lấy snapshot in-memory hiện tại — không đọc lại đĩa.</summary>
    IReadOnlyList<TodoItem> GetAll();

    /// <summary>Tìm task theo Id trong in-memory. Trả null nếu không tìm thấy.</summary>
    TodoItem? GetById(Guid id);

    /// <summary>
    /// Thêm task vào in-memory và persist ngay (US-006 BR1).
    /// Ném <see cref="StorageException"/> nếu ghi đĩa thất bại.
    /// </summary>
    void Add(TodoItem item);

    /// <summary>
    /// Cập nhật task trong in-memory và persist ngay.
    /// Trả <c>false</c> nếu không tìm thấy Id.
    /// Ném <see cref="StorageException"/> nếu ghi đĩa thất bại.
    /// </summary>
    bool Update(TodoItem item);

    /// <summary>
    /// Xóa task khỏi in-memory và persist ngay.
    /// Trả <c>false</c> nếu không tìm thấy Id.
    /// Ném <see cref="StorageException"/> nếu ghi đĩa thất bại.
    /// </summary>
    bool Delete(Guid id);
}
