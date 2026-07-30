using System.Security.Cryptography;
using System.Text;

namespace MyGit.Core;

public record GitObject(string Type, byte[] Content);

/// <summary>
/// Đọc/ghi object theo đúng format Git thật: "<type> <size>\0<content>", nén zlib,
/// lưu tại .mygit/objects/&lt;2 ký tự đầu hash&gt;/&lt;38 ký tự còn lại&gt;.
/// Hash = SHA1 của phần chưa nén (header + content).
/// </summary>
public static class ObjectDatabase
{
    public static string Hash(string type, byte[] content)
    {
        var header = Encoding.UTF8.GetBytes($"{type} {content.Length}\0");
        var full = new byte[header.Length + content.Length];
        Buffer.BlockCopy(header, 0, full, 0, header.Length);
        Buffer.BlockCopy(content, 0, full, header.Length, content.Length);
        var sha1 = SHA1.HashData(full);
        return Convert.ToHexString(sha1).ToLowerInvariant();
    }

    public static string Write(Repository repo, string type, byte[] content)
    {
        var header = Encoding.UTF8.GetBytes($"{type} {content.Length}\0");
        var full = new byte[header.Length + content.Length];
        Buffer.BlockCopy(header, 0, full, 0, header.Length);
        Buffer.BlockCopy(content, 0, full, header.Length, content.Length);

        var hash = Convert.ToHexString(SHA1.HashData(full)).ToLowerInvariant();
        var dir = Path.Combine(repo.ObjectsDir, hash[..2]);
        var file = Path.Combine(dir, hash[2..]);

        if (!File.Exists(file))
        {
            Directory.CreateDirectory(dir);
            File.WriteAllBytes(file, ZlibHelper.Compress(full));
        }
        return hash;
    }

    public static GitObject Read(Repository repo, string hash)
    {
        hash = ResolveShortHash(repo, hash);
        var file = Path.Combine(repo.ObjectsDir, hash[..2], hash[2..]);
        if (!File.Exists(file))
            throw new FileNotFoundException($"Object {hash} not found");

        var full = ZlibHelper.Decompress(File.ReadAllBytes(file));
        var nullIndex = Array.IndexOf(full, (byte)0);
        var header = Encoding.UTF8.GetString(full, 0, nullIndex);
        var spaceIndex = header.IndexOf(' ');
        var type = header[..spaceIndex];
        var content = full[(nullIndex + 1)..];
        return new GitObject(type, content);
    }

    /// <summary>Cho phép gõ tắt hash (giống git) — tìm object khớp tiền tố duy nhất.</summary>
    public static string ResolveShortHash(Repository repo, string hashPrefix)
    {
        if (hashPrefix.Length == 40) return hashPrefix;
        if (hashPrefix.Length < 4)
            throw new ArgumentException("Hash prefix phải có ít nhất 4 ký tự");

        var dir = Path.Combine(repo.ObjectsDir, hashPrefix[..2]);
        if (!Directory.Exists(dir))
            throw new FileNotFoundException($"Không tìm thấy object khớp '{hashPrefix}'");

        var rest = hashPrefix[2..];
        var matches = Directory.GetFiles(dir)
            .Select(Path.GetFileName)
            .Where(f => f!.StartsWith(rest))
            .ToList();

        if (matches.Count == 0)
            throw new FileNotFoundException($"Không tìm thấy object khớp '{hashPrefix}'");
        if (matches.Count > 1)
            throw new InvalidOperationException($"'{hashPrefix}' không rõ ràng — khớp {matches.Count} object");

        return hashPrefix[..2] + matches[0];
    }
}
