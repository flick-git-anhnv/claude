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
    [Description("KZTEK sidebar navigation item — active state with orange left border.")]
    public class KzSidebarItem : Control
    {
        private bool   _isActive;
        private bool   _isHovered;
        private Image  _icon;
        private string _itemText = "Menu item";

        [Category("•KZTEK"), DefaultValue(false)]
        public bool IsActive
        {
            get => _isActive;
            set { _isActive = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(null)]
        public Image Icon
        {
            get => _icon;
            set { _icon = value; Invalidate(); }
        }

        public override string Text
        {
            get => _itemText;
            set { _itemText = value; Invalidate(); }
        }

        [Category("•KZTEK")]
        public event EventHandler ItemClicked;

        public KzSidebarItem()
        {
            SetStyle(ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;
            Height = KzTokens.SidebarItemH;
            Cursor = Cursors.Hand;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.ClearTypeGridFit;

            var bounds = new Rectangle(0, 0, Width, Height);

            // ── Hover background (gradient) ───────────────────
            if (_isHovered && !_isActive)
                KzThemeHelper.DrawSidebarItemHoverBg(g, bounds);

            // ── Active background ──────────────────────────────
            if (_isActive)
            {
                using (var bg = new SolidBrush(Color.FromArgb(31, KzTokens.Orange500)))
                    g.FillRectangle(bg, bounds);
            }

            // ── Active left border ─────────────────────────────
            if (_isActive)
            {
                using (var pen = new Pen(KzTokens.Orange500, KzTokens.SidebarActiveBar))
                    g.DrawLine(pen,
                        KzTokens.SidebarActiveBar / 2, 0,
                        KzTokens.SidebarActiveBar / 2, Height);
            }
            else if (_isHovered)
            {
                using (var pen = new Pen(Color.FromArgb(127, KzTokens.Orange500), KzTokens.SidebarActiveBar))
                    g.DrawLine(pen,
                        KzTokens.SidebarActiveBar / 2, 0,
                        KzTokens.SidebarActiveBar / 2, Height);
            }

            // ── Icon ──────────────────────────────────────────
            int iconSize = 18;
            int iconX = KzTokens.SidebarPadH;
            int iconY = (Height - iconSize) / 2;

            if (_icon != null)
            {
                // Tint icon white
                var attrs = new System.Drawing.Imaging.ImageAttributes();
                var matrix = new System.Drawing.Imaging.ColorMatrix(new float[][]
                {
                    new float[]{0,0,0,0,0},
                    new float[]{0,0,0,0,0},
                    new float[]{0,0,0,0,0},
                    new float[]{0,0,0,1,0},
                    new float[]{1,1,1,0,1}
                });
                attrs.SetColorMatrix(matrix);
                g.DrawImage(_icon,
                    new Rectangle(iconX, iconY, iconSize, iconSize),
                    0, 0, _icon.Width, _icon.Height,
                    GraphicsUnit.Pixel, attrs);
            }
            else
            {
                // Draw placeholder circle
                Color dotColor = _isActive ? KzTokens.Orange300
                               : _isHovered ? KzTokens.Navy300
                               : KzTokens.Navy300;
                using (var brush = new SolidBrush(dotColor))
                    g.FillEllipse(brush, iconX + 3, iconY + 3, 12, 12);
            }

            // ── Text ──────────────────────────────────────────
            int textX = KzTokens.SidebarPadH + iconSize + 10;
            var textRect = new Rectangle(textX, 0, Width - textX - 8, Height);

            Color textColor = _isActive  ? KzTokens.White
                            : _isHovered ? KzTokens.White
                            : KzTokens.Navy300;

            FontStyle style = _isActive ? FontStyle.Bold : FontStyle.Regular;
            using var font = KzThemeHelper.GetFont(KzTokens.FontBody, style);
            KzThemeHelper.DrawCenteredText(g, _itemText, font, textColor, textRect, StringAlignment.Near);
        }

        protected override void OnMouseEnter(EventArgs e)
        {
            _isHovered = true;
            Invalidate();
            base.OnMouseEnter(e);
        }

        protected override void OnMouseLeave(EventArgs e)
        {
            _isHovered = false;
            Invalidate();
            base.OnMouseLeave(e);
        }

        protected override void OnClick(EventArgs e)
        {
            ItemClicked?.Invoke(this, e);
            base.OnClick(e);
        }
    }
}

