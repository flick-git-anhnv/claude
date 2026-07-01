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
    [Description("KZTEK picture box — Rectangle, Rounded, and Circle shapes with captions and placeholder.")]
    public class KzPictureBox : Control
    {
        private Image                  _image;
        private KzPictureSizeMode      _sizeMode       = KzPictureSizeMode.Zoom;
        private KzPictureShape         _shape          = KzPictureShape.Rounded;
        private int                    _cornerRadius   = 12;
        private KzPictureBorderVariant _borderVariant  = KzPictureBorderVariant.Default;
        private float                  _borderWidth    = 1.5f;
        private bool                   _showShadow     = true;
        private string                 _caption        = string.Empty;
        private KzCaptionPosition      _captionPos     = KzCaptionPosition.None;
        private string                 _placeholderText = "No image";
        private bool                   _isHovered;

        // ── Properties ────────────────────────────────────────

        [Category("•KZTEK"), DefaultValue(null)]
        public Image Image
        {
            get => _image;
            set { _image = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(KzPictureSizeMode.Zoom)]
        public KzPictureSizeMode SizeMode
        {
            get => _sizeMode;
            set { _sizeMode = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(KzPictureShape.Rounded)]
        public KzPictureShape Shape
        {
            get => _shape;
            set { _shape = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(12)]
        public int CornerRadius
        {
            get => _cornerRadius;
            set { _cornerRadius = Math.Max(0, value); Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(KzPictureBorderVariant.Default)]
        public KzPictureBorderVariant BorderVariant
        {
            get => _borderVariant;
            set { _borderVariant = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(1.5f)]
        public float BorderWidth
        {
            get => _borderWidth;
            set { _borderWidth = Math.Max(0f, value); Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(true)]
        public bool ShowShadow
        {
            get => _showShadow;
            set { _showShadow = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue("")]
        public string Caption
        {
            get => _caption;
            set { _caption = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(KzCaptionPosition.None)]
        public KzCaptionPosition CaptionPosition
        {
            get => _captionPos;
            set { _captionPos = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue("No image")]
        public string PlaceholderText
        {
            get => _placeholderText;
            set { _placeholderText = value; Invalidate(); }
        }

        // ── Constructor ───────────────────────────────────────

        public KzPictureBox()
        {
            SetStyle(ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;
            Size = new Size(200, 150);
        }

        // ── Paint ─────────────────────────────────────────────

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode      = SmoothingMode.AntiAlias;
            g.InterpolationMode  = InterpolationMode.HighQualityBicubic;
            g.PixelOffsetMode    = PixelOffsetMode.HighQuality;

            var rect = new Rectangle(2, 2, Width - 4, Height - 4);

            if (_showShadow && _borderVariant != KzPictureBorderVariant.None)
                KzThemeHelper.DrawCardShadow(g, rect, GetRadius(rect), _isHovered);

            using var clipPath = BuildShapePath(rect);
            g.SetClip(clipPath);

            using (var bg = new SolidBrush(KzTokens.BgAlt))
                g.FillPath(bg, clipPath);

            if (_image != null)
                PaintImage(g, rect);
            else
                PaintPlaceholder(g, rect);

            if (!string.IsNullOrEmpty(_caption) && _captionPos != KzCaptionPosition.None)
                PaintCaption(g, rect);

            g.ResetClip();

            if (_borderVariant != KzPictureBorderVariant.None && _borderWidth > 0f)
            {
                var borderColor = ResolveBorderColor();
                using var pen  = new Pen(borderColor, _borderWidth);
                using var path = BuildShapePath(rect);
                g.DrawPath(pen, path);
            }
        }

        // ── Image drawing ─────────────────────────────────────

        private void PaintImage(Graphics g, Rectangle rect)
        {
            if (_sizeMode == KzPictureSizeMode.Tile)
            {
                using var tb = new TextureBrush(_image, WrapMode.Tile);
                g.FillRectangle(tb, rect);
                return;
            }
            g.DrawImage(_image, CalcDestRect(rect, _image.Width, _image.Height));
        }

        private Rectangle CalcDestRect(Rectangle bounds, int imgW, int imgH)
        {
            switch (_sizeMode)
            {
                case KzPictureSizeMode.Stretch:
                    return bounds;

                case KzPictureSizeMode.Center:
                    return new Rectangle(
                        bounds.X + (bounds.Width  - imgW) / 2,
                        bounds.Y + (bounds.Height - imgH) / 2,
                        imgW, imgH);

                case KzPictureSizeMode.Fill:
                {
                    float s = Math.Max((float)bounds.Width / imgW, (float)bounds.Height / imgH);
                    int   w = (int)(imgW * s), h = (int)(imgH * s);
                    return new Rectangle(
                        bounds.X + (bounds.Width  - w) / 2,
                        bounds.Y + (bounds.Height - h) / 2,
                        w, h);
                }

                default: // Zoom
                {
                    float s = Math.Min((float)bounds.Width / imgW, (float)bounds.Height / imgH);
                    int   w = (int)(imgW * s), h = (int)(imgH * s);
                    return new Rectangle(
                        bounds.X + (bounds.Width  - w) / 2,
                        bounds.Y + (bounds.Height - h) / 2,
                        w, h);
                }
            }
        }

        // ── Placeholder ───────────────────────────────────────

        private void PaintPlaceholder(Graphics g, Rectangle rect)
        {
            int iconW = Math.Clamp(rect.Width / 4, 24, 56);
            int iconH = (int)(iconW * 0.68f);
            int cx    = rect.X + rect.Width  / 2;
            int cy    = rect.Y + rect.Height / 2 - (string.IsNullOrEmpty(_placeholderText) ? 0 : 10);

            var body = new Rectangle(cx - iconW / 2, cy - iconH / 2, iconW, iconH);

            using var pen = new Pen(KzTokens.Navy300, 1.5f) { LineJoin = LineJoin.Round };

            // Camera body
            KzThemeHelper.DrawRoundedBorder(g, pen, body, 3);

            // Lens circle
            int ld = iconH / 2;
            g.DrawEllipse(pen,
                cx - ld / 2,
                body.Y + (body.Height - ld) / 2,
                ld, ld);

            // Viewfinder bump at top-center
            int bw = ld / 2 + 1, bh = Math.Max(3, iconH / 5);
            var bump = new Rectangle(cx - bw / 2, body.Y - bh, bw, bh);
            using (var fill = new SolidBrush(KzTokens.BgAlt))
                g.FillRectangle(fill, bump);
            KzThemeHelper.DrawRoundedBorder(g, pen, bump, 2);

            // Placeholder label
            if (!string.IsNullOrEmpty(_placeholderText))
            {
                using var font  = KzThemeHelper.GetFont(KzTokens.FontSm);
                var textRect    = new Rectangle(rect.X + 8, body.Bottom + 8, rect.Width - 16, 20);
                KzThemeHelper.DrawCenteredText(g, _placeholderText, font, KzTokens.Navy300, textRect);
            }
        }

        // ── Caption overlay ───────────────────────────────────

        private void PaintCaption(Graphics g, Rectangle rect)
        {
            const int h = 36;
            var capRect = _captionPos == KzCaptionPosition.Top
                ? new Rectangle(rect.X, rect.Y,          rect.Width, h)
                : new Rectangle(rect.X, rect.Bottom - h, rect.Width, h);

            using var overlay = new SolidBrush(Color.FromArgb(160, KzTokens.Navy900));
            g.FillRectangle(overlay, capRect);

            using var font = KzThemeHelper.GetFont(KzTokens.FontSm);
            KzThemeHelper.DrawCenteredText(g, _caption, font, KzTokens.White, capRect);
        }

        // ── Shape helpers ─────────────────────────────────────

        private GraphicsPath BuildShapePath(Rectangle rect)
        {
            switch (_shape)
            {
                case KzPictureShape.Circle:
                {
                    int d  = Math.Min(rect.Width, rect.Height);
                    var cr = new Rectangle(
                        rect.X + (rect.Width  - d) / 2,
                        rect.Y + (rect.Height - d) / 2,
                        d, d);
                    var p = new GraphicsPath();
                    p.AddEllipse(cr);
                    return p;
                }
                case KzPictureShape.Rounded:
                    return KzThemeHelper.RoundedRect(rect, _cornerRadius);
                default:
                {
                    var p = new GraphicsPath();
                    p.AddRectangle(rect);
                    return p;
                }
            }
        }

        private int GetRadius(Rectangle rect) => _shape switch
        {
            KzPictureShape.Circle  => Math.Min(rect.Width, rect.Height) / 2,
            KzPictureShape.Rounded => _cornerRadius,
            _                      => 0
        };

        private Color ResolveBorderColor()
        {
            if (_isHovered && _borderVariant == KzPictureBorderVariant.Default)
                return KzTokens.Orange500;
            return _borderVariant switch
            {
                KzPictureBorderVariant.Navy   => KzTokens.Navy700,
                KzPictureBorderVariant.Accent => KzTokens.Orange500,
                _                             => KzTokens.Border
            };
        }

        // ── Mouse ─────────────────────────────────────────────

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
