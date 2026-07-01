using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using Guna.UI2.WinForms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System data grid — Navy header, alternating rows, hover highlight.")]
    public class KzDataGrid : Guna2DataGridView
    {
        private int _hoveredRow = -1;

        public KzDataGrid()
        {
            ApplyStyle();
            WireHover();
        }

        private void WireHover()
        {
            CellMouseEnter += (s, e) =>
            {
                if (e.RowIndex < 0) return;
                int prev = _hoveredRow;
                _hoveredRow = e.RowIndex;
                if (prev >= 0 && prev < RowCount) InvalidateRow(prev);
                InvalidateRow(_hoveredRow);
            };
            CellMouseLeave += (s, e) =>
            {
                if (e.RowIndex != _hoveredRow) return;
                int prev = _hoveredRow;
                _hoveredRow = -1;
                if (prev >= 0 && prev < RowCount) InvalidateRow(prev);
            };
            CellFormatting += (s, e) =>
            {
                if (e.RowIndex < 0 || e.RowIndex != _hoveredRow) return;
                if (Rows[e.RowIndex].Selected) return;
                e.CellStyle.BackColor = KzTokens.Navy100;
                e.CellStyle.SelectionBackColor = KzTokens.Navy100;
                // KHÔNG set e.FormattingApplied = true ở đây: ta chỉ đổi màu nền,
                // không tự convert e.Value sang chuỗi hiển thị. Set cờ này sẽ khiến
                // grid coi value int (cột STT) là "đã format" và ném
                // FormatException: "Formatted value of the cell has a wrong type".
            };
        }

        private void ApplyStyle()
        {
            // ── Grid chrome ───────────────────────────────────
            BorderStyle = BorderStyle.None;
            BackgroundColor = KzTokens.BgDefault;
            GridColor = KzTokens.Border;
            CellBorderStyle = DataGridViewCellBorderStyle.SingleHorizontal;
            RowHeadersVisible = false;
            AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
            SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            Font = KzThemeHelper.GetFont(KzTokens.FontBody);
            EnableHeadersVisualStyles = false;

            // ── Column header ─────────────────────────────────
            ColumnHeadersDefaultCellStyle = new DataGridViewCellStyle
            {
                BackColor = KzTokens.Navy900,
                ForeColor = KzTokens.White,
                Font = KzThemeHelper.GetFont(KzTokens.FontBody, FontStyle.Bold),
                SelectionBackColor = KzTokens.Navy900,
                SelectionForeColor = KzTokens.White,
                Alignment = DataGridViewContentAlignment.MiddleLeft
            };
            ColumnHeadersHeight = KzTokens.HeightMd;
            ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.DisableResizing;

            // ── Row default ───────────────────────────────────
            DefaultCellStyle = new DataGridViewCellStyle
            {
                BackColor = KzTokens.White,
                ForeColor = KzTokens.Text,
                Font = KzThemeHelper.GetFont(KzTokens.FontBody),
                SelectionBackColor = KzTokens.Navy100,
                SelectionForeColor = KzTokens.Navy900,
                Padding = new Padding(8, 0, 8, 0)
            };
            RowsDefaultCellStyle = DefaultCellStyle;

            // ── Alternating row ───────────────────────────────
            AlternatingRowsDefaultCellStyle = new DataGridViewCellStyle
            {
                BackColor = KzTokens.BgAlt,
                ForeColor = KzTokens.Text,
                Font = KzThemeHelper.GetFont(KzTokens.FontBody),
                SelectionBackColor = KzTokens.Navy100,
                SelectionForeColor = KzTokens.Navy900,
                Padding = new Padding(8, 0, 8, 0)
            };

            // ── Row height ────────────────────────────────────
            RowTemplate.Height = KzTokens.HeightMd;

            // ── Guna ThemeStyle ───────────────────────────────
            ThemeStyle.BackColor = KzTokens.White;
            ThemeStyle.GridColor = KzTokens.Border;
        }
    }
}
