using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using TodoApp.Models;

namespace TodoApp.Data
{
    public class TaskRepository
    {
        private readonly string _filePath;
        private List<TodoTask> _tasks;

        private static readonly JsonSerializerOptions _jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true
        };

        public TaskRepository(string dataDirectory = "data")
        {
            // Lưu JSON cạnh assembly, trong thư mục "data"
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string dir = Path.Combine(baseDir, dataDirectory);
            Directory.CreateDirectory(dir);
            _filePath = Path.Combine(dir, "tasks.json");
            _tasks = Load();
        }

        // ── Read ───────────────────────────────────────────────
        public IReadOnlyList<TodoTask> GetAll() => _tasks.AsReadOnly();

        public TodoTask GetById(Guid id) => _tasks.Find(t => t.Id == id);

        // ── Create ─────────────────────────────────────────────
        public void Add(TodoTask task)
        {
            if (task == null) throw new ArgumentNullException(nameof(task));
            _tasks.Add(task);
            Save();
        }

        // ── Update ─────────────────────────────────────────────
        public bool Update(TodoTask updated)
        {
            int idx = _tasks.FindIndex(t => t.Id == updated.Id);
            if (idx < 0) return false;
            _tasks[idx] = updated;
            Save();
            return true;
        }

        // ── Delete ─────────────────────────────────────────────
        public bool Delete(Guid id)
        {
            int removed = _tasks.RemoveAll(t => t.Id == id);
            if (removed == 0) return false;
            Save();
            return true;
        }

        // ── Toggle Done ────────────────────────────────────────
        public bool ToggleDone(Guid id)
        {
            TodoTask task = GetById(id);
            if (task == null) return false;
            task.IsDone = !task.IsDone;
            Save();
            return true;
        }

        // ── Persistence ────────────────────────────────────────
        private List<TodoTask> Load()
        {
            if (!File.Exists(_filePath))
                return new List<TodoTask>();

            try
            {
                string json = File.ReadAllText(_filePath);
                return JsonSerializer.Deserialize<List<TodoTask>>(json, _jsonOptions)
                       ?? new List<TodoTask>();
            }
            catch
            {
                // File bị corrupt → bắt đầu lại với danh sách rỗng
                return new List<TodoTask>();
            }
        }

        private void Save()
        {
            try
            {
                string json = JsonSerializer.Serialize(_tasks, _jsonOptions);
                // Ghi qua file tạm rồi replace để tránh corrupt nếu crash giữa chừng
                string tmp = _filePath + ".tmp";
                File.WriteAllText(tmp, json);
                if (File.Exists(_filePath)) File.Delete(_filePath);
                File.Move(tmp, _filePath);
            }
            catch (Exception ex)
            {
                // Không crash app — báo user và giữ nguyên state trong RAM
                System.Windows.Forms.MessageBox.Show(
                    "Không thể lưu dữ liệu: " + ex.Message,
                    "Lỗi lưu file",
                    System.Windows.Forms.MessageBoxButtons.OK,
                    System.Windows.Forms.MessageBoxIcon.Error);
            }
        }
    }
}
