using MyGit.Core;

if (args.Length == 0)
{
    PrintUsage();
    return 1;
}

try
{
    switch (args[0])
    {
        case "init":
            {
                var repo = Repository.Init(Directory.GetCurrentDirectory());
                Console.WriteLine($"Initialized empty MyGit repository in {repo.GitDir}");
                break;
            }

        case "hash-object":
            {
                // mygit hash-object -w <file>
                var write = args.Contains("-w");
                var filePath = args.Last();
                var repo = Repository.Discover(Directory.GetCurrentDirectory());
                var content = File.ReadAllBytes(filePath);
                var hash = write
                    ? ObjectDatabase.Write(repo, "blob", content)
                    : ObjectDatabase.Hash("blob", content);
                Console.WriteLine(hash);
                break;
            }

        case "cat-file":
            {
                // mygit cat-file -p <hash>
                var repo = Repository.Discover(Directory.GetCurrentDirectory());
                var hash = args.Last();
                var obj = ObjectDatabase.Read(repo, hash);

                if (obj.Type == "tree")
                {
                    foreach (var entry in TreeBuilder.ParseTree(obj.Content))
                        Console.WriteLine($"{entry.Mode} {(entry.IsTree ? "tree" : "blob")} {entry.HashHex}\t{entry.Name}");
                }
                else
                {
                    Console.Out.Write(System.Text.Encoding.UTF8.GetString(obj.Content));
                }
                break;
            }

        case "write-tree":
            {
                var repo = Repository.Discover(Directory.GetCurrentDirectory());
                var hash = TreeBuilder.WriteTree(repo, repo.WorkDir);
                Console.WriteLine(hash);
                break;
            }

        case "commit-tree":
            {
                // mygit commit-tree <tree-hash> [-p <parent>] -m <message>
                var repo = Repository.Discover(Directory.GetCurrentDirectory());
                var treeHash = args[1];
                string? parent = null;
                string message = "";
                for (int i = 2; i < args.Length; i++)
                {
                    if (args[i] == "-p") parent = args[++i];
                    else if (args[i] == "-m") message = args[++i];
                }
                var hash = CommitService.CommitTree(repo, treeHash, parent, message, "MyGit User <you@example.com>");
                Console.WriteLine(hash);
                break;
            }

        case "commit":
            {
                // mygit commit -m "message"
                var repo = Repository.Discover(Directory.GetCurrentDirectory());
                var mIdx = Array.IndexOf(args, "-m");
                var message = mIdx >= 0 && mIdx + 1 < args.Length ? args[mIdx + 1] : "";
                var hash = CommitService.Commit(repo, message);
                Console.WriteLine(hash);
                break;
            }

        case "log":
            {
                var repo = Repository.Discover(Directory.GetCurrentDirectory());
                var current = repo.ReadHeadCommit();
                if (current == null)
                {
                    Console.WriteLine("(chưa có commit nào)");
                    break;
                }
                while (current != null)
                {
                    var obj = ObjectDatabase.Read(repo, current);
                    var commit = CommitService.ParseCommit(obj.Content);
                    Console.WriteLine($"commit {current}");
                    Console.WriteLine($"Author: {commit.AuthorLine}");
                    Console.WriteLine();
                    Console.WriteLine($"    {commit.Message}");
                    Console.WriteLine();
                    current = commit.ParentHash;
                }
                break;
            }

        default:
            PrintUsage();
            return 1;
    }
    return 0;
}
catch (Exception ex)
{
    Console.Error.WriteLine($"mygit: {ex.Message}");
    return 1;
}

static void PrintUsage()
{
    Console.WriteLine("""
        MyGit — tự viết lại Git core để học cơ chế bên trong.
        Usage:
          mygit init
          mygit hash-object -w <file>
          mygit cat-file -p <hash>
          mygit write-tree
          mygit commit-tree <tree-hash> [-p <parent>] -m <message>
          mygit commit -m <message>
          mygit log
        """);
}
