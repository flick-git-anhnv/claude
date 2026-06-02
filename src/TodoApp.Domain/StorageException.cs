namespace TodoApp.Domain;

/// <summary>
/// Exception ném ra bởi Infrastructure khi không thể đọc/ghi storage.
/// Application bắt exception này và đổi thành OperationResult.Fail(Storage).
/// </summary>
public sealed class StorageException : Exception
{
    public StorageException(string message) : base(message) { }

    public StorageException(string message, Exception innerException)
        : base(message, innerException) { }
}
