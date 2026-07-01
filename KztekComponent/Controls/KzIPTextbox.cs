using KztekComponent.Theme;
using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace KztekComponent.Controls
{
    [DefaultEvent("IPAddressChanged")]
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK IP address input — 4 octets with auto-advance and 0-255 validation.")]
    public class KzIPTextbox : UserControl
    {
        private readonly TextBox[] _octets = new TextBox[4];
        private readonly Label[]   _dots   = new Label[3];

        private KzInputState _state       = KzInputState.Default;
        private bool         _focused     = false;
        private bool         _suppressEvt = false;

        public event EventHandler IPAddressChanged;

        // ── Properties ─────────────────────────────────────────────────────────

        [Category("•KZTEK")]
        [Description("Input state (Default, Error, Disabled). Focus is automatic.")]
        [DefaultValue(KzInputState.Default)]
        public KzInputState InputState
        {
            get => _state;
            set { _state = value; ApplyState(); Invalidate(); }
        }

        [Category("•KZTEK")]
        [Description("Get or set the IP address (e.g. '192.168.1.1'). Set to empty string to clear.")]
        public string IPAddress
        {
            get => $"{_octets[0].Text}.{_octets[1].Text}.{_octets[2].Text}.{_octets[3].Text}";
            set
            {
                var parts = (value ?? "").Split('.');
                for (int i = 0; i < 4; i++)
                    _octets[i].Text = (i < parts.Length) ? parts[i] : "";
            }
        }

        [Browsable(false)]
        [Description("Returns true when all 4 octets are valid integers in the range 0–255.")]
        public bool IsValid
        {
            get
            {
                foreach (var o in _octets)
                    if (!int.TryParse(o.Text, out int v) || v < 0 || v > 255) return false;
                return true;
            }
        }

        // ── Constructor ────────────────────────────────────────────────────────

        public KzIPTextbox()
        {
            SetStyle(
                ControlStyles.UserPaint |
                ControlStyles.OptimizedDoubleBuffer |
                ControlStyles.AllPaintingInWmPaint |
                ControlStyles.ResizeRedraw |
                ControlStyles.SupportsTransparentBackColor, true);

            BackColor   = KzTokens.White;
            Height      = KzTokens.HeightMd;
            Width       = 210;
            MinimumSize = new Size(160, KzTokens.HeightMd);
            Padding     = new Padding(1);

            BuildOctets();

            Enter += (s, e) => { _focused = true;  Invalidate(); };
            Leave += (s, e) => { _focused = false; Invalidate(); };
        }

        // ── Build ──────────────────────────────────────────────────────────────

        private void BuildOctets()
        {
            for (int i = 0; i < 4; i++)
            {
                int idx = i;
                var tb = new TextBox
                {
                    BorderStyle = BorderStyle.None,
                    MaxLength   = 3,
                    TextAlign   = HorizontalAlignment.Center,
                    BackColor   = KzTokens.White,
                    ForeColor   = KzTokens.Ink,
                    Font        = KzThemeHelper.GetFont(KzTokens.FontMd),
                    Width       = 38,
                };
                tb.TextChanged += (s, e) => OnOctetChanged(idx);
                tb.KeyDown     += (s, e) => OnOctetKeyDown(idx, e);
                tb.KeyPress    += OnOctetKeyPress;
                _octets[i]      = tb;
                Controls.Add(tb);

                if (i < 3)
                {
                    var dot = new Label
                    {
                        Text      = ".",
                        Width     = 10,
                        TextAlign = ContentAlignment.MiddleCenter,
                        BackColor = KzTokens.White,
                        ForeColor = KzTokens.Ink,
                        Font      = KzThemeHelper.GetFont(KzTokens.FontMd),
                    };
                    _dots[i] = dot;
                    Controls.Add(dot);
                }
            }

            PositionControls();
        }

        // ── Layout ─────────────────────────────────────────────────────────────

        private void PositionControls()
        {
            const int octetW = 38;
            const int dotW   = 10;
            const int totalW = 4 * octetW + 3 * dotW;

            int startX = Math.Max(12, (Width - totalW) / 2);
            int textH  = _octets[0].PreferredHeight;
            int topY   = Math.Max(1, (Height - textH) / 2);
            int x      = startX;

            for (int i = 0; i < 4; i++)
            {
                _octets[i].SetBounds(x, topY, octetW, textH);
                x += octetW;
                if (i < 3)
                {
                    _dots[i].SetBounds(x, topY, dotW, textH);
                    x += dotW;
                }
            }
        }

        // ── Octet handlers ─────────────────────────────────────────────────────

        private void OnOctetChanged(int idx)
        {
            if (_suppressEvt) return;

            var tb = _octets[idx];

            // Clamp to 255
            if (int.TryParse(tb.Text, out int v) && v > 255)
            {
                _suppressEvt = true;
                tb.Text = "255";
                tb.SelectionStart = 3;
                _suppressEvt = false;
            }

            // Auto-advance after 3 digits
            if (tb.Text.Length == 3 && idx < 3)
                _octets[idx + 1].Focus();

            IPAddressChanged?.Invoke(this, EventArgs.Empty);
        }

        private void OnOctetKeyDown(int idx, KeyEventArgs e)
        {
            switch (e.KeyCode)
            {
                // "." or numpad "." → advance to next octet
                case Keys.OemPeriod:
                case Keys.Decimal:
                    if (idx < 3) { _octets[idx + 1].Focus(); _octets[idx + 1].SelectAll(); }
                    e.SuppressKeyPress = true;
                    break;

                // Backspace on empty octet → go back
                case Keys.Back:
                    if (_octets[idx].Text.Length == 0 && idx > 0)
                    {
                        _octets[idx - 1].Focus();
                        _octets[idx - 1].SelectionStart = _octets[idx - 1].Text.Length;
                        e.SuppressKeyPress = true;
                    }
                    break;

                // Right-arrow at end of octet → advance
                case Keys.Right:
                    if (_octets[idx].SelectionStart >= _octets[idx].Text.Length && idx < 3)
                    {
                        _octets[idx + 1].Focus();
                        _octets[idx + 1].SelectionStart = 0;
                    }
                    break;

                // Left-arrow at start of octet → go back
                case Keys.Left:
                    if (_octets[idx].SelectionStart == 0 && idx > 0)
                    {
                        _octets[idx - 1].Focus();
                        _octets[idx - 1].SelectionStart = _octets[idx - 1].Text.Length;
                    }
                    break;
            }
        }

        private static void OnOctetKeyPress(object sender, KeyPressEventArgs e)
        {
            if (!char.IsDigit(e.KeyChar) && e.KeyChar != (char)Keys.Back)
                e.Handled = true;
        }

        // ── State ──────────────────────────────────────────────────────────────

        private void ApplyState()
        {
            bool  disabled = _state == KzInputState.Disabled;
            Color bg       = disabled ? KzTokens.BgAlt : KzTokens.White;
            Color fg       = disabled ? KzTokens.TextMuted : KzTokens.Ink;

            BackColor = bg;

            foreach (var tb in _octets)
            {
                tb.Enabled   = !disabled;
                tb.BackColor = bg;
                tb.ForeColor = fg;
            }
            foreach (var dot in _dots)
            {
                dot.BackColor = bg;
                dot.ForeColor = fg;
            }
        }

        // ── Paint ──────────────────────────────────────────────────────────────

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;

            bool  disabled = _state == KzInputState.Disabled;
            Color bg       = disabled ? KzTokens.BgAlt : KzTokens.White;
            var   rect     = new Rectangle(0, 0, Width - 1, Height - 1);

            using (var brush = new SolidBrush(bg))
                KzThemeHelper.FillRoundedRect(g, brush, rect, KzTokens.RadiusMd);

            Color borderColor = GetBorderColor();
            float borderWidth = (_focused || _state == KzInputState.Focus) ? 2f : 1f;

            using (var pen = new Pen(borderColor, borderWidth))
                KzThemeHelper.DrawRoundedBorder(g, pen, rect, KzTokens.RadiusMd);
        }

        private Color GetBorderColor()
        {
            switch (_state)
            {
                case KzInputState.Error:    return KzTokens.Error;
                case KzInputState.Disabled: return KzTokens.Border;
                case KzInputState.Focus:    return KzTokens.Orange500;
                default:                    return _focused ? KzTokens.Orange500 : KzTokens.Divider;
            }
        }

        // ── Resize ─────────────────────────────────────────────────────────────

        protected override void OnSizeChanged(EventArgs e)
        {
            base.OnSizeChanged(e);
            if (_octets[0] != null) PositionControls();
        }
    }
}
