namespace MyGit.Core;

/// <summary>Đại diện cho 1 thư mục .mygit — tương đương .git thật.</summary>
public class Repository
{
    public string WorkDir { get; }
    public string GitDir { get; }
    public string ObjectsDir => Path.Combine(GitDir, "objects");
    public string RefsHeadsDir => Path.Combine(GitDir, "refs", "heads");
    public string HeadFile => Path.Combine(GitDir, "HEAD");

    private Repository(string workDir)
    {
        WorkDir = workDir;
        GitDir = Path.Combine(workDir, ".mygit");
    }

    public static Repository Init(string workDir)
    {
        var repo = new Repository(workDir);
        Directory.CreateDirectory(repo.ObjectsDir);
        Directory.CreateDirectory(repo.RefsHeadsDir);
        File.WriteAllText(repo.HeadFile, "ref: refs/heads/main\n");
        return repo;
    }

    public static Repository Discover(string startDir)
    {
        var dir = startDir;
        while (dir != null)
        {
            if (Directory.Exists(Path.Combine(dir, ".mygit")))
                return new Repository(dir);
            dir = Path.GetDirectoryName(dir);
        }
        throw new InvalidOperationException("Not a mygit repository (or any parent). Run 'mygit init' first.");
    }

    /// <summary>Đọc ref hiện tại (HEAD) ra hash commit, hoặc null nếu chưa có commit nào.</summary>
    public string? ReadHeadCommit()
    {
        var headContent = File.ReadAllText(HeadFile).Trim();
        if (headContent.StartsWith("ref: "))
        {
            var refPath = Path.Combine(GitDir, headContent.Substring(5));
            if (!File.Exists(refPath)) return null;
            return File.ReadAllText(refPath).Trim();
        }
        return headContent; // detached HEAD — hash trực tiếp
    }

    /// <summary>Cập nhật branch hiện tại (HEAD) trỏ tới commit hash mới.</summary>
    public void UpdateHead(string commitHash)
    {
        var headContent = File.ReadAllText(HeadFile).Trim();
        if (headContent.StartsWith("ref: "))
        {
            var refPath = Path.Combine(GitDir, headContent.Substring(5));
            Directory.CreateDirectory(Path.GetDirectoryName(refPath)!);
            File.WriteAllText(refPath, commitHash + "\n");
        }
        else
        {
            File.WriteAllText(HeadFile, commitHash + "\n");
        }
    }
}
