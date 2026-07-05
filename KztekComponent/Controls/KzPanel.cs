using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System panel — rounded container with border and optional shadow.")]
    public class KzPanel : Panel
    {
        private bool _showShadow = true;
        private bool _isHovered;

        [Category("•KZTEK")]
        [DefaultValue(true)]
        public bool ShowShadow
        {
            get => _showShadow;
            set { _showShadow = value; Invalidate(); }
        }

        public KzPanel()
        {
            SetStyle(ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);

            Size      = new Size(300, 200);
            Padding   = new Padding(16);
            BackColor = Color.Transparent;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;

            var rect = new Rectangle(1, 1, Width - 3, Height - 3);

            if (_showShadow)
                KzThemeHelper.DrawCardShadow(g, rect, KzTokens.RadiusLg, _isHovered);

            // UI-002 fix: dùng BackColor thực tế thay vì hardcode White
            // để panel có thể render màu Navy900 / bất kỳ màu nền nào được set.
            var fillColor = BackColor == Color.Transparent ? KzTokens.White : BackColor;
            using (var brush = new SolidBrush(fillColor))
                KzThemeHelper.FillRoundedRect(g, brush, rect, KzTokens.RadiusLg);

            using (var pen = new Pen(KzTokens.Border, 1f))
                KzThemeHelper.DrawRoundedBorder(g, pen, rect, KzTokens.RadiusLg);
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
    }
}
