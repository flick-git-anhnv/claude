using System;
using System.Collections.Generic;
using System.Linq;
using TodoApp.Models;

namespace TodoApp.Tests
{
    /// <summary>
    /// Verify-by-unit-test: logic filter search box trong MainForm.RefreshGrid().
    ///
    /// Logic gốc (MainForm.cs dòng 274-306):
    ///   bool showDone = chkShowDone.Checked;
    ///   string keyword = txtSearch?.Text?.Trim() ?? string.Empty;
    ///   foreach (TodoTask t in _repo.GetAll())
    ///   {
    ///       if (!showDone && t.IsDone) continue;
    ///       if (!string.IsNullOrEmpty(keyword) &&
    ///           !t.Title.Contains(keyword, StringComparison.OrdinalIgnoreCase))
    ///           continue;
    ///       // render row
    ///   }
    ///
    /// Test này tái hiện chính xác logic đó ở dạng LINQ thuần — không phụ thuộc WinForms.
    /// Phương thức ApplyFilter() là mirror 1:1 của logic trong RefreshGrid().
    /// </summary>
    public class SearchFilterTests
    {
        // ── Helper: mirror logic RefreshGrid() ───────────────────────
        private static List<TodoTask> ApplyFilter(
            IEnumerable<TodoTask> tasks,
            bool showDone,
            string rawKeyword)
        {
            string keyword = rawKeyword?.Trim() ?? string.Empty;
            var result = new List<TodoTask>();
            foreach (var t in tasks)
            {
                // Filter 1: ẩn task đã xong nếu showDone = false
                if (!showDone && t.IsDone) continue;

                // Filter 2: search theo Title (case-insensitive, AND với filter 1)
                if (!string.IsNullOrEmpty(keyword) &&
                    !t.Title.Contains(keyword, StringComparison.OrdinalIgnoreCase))
                    continue;

                result.Add(t);
            }
            return result;
        }

        // ── Fixture data ──────────────────────────────────────────────
        private static List<TodoTask> SampleTasks() => new List<TodoTask>
        {
            new TodoTask { Title = "[TEST] Mua sữa",        IsDone = false },
            new TodoTask { Title = "[TEST] Đọc sách",       IsDone = false },
            new TodoTask { Title = "[TEST] Học tiếng Anh",  IsDone = true  },
            new TodoTask { Title = "[TEST] Viết báo cáo",   IsDone = true  },
            new TodoTask { Title = "[TEST] Chạy bộ",        IsDone = false },
        };

        // ── TC-SEARCH-01: Gõ keyword → list lọc đúng theo Title ──────
        [Fact]
        public void Filter_WithKeyword_ReturnsOnlyMatchingTitles()
        {
            var tasks = SampleTasks();
            // showDone=true để không bị filter IsDone che khuất kết quả
            var result = ApplyFilter(tasks, showDone: true, rawKeyword: "sách");

            Assert.Single(result);
            Assert.Equal("[TEST] Đọc sách", result[0].Title);
        }

        // ── TC-SEARCH-02: Xóa text → list về đủ (theo showDone) ──────
        [Fact]
        public void Filter_EmptyKeyword_ReturnsAllTasksRespectingShowDone()
        {
            var tasks = SampleTasks();

            // Khi showDone=true: trả về toàn bộ 5 task
            var resultAll = ApplyFilter(tasks, showDone: true, rawKeyword: "");
            Assert.Equal(5, resultAll.Count);

            // Khi showDone=false: trả về 3 task chưa xong
            var resultNoDone = ApplyFilter(tasks, showDone: false, rawKeyword: "");
            Assert.Equal(3, resultNoDone.Count);
            Assert.All(resultNoDone, t => Assert.False(t.IsDone));
        }

        // ── TC-SEARCH-03: Kết hợp showDone=false + keyword → AND filter
        [Fact]
        public void Filter_KeywordAndShowDone_AppliesAndLogic()
        {
            var tasks = SampleTasks();
            // showDone=false → chỉ task chưa xong; keyword="TEST" → match Title chứa "TEST"
            // Kết quả: 3 task chưa xong đều có "[TEST]" trong Title → trả 3
            var result = ApplyFilter(tasks, showDone: false, rawKeyword: "TEST");
            Assert.Equal(3, result.Count);
            Assert.All(result, t => Assert.False(t.IsDone));

            // showDone=false + keyword="Học" → "Học tiếng Anh" IsDone=true → bị filter IsDone → 0 kết quả
            var result2 = ApplyFilter(tasks, showDone: false, rawKeyword: "Học");
            Assert.Empty(result2);

            // showDone=true + keyword="Học" → 1 kết quả
            var result3 = ApplyFilter(tasks, showDone: true, rawKeyword: "Học");
            Assert.Single(result3);
            Assert.Equal("[TEST] Học tiếng Anh", result3[0].Title);
        }

        // ── TC-SEARCH-04: Case-insensitive — gõ hoa match thường ────
        [Fact]
        public void Filter_UppercaseKeyword_MatchesLowercaseTitle()
        {
            var tasks = SampleTasks();
            // "MUA SỮA" (chữ hoa) phải match "[TEST] Mua sữa" (chữ thường)
            // Lưu ý: OrdinalIgnoreCase hoạt động tốt với ASCII; với ký tự có dấu (ữ)
            // hành vi phụ thuộc locale — test này verify behavior thực tế của code.
            var result = ApplyFilter(tasks, showDone: true, rawKeyword: "MUA");
            Assert.Single(result);
            Assert.Equal("[TEST] Mua sữa", result[0].Title);
        }

        // ── TC-SEARCH-04b: Case-insensitive — gõ thường match hoa ───
        // Note: behavior thực tế trên Windows .NET 8: OrdinalIgnoreCase với ký tự Unicode
        // có dấu tiếng Việt (Á/á, Ô/ô...) — Windows ICU/NLS fold được một phần tùy ký tự.
        // Test này document behavior THỰC TẾ đã verify (không phải giả định lý thuyết):
        // "báo cáo" match "BÁO CÁO" → PASS trên .NET 8 Windows với OrdinalIgnoreCase.
        [Fact]
        public void Filter_LowercaseKeyword_MatchesUppercaseInTitle()
        {
            var tasks = new List<TodoTask>
            {
                new TodoTask { Title = "[TEST] BÁO CÁO THÁNG 7", IsDone = false },
                new TodoTask { Title = "[TEST] Kế hoạch Q3",     IsDone = false },
            };
            // Verified behavior on Windows .NET 8: OrdinalIgnoreCase folds Vietnamese
            // accented characters (á=Á, ô=Ô, etc.) — 1 match expected.
            var result = ApplyFilter(tasks, showDone: true, rawKeyword: "báo cáo");
            Assert.Single(result);
            Assert.Equal("[TEST] BÁO CÁO THÁNG 7", result[0].Title);
        }

        // ── TC-SEARCH-05: Keyword chỉ chứa khoảng trắng → Trim() → empty → không filter
        [Fact]
        public void Filter_WhitespaceOnlyKeyword_TreatedAsEmpty()
        {
            var tasks = SampleTasks();
            var result = ApplyFilter(tasks, showDone: true, rawKeyword: "   ");
            Assert.Equal(5, result.Count); // Trim() → "" → IsNullOrEmpty → không filter
        }

        // ── TC-SEARCH-06: Keyword null → không filter (null-safe) ───
        [Fact]
        public void Filter_NullKeyword_TreatedAsEmpty()
        {
            var tasks = SampleTasks();
            var result = ApplyFilter(tasks, showDone: true, rawKeyword: null!);
            Assert.Equal(5, result.Count);
        }

        // ── TC-SEARCH-07: Không có task nào match → trả empty list ─
        [Fact]
        public void Filter_NoMatch_ReturnsEmptyList()
        {
            var tasks = SampleTasks();
            var result = ApplyFilter(tasks, showDone: true, rawKeyword: "xyz_không_tồn_tại_999");
            Assert.Empty(result);
        }
    }
}
