# MyGit — Tự viết lại Git (học tập cá nhân)

Dự án học tập theo tinh thần [`build-your-own-x`](https://github.com/codecrafters-io/build-your-own-x):
tự viết lại core của Git bằng C#/.NET để hiểu cơ chế object storage, tree, commit — sau đó bọc thêm
1 web UI đơn giản để mô phỏng GitHub.

> Đây KHÔNG phải sản phẩm KZTEK — chỉ là project học tập cá nhân, đặt trong `learning/` để tách biệt
> khỏi source chính thức của công ty.

## Yêu cầu

- .NET 8 SDK trở lên (`dotnet --version` để kiểm tra). Sandbox hiện tại không có sẵn .NET nên bạn
  cần chạy các lệnh dưới đây trên máy local.

## Build

```bash
cd learning/mygithub
dotnet build
```

## Chạy thử (Phase 1 — Git core)

```bash
mkdir /tmp/demo && cd /tmp/demo
dotnet run --project <đường-dẫn-tới>/MyGit.Cli -- init

echo "hello mygit" > file.txt
dotnet run --project <đường-dẫn-tới>/MyGit.Cli -- hash-object -w file.txt
# in ra 1 sha1 hash, vd: 3b18e512dba79e4c8300dd08aeb37f8e728b8dad

dotnet run --project <đường-dẫn-tới>/MyGit.Cli -- cat-file -p 3b18e512dba79e4c8300dd08aeb37f8e728b8dad
# in lại đúng nội dung "hello mygit"

dotnet run --project <đường-dẫn-tới>/MyGit.Cli -- commit -m "commit đầu tiên"
# in ra hash commit

dotnet run --project <đường-dẫn-tới>/MyGit.Cli -- log
```

**Kiểm chứng thú vị:** hash bạn nhận được từ `hash-object` phải **giống hệt** hash mà `git hash-object`
thật tạo ra cho cùng nội dung file — vì format object (`blob <size>\0<content>`, SHA1, zlib) được cài
đúng chuẩn Git.

```bash
git hash-object file.txt   # so sánh với kết quả mygit ở trên
```

## Cấu trúc code

```
src/
├── MyGit.Core/
│   ├── ZlibHelper.cs        — nén/giải nén object (Git dùng zlib cho mọi object)
│   ├── ObjectDatabase.cs     — hash-object, cat-file: đọc/ghi blob/tree/commit vào .mygit/objects
│   ├── Repository.cs         — init, HEAD, refs/heads
│   ├── TreeBuilder.cs        — write-tree: snapshot thư mục thành tree object (đệ quy)
│   └── CommitService.cs      — commit-tree, commit, log: tạo & đọc commit object
└── MyGit.Cli/
    └── Program.cs             — CLI: init | hash-object | cat-file | write-tree | commit-tree | commit | log
```

## Đã học được gì ở Phase 1

- Object model của Git: mọi thứ (file, thư mục, commit) đều là 1 object bất biến, định danh bằng
  SHA1 của chính nội dung nó (content-addressable storage).
- Vì sao đổi 1 dòng trong file → tạo ra 1 blob **hoàn toàn mới** thay vì "sửa" blob cũ (immutability).
- Tree là cấu trúc thư mục dạng cây, trỏ tới blob/tree con bằng hash.
- Commit chỉ là 1 con trỏ tới 1 tree + con trỏ tới commit cha → toàn bộ lịch sử là 1 linked list
  (thực ra là DAG khi có merge).
- HEAD chỉ là 1 file text trỏ tới ref, ref chỉ là 1 file text chứa hash commit.

## Việc tiếp theo (đề xuất, chưa làm)

Có thể mở rộng dần theo đúng lộ trình build-your-own-x:

| Việc | Độ khó | Học được gì |
|---|---|---|
| `status` + index/staging area (`add`) | Trung bình | Vùng đệm giữa working dir và commit |
| `branch` / `checkout` | Trung bình | Refs, di chuyển HEAD, restore working dir |
| `diff` giữa 2 tree | Trung bình | So sánh nội dung theo từng blob |
| Pack file + delta compression | Khó | Cách Git nén lịch sử để lưu hiệu quả |
| Giao thức smart HTTP (`git clone` qua HTTP) | Khó | Nền tảng để xây "GitHub" thật (Phase 2) |

## Phase 2 — Mini GitHub (web UI), CHƯA triển khai

Ý tưởng: dùng ASP.NET Core (Razor Pages hoặc Minimal API + React) bọc lên `MyGit.Core` để có:

- Trang danh sách repo, trang duyệt file theo tree (dùng lại `TreeBuilder.ParseTree`)
- Trang xem lịch sử commit (dùng lại `CommitService.ParseCommit` + `log`)
- Trang xem nội dung file tại 1 commit cụ thể (`cat-file`)
- (Nâng cao) Issue/PR đơn giản lưu trong SQLite — không liên quan tới Git object model, là phần
  "GitHub" thêm vào trên nền Git

Sẽ triển khai ở lần làm việc sau khi bạn xác nhận Phase 1 chạy đúng trên máy local.
