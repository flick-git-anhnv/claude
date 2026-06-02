using FluentAssertions;
using System.Text.Json;
using TodoApp.Domain;
using TodoApp.Infrastructure;

namespace TodoApp.Infrastructure.Tests;

public sealed class JsonFileRepositoryTests : IDisposable
{
    private readonly string _tempDir;
    private readonly JsonStorageOptions _options;

    public JsonFileRepositoryTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), $"todoapp-test-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_tempDir);

        Environment.SetEnvironmentVariable("TODOAPP_DATA_DIR", _tempDir);
        _options = new JsonStorageOptions();
    }

    public void Dispose()
    {
        Environment.SetEnvironmentVariable("TODOAPP_DATA_DIR", null);
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private JsonFileRepository CreateRepo() => new(_options);

    private static TodoItem MakeItem(string title = "Test task") => new()
    {
        Id = Guid.NewGuid(),
        Title = title,
        Status = TodoStatus.Pending,
        CreatedAt = DateTime.Now
    };

    [Fact]
    public void Load_FileNotExists_ReturnsEmptyList()
    {
        var repo = CreateRepo();
        var items = repo.Load();
        items.Should().BeEmpty();
    }

    [Fact]
    public void Load_ValidFile_ReturnsCorrectItems()
    {
        var repo = CreateRepo();
        var item = MakeItem("Hello");
        repo.Load();
        repo.Add(item);

        var repo2 = CreateRepo();
        var loaded = repo2.Load();

        loaded.Should().HaveCount(1);
        loaded[0].Title.Should().Be("Hello");
    }

    [Fact]
    public void Load_CorruptFile_ReturnsEmptyAndBacksUp()
    {
        File.WriteAllText(_options.TodosFilePath, "{ invalid json }}}}");

        var repo = CreateRepo();
        var items = repo.Load();

        items.Should().BeEmpty();
        repo.CorruptionDetected.Should().BeTrue();
        File.Exists(_options.BackupFilePath).Should().BeTrue();
        File.Exists(_options.TodosFilePath).Should().BeFalse();
    }

    [Fact]
    public void Add_PersistsItem_FileExistsAfterAdd()
    {
        var repo = CreateRepo();
        repo.Load();
        repo.Add(MakeItem());

        File.Exists(_options.TodosFilePath).Should().BeTrue();
    }

    [Fact]
    public void Add_AtomicWrite_NoTempFileLeftBehind()
    {
        var repo = CreateRepo();
        repo.Load();
        repo.Add(MakeItem());

        File.Exists(_options.TempFilePath).Should().BeFalse();
    }

    [Fact]
    public void Update_ExistingItem_UpdatesPersisted()
    {
        var repo = CreateRepo();
        repo.Load();
        var item = MakeItem("Original");
        repo.Add(item);

        item.Title = "Updated";
        repo.Update(item);

        var repo2 = CreateRepo();
        var loaded = repo2.Load();
        loaded[0].Title.Should().Be("Updated");
    }

    [Fact]
    public void Delete_ExistingItem_RemovedFromFile()
    {
        var repo = CreateRepo();
        repo.Load();
        var item = MakeItem();
        repo.Add(item);
        repo.Delete(item.Id);

        var repo2 = CreateRepo();
        repo2.Load().Should().BeEmpty();
    }

    [Fact]
    public void Load_MissingPriorityField_DefaultsToNone()
    {
        // Simulate data written before Priority field existed
        var json = """
            {
              "schemaVersion": 1,
              "items": [
                {
                  "id": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                  "title": "Old task",
                  "status": 0,
                  "createdAt": "2026-01-01T10:00:00"
                }
              ]
            }
            """;
        Directory.CreateDirectory(_tempDir);
        File.WriteAllText(_options.TodosFilePath, json);

        var repo = CreateRepo();
        var items = repo.Load();

        items.Should().HaveCount(1);
        items[0].Priority.Should().Be(Priority.None);
        items[0].DueDate.Should().BeNull();
    }

    [Fact]
    public void GetAll_BeforeLoad_ReturnsEmpty()
    {
        var repo = CreateRepo();
        repo.GetAll().Should().BeEmpty();
    }

    [Fact]
    public void GetById_ExistingId_ReturnsItem()
    {
        var repo = CreateRepo();
        repo.Load();
        var item = MakeItem();
        repo.Add(item);

        repo.GetById(item.Id).Should().NotBeNull();
    }

    [Fact]
    public void GetById_NonExistentId_ReturnsNull()
    {
        var repo = CreateRepo();
        repo.Load();
        repo.GetById(Guid.NewGuid()).Should().BeNull();
    }
}
