using KztekComponent.Theme;
using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System tab control — underline style, Navy text, Orange active indicator.")]
    public class KzTabControl : TabControl
    {
        private int _hoveredIndex = -1;

        public KzTabControl()
        {
            DrawMode   = TabDrawMode.OwnerDrawFixed;
            ItemSize   = new Size(0, 40);
            SizeMode   = TabSizeMode.Normal;
            Appearance = TabAppearance.Normal;
            Font       = KzThemeHelper.GetFont(KzTokens.FontMd);
            Padding    = new Point(16, 0);

            MouseMove  += OnMouseMove;
            MouseLeave += OnMouseLeave;
        }

        protected override void OnDrawItem(DrawItemEventArgs e)
        {
            var  tab        = TabPages[e.Index];
            bool isSelected = e.Index == SelectedIndex;
            bool isHovered  = e.Index == _hoveredIndex && !isSelected;

            var g = e.Graphics;
            g.SmoothingMode     = SmoothingMode.AntiAlias;
            g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.ClearTypeGridFit;

            var bgColor = BackColor == Color.Empty ? SystemColors.Control : BackColor;
            g.FillRectangle(new SolidBrush(bgColor), e.Bounds);

            Color textColor = isSelected ? KzTokens.Navy900
                            : isHovered  ? KzTokens.Text
                            : KzTokens.TextMuted;

            using var font  = isSelected
                ? KzThemeHelper.GetFont(KzTokens.FontMd, FontStyle.Bold)
                : KzThemeHelper.GetFont(KzTokens.FontMd);
            using var brush = new SolidBrush(textColor);

            var sf = new StringFormat
            {
                Alignment     = StringAlignment.Center,
                LineAlignment = StringAlignment.Center,
            };
            g.DrawString(tab.Text, font, brush, e.Bounds, sf);

            if (isSelected)
            {
                var indicator = new Rectangle(e.Bounds.X + 4, e.Bounds.Bottom - 3, e.Bounds.Width - 8, 3);
                g.FillRectangle(new SolidBrush(KzTokens.Orange500), indicator);
            }
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            if (TabCount == 0) return;
            int y = GetTabRect(0).Bottom;
            using var pen = new Pen(KzTokens.Border, 1f);
            e.Graphics.DrawLine(pen, 0, y, Width, y);
        }

        private void OnMouseMove(object? sender, MouseEventArgs e)
        {
            for (int i = 0; i < TabCount; i++)
            {
                if (GetTabRect(i).Contains(e.Location))
                {
                    if (_hoveredIndex != i) { _hoveredIndex = i; Invalidate(); }
                    return;
                }
            }
            if (_hoveredIndex != -1) { _hoveredIndex = -1; Invalidate(); }
        }

        private void OnMouseLeave(object? sender, EventArgs e)
        {
            if (_hoveredIndex != -1) { _hoveredIndex = -1; Invalidate(); }
        }
    }
}
