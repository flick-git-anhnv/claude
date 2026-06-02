using FluentAssertions;
using Moq;
using TodoApp.Domain;

namespace TodoApp.Application.Tests;

public class TodoServiceDeleteTests
{
    private readonly Mock<ITodoRepository> _repoMock = new();
    private readonly TodoService _sut;
    private readonly TodoItem _existing;

    public TodoServiceDeleteTests()
    {
        _existing = new TodoItem
        {
            Id = Guid.NewGuid(),
            Title = "Task to delete",
            CreatedAt = DateTime.Now
        };
        _repoMock.Setup(r => r.GetById(_existing.Id)).Returns(_existing);
        _repoMock.Setup(r => r.Delete(_existing.Id)).Returns(true);
        _sut = new TodoService(_repoMock.Object);
    }

    [Fact]
    public void Delete_ExistingId_ReturnsOk()
    {
        var result = _sut.Delete(_existing.Id);

        result.Success.Should().BeTrue();
        _repoMock.Verify(r => r.Delete(_existing.Id), Times.Once);
    }

    [Fact]
    public void Delete_NonExistentId_ReturnsNotFound()
    {
        _repoMock.Setup(r => r.GetById(It.IsAny<Guid>())).Returns((TodoItem?)null);

        var result = _sut.Delete(Guid.NewGuid());

        result.Success.Should().BeFalse();
        result.ErrorKind.Should().Be(OperationErrorKind.NotFound);
    }

    [Fact]
    public void Delete_StorageFails_ReturnsStorageFail()
    {
        _repoMock.Setup(r => r.Delete(_existing.Id))
                 .Throws(new StorageException("disk"));

        var result = _sut.Delete(_existing.Id);

        result.Success.Should().BeFalse();
        result.ErrorKind.Should().Be(OperationErrorKind.Storage);
    }
}
