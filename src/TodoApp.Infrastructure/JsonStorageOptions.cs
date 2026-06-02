namespace TodoApp.Infrastructure;

/// <summary>
/// Cấu hình đường dẫn file lưu trữ JSON.
/// Mặc định: %LOCALAPPDATA%\KZTEK\TodoApp\ (OQ4).
/// Override bằng biến môi trường TODOAPP_DATA_DIR (phục vụ test).
/// </summary>
public sealed class JsonStorageOptions
{
    private const string EnvVarName = "TODOAPP_DATA_DIR";
    private const string DefaultSubPath = @"KZTEK\TodoApp";

    /// <summary>Thư mục chứa file dữ liệu.</summary>
    public string DataDirectory { get; }

    /// <summary>Đường dẫn đầy đủ đến file dữ liệu chính.</summary>
    public string TodosFilePath => Path.Combine(DataDirectory, "todos.json");

    /// <summary>Đường dẫn file tạm dùng cho atomic write.</summary>
    public string TempFilePath => Path.Combine(DataDirectory, "todos.tmp");

    /// <summary>Đường dẫn file backup khi file chính bị corrupt.</summary>
    public string BackupFilePath => Path.Combine(DataDirectory, "todos.bak.json");

    public JsonStorageOptions()
    {
        var overrideDir = Environment.GetEnvironmentVariable(EnvVarName);
        if (!string.IsNullOrWhiteSpace(overrideDir))
        {
            DataDirectory = overrideDir;
        }
        else
        {
            var localAppData = Environment.GetFolderPath(
                Environment.SpecialFolder.LocalApplicationData);
            DataDirectory = Path.Combine(localAppData, DefaultSubPath);
        }
    }

    /// <summary>Constructor dành cho test — truyền thư mục trực tiếp.</summary>
    public JsonStorageOptions(string dataDirectory)
    {
        DataDirectory = dataDirectory;
    }
}
