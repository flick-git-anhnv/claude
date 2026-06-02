using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using TodoApp.Application;
using TodoApp.Domain;
using TodoApp.Infrastructure;

namespace TodoApp.Integration.Tests;

public sealed class CrudPersistenceTests : IDisposable
{
    private readonly string _tempDir;

    public CrudPersistenceTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), $"todoapp-it-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_tempDir);
        Environment.SetEnvironmentVariable("TODOAPP_DATA_DIR", _tempDir);
    }

    public void Dispose()
    {
        Environment.SetEnvironmentVariable("TODOAPP_DATA_DIR", null);
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private static ITodoService BuildService()
    {
        var services = new ServiceCollection();
        services.AddSingleton<JsonStorageOptions>();
        services.AddSingleton<ITodoRepository, JsonFileRepository>();
        services.AddSingleton<ITodoService, TodoService>();
        return services.BuildServiceProvider().GetRequiredService<ITodoService>();
    }

    [Fact]
    public void CrudCycle_PersistsAndReloadsCorrectly()
    {
        // --- Session 1: create 3, toggle 1, update 1, delete 1 ---
        var svc1 = BuildService();
        svc1.Initialize();

        var r1 = svc1.Create(new CreateTodoRequest("Task A"));
        var r2 = svc1.Create(new CreateTodoRequest("Task B"));
        var r3 = svc1.Create(new CreateTodoRequest("Task C"));

        r1.Success.Should().BeTrue();
        r2.Success.Should().BeTrue();
        r3.Success.Should().BeTrue();

        // Toggle Task A -> Completed
        svc1.ToggleComplete(r1.Value!.Id).Success.Should().BeTrue();

        // Update Task B
        svc1.Update(r2.Value!.Id, new UpdateTodoRequest("Task B Updated", "desc", Priority.High, null))
            .Success.Should().BeTrue();

        // Delete Task C
        svc1.Delete(r3.Value!.Id).Success.Should().BeTrue();

        // --- Session 2: reload and verify ---
        var svc2 = BuildService();
        var initResult = svc2.Initialize();

        initResult.Success.Should().BeTrue();
        initResult.Value.Should().Be(2); // Task A + Task B remain

        var all = svc2.GetTasks(TaskFilter.All);
        all.Should().HaveCount(2);

        var taskA = all.FirstOrDefault(t => t.Id == r1.Value!.Id);
        taskA.Should().NotBeNull();
        taskA!.Status.Should().Be(TodoStatus.Completed);
        taskA.CompletedAt.Should().NotBeNull();

        var taskB = all.FirstOrDefault(t => t.Id == r2.Value!.Id);
        taskB.Should().NotBeNull();
        taskB!.Title.Should().Be("Task B Updated");
        taskB.Priority.Should().Be(Priority.High);

        var counts = svc2.GetCounts();
        counts.Total.Should().Be(2);
        counts.Completed.Should().Be(1);
        counts.Pending.Should().Be(1);
    }

    [Fact]
    public void FirstRun_EmptyApp_WorksWithNoFile()
    {
        var svc = BuildService();
        var result = svc.Initialize();

        result.Success.Should().BeTrue();
        result.Value.Should().Be(0);
        svc.GetTasks().Should().BeEmpty();
    }
}
