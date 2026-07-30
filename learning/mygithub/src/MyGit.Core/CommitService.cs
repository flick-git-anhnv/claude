using System.Text;

namespace MyGit.Core;

public record CommitInfo(string TreeHash, string? ParentHash, string AuthorLine, string Message);

public static class CommitService
{
    public static string CommitTree(Repository repo, string treeHash, string? parentHash, string message, string author)
    {
        var timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        var sb = new StringBuilder();
        sb.Append($"tree {treeHash}\n");
        if (parentHash != null)
            sb.Append($"parent {parentHash}\n");
        sb.Append($"author {author} {timestamp} +0000\n");
        sb.Append($"committer {author} {timestamp} +0000\n");
        sb.Append('\n');
        sb.Append(message);
        sb.Append('\n');

        var content = Encoding.UTF8.GetBytes(sb.ToString());
        return ObjectDatabase.Write(repo, "commit", content);
    }

    /// <summary>Lệnh "commit" cấp cao: snapshot toàn bộ working dir thành 1 commit mới, cập nhật HEAD.</summary>
    public static string Commit(Repository repo, string message, string author = "MyGit User <you@example.com>")
    {
        var treeHash = TreeBuilder.WriteTree(repo, repo.WorkDir);
        var parentHash = repo.ReadHeadCommit();
        var commitHash = CommitTree(repo, treeHash, parentHash, message, author);
        repo.UpdateHead(commitHash);
        return commitHash;
    }

    public static CommitInfo ParseCommit(byte[] content)
    {
        var text = Encoding.UTF8.GetString(content);
        var lines = text.Split('\n');
        string tree = "", parent = "";
        string author = "";
        int i = 0;
        for (; i < lines.Length; i++)
        {
            var line = lines[i];
            if (line.Length == 0) { i++; break; } // dòng trống ngăn cách header/message
            if (line.StartsWith("tree ")) tree = line[5..];
            else if (line.StartsWith("parent ")) parent = line[7..];
            else if (line.StartsWith("author ")) author = line[7..];
        }
        var message = string.Join('\n', lines[i..]).TrimEnd('\n');
        return new CommitInfo(tree, string.IsNullOrEmpty(parent) ? null : parent, author, message);
    }
}
