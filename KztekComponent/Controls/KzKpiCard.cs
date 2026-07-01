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
    [Description("KZTEK Design System KPI card — metric value, label, delta indicator.")]
    public class KzKpiCard : Control
    {
        private string          _label       = "Lượt vào hôm nay";
        private string          _value       = "1,284";
        private string          _valueSuffix = string.Empty;
        private string          _delta       = "+12.4%";
        private KzDeltaDirection _deltaDir   = KzDeltaDirection.Up;
        private string          _subtitle    = "so với hôm qua";
        private bool            _isHovered;

        [Category("•KZTEK"), DefaultValue("Lượt vào hôm nay")]
        public string MetricLabel
        {
            get => _label;
            set { _label = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue("1,284")]
        public string MetricValue
        {
            get => _value;
            set { _value = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue("")]
        public string ValueSuffix
        {
            get => _valueSuffix;
            set { _valueSuffix = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue("+12.4%")]
        public string Delta
        {
            get => _delta;
            set { _delta = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(KzDeltaDirection.Up)]
        public KzDeltaDirection DeltaDirection
        {
            get => _deltaDir;
            set { _deltaDir = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue("so với hôm qua")]
        public string Subtitle
        {
            get => _subtitle;
            set { _subtitle = value; Invalidate(); }
        }

        public KzKpiCard()
        {
            SetStyle(ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;
            Size = new Size(240, 130);
            Cursor = Cursors.Hand;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.ClearTypeGridFit;

            var rect = new Rectangle(1, 1, Width - 3, Height - 3);

            // ── Shadow ────────────────────────────────────────
            KzThemeHelper.DrawCardShadow(g, rect, KzTokens.RadiusLg, _isHovered);

            // ── Card background ───────────────────────────────
            using (var bg = new SolidBrush(KzTokens.White))
                KzThemeHelper.FillRoundedRect(g, bg, rect, KzTokens.RadiusLg);

            // ── Border (orange on hover) ───────────────────────
            Color borderColor = _isHovered ? KzTokens.Orange500 : KzTokens.Border;
            using (var pen = new Pen(borderColor, 1f))
                KzThemeHelper.DrawRoundedBorder(g, pen, rect, KzTokens.RadiusLg);

            int pad = 20;
            int x = rect.X + pad;
            int y = rect.Y + pad;

            // ── Orange accent bar ─────────────────────────────
            using (var accentBrush = new SolidBrush(KzTokens.Orange500))
                g.FillRoundedRectangle(accentBrush,
                    new Rectangle(x, y, KzTokens.KpiBarW, KzTokens.KpiBarH), 2);
            y += KzTokens.KpiBarH + 10;

            // ── Label ─────────────────────────────────────────
            using var labelFont = KzThemeHelper.GetFont(KzTokens.FontSm, FontStyle.Bold);
            var labelRect = new Rectangle(x, y, Width - pad * 2, 18);
            using (var brush = new SolidBrush(KzTokens.TextMuted))
                g.DrawString(_label.ToUpper(), labelFont, brush, labelRect);
            y += 22;

            // ── Value ─────────────────────────────────────────
            try
            {
                using var valFont = new Font("Manrope", 28f, FontStyle.Bold, GraphicsUnit.Pixel);
                var valRect = new Rectangle(x, y, Width - pad * 2, 44);
                using (var brush = new SolidBrush(KzTokens.Navy900))
                    g.DrawString(_value, valFont, brush, valRect);

                // Suffix (smaller)
                if (!string.IsNullOrEmpty(_valueSuffix))
                {
                    float mainW = g.MeasureString(_value, valFont).Width;
                    using var sfxFont = KzThemeHelper.GetFont(KzTokens.FontH3);
                    var sfxRect = new Rectangle((int)(x + mainW), y + 14,
                        Width - pad * 2 - (int)mainW, 30);
                    using (var brush = new SolidBrush(KzTokens.TextMuted))
                        g.DrawString(_valueSuffix, sfxFont, brush, sfxRect);
                }
            }
            catch
            {
                using var valFont = KzThemeHelper.GetFont(KzTokens.FontDisplay, FontStyle.Bold);
                var valRect = new Rectangle(x, y, Width - pad * 2, 44);
                using (var brush = new SolidBrush(KzTokens.Navy900))
                    g.DrawString(_value, valFont, brush, valRect);
            }
            y += 46;

            // ── Delta + subtitle ──────────────────────────────
            Color deltaColor = _deltaDir == KzDeltaDirection.Up   ? KzTokens.Success
                             : _deltaDir == KzDeltaDirection.Down  ? KzTokens.Error
                             : KzTokens.TextMuted;

            using var deltaFont = KzThemeHelper.GetFont(KzTokens.FontBody, FontStyle.Bold);
            using var subFont   = KzThemeHelper.GetFont(KzTokens.FontBody);
            string arrow = _deltaDir == KzDeltaDirection.Up   ? "▲ "
                         : _deltaDir == KzDeltaDirection.Down  ? "▼ "
                         : "";

            using (var dBrush = new SolidBrush(deltaColor))
                g.DrawString(arrow + _delta, deltaFont, dBrush, new Point(x, y));

            float dw = g.MeasureString(arrow + _delta, deltaFont).Width;
            using (var sBrush = new SolidBrush(KzTokens.TextMuted))
                g.DrawString("  " + _subtitle, subFont, sBrush, new PointF(x + dw, y));
        }

        protected override void OnMouseEnter(EventArgs e) { _isHovered = true;  Invalidate(); base.OnMouseEnter(e); }
        protected override void OnMouseLeave(EventArgs e) { _isHovered = false; Invalidate(); base.OnMouseLeave(e); }
    }

    // Extension for rounded rectangle on Graphics
    internal static class GraphicsExtensions
    {
        public static void FillRoundedRectangle(this Graphics g, Brush brush, Rectangle rect, int radius)
        {
            using var path = KzThemeHelper.RoundedRect(rect, radius);
            g.FillPath(brush, path);
        }
    }
}

