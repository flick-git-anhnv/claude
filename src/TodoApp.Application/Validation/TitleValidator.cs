using TodoApp.Domain;

namespace TodoApp.Application.Validation;

public static class TitleValidator
{
    public static (bool IsValid, string? ErrorMessage) Validate(string? title)
    {
        var trimmed = title?.Trim() ?? string.Empty;

        if (trimmed.Length == 0)
            return (false, "MSG-001: Tiêu đề không được để trống.");

        if (trimmed.Length > TodoConstants.MaxTitleLength)
            return (false, $"MSG-002: Tiêu đề không được vượt quá {TodoConstants.MaxTitleLength} ký tự.");

        return (true, null);
    }

    public static (bool IsValid, string? ErrorMessage) ValidateDescription(string? description)
    {
        if (description is not null && description.Length > TodoConstants.MaxDescriptionLength)
            return (false, $"MSG-003: Mô tả không được vượt quá {TodoConstants.MaxDescriptionLength} ký tự.");

        return (true, null);
    }
}
