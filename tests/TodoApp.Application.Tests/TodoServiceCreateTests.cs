using FluentAssertions;
using Moq;
using TodoApp.Domain;

namespace TodoApp.Application.Tests;

public class TodoServiceCreateTests
{
    private readonly Mock<ITodoRepository> _repoMock = new();
    private readonly TodoService _sut;

    public TodoServiceCreateTests()
    {
        _repoMock.Setup(r => r.GetById(It.IsAny<Guid>())).Returns((TodoItem?)null);
        _sut = new TodoService(_repoMock.Object);
    }

    [Fact]
    public void Create_ValidTitle_ReturnsOkWithPendingItem()
    {
        var result = _sut.Create(new CreateTodoRequest("Mua sắm"));

        result.Success.Should().BeTrue();
        result.Value!.Title.Should().Be("Mua sắm");
        result.Value.Status.Should().Be(TodoStatus.Pending);
        result.Value.Id.Should().NotBe(Guid.Empty);
        result.Value.CreatedAt.Should().BeCloseTo(DateTime.Now, TimeSpan.FromSeconds(2));
        result.Value.CompletedAt.Should().BeNull();
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    public void Create_EmptyOrWhitespaceTitle_ReturnsValidationFail(string title)
    {
        var result = _sut.Create(new CreateTodoRequest(title));

        result.Success.Should().BeFalse();
        result.ErrorKind.Should().Be(OperationErrorKind.Validation);
        result.ErrorMessage.Should().Contain("MSG-001");
    }

    [Fact]
    public void Create_TitleExceeds200Chars_ReturnsValidationFail()
    {
        var result = _sut.Create(new CreateTodoRequest(new string('A', 201)));

        result.Success.Should().BeFalse();
        result.ErrorKind.Should().Be(OperationErrorKind.Validation);
        result.ErrorMessage.Should().Contain("MSG-002");
    }

    [Fact]
    public void Create_DescriptionExceeds1000Chars_ReturnsValidationFail()
    {
        var result = _sut.Create(new CreateTodoRequest("Task", new string('x', 1001)));

        result.Success.Should().BeFalse();
        result.ErrorKind.Should().Be(OperationErrorKind.Validation);
        result.ErrorMessage.Should().Contain("MSG-003");
    }

    [Fact]
    public void Create_TitleWithLeadingSpaces_TrimsTitle()
    {
        var result = _sut.Create(new CreateTodoRequest("  Mua sắm  "));

        result.Success.Should().BeTrue();
        result.Value!.Title.Should().Be("Mua sắm");
    }

    [Fact]
    public void Create_StorageFails_ReturnsStorageFail()
    {
        _repoMock.Setup(r => r.Add(It.IsAny<TodoItem>()))
                 .Throws(new StorageException("disk full"));

        var result = _sut.Create(new CreateTodoRequest("Task"));

        result.Success.Should().BeFalse();
        result.ErrorKind.Should().Be(OperationErrorKind.Storage);
        result.ErrorMessage.Should().Contain("MSG-012");
    }

    [Fact]
    public void Create_WithPriorityAndDueDate_SetsValues()
    {
        var due = new DateOnly(2026, 12, 31);
        var result = _sut.Create(new CreateTodoRequest("Task", null, Priority.High, due));

        result.Success.Should().BeTrue();
        result.Value!.Priority.Should().Be(Priority.High);
        result.Value.DueDate.Should().Be(due);
    }
}
