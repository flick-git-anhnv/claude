using FluentAssertions;
using Moq;
using TodoApp.Domain;

namespace TodoApp.Application.Tests;

public class TodoServiceFilterTests
{
    private readonly Mock<ITodoRepository> _repoMock = new();
    private readonly TodoService _sut;

    private static TodoItem MakeItem(TodoStatus status, DateTime createdAt) => new()
    {
        Id = Guid.NewGuid(),
        Title = "Task",
        Status = status,
        CreatedAt = createdAt
    };

    public TodoServiceFilterTests()
    {
        var items = new List<TodoItem>
        {
            MakeItem(TodoStatus.Pending,   DateTime.Now.AddHours(-1)),
            MakeItem(TodoStatus.Pending,   DateTime.Now.AddHours(-2)),
            MakeItem(TodoStatus.Completed, DateTime.Now.AddHours(-3)),
        };
        _repoMock.Setup(r => r.GetAll()).Returns(items.AsReadOnly());
        _sut = new TodoService(_repoMock.Object);
    }

    [Fact]
    public void GetTasks_FilterAll_ReturnsAllThree()
    {
        var result = _sut.GetTasks(TaskFilter.All);
        result.Count.Should().Be(3);
    }

    [Fact]
    public void GetTasks_FilterPending_ReturnsTwoPending()
    {
        var result = _sut.GetTasks(TaskFilter.Pending);
        result.Should().HaveCount(2);
        result.Should().OnlyContain(i => i.Status == TodoStatus.Pending);
    }

    [Fact]
    public void GetTasks_FilterCompleted_ReturnsOneCompleted()
    {
        var result = _sut.GetTasks(TaskFilter.Completed);
        result.Should().HaveCount(1);
        result.Should().OnlyContain(i => i.Status == TodoStatus.Completed);
    }

    [Fact]
    public void GetTasks_SortedCreatedAtDesc()
    {
        var result = _sut.GetTasks(TaskFilter.All);

        result[0].CreatedAt.Should().BeAfter(result[1].CreatedAt);
        result[1].CreatedAt.Should().BeAfter(result[2].CreatedAt);
    }

    [Fact]
    public void GetByDisplayIndex_ValidIndex_ReturnsCorrectItem()
    {
        var allSorted = _sut.GetTasks(TaskFilter.All);
        var first = _sut.GetByDisplayIndex(1, TaskFilter.All);

        first.Should().NotBeNull();
        first!.Id.Should().Be(allSorted[0].Id);
    }

    [Fact]
    public void GetByDisplayIndex_OutOfRange_ReturnsNull()
    {
        _sut.GetByDisplayIndex(0, TaskFilter.All).Should().BeNull();
        _sut.GetByDisplayIndex(99, TaskFilter.All).Should().BeNull();
    }

    [Fact]
    public void GetCounts_ReturnsCorrectNumbers()
    {
        var counts = _sut.GetCounts();

        counts.Total.Should().Be(3);
        counts.Pending.Should().Be(2);
        counts.Completed.Should().Be(1);
    }
}
