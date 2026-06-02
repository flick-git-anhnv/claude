using FluentAssertions;
using TodoApp.Application.Validation;

namespace TodoApp.Application.Tests;

public class TitleValidatorTests
{
    [Fact]
    public void Validate_EmptyString_ReturnsInvalid()
    {
        var (valid, error) = TitleValidator.Validate("");
        valid.Should().BeFalse();
        error.Should().Contain("MSG-001");
    }

    [Fact]
    public void Validate_WhitespaceOnly_ReturnsInvalid()
    {
        var (valid, error) = TitleValidator.Validate("   ");
        valid.Should().BeFalse();
        error.Should().Contain("MSG-001");
    }

    [Fact]
    public void Validate_Null_ReturnsInvalid()
    {
        var (valid, _) = TitleValidator.Validate(null);
        valid.Should().BeFalse();
    }

    [Fact]
    public void Validate_OneChar_ReturnsValid()
    {
        var (valid, error) = TitleValidator.Validate("A");
        valid.Should().BeTrue();
        error.Should().BeNull();
    }

    [Fact]
    public void Validate_Exactly200Chars_ReturnsValid()
    {
        var (valid, _) = TitleValidator.Validate(new string('x', 200));
        valid.Should().BeTrue();
    }

    [Fact]
    public void Validate_201Chars_ReturnsInvalid()
    {
        var (valid, error) = TitleValidator.Validate(new string('x', 201));
        valid.Should().BeFalse();
        error.Should().Contain("MSG-002");
    }

    [Fact]
    public void ValidateDescription_Null_ReturnsValid()
    {
        var (valid, _) = TitleValidator.ValidateDescription(null);
        valid.Should().BeTrue();
    }

    [Fact]
    public void ValidateDescription_Exactly1000Chars_ReturnsValid()
    {
        var (valid, _) = TitleValidator.ValidateDescription(new string('x', 1000));
        valid.Should().BeTrue();
    }

    [Fact]
    public void ValidateDescription_1001Chars_ReturnsInvalid()
    {
        var (valid, error) = TitleValidator.ValidateDescription(new string('x', 1001));
        valid.Should().BeFalse();
        error.Should().Contain("MSG-003");
    }
}
