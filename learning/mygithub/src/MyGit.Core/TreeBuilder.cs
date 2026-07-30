using System.Text;

namespace MyGit.Core;

public record TreeEntry(string Mode, string Name, string HashHex, bool IsTree);

/// <summary>
/// Xây dựng tree object từ 1 thư mục trên đĩa — đệ quy giống git write-tree.
/// Format 1 entry trong tree: "<mode> <name>\0<20-byte-raw-sha1>" (không phải hex!).
/// </summary>
public static class TreeBuilder
{
    private const string FileMode = "100644";
    private const string DirMode = "40000";

    public static string WriteTree(Repository repo, string dirPath)
    {
        var entries = new List<(string mode, string name, byte[] rawHash)>();

        foreach (var path in Directory.EnumerateFileSystemEntries(dirPath).OrderBy(p => Path.GetFileName(p), StringComparer.Ordinal))
        {
            var name = Path.GetFileName(path)!;
            if (name == ".mygit" || name == ".git") continue;

            if (Directory.Exists(path))
            {
                if (!Directory.EnumerateFileSystemEntries(path).Any()) continue; // bỏ qua thư mục rỗng, giống git
                var subTreeHash = WriteTree(repo, path);
                entries.Add((DirMode, name, Convert.FromHexString(subTreeHash)));
            }
            else
            {
                var content = File.ReadAllBytes(path);
                var blobHash = ObjectDatabase.Write(repo, "blob", content);
                entries.Add((FileMode, name, Convert.FromHexString(blobHash)));
            }
        }

        using var buffer = new MemoryStream();
        foreach (var (mode, name, rawHash) in entries)
        {
            var header = Encoding.UTF8.GetBytes($"{mode} {name}\0");
            buffer.Write(header, 0, header.Length);
            buffer.Write(rawHash, 0, rawHash.Length);
        }

        return ObjectDatabase.Write(repo, "tree", buffer.ToArray());
    }

    public static List<TreeEntry> ParseTree(byte[] treeContent)
    {
        var entries = new List<TreeEntry>();
        int i = 0;
        while (i < treeContent.Length)
        {
            int spaceIdx = Array.IndexOf(treeContent, (byte)' ', i);
            var mode = Encoding.UTF8.GetString(treeContent, i, spaceIdx - i);

            int nullIdx = Array.IndexOf(treeContent, (byte)0, spaceIdx + 1);
            var name = Encoding.UTF8.GetString(treeContent, spaceIdx + 1, nullIdx - spaceIdx - 1);

            var rawHash = treeContent[(nullIdx + 1)..(nullIdx + 21)];
            var hashHex = Convert.ToHexString(rawHash).ToLowerInvariant();

            entries.Add(new TreeEntry(mode, name, hashHex, mode == DirMode));
            i = nullIdx + 21;
        }
        return entries;
    }
}
