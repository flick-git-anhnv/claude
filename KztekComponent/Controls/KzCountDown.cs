using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Text;
using System.Windows.Forms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK countdown timer — segmented cards for Days, Hours, Minutes, Seconds.")]
    public class KzCountDown : Control
    {
        // ── Constants ─────────────────────────────────────────
        private const int LabelHeight = 18;
        private const int SepWidth    = 18; // colon-dot separator width
        private const int GapWidth    = 6;  // gap when separators are hidden

        // ── Fields ────────────────────────────────────────────
        private DateTime           _targetDateTime  = DateTime.Now.AddDays(1);
        private KzCountDownVariant _variant         = KzCountDownVariant.Default;
        private KzCountDownMode    _mode            = KzCountDownMode.Full;
        private bool               _showLabels      = true;
        private bool               _showSeparators  = true;
        private bool               _blinkSeparators = false;
        private bool               _autoStart       = true;
        private int                _segmentWidth    = 72;
        private int                _segmentHeight   = 76;

        private bool _isRunning  = false;
        private bool _isComplete = false;
        private bool _sepVisible = true; // toggles for blink effect

        private readonly System.Windows.Forms.Timer _timer;

        // ── Events ────────────────────────────────────────────
        [Category("•KZTEK")]
        [Description("Fires every second while the countdown is running.")]
        public event EventHandler Tick;

        [Category("•KZTEK")]
        [Description("Fires once when the countdown reaches zero.")]
        public event EventHandler Completed;

        // ── Properties ────────────────────────────────────────
        [Category("•KZTEK")]
        [Description("Target date and time the countdown counts down to.")]
        public DateTime TargetDateTime
        {
            get => _targetDateTime;
            set { _targetDateTime = value; _isComplete = false; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(KzCountDownVariant.Default)]
        public KzCountDownVariant Variant
        {
            get => _variant;
            set { _variant = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(KzCountDownMode.Full)]
        [Description("Full = D:H:M:S | TimeOnly = Total-H:M:S | Compact = Total-M:S")]
        public KzCountDownMode Mode
        {
            get => _mode;
            set { _mode = value; RecalcSize(); Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(true)]
        [Description("Show NGÀY/GIỜ/PHÚT/GIÂY labels beneath each segment.")]
        public bool ShowLabels
        {
            get => _showLabels;
            set { _showLabels = value; RecalcSize(); Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(true)]
        [Description("Show colon dot separators between segments.")]
        public bool ShowSeparators
        {
            get => _showSeparators;
            set { _showSeparators = value; RecalcSize(); Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(false)]
        [Description("Blink separator dots on each tick (every second).")]
        public bool BlinkSeparators
        {
            get => _blinkSeparators;
            set { _blinkSeparators = value; }
        }

        [Category("•KZTEK"), DefaultValue(true)]
        [Description("Automatically start the countdown when the control loads.")]
        public bool AutoStart
        {
            get => _autoStart;
            set { _autoStart = value; }
        }

        [Category("•KZTEK"), DefaultValue(72)]
        [Description("Width in pixels of each digit segment card.")]
        public int SegmentWidth
        {
            get => _segmentWidth;
            set { _segmentWidth = Math.Max(40, value); RecalcSize(); Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(76)]
        [Description("Height in pixels of each digit segment card.")]
        public int SegmentHeight
        {
            get => _segmentHeight;
            set { _segmentHeight = Math.Max(32, value); RecalcSize(); Invalidate(); }
        }

        [Browsable(false)]
        public bool IsRunning => _isRunning;

        [Browsable(false)]
        public bool IsComplete => _isComplete;

        [Browsable(false)]
        public TimeSpan Remaining
        {
            get
            {
                var ts = _targetDateTime - DateTime.Now;
                return ts < TimeSpan.Zero ? TimeSpan.Zero : ts;
            }
        }

        // ── Constructor ───────────────────────────────────────
        public KzCountDown()
        {
            SetStyle(ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;

            _timer = new System.Windows.Forms.Timer { Interval = 1000 };
            _timer.Tick += OnTimerTick;

            RecalcSize();
        }

        // ── Lifecycle ─────────────────────────────────────────
        protected override void OnHandleCreated(EventArgs e)
        {
            base.OnHandleCreated(e);
            if (_autoStart && !_isComplete)
                Start();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _timer.Stop();
                _timer.Dispose();
            }
            base.Dispose(disposing);
        }

        // ── Public API ────────────────────────────────────────
        public void Start()
        {
            if (_isRunning || _isComplete) return;
            if (_targetDateTime <= DateTime.Now) return;
            _isRunning = true;
            _timer.Start();
        }

        public void Stop()
        {
            _isRunning = false;
            _timer.Stop();
        }

        public void Reset()
        {
            Stop();
            _isComplete = false;
            _sepVisible = true;
            Invalidate();
        }

        public void Reset(DateTime newTarget)
        {
            Stop();
            _targetDateTime = newTarget;
            _isComplete = false;
            _sepVisible = true;
            Invalidate();
        }

        // ── Internal timer ────────────────────────────────────
        private void OnTimerTick(object sender, EventArgs e)
        {
            _sepVisible = !_sepVisible;
            Invalidate();
            Tick?.Invoke(this, EventArgs.Empty);

            if (Remaining == TimeSpan.Zero)
            {
                _isComplete = true;
                Stop();
                Completed?.Invoke(this, EventArgs.Empty);
            }
        }

        // ── Size ──────────────────────────────────────────────
        private void RecalcSize()
        {
            int n    = SegmentCount();
            int sepW = _showSeparators ? SepWidth : GapWidth;
            int w    = n * _segmentWidth + (n - 1) * sepW;
            int h    = _segmentHeight + (_showLabels ? LabelHeight : 0);
            Size = new Size(w, h);
        }

        private int SegmentCount() => _mode switch
        {
            KzCountDownMode.Compact  => 2,
            KzCountDownMode.TimeOnly => 3,
            _                        => 4
        };

        private (int val, string lbl)[] GetSegments()
        {
            var rem = Remaining;
            switch (_mode)
            {
                case KzCountDownMode.Compact:
                    return new[]
                    {
                        ((int)rem.TotalMinutes, "Phút"),
                        (rem.Seconds,           "Giây")
                    };
                case KzCountDownMode.TimeOnly:
                    return new[]
                    {
                        ((int)rem.TotalHours, "Giờ"),
                        (rem.Minutes,         "Phút"),
                        (rem.Seconds,         "Giây")
                    };
                default:
                    return new[]
                    {
                        ((int)rem.TotalDays, "Ngày"),
                        (rem.Hours,          "Giờ"),
                        (rem.Minutes,        "Phút"),
                        (rem.Seconds,        "Giây")
                    };
            }
        }

        // ── Colors ────────────────────────────────────────────
        private void GetVariantColors(
            out Color cardBg, out Color cardBgLight,
            out Color cardFg, out Color labelFg, out Color sepColor)
        {
            switch (_variant)
            {
                case KzCountDownVariant.Accent:
                    cardBg      = KzTokens.Orange500;
                    cardBgLight = KzTokens.Orange600;
                    cardFg      = KzTokens.White;
                    labelFg     = KzTokens.Orange300;
                    sepColor    = KzTokens.Orange300;
                    break;
                case KzCountDownVariant.Success:
                    cardBg      = KzTokens.Success;
                    cardBgLight = Color.FromArgb(0x0E, 0x8A, 0x3C);
                    cardFg      = KzTokens.White;
                    labelFg     = KzTokens.SuccessBg;
                    sepColor    = KzTokens.SuccessBg;
                    break;
                case KzCountDownVariant.Danger:
                    cardBg      = KzTokens.Error;
                    cardBgLight = Color.FromArgb(0xBF, 0x1C, 0x1C);
                    cardFg      = KzTokens.White;
                    labelFg     = KzTokens.ErrorBg;
                    sepColor    = KzTokens.ErrorBg;
                    break;
                case KzCountDownVariant.Light:
                    cardBg      = KzTokens.Navy100;
                    cardBgLight = KzTokens.White;
                    cardFg      = KzTokens.Navy900;
                    labelFg     = KzTokens.Navy700;
                    sepColor    = KzTokens.Navy300;
                    break;
                default: // Default = Navy
                    cardBg      = KzTokens.Navy900;
                    cardBgLight = KzTokens.Navy1000;
                    cardFg      = KzTokens.White;
                    labelFg     = KzTokens.Navy300;
                    sepColor    = KzTokens.Navy300;
                    break;
            }
        }

        // ── Paint ─────────────────────────────────────────────
        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode     = SmoothingMode.AntiAlias;
            g.TextRenderingHint = TextRenderingHint.ClearTypeGridFit;
            g.PixelOffsetMode   = PixelOffsetMode.HighQuality;

            GetVariantColors(out Color cardBg, out Color cardBgLight,
                             out Color cardFg, out Color labelFg, out Color sepColor);

            var segs   = GetSegments();
            int sepW   = _showSeparators ? SepWidth : GapWidth;
            int cardH  = _segmentHeight;
            int labelH = _showLabels ? LabelHeight : 0;
            int x      = 0;

            for (int i = 0; i < segs.Length; i++)
            {
                DrawSegment(g, x, cardH, labelH, segs[i].val, segs[i].lbl,
                            cardBg, cardBgLight, cardFg, labelFg);
                x += _segmentWidth;

                if (i < segs.Length - 1)
                {
                    if (_showSeparators)
                    {
                        bool draw = !_blinkSeparators || _sepVisible;
                        if (draw) DrawSeparatorDots(g, x, cardH, sepColor);
                    }
                    x += sepW;
                }
            }
        }

        private void DrawSegment(Graphics g, int x, int cardH, int labelH,
            int value, string label,
            Color cardBg, Color cardBgLight, Color cardFg, Color labelFg)
        {
            var cardRect = new Rectangle(x, 0, _segmentWidth - 1, cardH - 1);

            // Shadow
            KzThemeHelper.DrawCardShadow(g, cardRect, KzTokens.RadiusMd);

            // Gradient fill — top darker, bottom lighter
            using (var grad = new LinearGradientBrush(
                new Rectangle(cardRect.X, cardRect.Y, cardRect.Width + 1, cardRect.Height + 1),
                cardBgLight, cardBg, LinearGradientMode.Vertical))
            {
                KzThemeHelper.FillRoundedRect(g, grad, cardRect, KzTokens.RadiusMd);
            }

            // Number
            float fontSize = Math.Max(12f, _segmentHeight * 0.35f);
            using var numFont  = KzThemeHelper.GetFont(fontSize, FontStyle.Bold);
            using var numBrush = new SolidBrush(cardFg);
            var numFmt = new StringFormat
            {
                Alignment     = StringAlignment.Center,
                LineAlignment = StringAlignment.Center,
                Trimming      = StringTrimming.None
            };
            g.DrawString(value.ToString("D2"), numFont, numBrush,
                new RectangleF(x, 0, _segmentWidth, cardH), numFmt);

            // Label
            if (labelH > 0)
            {
                using var lblFont  = KzThemeHelper.GetFont(KzTokens.FontXs, FontStyle.Regular);
                using var lblBrush = new SolidBrush(labelFg);
                var lblFmt = new StringFormat
                {
                    Alignment     = StringAlignment.Center,
                    LineAlignment = StringAlignment.Center
                };
                g.DrawString(label.ToUpper(), lblFont, lblBrush,
                    new RectangleF(x, cardH, _segmentWidth, labelH), lblFmt);
            }
        }

        private void DrawSeparatorDots(Graphics g, int x, int cardH, Color color)
        {
            int dotSize = 5;
            int cx      = x + SepWidth / 2 - dotSize / 2;
            int y1      = cardH / 3 - dotSize / 2;
            int y2      = 2 * cardH / 3 - dotSize / 2;
            using var brush = new SolidBrush(color);
            g.FillEllipse(brush, cx, y1, dotSize, dotSize);
            g.FillEllipse(brush, cx, y2, dotSize, dotSize);
        }

        protected override void OnResize(EventArgs e) { base.OnResize(e); Invalidate(); }
    }
}
