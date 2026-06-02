using FluentAssertions;
using Moq;
using TodoApp.Domain;

namespace TodoApp.Application.Tests;

public class TodoServiceUpdateTests
{
    private readonly Mock<ITodoRepository> _repoMock = new();
    private readonly TodoService _sut;
    private readonly TodoItem _existing;

    public TodoServiceUpdateTests()
    {
        _existing = new TodoItem
        {
            Id = Guid.NewGuid(),
            Title = "Original",
            Description = "Desc",
            Status = TodoStatus.Pending,
            Priority = Priority.None,
            CreatedAt = DateTime.Now.AddDays(-1)
        };
        _repoMock.Setup(r => r.GetById(_existing.Id)).Returns(_existing);
        _repoMock.Setup(r => r.Update(It.IsAny<TodoItem>())).Returns(true);
        _sut = new TodoService(_repoMock.Object);
    }

    [Fact]
    public void Update_ValidTitle_ReturnsOkAndSetsUpdatedAt()
    {
        var result = _sut.Update(_existing.Id,
            new UpdateTodoRequest("New Title", null, Priority.Medium, null));

        result.Success.Should().BeTrue();
        result.Value!.Title.Should().Be("New Title");
        result.Value.UpdatedAt.Should().NotBeNull();
        result.Value.UpdatedAt.Should().BeCloseTo(DateTime.Now, TimeSpan.FromSeconds(2));
    }

    [Fact]
    public void Update_DoesNotChangeCreatedAt()
    {
        var originalCreated = _existing.CreatedAt;

        _sut.Update(_existing.Id, new UpdateTodoRequest("New", null, Priority.None, null));

        _existing.CreatedAt.Should().Be(originalCreated);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    public void Update_EmptyTitle_ReturnsValidationFail(string title)
    {
        var result = _sut.Update(_existing.Id,
            new UpdateTodoRequest(title, null, Priority.None, null));

        result.Success.Should().BeFalse();
        result.ErrorKind.Should().Be(OperationErrorKind.Validation);
    }

    [Fact]
    public void Update_NonExistentId_ReturnsNotFound()
    {
        _repoMock.Setup(r => r.GetById(It.IsAny<Guid>())).Returns((TodoItem?)null);

        var result = _sut.Update(Guid.NewGuid(),
            new UpdateTodoRequest("X", null, Priority.None, null));

        result.Success.Should().BeFalse();
        result.ErrorKind.Should().Be(OperationErrorKind.NotFound);
    }

    [Fact]
    public void Update_StorageFails_RollsBackAndReturnsStorageFail()
    {
        _repoMock.Setup(r => r.Update(It.IsAny<TodoItem>()))
                 .Throws(new StorageException("disk"));

        var result = _sut.Update(_existing.Id,
            new UpdateTodoRequest("New Title", null, Priority.None, null));

        result.Success.Should().BeFalse();
        result.ErrorKind.Should().Be(OperationErrorKind.Storage);
        _existing.Title.Should().Be("Original");
    }
}
