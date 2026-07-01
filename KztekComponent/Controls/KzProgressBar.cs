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
    [Description("KZTEK Design System progress bar — pill-shaped track + fill.")]
    public class KzProgressBar : Control
    {
        private int   _value         = 0;
        private int   _minimum       = 0;
        private int   _maximum       = 100;
        private Color _progressColor;
        private Color _trackColor;

        [Category("•KZTEK")]
        [DefaultValue(0)]
        public int Value
        {
            get => _value;
            set { _value = Math.Max(_minimum, Math.Min(_maximum, value)); Invalidate(); }
        }

        [Category("•KZTEK")]
        [DefaultValue(0)]
        public int Minimum
        {
            get => _minimum;
            set { _minimum = value; Invalidate(); }
        }

        [Category("•KZTEK")]
        [DefaultValue(100)]
        public int Maximum
        {
            get => _maximum;
            set { _maximum = value; Invalidate(); }
        }

        [Category("•KZTEK")]
        public Color ProgressColor
        {
            get => _progressColor;
            set { _progressColor = value; Invalidate(); }
        }

        [Category("•KZTEK")]
        public Color TrackColor
        {
            get => _trackColor;
            set { _trackColor = value; Invalidate(); }
        }

        public KzProgressBar()
        {
            _progressColor = KzTokens.Navy900;
            _trackColor    = KzTokens.Navy100;

            SetStyle(ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);

            Size      = new Size(300, 10);
            BackColor = Color.Transparent;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode   = SmoothingMode.AntiAlias;
            g.PixelOffsetMode = PixelOffsetMode.HighQuality;

            int r    = Height / 2;
            var rect = new Rectangle(0, 0, Width - 1, Height - 1);

            using (var brush = new SolidBrush(_trackColor))
            using (var path  = BuildRoundRect(rect, r))
                g.FillPath(brush, path);

            if (_maximum > _minimum && _value > _minimum)
            {
                double pct   = (double)(_value - _minimum) / (_maximum - _minimum);
                int    fillW = Math.Max(Height, (int)(Width * pct));
                var    fill  = new Rectangle(0, 0, Math.Min(fillW, Width - 1), Height - 1);

                using (var brush = new SolidBrush(_progressColor))
                using (var path  = BuildRoundRect(fill, r))
                    g.FillPath(brush, path);
            }
        }

        private static GraphicsPath BuildRoundRect(Rectangle r, int radius)
        {
            int d    = radius * 2;
            var path = new GraphicsPath();
            path.AddArc(r.X,          r.Y,          d, d, 180, 90);
            path.AddArc(r.Right - d,  r.Y,          d, d, 270, 90);
            path.AddArc(r.Right - d,  r.Bottom - d, d, d,   0, 90);
            path.AddArc(r.X,          r.Bottom - d, d, d,  90, 90);
            path.CloseFigure();
            return path;
        }
    }
}
