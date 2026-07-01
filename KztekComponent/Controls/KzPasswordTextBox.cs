using Guna.UI2.WinForms;
using KztekComponent.Theme;
using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace KztekComponent.Controls
{
    /// <summary>
    /// KZTEK Design System password input — eye toggle inside border.
    /// The outer panel draws the border; inner KzTextBox has no border.
    /// </summary>
    [DefaultEvent("TextChanged")]
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK password input with show/hide eye inside the field.")]
    public class KzPasswordTextBox : UserControl
    {
        // ── Inner controls ─────────────────────────────────────────────────────
        private readonly Guna2TextBox _input;
        private readonly Panel        _eye;

        // ── State ──────────────────────────────────────────────────────────────
        private KzInputState _state      = KzInputState.Default;
        private bool         _showPass   = false;
        private bool         _eyeHovered = false;
        private bool         _focused    = false;

        // ── Events ─────────────────────────────────────────────────────────────
        public new event EventHandler TextChanged;

        // ── Properties ────────────────────────────────────────────────────────

        [Category("•KZTEK")]
        [DefaultValue(KzInputState.Default)]
        public KzInputState InputState
        {
            get => _state;
            set { _state = value; ApplyState(); Invalidate(); }
        }

        [Browsable(true)]
        public new string Text
        {
            get => _input.Text;
            set => _input.Text = value;
        }

        [Category("•KZTEK")]
        public string PlaceholderText
        {
            get => _input.PlaceholderText;
            set => _input.PlaceholderText = value;
        }

        [Category("•KZTEK")]
        [DefaultValue(false)]
        public bool ShowPassword
        {
            get => _showPass;
            set { _showPass = value; _input.PasswordChar = _showPass ? '\0' : '●'; _eye.Invalidate(); }
        }

        [Browsable(false)]
        public int SelectionStart
        {
            get => _input.SelectionStart;
            set => _input.SelectionStart = value;
        }

        // ── Constructor ────────────────────────────────────────────────────────

        public KzPasswordTextBox()
        {
            SetStyle(ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);

            BackColor   = KzTokens.White;
            Height      = KzTokens.HeightMd;
            MinimumSize = new Size(120, KzTokens.HeightMd);
            Padding     = new Padding(1); // border inset

            // ── Borderless inner textbox ───────────────────────────────────────
            _input = new Guna2TextBox
            {
                Dock              = DockStyle.Fill,
                PasswordChar      = '●',
                PlaceholderText   = "Nhập mật khẩu",
                BorderThickness   = 0,
                FillColor         = KzTokens.White,
                ShadowDecoration  = { Enabled = false },
                ForeColor         = KzTokens.Ink,
                PlaceholderForeColor = KzTokens.TextMuted,
                Font              = KzThemeHelper.GetFont(KzTokens.FontMd),
                Padding           = new Padding(12, 0, 44, 0),
            };
            _input.TextChanged += (s, e) => TextChanged?.Invoke(this, e);
            _input.GotFocus    += (_, __) => { _focused = true;  Invalidate(); };
            _input.LostFocus   += (_, __) => { _focused = false; Invalidate(); };

            // ── Eye button (transparent, docked right, overlaid) ───────────────
            _eye = new Panel
            {
                Width     = 40,
                Dock      = DockStyle.Right,
                BackColor = Color.Transparent,
                Cursor    = Cursors.Hand,
            };
            _eye.Paint      += OnEyePaint;
            _eye.Click      += OnEyeClick;
            _eye.MouseEnter += (_, __) => { _eyeHovered = true;  _eye.Invalidate(); };
            _eye.MouseLeave += (_, __) => { _eyeHovered = false; _eye.Invalidate(); };

            Controls.Add(_input);
            Controls.Add(_eye);
        }

        // ── Painting ───────────────────────────────────────────────────────────

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;

            bool disabled = _state == KzInputState.Disabled;
            Color bg = disabled ? KzTokens.BgAlt : KzTokens.White;

            var rect = new Rectangle(0, 0, Width - 1, Height - 1);

            // Background
            using (var brush = new SolidBrush(bg))
                KzThemeHelper.FillRoundedRect(g, brush, rect, KzTokens.RadiusMd);

            // Border
            Color border = _state switch
            {
                KzInputState.Error   => KzTokens.Error,
                KzInputState.Disabled => KzTokens.Border,
                KzInputState.Focus   => KzTokens.Orange500,
                _                    => _focused ? KzTokens.Orange500 : KzTokens.Divider,
            };
            float borderW = _focused || _state == KzInputState.Focus ? 2f : 1f;

            using (var pen = new Pen(border, borderW))
                KzThemeHelper.DrawRoundedBorder(g, pen, rect, KzTokens.RadiusMd);
        }

        private void ApplyState()
        {
            bool disabled = _state == KzInputState.Disabled;
            _input.Enabled   = !disabled;
            _input.FillColor = disabled ? KzTokens.BgAlt : KzTokens.White;
            _input.ForeColor = disabled ? KzTokens.TextMuted : KzTokens.Ink;
            BackColor        = disabled ? KzTokens.BgAlt : KzTokens.White;
        }

        // ── Eye icon ───────────────────────────────────────────────────────────

        private void OnEyeClick(object? s, EventArgs e)
        {
            _showPass        = !_showPass;
            _input.PasswordChar = _showPass ? '\0' : '●';
            _eye.Invalidate();
        }

        private void OnEyePaint(object? sender, PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode   = SmoothingMode.AntiAlias;
            g.PixelOffsetMode = PixelOffsetMode.HighQuality;

            float cx = _eye.Width  / 2f;
            float cy = _eye.Height / 2f;
            Color col = _eyeHovered ? KzTokens.Navy900 : KzTokens.TextMuted;

            using var pen = new Pen(col, 1.5f) { LineJoin = LineJoin.Round, StartCap = LineCap.Round, EndCap = LineCap.Round };

            // Eye outline (lens shape)
            using var eyePath = new GraphicsPath();
            eyePath.AddBezier(cx - 10, cy,   cx - 4, cy - 5.5f, cx + 4, cy - 5.5f, cx + 10, cy);
            eyePath.AddBezier(cx + 10, cy,   cx + 4, cy + 5.5f, cx - 4, cy + 5.5f, cx - 10, cy);
            eyePath.CloseFigure();
            g.DrawPath(pen, eyePath);

            if (_showPass)
            {
                // Eye OPEN — filled pupil
                using var fill = new SolidBrush(col);
                g.FillEllipse(fill, cx - 2.8f, cy - 2.8f, 5.6f, 5.6f);
            }
            else
            {
                // Eye CLOSED — pupil + diagonal slash
                using var fill = new SolidBrush(col);
                g.FillEllipse(fill, cx - 2f, cy - 2f, 4f, 4f);
                using var slash = new Pen(col, 1.5f) { StartCap = LineCap.Round, EndCap = LineCap.Round };
                g.DrawLine(slash, cx - 8, cy + 6, cx + 8, cy - 6);
            }
        }

        // ── Resize ─────────────────────────────────────────────────────────────

        protected override void OnSizeChanged(EventArgs e)
        {
            base.OnSizeChanged(e);
            if (_eye   is not null) _eye.Height   = Height;
            if (_input is not null) _input.Height = Height;
        }
    }
}
