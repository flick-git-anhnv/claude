using KztekComponent.Theme;
using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Text;
using System.Windows.Forms;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK circular countdown ring — duration-based, designed for auto-close dialogs/forms.")]
    public class KzRoundCountdown : Control
    {
        // ── Fields ────────────────────────────────────────────
        private int                _duration   = 10;
        private int                _remaining  = 10;
        private KzCountDownVariant _variant    = KzCountDownVariant.Default;
        private bool               _showNumber = true;
        private string             _subLabel   = "giây";
        private float              _trackWidth = 8f;
        private int                _diameter   = 80;
        private bool               _autoStart  = true;
        private bool               _isRunning  = false;
        private bool               _isComplete = false;
        private Control            _targetControl;

        private readonly System.Windows.Forms.Timer _timer;

        // ── Events ────────────────────────────────────────────
        [Category("•KZTEK")]
        [Description("Fires every second while the countdown is running.")]
        public event EventHandler Tick;

        [Category("•KZTEK")]
        [Description("Fires once when the countdown reaches zero.")]
        public event EventHandler Completed;

        // ── Properties ────────────────────────────────────────
        [Category("•KZTEK"), DefaultValue(10)]
        [Description("Total countdown duration in seconds.")]
        public int Duration
        {
            get => _duration;
            set
            {
                _duration   = Math.Max(1, value);
                _remaining  = _duration;
                _isComplete = false;
                Invalidate();
            }
        }

        [Category("•KZTEK"), DefaultValue(KzCountDownVariant.Default)]
        public KzCountDownVariant Variant
        {
            get => _variant;
            set { _variant = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(true)]
        [Description("Show remaining seconds in the center of the ring.")]
        public bool ShowNumber
        {
            get => _showNumber;
            set { _showNumber = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue("giây")]
        [Description("Sub-label shown below the number. Empty string to hide.")]
        public string SubLabel
        {
            get => _subLabel;
            set { _subLabel = value ?? ""; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(8f)]
        [Description("Thickness of the circular ring track in pixels.")]
        public float TrackWidth
        {
            get => _trackWidth;
            set { _trackWidth = Math.Max(2f, Math.Min(value, _diameter / 2f - 4f)); Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(80)]
        [Description("Diameter of the control in pixels. Control size is always Diameter × Diameter.")]
        public int Diameter
        {
            get => _diameter;
            set
            {
                _diameter = Math.Max(40, value);
                Size = new Size(_diameter, _diameter);
                Invalidate();
            }
        }

        [Category("•KZTEK"), DefaultValue(true)]
        [Description("Automatically start countdown when the control loads.")]
        public bool AutoStart
        {
            get => _autoStart;
            set { _autoStart = value; }
        }

        [Category("•KZTEK"), DefaultValue(null)]
        [Description("Any mouse click on this control or its children will reset and restart the countdown.")]
        public Control TargetControl
        {
            get => _targetControl;
            set
            {
                if (_targetControl != null) UnhookTarget(_targetControl);
                _targetControl = value;
                if (_targetControl != null) HookTarget(_targetControl);
            }
        }

        [Browsable(false)]
        public bool IsRunning => _isRunning;

        [Browsable(false)]
        public bool IsComplete => _isComplete;

        [Browsable(false)]
        [Description("Remaining seconds.")]
        public int Remaining => _remaining;

        // ── Constructor ───────────────────────────────────────
        public KzRoundCountdown()
        {
            SetStyle(ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;

            _timer = new System.Windows.Forms.Timer { Interval = 1000 };
            _timer.Tick += OnTimerTick;

            Size = new Size(_diameter, _diameter);
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
                if (_targetControl != null) UnhookTarget(_targetControl);
                _timer.Stop();
                _timer.Dispose();
            }
            base.Dispose(disposing);
        }

        // ── Public API ────────────────────────────────────────
        public void Start()
        {
            if (_isRunning || _isComplete) return;
            _isRunning = true;
            _timer.Start();
        }

        public void Stop()
        {
            _isRunning = false;
            _autoStart = false; // Ngăn việc bị tự động chạy lại khi handle được khởi tạo
            _timer.Stop();
        }

        /// <summary>Reset về Duration ban đầu, không đổi Duration.</summary>
        public void Reset()
        {
            Stop();
            _remaining  = _duration;
            _isComplete = false;
            Invalidate();
        }

        /// <summary>Reset và đặt lại Duration mới (giây).</summary>
        public void Reset(int newDuration)
        {
            Stop();
            _duration   = Math.Max(1, newDuration);
            _remaining  = _duration;
            _isComplete = false;
            Invalidate();
        }

        // ── Target control hooks ──────────────────────────────
        private void HookTarget(Control ctrl)
        {
            ctrl.MouseDown    += OnTargetActivity;
            ctrl.ControlAdded += OnTargetChildAdded;
            foreach (Control child in ctrl.Controls)
                HookTarget(child);
        }

        private void UnhookTarget(Control ctrl)
        {
            ctrl.MouseDown    -= OnTargetActivity;
            ctrl.ControlAdded -= OnTargetChildAdded;
            foreach (Control child in ctrl.Controls)
                UnhookTarget(child);
        }

        private void OnTargetChildAdded(object sender, ControlEventArgs e)
        {
            HookTarget(e.Control);
        }

        private void OnTargetActivity(object sender, MouseEventArgs e)
        {
            Reset();
            Start();
        }

        // ── Internal ──────────────────────────────────────────
        private void OnTimerTick(object sender, EventArgs e)
        {
            // Thêm dòng này để chặn các nhịp Tick "rác" còn sót lại sau khi đã Stop
            if (!_isRunning) return;

            if (_remaining > 0) _remaining--;
            Invalidate();
            Tick?.Invoke(this, EventArgs.Empty);

            if (_remaining == 0)
            {
                _isComplete = true;
                Stop();
                Completed?.Invoke(this, EventArgs.Empty);
            }
        }

        // ── Colors ────────────────────────────────────────────
        private void GetVariantColors(
            out Color trackColor, out Color progressColor,
            out Color numberColor, out Color labelColor)
        {
            switch (_variant)
            {
                case KzCountDownVariant.Accent:
                    trackColor    = KzTokens.Orange300;
                    progressColor = KzTokens.Orange500;
                    numberColor   = KzTokens.Orange500;
                    labelColor    = KzTokens.Orange600;
                    break;
                case KzCountDownVariant.Success:
                    trackColor    = KzTokens.SuccessBg;
                    progressColor = KzTokens.Success;
                    numberColor   = KzTokens.Success;
                    labelColor    = KzTokens.SuccessFg;
                    break;
                case KzCountDownVariant.Danger:
                    trackColor    = KzTokens.ErrorBg;
                    progressColor = KzTokens.Error;
                    numberColor   = KzTokens.Error;
                    labelColor    = KzTokens.ErrorFg;
                    break;
                case KzCountDownVariant.Light:
                    trackColor    = KzTokens.Border;
                    progressColor = KzTokens.Navy300;
                    numberColor   = KzTokens.Navy700;
                    labelColor    = KzTokens.TextMuted;
                    break;
                default: // Default = Navy
                    trackColor    = KzTokens.Navy100;
                    progressColor = KzTokens.Navy900;
                    numberColor   = KzTokens.Navy900;
                    labelColor    = KzTokens.Navy700;
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

            GetVariantColors(out Color trackColor, out Color progressColor,
                             out Color numberColor, out Color labelColor);

            // Arc bounding box — inset by pen half-width so the stroke stays within bounds
            int pad     = (int)Math.Ceiling(_trackWidth / 2f) + 1;
            var arcRect = new RectangleF(pad, pad, _diameter - pad * 2f - 1f, _diameter - pad * 2f - 1f);

            // ── Track (full background ring) ──────────────────
            using (var trackPen = new Pen(trackColor, _trackWidth)
                { StartCap = LineCap.Round, EndCap = LineCap.Round })
            {
                g.DrawEllipse(trackPen, arcRect);
            }

            // ── Progress arc (depletes clockwise) ─────────────
            // sweepAngle = 360 * fraction remaining → full at start, zero at end
            float progress   = _duration > 0 ? (float)_remaining / _duration : 0f;
            float sweepAngle = 360f * progress;

            if (sweepAngle > 0.5f)
            {
                using (var progressPen = new Pen(progressColor, _trackWidth)
                    { StartCap = LineCap.Round, EndCap = LineCap.Round })
                {
                    g.DrawArc(progressPen, arcRect, -90f, -sweepAngle);
                }
            }

            // ── Center text ───────────────────────────────────
            if (_showNumber)
            {
                // Scale number font proportionally to inner diameter
                float innerD    = _diameter - _trackWidth * 2f - 12f;
                float numFontSz = Math.Max(12f, innerD * 0.35f);
                bool  hasLabel  = !string.IsNullOrEmpty(_subLabel) && _diameter >= 60;

                float numH   = numFontSz * 1.25f;
                float lblH   = hasLabel ? KzTokens.FontXs * 1.4f : 0f;
                float totalH = numH + lblH;
                float startY = (_diameter - totalH) / 2f;

                var centerFmt = new StringFormat
                {
                    Alignment     = StringAlignment.Center,
                    LineAlignment = StringAlignment.Center
                };

                using var numFont  = KzThemeHelper.GetFont(numFontSz, FontStyle.Bold);
                using var numBrush = new SolidBrush(numberColor);
                g.DrawString(_remaining.ToString(), numFont, numBrush,
                    new RectangleF(0f, startY, _diameter, numH), centerFmt);

                if (hasLabel)
                {
                    using var lblFont  = KzThemeHelper.GetFont(KzTokens.FontXs, FontStyle.Regular);
                    using var lblBrush = new SolidBrush(labelColor);
                    g.DrawString(_subLabel, lblFont, lblBrush,
                        new RectangleF(0f, startY + numH, _diameter, lblH), centerFmt);
                }
            }
        }

        protected override void OnResize(EventArgs e) { base.OnResize(e); Invalidate(); }
    }
}
