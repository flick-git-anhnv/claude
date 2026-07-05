using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
using KztekComponent.Controls;
using KztekComponent.Theme;
using TodoApp.Data;
using TodoApp.Models;

namespace TodoApp.Forms
{
    /// <summary>
    /// Form chính của Todo App.
    /// UI hoàn toàn dùng KztekComponent (KzLabel, KzTextBox, KzButton, KzDataGrid, KzPanel, KzCheckBox).
    /// Layout: header + toolbar trên, KzDataGrid chiếm phần còn lại.
    /// </summary>
    public partial class MainForm : Form
    {
        // ── Repository ────────────────────────────────────────
        private readonly TaskRepository _repo = new TaskRepository();

        // ── KztekComponent controls ───────────────────────────
        private KzPanel   pnlHeader;
        private KzLabel   lblAppTitle;
        private KzLabel   lblSubtitle;

        private KzPanel   pnlToolbar;
        private KzButton  btnAdd;
        private KzButton  btnEdit;
        private KzButton  btnDelete;
        private KzButton  btnToggleDone;
        private KzCheckBox chkShowDone;

        private KzPanel   pnlSearch;
        private KzLabel   lblSearch;
        private KzTextBox txtSearch;

        private KzDataGrid grid;

        // ── DataGridView columns (index constants) ────────────
        private const int ColDone       = 0;
        private const int ColTitle      = 1;
        private const int ColDesc       = 2;
        private const int ColCreatedAt  = 3;
        private const int ColId         = 4; // hidden

        public MainForm()
        {
            InitializeComponent();
            RefreshGrid();
        }

        // ════════════════════════════════════════════════════════
        //  InitializeComponent — thuần code, không dùng Designer
        // ════════════════════════════════════════════════════════
        private void InitializeComponent()
        {
            // ── Form ──────────────────────────────────────────
            Text = "Todo App — KZTEK";
            Size = new Size(900, 620);
            MinimumSize = new Size(700, 480);
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = KzTokens.BgDefault;
            Font = KzThemeHelper.GetFont(KzTokens.FontBody);

            // ── Header panel ──────────────────────────────────
            pnlHeader = new KzPanel
            {
                ShowShadow = false,
                Dock = DockStyle.Top,
                Height = 72,
                BackColor = KzTokens.Navy900,
                Padding = new Padding(20, 0, 20, 0)
            };

            lblAppTitle = new KzLabel
            {
                LabelType = KzLabelType.H3,
                Text = "Todo App",
                ForeColor = KzTokens.White,
                AutoSize = true,
                Location = new Point(20, 22)   // UI-002: tăng từ 14→22px để đảm bảo
                                               // hiển thị trong client area (H3 font cao ~20px,
                                               // y=14 có thể bị clipped bởi panel padding top=0
                                               // khi DPI scaling áp dụng margin nội bộ)
            };

            lblSubtitle = new KzLabel
            {
                LabelType = KzLabelType.Small,
                Text = "Quản lý công việc của bạn",
                ForeColor = KzTokens.Navy300,
                AutoSize = true,
                Location = new Point(20, 48)   // UI-002: tăng từ 42→48px (cách title ~26px vertical)
            };

            pnlHeader.Controls.Add(lblAppTitle);
            pnlHeader.Controls.Add(lblSubtitle);

            // ── Toolbar panel ─────────────────────────────────
            pnlToolbar = new KzPanel
            {
                ShowShadow = false,
                Dock = DockStyle.Top,
                Height = 56,
                Padding = new Padding(12, 8, 12, 8),
                BackColor = KzTokens.BgAlt
            };

            btnAdd = new KzButton
            {
                Variant = KzButtonVariant.Primary,
                Text = "Thêm",
                Width = 110,   // UI-001: tăng từ 88→110px (DPI 125-150% an toàn)
                Height = 36,
                Location = new Point(12, 10)
            };
            btnAdd.Click += BtnAdd_Click;

            btnEdit = new KzButton
            {
                Variant = KzButtonVariant.Secondary,
                Text = "Sửa",
                Width = 100,   // UI-001: tăng từ 80→100px
                Height = 36,
                Location = new Point(130, 10),  // 12 + 110 + 8 gap
                Enabled = false
            };
            btnEdit.Click += BtnEdit_Click;

            btnDelete = new KzButton
            {
                Variant = KzButtonVariant.Danger,
                Text = "Xoá",
                Width = 100,   // UI-001: tăng từ 80→100px
                Height = 36,
                Location = new Point(238, 10),  // 130 + 100 + 8 gap
                Enabled = false
            };
            btnDelete.Click += BtnDelete_Click;

            btnToggleDone = new KzButton
            {
                Variant = KzButtonVariant.Accent,
                Text = "Đánh dấu xong",
                Width = 170,   // UI-001: tăng từ 140→170px (đủ cho "Đánh dấu chưa xong")
                Height = 36,
                Location = new Point(346, 10),  // 238 + 100 + 8 gap
                Enabled = false
            };
            btnToggleDone.Click += BtnToggleDone_Click;

            chkShowDone = new KzCheckBox
            {
                Text = "Hiện task đã xong",
                Checked = true,
                Location = new Point(524, 14)   // 346 + 170 + 8 gap
            };
            chkShowDone.CheckedChanged += (s, e) => RefreshGrid();

            pnlToolbar.Controls.Add(btnAdd);
            pnlToolbar.Controls.Add(btnEdit);
            pnlToolbar.Controls.Add(btnDelete);
            pnlToolbar.Controls.Add(btnToggleDone);
            pnlToolbar.Controls.Add(chkShowDone);

            // ── Search panel ──────────────────────────────────
            pnlSearch = new KzPanel
            {
                ShowShadow = false,
                Dock = DockStyle.Top,
                Height = 46,
                Padding = new Padding(12, 6, 12, 6),
                BackColor = KzTokens.BgDefault
            };

            lblSearch = new KzLabel
            {
                LabelType = KzLabelType.Body,
                Text = "Tìm kiếm:",
                AutoSize = true,
                Location = new Point(12, 12)
            };

            txtSearch = new KzTextBox
            {
                Width = 300,
                Height = 30,
                Location = new Point(82, 8),
                PlaceholderText = "Nhập tên task..."
            };
            txtSearch.TextChanged += TxtSearch_TextChanged;

            pnlSearch.Controls.Add(lblSearch);
            pnlSearch.Controls.Add(txtSearch);

            // ── DataGrid ──────────────────────────────────────
            grid = new KzDataGrid
            {
                Dock = DockStyle.Fill,
                ReadOnly = true,
                MultiSelect = false,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect,
                AllowUserToAddRows = false,
                AllowUserToDeleteRows = false,
                AllowUserToResizeRows = false
            };

            BuildGridColumns();

            grid.SelectionChanged += Grid_SelectionChanged;
            grid.CellDoubleClick  += Grid_CellDoubleClick;

            // ── Add to form (order matters: Fill goes last) ───
            Controls.Add(grid);        // Fill — thêm trước
            Controls.Add(pnlSearch);   // Top — search bar, trên grid
            Controls.Add(pnlToolbar);  // Top — che phía trên search
            Controls.Add(pnlHeader);   // Top — che phía trên toolbar
        }

        // ── Column definitions ────────────────────────────────
        private void BuildGridColumns()
        {
            grid.Columns.Clear();

            // Done checkbox
            var colDone = new DataGridViewCheckBoxColumn
            {
                Name = "Done",
                HeaderText = "Xong",
                Width = 55,
                ReadOnly = true,
                Resizable = DataGridViewTriState.False
            };

            // Title
            var colTitle = new DataGridViewTextBoxColumn
            {
                Name = "Title",
                HeaderText = "Tiêu đề",
                Width = 220,
                ReadOnly = true
            };

            // Description
            var colDesc = new DataGridViewTextBoxColumn
            {
                Name = "Description",
                HeaderText = "Mô tả",
                AutoSizeMode = DataGridViewAutoSizeColumnMode.Fill,
                ReadOnly = true
            };

            // Created At
            var colCreated = new DataGridViewTextBoxColumn
            {
                Name = "CreatedAt",
                HeaderText = "Tạo lúc",
                Width = 140,
                ReadOnly = true
            };

            // Id (ẩn — dùng để map row → Guid)
            var colId = new DataGridViewTextBoxColumn
            {
                Name = "Id",
                HeaderText = "Id",
                Visible = false
            };

            grid.Columns.AddRange(colDone, colTitle, colDesc, colCreated, colId);
        }

        // ════════════════════════════════════════════════════════
        //  Data binding
        // ════════════════════════════════════════════════════════
        private void RefreshGrid()
        {
            grid.Rows.Clear();
            bool showDone = chkShowDone.Checked;
            string keyword = txtSearch?.Text?.Trim() ?? string.Empty;

            foreach (TodoTask t in _repo.GetAll())
            {
                // Filter 1: ẩn task đã xong nếu chkShowDone bỏ chọn
                if (!showDone && t.IsDone) continue;

                // Filter 2: search theo Title (case-insensitive, AND với filter 1)
                if (!string.IsNullOrEmpty(keyword) &&
                    !t.Title.Contains(keyword, StringComparison.OrdinalIgnoreCase))
                    continue;

                int idx = grid.Rows.Add();
                DataGridViewRow row = grid.Rows[idx];
                row.Cells[ColDone].Value      = t.IsDone;
                row.Cells[ColTitle].Value     = t.Title;
                row.Cells[ColDesc].Value      = t.Description;
                row.Cells[ColCreatedAt].Value = t.CreatedAt.ToString("dd/MM/yyyy HH:mm");
                row.Cells[ColId].Value        = t.Id.ToString();

                // Task đã xong → hiển thị mờ hơn
                if (t.IsDone)
                {
                    row.DefaultCellStyle.ForeColor = KzTokens.TextMuted;
                }
            }

            UpdateButtonState();
        }

        private Guid? SelectedId()
        {
            if (grid.CurrentRow == null) return null;
            string raw = grid.CurrentRow.Cells[ColId].Value?.ToString();
            return Guid.TryParse(raw, out Guid id) ? id : (Guid?)null;
        }

        private void UpdateButtonState()
        {
            bool hasSelection = grid.CurrentRow != null && grid.SelectedRows.Count > 0;
            btnEdit.Enabled        = hasSelection;
            btnDelete.Enabled      = hasSelection;
            btnToggleDone.Enabled  = hasSelection;

            if (hasSelection)
            {
                Guid? id = SelectedId();
                if (id.HasValue)
                {
                    TodoTask t = _repo.GetById(id.Value);
                    btnToggleDone.Text = (t != null && t.IsDone) ? "Đánh dấu chưa xong" : "Đánh dấu xong";
                }
            }
            else
            {
                btnToggleDone.Text = "Đánh dấu xong";
            }
        }

        // ════════════════════════════════════════════════════════
        //  Event handlers
        // ════════════════════════════════════════════════════════
        private void Grid_SelectionChanged(object sender, EventArgs e)
        {
            UpdateButtonState();
        }

        private void Grid_CellDoubleClick(object sender, DataGridViewCellEventArgs e)
        {
            if (e.RowIndex < 0) return;
            OpenEditDialog();
        }

        private void BtnAdd_Click(object sender, EventArgs e)
        {
            using (var dlg = new EditTaskForm())
            {
                if (dlg.ShowDialog(this) == DialogResult.OK && dlg.Result != null)
                {
                    _repo.Add(dlg.Result);
                    RefreshGrid();
                }
            }
        }

        private void BtnEdit_Click(object sender, EventArgs e)
        {
            OpenEditDialog();
        }

        private void OpenEditDialog()
        {
            Guid? id = SelectedId();
            if (!id.HasValue) return;

            TodoTask task = _repo.GetById(id.Value);
            if (task == null) return;

            // Clone để dialog làm việc trên bản sao; nếu OK mới update
            TodoTask clone = new TodoTask
            {
                Id          = task.Id,
                Title       = task.Title,
                Description = task.Description,
                IsDone      = task.IsDone,
                CreatedAt   = task.CreatedAt
            };

            using (var dlg = new EditTaskForm(clone))
            {
                if (dlg.ShowDialog(this) == DialogResult.OK && dlg.Result != null)
                {
                    _repo.Update(dlg.Result);
                    RefreshGrid();
                }
            }
        }

        private void BtnDelete_Click(object sender, EventArgs e)
        {
            Guid? id = SelectedId();
            if (!id.HasValue) return;

            TodoTask task = _repo.GetById(id.Value);
            string title = task?.Title ?? "task này";

            DialogResult confirm = MessageBox.Show(
                $"Bạn có chắc muốn xoá \"{title}\"?",
                "Xác nhận xoá",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Warning,
                MessageBoxDefaultButton.Button2);

            if (confirm == DialogResult.Yes)
            {
                _repo.Delete(id.Value);
                RefreshGrid();
            }
        }

        private void BtnToggleDone_Click(object sender, EventArgs e)
        {
            Guid? id = SelectedId();
            if (!id.HasValue) return;

            _repo.ToggleDone(id.Value);
            RefreshGrid();
        }

        private void TxtSearch_TextChanged(object sender, EventArgs e)
        {
            RefreshGrid();
        }
    }
}
