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
    [Description("KZTEK Design System card panel — Default, Dark (navy), Feature variants.")]
    public class KzCard : Panel
    {
        private KzCardVariant _variant = KzCardVariant.Default;
        private bool          _isHovered;
        private bool          _elevated;  // show elevated shadow (hover state)
        private string        _cardTitle = string.Empty;
        private string        _cardText  = string.Empty;
        private Image         _featureIcon;

        [Category("•KZTEK"), DefaultValue(KzCardVariant.Default)]
        public KzCardVariant CardVariant
        {
            get => _variant;
            set { _variant = value; ApplyStyle(); Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue("")]
        public string CardTitle
        {
            get => _cardTitle;
            set { _cardTitle = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue("")]
        public string CardText
        {
            get => _cardText;
            set { _cardText = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(null)]
        public Image FeatureIcon
        {
            get => _featureIcon;
            set { _featureIcon = value; Invalidate(); }
        }

        public KzCard()
        {
            SetStyle(ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);
            Size = new Size(280, 160);
            Padding = new Padding(20);
            ApplyStyle();
        }

        private void ApplyStyle()
        {
            BackColor = Color.Transparent;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.ClearTypeGridFit;

            var rect = new Rectangle(1, 1, Width - 3, Height - 3);
            bool dark = _variant == KzCardVariant.Dark;

            // ── Shadow ────────────────────────────────────────
            KzThemeHelper.DrawCardShadow(g, rect, KzTokens.RadiusLg, _isHovered);

            // ── Background ────────────────────────────────────
            Color bgColor = dark ? KzTokens.Navy900 : KzTokens.White;
            using (var brush = new SolidBrush(bgColor))
                KzThemeHelper.FillRoundedRect(g, brush, rect, KzTokens.RadiusLg);

            // ── Border ────────────────────────────────────────
            Color borderColor = _isHovered ? KzTokens.Orange500 : KzTokens.Border;
            if (dark) borderColor = Color.Transparent;
            if (borderColor != Color.Transparent)
                using (var pen = new Pen(borderColor, 1f))
                    KzThemeHelper.DrawRoundedBorder(g, pen, rect, KzTokens.RadiusLg);

            // ── Content area ──────────────────────────────────
            var content = new Rectangle(
                rect.X + 20, rect.Y + 18,
                rect.Width - 40, rect.Height - 36);

            int y = content.Y;

            // Feature icon box
            if (_variant == KzCardVariant.Feature && _featureIcon != null)
            {
                var iconRect = new Rectangle(content.X, y, 36, 36);
                using (var iconBg = new SolidBrush(Color.FromArgb(31, KzTokens.Orange500)))
                    KzThemeHelper.FillRoundedRect(g, iconBg, iconRect, KzTokens.RadiusMd);
                g.DrawImage(_featureIcon, new Rectangle(iconRect.X + 8, iconRect.Y + 8, 20, 20));
                y += 48;
            }

            // Title
            if (!string.IsNullOrEmpty(_cardTitle))
            {
                using var titleFont = KzThemeHelper.GetFont(KzTokens.FontLg, FontStyle.Bold);
                Color titleColor = dark ? KzTokens.White : KzTokens.Navy900;
                var titleRect = new Rectangle(content.X, y, content.Width, 28);
                KzThemeHelper.DrawCenteredText(g, _cardTitle, titleFont, titleColor,
                    titleRect, StringAlignment.Near);
                y += 36;
            }

            // Body text
            if (!string.IsNullOrEmpty(_cardText))
            {
                using var bodyFont = KzThemeHelper.GetFont(KzTokens.FontBody);
                Color bodyColor = dark ? KzTokens.Navy300 : KzTokens.Text;
                var bodyRect = new Rectangle(content.X, y, content.Width, content.Bottom - y);
                using var brush = new SolidBrush(bodyColor);
                var fmt = new StringFormat { Trimming = StringTrimming.EllipsisWord };
                g.DrawString(_cardText, bodyFont, brush, bodyRect, fmt);
            }
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
