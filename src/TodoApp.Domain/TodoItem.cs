namespace TodoApp.Domain;

/// <summary>Entity chính đại diện cho một công việc trong hệ thống.</summary>
public sealed class TodoItem
{
    /// <summary>Định danh duy nhất, do hệ thống sinh khi tạo (BR-GLOBAL-06).</summary>
    public Guid Id { get; init; }

    /// <summary>Tiêu đề task — bắt buộc, tối đa 200 ký tự (BR-GLOBAL-01).</summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>Mô tả tuỳ chọn, tối đa 1000 ký tự (BR-GLOBAL-02).</summary>
    public string? Description { get; set; }

    /// <summary>Trạng thái hiện tại — mặc định Pending khi tạo (BR-GLOBAL-05).</summary>
    public TodoStatus Status { get; set; } = TodoStatus.Pending;

    /// <summary>Mức độ ưu tiên — mặc định None (OQ-BA-09).</summary>
    public Priority Priority { get; set; } = Priority.None;

    /// <summary>Ngày đến hạn (date-only, US-010 BR5) — tùy chọn.</summary>
    public DateOnly? DueDate { get; set; }

    /// <summary>Thời điểm tạo — không thay đổi sau khi tạo (BR-US001-6).</summary>
    public DateTime CreatedAt { get; init; }

    /// <summary>Thời điểm sửa lần cuối — cập nhật mỗi lần Update (US-003 BR3).</summary>
    public DateTime? UpdatedAt { get; set; }

    /// <summary>Thời điểm hoàn thành — set khi Completed, null khi Pending (US-005 BR2/BR3).</summary>
    public DateTime? CompletedAt { get; set; }

    /// <summary>
    /// Task đã quá hạn: có DueDate, còn Pending, và DueDate đã qua hôm nay (US-010 BR3).
    /// Không persist — tính toán tại runtime.
    /// </summary>
    public bool IsOverdue =>
        DueDate.HasValue
        && Status == TodoStatus.Pending
        && DueDate.Value < DateOnly.FromDateTime(DateTime.Now);

    /// <summary>
    /// Task đến hạn hôm nay: có DueDate, còn Pending, và DueDate == hôm nay (US-010 BR4).
    /// Không persist — tính toán tại runtime.
    /// </summary>
    public bool IsDueToday =>
        DueDate.HasValue
        && Status == TodoStatus.Pending
        && DueDate.Value == DateOnly.FromDateTime(DateTime.Now);
}
