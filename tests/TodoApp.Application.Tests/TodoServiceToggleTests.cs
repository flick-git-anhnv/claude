using FluentAssertions;
using Moq;
using TodoApp.Domain;

namespace TodoApp.Application.Tests;

public class TodoServiceToggleTests
{
    private readonly Mock<ITodoRepository> _repoMock = new();
    private readonly TodoService _sut;
    private readonly TodoItem _item;

    public TodoServiceToggleTests()
    {
        _item = new TodoItem
        {
            Id = Guid.NewGuid(),
            Title = "Task",
            Status = TodoStatus.Pending,
            CreatedAt = DateTime.Now
        };
        _repoMock.Setup(r => r.GetById(_item.Id)).Returns(_item);
        _repoMock.Setup(r => r.Update(It.IsAny<TodoItem>())).Returns(true);
        _sut = new TodoService(_repoMock.Object);
    }

    [Fact]
    public void Toggle_PendingToCompleted_SetsCompletedAt()
    {
        var result = _sut.ToggleComplete(_item.Id);

        result.Success.Should().BeTrue();
        result.Value!.Status.Should().Be(TodoStatus.Completed);
        result.Value.CompletedAt.Should().NotBeNull();
        result.Value.CompletedAt.Should().BeCloseTo(DateTime.Now, TimeSpan.FromSeconds(2));
    }

    [Fact]
    public void Toggle_CompletedToPending_ClearsCompletedAt()
    {
        _item.Status = TodoStatus.Completed;
        _item.CompletedAt = DateTime.Now.AddMinutes(-5);

        var result = _sut.ToggleComplete(_item.Id);

        result.Success.Should().BeTrue();
        result.Value!.Status.Should().Be(TodoStatus.Pending);
        result.Value.CompletedAt.Should().BeNull();
    }

    [Fact]
    public void Toggle_ThreeTimes_EndsAsCompleted()
    {
        _sut.ToggleComplete(_item.Id); // Pending -> Completed
        _sut.ToggleComplete(_item.Id); // Completed -> Pending
        var result = _sut.ToggleComplete(_item.Id); // Pending -> Completed

        result.Value!.Status.Should().Be(TodoStatus.Completed);
    }

    [Fact]
    public void Toggle_NonExistentId_ReturnsNotFound()
    {
        _repoMock.Setup(r => r.GetById(It.IsAny<Guid>())).Returns((TodoItem?)null);

        var result = _sut.ToggleComplete(Guid.NewGuid());

        result.Success.Should().BeFalse();
        result.ErrorKind.Should().Be(OperationErrorKind.NotFound);
    }

    [Fact]
    public void Toggle_StorageFails_RollsBackStatus()
    {
        _repoMock.Setup(r => r.Update(It.IsAny<TodoItem>()))
                 .Throws(new StorageException("disk"));

        var result = _sut.ToggleComplete(_item.Id);

        result.Success.Should().BeFalse();
        result.ErrorKind.Should().Be(OperationErrorKind.Storage);
        _item.Status.Should().Be(TodoStatus.Pending);
        _item.CompletedAt.Should().BeNull();
    }
}
