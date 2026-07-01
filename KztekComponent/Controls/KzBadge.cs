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
    [Description("KZTEK Design System badge — Status pill, Tag variants.")]
    public class KzBadge : Control
    {
        private KzBadgeVariant _variant = KzBadgeVariant.Success;
        private KzBadgeType    _type    = KzBadgeType.StatusPill;
        private bool           _showDot = true;
        private string         _text    = "Đang hoạt động";
        private bool           _isHovered;

        [Category("•KZTEK"), DefaultValue(KzBadgeVariant.Success)]
        public KzBadgeVariant BadgeVariant
        {
            get => _variant;
            set { _variant = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(KzBadgeType.StatusPill)]
        public KzBadgeType BadgeType
        {
            get => _type;
            set { _type = value; Invalidate(); SizeToContent(); }
        }

        [Category("•KZTEK"), DefaultValue(true)]
        public bool ShowDot
        {
            get => _showDot;
            set { _showDot = value; Invalidate(); SizeToContent(); }
        }

        [Category("•KZTEK"), DefaultValue("Đang hoạt động")]
        public override string Text
        {
            get => _text;
            set { _text = value; SizeToContent(); Invalidate(); }
        }

        public KzBadge()
        {
            SetStyle(ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;
            Cursor = Cursors.Default;
            SizeToContent();
        }

        private void GetColors(out Color bg, out Color fg, out Color border)
        {
            switch (_variant)
            {
                case KzBadgeVariant.Warning:
                    bg = KzTokens.WarningBg; fg = KzTokens.WarningFg; border = KzTokens.Warning; break;
                case KzBadgeVariant.Error:
                    bg = KzTokens.ErrorBg;   fg = KzTokens.ErrorFg;   border = KzTokens.Error;   break;
                case KzBadgeVariant.Info:
                    bg = KzTokens.InfoBg;    fg = KzTokens.InfoFg;    border = KzTokens.Info;    break;
                case KzBadgeVariant.Neutral:
                    bg = Color.FromArgb(102, KzTokens.Navy300); fg = KzTokens.Navy900; border = Color.Transparent; break;
                case KzBadgeVariant.Accent:
                    bg = KzTokens.Orange300; fg = KzTokens.Navy1000;  border = Color.Transparent; break;
                default: // Success
                    bg = KzTokens.SuccessBg; fg = KzTokens.SuccessFg; border = KzTokens.Success; break;
            }
        }

        private Color GetDotColor()
        {
            switch (_variant)
            {
                case KzBadgeVariant.Warning: return KzTokens.Warning;
                case KzBadgeVariant.Error:   return KzTokens.Error;
                case KzBadgeVariant.Info:    return KzTokens.Info;
                default:                     return KzTokens.Success;
            }
        }

        private void SizeToContent()
        {
            using var g = CreateGraphics();
            Font font = _type == KzBadgeType.Tag
                ? KzThemeHelper.GetFont(KzTokens.FontXs, FontStyle.Bold)
                : KzThemeHelper.GetFont(KzTokens.FontSm, FontStyle.Bold);

            var textSize = g.MeasureString(_text, font);
            int padH = _type == KzBadgeType.Tag ? 8 : 12;
            int padV = _type == KzBadgeType.Tag ? 3 : 5;
            int dotSpace = (_type == KzBadgeType.StatusPill && _showDot) ? 16 : 0;

            int w = (int)textSize.Width + padH * 2 + dotSpace;
            int h = (int)textSize.Height + padV * 2;
            Size = new Size(Math.Max(w, 40), Math.Max(h, 20));
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.ClearTypeGridFit;

            GetColors(out Color bg, out Color fg, out Color border);

            var rect = new Rectangle(0, 0, Width - 1, Height - 1);

            // ── Background ────────────────────────────────────
            if (_type == KzBadgeType.Tag)
            {
                // Tag: hover → orange fill
                Color fillBg = _isHovered ? KzTokens.Orange500 : KzTokens.Navy100;
                Color fillFg = _isHovered ? KzTokens.White : KzTokens.Navy700;
                Color fillBorder = _isHovered ? KzTokens.Orange500 : KzTokens.Border;

                using (var brush = new SolidBrush(fillBg))
                    KzThemeHelper.FillRoundedRect(g, brush, rect, KzTokens.RadiusSm);
                using (var pen = new Pen(fillBorder))
                    KzThemeHelper.DrawRoundedBorder(g, pen, rect, KzTokens.RadiusSm);

                using var fgBrush = new SolidBrush(fillFg);
                using var font = KzThemeHelper.GetFont(KzTokens.FontXs, FontStyle.Bold);
                KzThemeHelper.DrawCenteredText(g, _text, font, fillFg, rect);
            }
            else
            {
                // StatusPill
                using (var brush = new SolidBrush(bg))
                    KzThemeHelper.FillRoundedRect(g, brush, rect, KzTokens.RadiusPill);

                if (border != Color.Transparent)
                    using (var pen = new Pen(border))
                        KzThemeHelper.DrawRoundedBorder(g, pen, rect, KzTokens.RadiusPill);

                using var font = KzThemeHelper.GetFont(KzTokens.FontSm, FontStyle.Bold);

                int x = 12;
                if (_showDot && _variant != KzBadgeVariant.Neutral && _variant != KzBadgeVariant.Accent)
                {
                    // Draw status dot
                    int dotSize = 6;
                    int dotY = (Height - dotSize) / 2;
                    using (var dotBrush = new SolidBrush(GetDotColor()))
                        g.FillEllipse(dotBrush, x, dotY, dotSize, dotSize);
                    x += dotSize + 6;
                }

                // Draw text
                var textRect = new Rectangle(x, 0, Width - x - 8, Height);
                using var fgBrush = new SolidBrush(fg);
                var fmt = new StringFormat
                {
                    LineAlignment = StringAlignment.Center,
                    Alignment = StringAlignment.Near,
                    Trimming = StringTrimming.EllipsisCharacter
                };
                g.DrawString(_text, font, fgBrush, textRect, fmt);
            }
        }

        protected override void OnMouseEnter(EventArgs e) { _isHovered = true;  Invalidate(); base.OnMouseEnter(e); }
        protected override void OnMouseLeave(EventArgs e) { _isHovered = false; Invalidate(); base.OnMouseLeave(e); }
        protected override void OnResize(EventArgs e)     { base.OnResize(e); Invalidate(); }
    }
}

