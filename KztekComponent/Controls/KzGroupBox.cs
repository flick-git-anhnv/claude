using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("KZTEK")]
    [Description("KZTEK Design System group box — section container with optional header title.")]
    public class KzGroupBox : Panel
    {
        private string             _title   = "";
        private KzGroupBoxVariant  _variant = KzGroupBoxVariant.Default;
        private const int          HeaderH  = 44;

        [Category("•KZTEK")]
        [DefaultValue("")]
        public string Title
        {
            get => _title;
            set
            {
                _title  = value;
                Padding = new Padding(16, string.IsNullOrEmpty(value) ? 16 : HeaderH + 8, 16, 16);
                Invalidate();
            }
        }

        [Category("•KZTEK")]
        [DefaultValue(KzGroupBoxVariant.Default)]
        public KzGroupBoxVariant Variant
        {
            get => _variant;
            set { _variant = value; Invalidate(); }
        }

        public KzGroupBox()
        {
            SetStyle(ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);

            Size      = new Size(400, 200);
            Padding   = new Padding(16);
            BackColor = Color.Transparent;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode     = SmoothingMode.AntiAlias;
            g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.ClearTypeGridFit;

            var rect = new Rectangle(1, 1, Width - 3, Height - 3);

            Color bg;
            Color border;
            float borderW;

            switch (_variant)
            {
                case KzGroupBoxVariant.Filled:
                    bg      = KzTokens.BgAlt;
                    border  = KzTokens.Border;
                    borderW = 1f;
                    break;
                case KzGroupBoxVariant.Outlined:
                    bg      = Color.Transparent;
                    border  = KzTokens.Divider;
                    borderW = 2f;
                    break;
                default:
                    bg      = KzTokens.White;
                    border  = KzTokens.Border;
                    borderW = 1f;
                    break;
            }

            if (bg != Color.Transparent)
                using (var brush = new SolidBrush(bg))
                    KzThemeHelper.FillRoundedRect(g, brush, rect, KzTokens.RadiusLg);

            using (var pen = new Pen(border, borderW))
                KzThemeHelper.DrawRoundedBorder(g, pen, rect, KzTokens.RadiusLg);

            if (!string.IsNullOrEmpty(_title))
            {
                using var font  = KzThemeHelper.GetFont(KzTokens.FontMd, FontStyle.Bold);
                using var brush = new SolidBrush(KzTokens.Navy900);
                var titleRect   = new Rectangle(rect.X + 16, rect.Y, rect.Width - 32, HeaderH);
                var sf          = new StringFormat { LineAlignment = StringAlignment.Center };
                g.DrawString(_title, font, brush, titleRect, sf);

                using var divPen = new Pen(KzTokens.Border, 1f);
                g.DrawLine(divPen, rect.X + 12, rect.Y + HeaderH, rect.Right - 12, rect.Y + HeaderH);
            }
        }
    }
}
