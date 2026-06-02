namespace TodoApp.Application;

/// <summary>Kiểu trả về chuẩn của tất cả method trong ITodoService — không throw exception nghiệp vụ.</summary>
public sealed class OperationResult<T>
{
    public bool Success { get; private init; }
    public T? Value { get; private init; }

    /// <summary>Mã thông báo lỗi (MSG-xxx) hoặc text mô tả.</summary>
    public string? ErrorMessage { get; private init; }

    public OperationErrorKind ErrorKind { get; private init; }

    public static OperationResult<T> Ok(T value) =>
        new() { Success = true, Value = value };

    public static OperationResult<T> Fail(OperationErrorKind kind, string message) =>
        new() { Success = false, ErrorKind = kind, ErrorMessage = message };
}

/// <summary>Loại lỗi trong OperationResult.</summary>
public enum OperationErrorKind
{
    None = 0,

    /// <summary>Lỗi validation: tiêu đề rỗng/quá dài, mô tả quá dài, ngày sai.</summary>
    Validation = 1,

    /// <summary>Task không tìm thấy theo Id hoặc display index.</summary>
    NotFound = 2,

    /// <summary>Lỗi đọc/ghi file storage.</summary>
    Storage = 3
}
