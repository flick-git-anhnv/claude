using System;
using System.Drawing;
using System.Windows.Forms;
using KztekComponent.Controls;
using KztekComponent.Theme;
using TodoApp.Models;

namespace TodoApp.Forms
{
    /// <summary>
    /// Dialog thêm task mới hoặc sửa task đã có.
    /// Dùng KzTextBox, KzLabel, KzButton, KzPanel từ KztekComponent.
    /// </summary>
    public class EditTaskForm : Form
    {
        // ── KztekComponent controls ────────────────────────────
        private KzLabel lblTitle;
        private KzLabel lblTitleInput;
        private KzLabel lblDescInput;
        private KzTextBox txtTitle;
        private KzTextBox txtDescription;
        private KzButton btnSave;
        private KzButton btnCancel;

        public TodoTask Result { get; private set; }

        private readonly TodoTask _editing; // null = add mode

        public EditTaskForm(TodoTask existing = null)
        {
            _editing = existing;
            InitializeComponent();

            if (_editing != null)
            {
                Text = "Sửa Task";
                lblTitle.Text = "Sửa Task";
                txtTitle.Text = _editing.Title;
                txtDescription.Text = _editing.Description;
            }
            else
            {
                Text = "Thêm Task Mới";
                lblTitle.Text = "Thêm Task Mới";
            }
        }

        private void InitializeComponent()
        {
            // ── Form ───────────────────────────────────────────
            Size = new Size(480, 320);
            StartPosition = FormStartPosition.CenterParent;
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;
            BackColor = KzTokens.BgDefault;
            Font = KzThemeHelper.GetFont(KzTokens.FontMd);

            // ── Heading ────────────────────────────────────────
            lblTitle = new KzLabel
            {
                LabelType = KzLabelType.H2,
                AutoSize = true,
                Location = new Point(24, 20)
            };

            // ── Title label + input ────────────────────────────
            lblTitleInput = new KzLabel
            {
                LabelType = KzLabelType.Body,
                Text = "Tiêu đề *",
                AutoSize = true,
                Location = new Point(24, 68)
            };

            txtTitle = new KzTextBox
            {
                Location = new Point(24, 88),
                Width = 408,
                Height = 36,
                PlaceholderText = "Nhập tiêu đề task..."
            };

            // ── Description label + input ──────────────────────
            lblDescInput = new KzLabel
            {
                LabelType = KzLabelType.Body,
                Text = "Mô tả",
                AutoSize = true,
                Location = new Point(24, 138)
            };

            txtDescription = new KzTextBox
            {
                Location = new Point(24, 158),
                Width = 408,
                Height = 60,
                Multiline = true,
                PlaceholderText = "Nhập mô tả (tuỳ chọn)..."
            };

            // ── Buttons ────────────────────────────────────────
            btnSave = new KzButton
            {
                Variant = KzButtonVariant.Primary,
                Text = "Lưu",
                Location = new Point(288, 240),
                Width = 80,
                Height = 36
            };
            btnSave.Click += BtnSave_Click;

            btnCancel = new KzButton
            {
                Variant = KzButtonVariant.Secondary,
                Text = "Huỷ",
                Location = new Point(378, 240),
                Width = 60,
                Height = 36
            };
            btnCancel.Click += (s, e) => { DialogResult = DialogResult.Cancel; Close(); };

            // ── Add to form ────────────────────────────────────
            Controls.Add(lblTitle);
            Controls.Add(lblTitleInput);
            Controls.Add(txtTitle);
            Controls.Add(lblDescInput);
            Controls.Add(txtDescription);
            Controls.Add(btnSave);
            Controls.Add(btnCancel);

            // UX: Enter = Save, Esc = Cancel
            AcceptButton = btnSave;
            CancelButton = btnCancel;
        }

        private void BtnSave_Click(object sender, EventArgs e)
        {
            string title = txtTitle.Text.Trim();
            if (string.IsNullOrEmpty(title))
            {
                MessageBox.Show("Vui lòng nhập tiêu đề task.", "Thiếu thông tin",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                txtTitle.Focus();
                return;
            }

            if (_editing != null)
            {
                _editing.Title = title;
                _editing.Description = txtDescription.Text.Trim();
                Result = _editing;
            }
            else
            {
                Result = new TodoTask
                {
                    Title = title,
                    Description = txtDescription.Text.Trim()
                };
            }

            DialogResult = DialogResult.OK;
            Close();
        }
    }
}
