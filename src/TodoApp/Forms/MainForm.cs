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
                Location = new Point(20, 14)
            };

            lblSubtitle = new KzLabel
            {
                LabelType = KzLabelType.Small,
                Text = "Quản lý công việc của bạn",
                ForeColor = KzTokens.Navy300,
                AutoSize = true,
                Location = new Point(20, 42)
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
                Width = 88,
                Height = 36,
                Location = new Point(12, 10)
            };
            btnAdd.Click += BtnAdd_Click;

            btnEdit = new KzButton
            {
                Variant = KzButtonVariant.Secondary,
                Text = "Sửa",
                Width = 80,
                Height = 36,
                Location = new Point(108, 10),
                Enabled = false
            };
            btnEdit.Click += BtnEdit_Click;

            btnDelete = new KzButton
            {
                Variant = KzButtonVariant.Danger,
                Text = "Xoá",
                Width = 80,
                Height = 36,
                Location = new Point(196, 10),
                Enabled = false
            };
            btnDelete.Click += BtnDelete_Click;

            btnToggleDone = new KzButton
            {
                Variant = KzButtonVariant.Accent,
                Text = "Đánh dấu xong",
                Width = 140,
                Height = 36,
                Location = new Point(284, 10),
                Enabled = false
            };
            btnToggleDone.Click += BtnToggleDone_Click;

            chkShowDone = new KzCheckBox
            {
                Text = "Hiện task đã xong",
                Checked = true,
                Location = new Point(442, 14)
            };
            chkShowDone.CheckedChanged += (s, e) => RefreshGrid();

            pnlToolbar.Controls.Add(btnAdd);
            pnlToolbar.Controls.Add(btnEdit);
            pnlToolbar.Controls.Add(btnDelete);
            pnlToolbar.Controls.Add(btnToggleDone);
            pnlToolbar.Controls.Add(chkShowDone);

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
            Controls.Add(pnlToolbar);  // Top — che phía trên grid
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

            foreach (TodoTask t in _repo.GetAll())
            {
                if (!showDone && t.IsDone) continue;

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
    }
}
