namespace TodoApp.ConsoleUI;

/// <summary>MSG-001..014 theo DESIGN §8.1.</summary>
public static class Messages
{
    public const string TitleEmpty        = "Tiêu đề không được để trống.";
    public const string TitleTooLong      = "Tiêu đề không được vượt quá 200 ký tự.";
    public const string DescTooLong       = "Mô tả không được vượt quá 1000 ký tự.";
    public const string DateInvalidFormat = "Ngày không hợp lệ. Nhập đúng định dạng yyyy-MM-dd.";
    public const string DateInPast        = "Cảnh báo: Ngày hạn đã qua. Bạn có muốn tiếp tục? (Y/N)";
    public const string TaskNotFound      = "Không tìm thấy công việc.";

    public const string TaskCreated       = "Công việc đã được tạo thành công!";
    public const string TaskUpdated       = "Công việc đã được cập nhật!";
    public const string TaskDeleted       = "Công việc đã được xóa!";
    public const string TaskCompleted     = "Đã đánh dấu hoàn thành!";
    public const string TaskReopened      = "Đã mở lại công việc!";

    public const string StorageError      = "Lỗi lưu dữ liệu. Kiểm tra quyền truy cập hoặc dung lượng đĩa.";
    public const string DataCorrupt       = "Dữ liệu bị hỏng đã được sao lưu. Bắt đầu với danh sách trống.";
    public const string PermissionError   = "Không có quyền đọc dữ liệu. Ứng dụng chạy với danh sách trống.";

    public const string ConfirmDelete     = "Xác nhận XÓA? Thao tác này không thể hoàn tác. (Y/N, mặc định N): ";
    public const string PressAnyKey       = "Nhấn phím bất kỳ để tiếp tục...";
    public const string InvalidChoice     = "Lựa chọn không hợp lệ. Vui lòng thử lại.";
}
