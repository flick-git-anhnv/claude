using System;
using System.IO;
using System.Linq;
using TodoApp.Data;
using TodoApp.Models;

namespace TodoApp.Tests
{
    /// <summary>
    /// Smoke-test logic CRUD + persistence của TaskRepository.
    /// Dùng thư mục tạm riêng cho mỗi test để tránh xung đột.
    /// </summary>
    public class TaskRepositoryTests : IDisposable
    {
        private readonly string _tempDir;
        private readonly TaskRepository _repo;

        public TaskRepositoryTests()
        {
            // Tạo thư mục tạm độc lập cho mỗi test instance
            _tempDir = Path.Combine(Path.GetTempPath(), "TodoAppTests_" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(_tempDir);
            _repo = new TaskRepository(_tempDir);
        }

        public void Dispose()
        {
            // Dọn dẹp sau mỗi test
            if (Directory.Exists(_tempDir))
                Directory.Delete(_tempDir, recursive: true);
        }

        // ── TC-01: Create ─────────────────────────────────────────
        [Fact]
        public void Add_ValidTask_ShouldIncreaseCount()
        {
            var task = new TodoTask { Title = "[TEST] Mua sữa", Description = "1 lít" };
            _repo.Add(task);
            Assert.Single(_repo.GetAll());
        }

        [Fact]
        public void Add_NullTask_ShouldThrow()
        {
            Assert.Throws<ArgumentNullException>(() => _repo.Add(null!));
        }

        // ── TC-02: Read ───────────────────────────────────────────
        [Fact]
        public void GetById_ExistingId_ShouldReturnTask()
        {
            var task = new TodoTask { Title = "[TEST] Đọc sách" };
            _repo.Add(task);
            var found = _repo.GetById(task.Id);
            Assert.NotNull(found);
            Assert.Equal("[TEST] Đọc sách", found.Title);
        }

        [Fact]
        public void GetById_NonExistingId_ShouldReturnNull()
        {
            var result = _repo.GetById(Guid.NewGuid());
            Assert.Null(result);
        }

        // ── TC-03: Update ─────────────────────────────────────────
        [Fact]
        public void Update_ExistingTask_ShouldChangeTitle()
        {
            var task = new TodoTask { Title = "[TEST] Gốc" };
            _repo.Add(task);

            task.Title = "[TEST] Đã sửa";
            bool result = _repo.Update(task);

            Assert.True(result);
            Assert.Equal("[TEST] Đã sửa", _repo.GetById(task.Id)!.Title);
        }

        [Fact]
        public void Update_NonExistingTask_ShouldReturnFalse()
        {
            var ghost = new TodoTask { Title = "[TEST] Không tồn tại" };
            bool result = _repo.Update(ghost);
            Assert.False(result);
        }

        // ── TC-04: Delete ─────────────────────────────────────────
        [Fact]
        public void Delete_ExistingId_ShouldRemoveTask()
        {
            var task = new TodoTask { Title = "[TEST] Xoá task này" };
            _repo.Add(task);

            bool result = _repo.Delete(task.Id);

            Assert.True(result);
            Assert.Empty(_repo.GetAll());
        }

        [Fact]
        public void Delete_NonExistingId_ShouldReturnFalse()
        {
            bool result = _repo.Delete(Guid.NewGuid());
            Assert.False(result);
        }

        // ── TC-05: ToggleDone ─────────────────────────────────────
        [Fact]
        public void ToggleDone_ShouldFlipIsDoneFlag()
        {
            var task = new TodoTask { Title = "[TEST] Toggle" };
            _repo.Add(task);
            Assert.False(task.IsDone);

            _repo.ToggleDone(task.Id);
            Assert.True(_repo.GetById(task.Id)!.IsDone);

            _repo.ToggleDone(task.Id);
            Assert.False(_repo.GetById(task.Id)!.IsDone);
        }

        // ── TC-06: Persistence (save + reload) ────────────────────
        [Fact]
        public void Persistence_AfterAddAndReload_ShouldStillHaveTasks()
        {
            // Thêm 3 task qua repo đầu tiên
            _repo.Add(new TodoTask { Title = "[TEST] Công việc 1" });
            _repo.Add(new TodoTask { Title = "[TEST] Công việc 2" });
            _repo.Add(new TodoTask { Title = "[TEST] Công việc 3" });

            // Tạo repo mới đọc lại từ cùng thư mục (mô phỏng restart app)
            var repo2 = new TaskRepository(_tempDir);

            Assert.Equal(3, repo2.GetAll().Count);
            Assert.Contains(repo2.GetAll(), t => t.Title == "[TEST] Công việc 1");
            Assert.Contains(repo2.GetAll(), t => t.Title == "[TEST] Công việc 3");
        }

        [Fact]
        public void Persistence_AfterDeleteAndReload_ShouldNotHaveDeletedTask()
        {
            var t1 = new TodoTask { Title = "[TEST] Giữ lại" };
            var t2 = new TodoTask { Title = "[TEST] Xoá đi" };
            _repo.Add(t1);
            _repo.Add(t2);

            _repo.Delete(t2.Id);

            var repo2 = new TaskRepository(_tempDir);
            Assert.Single(repo2.GetAll());
            Assert.DoesNotContain(repo2.GetAll(), t => t.Title == "[TEST] Xoá đi");
        }

        [Fact]
        public void Persistence_AfterToggleDoneAndReload_ShouldKeepIsDoneState()
        {
            var task = new TodoTask { Title = "[TEST] Toggle persist" };
            _repo.Add(task);
            _repo.ToggleDone(task.Id);

            var repo2 = new TaskRepository(_tempDir);
            var loaded = repo2.GetById(task.Id);

            Assert.NotNull(loaded);
            Assert.True(loaded!.IsDone);
        }

        // ── TC-07: JSON file auto-created ────────────────────────
        [Fact]
        public void JsonFile_ShouldBeCreatedAfterAdd()
        {
            string jsonPath = Path.Combine(_tempDir, "tasks.json");
            Assert.False(File.Exists(jsonPath)); // chưa có trước khi add

            _repo.Add(new TodoTask { Title = "[TEST] Check file" });

            Assert.True(File.Exists(jsonPath));
        }
    }
}
