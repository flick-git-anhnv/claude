namespace TodoApp.Domain;

/// <summary>Hằng số nghiệp vụ dùng chung giữa Domain và Application (BR-GLOBAL-01/02).</summary>
public static class TodoConstants
{
    /// <summary>Độ dài tối đa của tiêu đề task (BR-GLOBAL-01).</summary>
    public const int MaxTitleLength = 200;

    /// <summary>Độ dài tối đa của mô tả task (BR-GLOBAL-02).</summary>
    public const int MaxDescriptionLength = 1000;
}
