using System.Text.Json;
using System.Text.Json.Serialization;
using TodoApp.Domain;

namespace TodoApp.Infrastructure;

/// <summary>
/// Implement ITodoRepository dùng file JSON.
/// - In-memory list là source-of-truth trong session.
/// - Mọi mutate (Add/Update/Delete) ghi xuống đĩa ngay sau khi cập nhật in-memory.
/// - Atomic write: ghi file tạm → rename (US-006 BR2).
/// - Corrupt load: backup .bak + list rỗng (US-007 BR3).
/// </summary>
public sealed class JsonFileRepository : ITodoRepository
{
    private readonly JsonStorageOptions _options;
    private readonly JsonSerializerOptions _jsonOptions;
    private List<TodoItem> _items = new();

    /// <summary>
    /// Cờ báo file bị corrupt khi Load — UI có thể dựa vào đây để hiển thị MSG-013.
    /// </summary>
    public bool CorruptionDetected { get; private set; }

    /// <summary>
    /// Cờ báo lỗi permission khi Load — UI hiển thị MSG-014.
    /// </summary>
    public bool PermissionErrorOnLoad { get; private set; }

    public JsonFileRepository(JsonStorageOptions options)
    {
        _options = options;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            WriteIndented = true,
            // Enum serialize dạng tên (Pending/Completed) thay vì số — dễ đọc, ổn định khi đổi thứ tự.
            // DateOnly/DateTime? dùng converter built-in .NET 8, không cần khai báo thêm.
            Converters =
            {
                new JsonStringEnumConverter()
            }
        };
    }

    // ----------------------------------------------------------------
    // LOAD
    // ----------------------------------------------------------------

    /// <inheritdoc/>
    public IReadOnlyList<TodoItem> Load()
    {
        EnsureDataDirectoryExists();

        if (!File.Exists(_options.TodosFilePath))
        {
            // First-run: file chưa tồn tại (US-007 Sc.2)
            _items = new List<TodoItem>();
            return _items.AsReadOnly();
        }

        try
        {
            var json = File.ReadAllText(_options.TodosFilePath);
            var dto = JsonSerializer.Deserialize<StorageFileDto>(json, _jsonOptions);
            _items = dto?.Items ?? new List<TodoItem>();
            return _items.AsReadOnly();
        }
        catch (JsonException ex)
        {
            // File corrupt (US-007 Sc.3) — backup rồi reset
            BackupCorruptFile();
            CorruptionDetected = true;
            _items = new List<TodoItem>();
            // Log nhẹ để trace (không phải exception thô lên UI)
            System.Diagnostics.Debug.WriteLine(
                $"[JsonFileRepository] Corrupt file backed up. Detail: {ex.Message}");
            return _items.AsReadOnly();
        }
        catch (UnauthorizedAccessException ex)
        {
            // Permission denied khi đọc (US-007 Sc.4)
            PermissionErrorOnLoad = true;
            _items = new List<TodoItem>();
            System.Diagnostics.Debug.WriteLine(
                $"[JsonFileRepository] Permission denied reading storage. Detail: {ex.Message}");
            return _items.AsReadOnly();
        }
        catch (IOException ex)
        {
            // Lỗi I/O khác khi đọc
            PermissionErrorOnLoad = true;
            _items = new List<TodoItem>();
            System.Diagnostics.Debug.WriteLine(
                $"[JsonFileRepository] I/O error reading storage. Detail: {ex.Message}");
            return _items.AsReadOnly();
        }
    }

    // ----------------------------------------------------------------
    // QUERY (in-memory, không đọc lại đĩa)
    // ----------------------------------------------------------------

    /// <inheritdoc/>
    public IReadOnlyList<TodoItem> GetAll() => _items.AsReadOnly();

    /// <inheritdoc/>
    public TodoItem? GetById(Guid id) =>
        _items.FirstOrDefault(i => i.Id == id);

    // ----------------------------------------------------------------
    // MUTATE + PERSIST
    // ----------------------------------------------------------------

    /// <inheritdoc/>
    public void Add(TodoItem item)
    {
        _items.Add(item);
        try
        {
            Save();
        }
        catch
        {
            // Rollback in-memory nếu ghi đĩa thất bại (US-001 EC1)
            _items.Remove(item);
            throw;
        }
    }

    /// <inheritdoc/>
    public bool Update(TodoItem item)
    {
        var index = _items.FindIndex(i => i.Id == item.Id);
        if (index < 0) return false;

        var original = _items[index];
        _items[index] = item;
        try
        {
            Save();
            return true;
        }
        catch
        {
            // Rollback in-memory
            _items[index] = original;
            throw;
        }
    }

    /// <inheritdoc/>
    public bool Delete(Guid id)
    {
        var item = _items.FirstOrDefault(i => i.Id == id);
        if (item is null) return false;

        _items.Remove(item);
        try
        {
            Save();
            return true;
        }
        catch
        {
            // Rollback in-memory
            _items.Add(item);
            throw;
        }
    }

    // ----------------------------------------------------------------
    // INTERNAL: Save (atomic write-then-rename, US-006 BR2)
    // ----------------------------------------------------------------

    private void Save()
    {
        var dto = new StorageFileDto
        {
            SchemaVersion = 1,
            Items = new List<TodoItem>(_items)
        };

        string json;
        try
        {
            json = JsonSerializer.Serialize(dto, _jsonOptions);
        }
        catch (Exception ex)
        {
            throw new StorageException("Không thể serialize dữ liệu JSON.", ex);
        }

        try
        {
            EnsureDataDirectoryExists();

            // Bước 1: ghi file tạm
            File.WriteAllText(_options.TempFilePath, json, System.Text.Encoding.UTF8);

            // Bước 2: atomic rename
            if (File.Exists(_options.TodosFilePath))
            {
                // File.Replace: gần atomic trên NTFS (US-006 BR2)
                File.Replace(_options.TempFilePath, _options.TodosFilePath, null);
            }
            else
            {
                File.Move(_options.TempFilePath, _options.TodosFilePath);
            }
        }
        catch (UnauthorizedAccessException ex)
        {
            CleanupTempFile();
            throw new StorageException(
                "Không có quyền ghi file dữ liệu. Kiểm tra quyền truy cập thư mục.", ex);
        }
        catch (IOException ex)
        {
            CleanupTempFile();
            throw new StorageException(
                "Lỗi I/O khi ghi file dữ liệu. Có thể đĩa đầy hoặc file đang bị khóa.", ex);
        }
    }

    // ----------------------------------------------------------------
    // HELPERS
    // ----------------------------------------------------------------

    private void EnsureDataDirectoryExists()
    {
        if (!Directory.Exists(_options.DataDirectory))
        {
            Directory.CreateDirectory(_options.DataDirectory);
        }
    }

    private void BackupCorruptFile()
    {
        try
        {
            if (File.Exists(_options.TodosFilePath))
            {
                // Xóa backup cũ nếu có rồi copy
                if (File.Exists(_options.BackupFilePath))
                    File.Delete(_options.BackupFilePath);
                File.Copy(_options.TodosFilePath, _options.BackupFilePath);
                File.Delete(_options.TodosFilePath);
            }
        }
        catch (Exception ex)
        {
            // Không để backup failure làm crash app (BR-GLOBAL-04)
            System.Diagnostics.Debug.WriteLine(
                $"[JsonFileRepository] Failed to backup corrupt file: {ex.Message}");
        }
    }

    private void CleanupTempFile()
    {
        try
        {
            if (File.Exists(_options.TempFilePath))
                File.Delete(_options.TempFilePath);
        }
        catch
        {
            // Bỏ qua — tmp sẽ bị ghi đè lần sau
        }
    }
}
