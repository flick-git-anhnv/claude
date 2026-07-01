using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Text;
using System.Windows.Forms;
using Guna.UI2.WinForms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [DefaultEvent("KeyPressed")]
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System virtual keyboard — Alpha/Numeric/Special modes, Portrait/Landscape.")]
    public class KzKeyboard : UserControl
    {
        // ── Public enums ─────────────────────────────────────────────────────
        public enum KzKeyboardOrientation { Portrait, Landscape }
        public enum KzKeyboardMode       { Alpha, Numeric, Special }

        // ── Events ───────────────────────────────────────────────────────────
        public event EventHandler<string>              KeyPressed;
        public event EventHandler<KzKeyboardOrientation> OrientationChanged;
        /// <summary>Fired when the VI/EN toggle is pressed. Arg = true when Vietnamese (Telex) is now active.</summary>
        public event EventHandler<bool>                LanguageChanged;

        // ── Key definition ────────────────────────────────────────────────────
        private struct KD
        {
            public string Lbl, LblUp, Val, ValUp;
            public float  W;
            public bool   Special;
        }

        // ── Factory helpers ───────────────────────────────────────────────────
        private static KD A(string lc) => new KD { Lbl = lc, LblUp = lc.ToUpperInvariant(), Val = lc, ValUp = lc.ToUpperInvariant(), W = 1f };
        private static KD C(string ch) => new KD { Lbl = ch, LblUp = ch, Val = ch, ValUp = ch, W = 1f };
        private static KD S(string lbl, string cmd, float w = 1.5f) => new KD { Lbl = lbl, LblUp = lbl, Val = cmd, ValUp = cmd, W = w, Special = true };
        private static KD SP(float w = 4f) => new KD { Lbl = "Space", LblUp = "Space", Val = " ", ValUp = " ", W = w, Special = true };

        // ── Key layout tables ─────────────────────────────────────────────────
        private static readonly KD[][] _alphaRows =
        {
            new[] { A("q"),A("w"),A("e"),A("r"),A("t"),A("y"),A("u"),A("i"),A("o"),A("p") },
            new[] { A("a"),A("s"),A("d"),A("f"),A("g"),A("h"),A("j"),A("k"),A("l") },
            new[] { S("Shift","SHIFT",1.5f), A("z"),A("x"),A("c"),A("v"),A("b"),A("n"),A("m"), S("⌫","BACK",1.5f) },
            new[] { S("?123","NUM",1.5f), C(","), S("EN","LANG",1.5f), SP(2.5f), C("."), S("Enter","ENTER",1.5f) }
        };

        private static readonly KD[][] _numRows =
        {
            new[] { C("1"),C("2"),C("3"),C("4"),C("5"),C("6"),C("7"),C("8"),C("9"),C("0") },
            new[] { C("@"),C("#"),C("$"),C("%"),C("^"),C("-"),C("+"),C("("),C(")"),C("/") },
            new[] { S("#+=","SPEC",1.5f), C("*"),C("\""),C("'"),C(":"),C(";"),C("!"),C("?"), S("⌫","BACK",1.5f) },
            new[] { S("ABC","ALPHA",1.5f), C(","), S("EN","LANG",1.5f), SP(2.5f), C("."), S("Enter","ENTER",1.5f) }
        };

        private static readonly KD[][] _specRows =
        {
            new[] { C("["),C("]"),C("{"),C("}"),C("<"),C(">"),C("="),C("_"),C("\\"),C("|") },
            new[] { C("~"),C("^"),C("`"),C("+"),C("-"),C("*"),C("/"),C(":"),C(";"),C("@") },
            new[] { S("?123","NUM",1.5f), C("."),C(","),C(":"),C(";"),C("!"),C("?"), S("⌫","BACK",1.5f) },
            new[] { S("ABC","ALPHA",1.5f), C("-"), S("EN","LANG",1.5f), SP(2.5f), C("/"), S("Enter","ENTER",1.5f) }
        };

        // ── State ─────────────────────────────────────────────────────────────
        private KzKeyboardOrientation _orientation = KzKeyboardOrientation.Portrait;
        private KzKeyboardMode        _mode        = KzKeyboardMode.Alpha;
        private bool                  _shifted     = false;
        private bool                  _capsLock    = false;
        private bool                  _enableTelex = false;
        private string                _pressedVal  = null;
        private Control               _target;
        private readonly System.Windows.Forms.Timer _pressTimer;

        private readonly List<(RectangleF R, KD Key)> _layout = new();

        // ── Sizing constants ──────────────────────────────────────────────────
        public static readonly Size PortraitSize  = new Size(390, 300);
        public static readonly Size LandscapeSize = new Size(640, 220);

        // ── Colour / style fields ─────────────────────────────────────────────
        private Color _keyBg     = Color.White;
        private Color _keyBgSpec = Color.FromArgb(0xCB, 0xC7, 0xBF);
        private Color _keyFg     = KzTokens.Text;
        private Color _kbBg      = Color.FromArgb(0xF0, 0xEB, 0xE1);
        private Color _pressedBg = KzTokens.Navy900;
        private Color _pressedFg = Color.White;
        private int   _pad       = 8;
        private int   _gap       = 9;
        private int   _keyRadius = 8;

        // ── Constructor ───────────────────────────────────────────────────────
        public KzKeyboard()
        {
            DoubleBuffered = true;
            SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer | ControlStyles.ResizeRedraw, true);
            Size      = PortraitSize;
            BackColor = _kbBg;
            Cursor    = Cursors.Hand;

            _pressTimer = new System.Windows.Forms.Timer { Interval = 110 };
            _pressTimer.Tick += (_, __) => { _pressedVal = null; _pressTimer.Stop(); Invalidate(); };
            MouseDown += OnMouseDown;
        }

        // ── Public properties ─────────────────────────────────────────────────

        [Category("•KZTEK")]
        [Description("Portrait or Landscape layout.")]
        public KzKeyboardOrientation Orientation
        {
            get => _orientation;
            set
            {
                if (_orientation == value) return;
                _orientation = value;
                Size = _orientation == KzKeyboardOrientation.Portrait ? PortraitSize : LandscapeSize;
                Invalidate();
                OrientationChanged?.Invoke(this, _orientation);
            }
        }

        [Category("•KZTEK")]
        [Description("TextBox, KzTextBox, or Guna2TextBox that receives keyboard input.")]
        public Control TargetControl
        {
            get => _target;
            set
            {
                _target = value;
                if (_target is Guna2NumericUpDown)
                {
                    _mode = KzKeyboardMode.Numeric;
                    Invalidate();
                }
            }
        }

        [Category("•KZTEK")]
        public Color KeyBackground
        {
            get => _keyBg;
            set { _keyBg = value; Invalidate(); }
        }

        [Category("•KZTEK")]
        public Color KeyboardBackground
        {
            get => _kbBg;
            set { _kbBg = value; BackColor = value; Invalidate(); }
        }

        [Category("•KZTEK")]
        [DefaultValue(8)]
        public int KeyRadius
        {
            get => _keyRadius;
            set { _keyRadius = Math.Max(0, value); Invalidate(); }
        }

        [Category("•KZTEK")]
        [DefaultValue(9)]
        public int KeySpacing
        {
            get => _gap;
            set { _gap = Math.Max(2, value); Invalidate(); }
        }

        [Category("•KZTEK")]
        [DefaultValue(false)]
        public bool DefaultUpperCase
        {
            get => _capsLock;
            set { _capsLock = value; _shifted = false; Invalidate(); }
        }

        [Category("•KZTEK")]
        [Description("Enable Vietnamese Telex input (aa→â, aw→ă, ow→ơ, uw→ư, dd→đ; tone: s f r x j z).")]
        [DefaultValue(false)]
        public bool EnableTelex
        {
            get => _enableTelex;
            set => _enableTelex = value;
        }

        // ── Public methods ────────────────────────────────────────────────────

        public void ToggleOrientation() =>
            Orientation = _orientation == KzKeyboardOrientation.Portrait
                ? KzKeyboardOrientation.Landscape
                : KzKeyboardOrientation.Portrait;

        // ── Painting ──────────────────────────────────────────────────────────

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            var g = e.Graphics;
            g.SmoothingMode     = SmoothingMode.AntiAlias;
            g.PixelOffsetMode   = PixelOffsetMode.HighQuality;
            g.TextRenderingHint = TextRenderingHint.ClearTypeGridFit;

            _layout.Clear();

            var rows = _mode switch
            {
                KzKeyboardMode.Numeric => _numRows,
                KzKeyboardMode.Special => _specRows,
                _                      => _alphaRows
            };

            BuildAndDraw(g, rows);
        }

        private void BuildAndDraw(Graphics g, KD[][] rows)
        {
            int   W     = Width  - _pad * 2;
            int   H     = Height - _pad * 2;
            int   nRows = rows.Length;
            float rowH  = (H - _gap * (nRows - 1)) / (float)nRows;
            float y     = _pad;

            foreach (var row in rows)
            {
                float totalW = 0f;
                foreach (var k in row) totalW += k.W;
                float unitW = (W - _gap * (row.Length - 1)) / totalW;
                float x = _pad;

                foreach (var key in row)
                {
                    var rect = new RectangleF(x, y, unitW * key.W, rowH);
                    _layout.Add((rect, key));
                    DrawKey(g, rect, key);
                    x += unitW * key.W + _gap;
                }
                y += rowH + _gap;
            }
        }

        private void DrawKey(Graphics g, RectangleF r, KD key)
        {
            string val         = ResolveVal(key);
            bool   pressed     = _pressedVal == val;
            bool   shiftActive = val == "SHIFT" && (_shifted || _capsLock);
            bool   langActive  = val == "LANG"  && _enableTelex;

            Color bg = pressed     ? _pressedBg
                     : shiftActive ? KzTokens.Navy900
                     : langActive  ? KzTokens.Orange500
                     : key.Special ? _keyBgSpec
                     : _keyBg;
            Color fg = (pressed || shiftActive || langActive) ? Color.White : _keyFg;

            if (!pressed)
            {
                using var sh = new SolidBrush(Color.FromArgb(22, 0, 0, 0));
                FillRR(g, sh, RectangleF.FromLTRB(r.Left + 1, r.Top + 2, r.Right + 1, r.Bottom + 2));
            }

            using var bgBrush    = new SolidBrush(bg);
            using var borderPen  = new Pen(Color.FromArgb(40, 0, 0, 0), 0.5f);
            FillRR(g, bgBrush, r);
            DrawRR(g, borderPen, r);

            string lbl = ResolveLabel(key);
            if (lbl.Length == 0) return;

            float fs = r.Height < 30 ? 7.5f
                     : r.Height < 42 ? 9.5f
                     : r.Height < 58 ? 11f
                     : r.Height < 80 ? 15f
                     : 18f;

            if      (lbl.Length >= 9) fs = Math.Max(fs * 0.52f, 6f);
            else if (lbl.Length >= 5) fs = Math.Max(fs * 0.85f, 7f);
            else if (lbl.Length >= 3) fs = Math.Max(fs * 0.90f, 7f);

            using var font    = new Font(KzTokens.FontFallback, fs, FontStyle.Regular);
            using var fgBrush = new SolidBrush(fg);
            var sf = new StringFormat
            {
                Alignment     = StringAlignment.Center,
                LineAlignment = StringAlignment.Center,
                Trimming      = StringTrimming.None,
            };
            g.DrawString(lbl, font, fgBrush, r, sf);
        }

        private string ResolveLabel(KD k)
        {
            if (k.Val == "LANG") return _enableTelex ? "VI" : "EN";
            if (k.Special) return k.Lbl;
            return (_shifted || _capsLock) ? k.LblUp : k.Lbl;
        }

        private string ResolveVal(KD k)
        {
            if (k.Special) return k.Val;
            return (_shifted || _capsLock) ? k.ValUp : k.Val;
        }

        // ── Mouse handling ────────────────────────────────────────────────────

        private void OnMouseDown(object sender, MouseEventArgs e)
        {
            foreach (var (rect, key) in _layout)
            {
                if (!rect.Contains(e.Location)) continue;
                string val = ResolveVal(key);
                _pressedVal = val;
                _pressTimer.Stop();
                _pressTimer.Start();
                Invalidate();
                ProcessKey(val);
                return;
            }
        }

        private void ProcessKey(string val)
        {
            switch (val)
            {
                case "SHIFT":
                    if (_capsLock)     { _capsLock = false; _shifted = false; }
                    else if (_shifted) { _shifted  = false; _capsLock = true; }
                    else               { _shifted  = true; }
                    Invalidate();
                    return;

                case "BACK":
                    DoBackspace();
                    KeyPressed?.Invoke(this, "BACKSPACE");
                    return;

                case "ENTER":
                    FocusNextControl();
                    KeyPressed?.Invoke(this, "ENTER");
                    return;

                case "FLIP":
                    ToggleOrientation();
                    return;

                case "NUM":   _mode = KzKeyboardMode.Numeric; Invalidate(); return;
                case "ALPHA": _mode = KzKeyboardMode.Alpha;   Invalidate(); return;
                case "SPEC":  _mode = KzKeyboardMode.Special; Invalidate(); return;

                case "LANG":
                    _enableTelex = !_enableTelex;
                    Invalidate();
                    LanguageChanged?.Invoke(this, _enableTelex);
                    return;

                default:
                    if (_enableTelex && val.Length == 1 && char.IsLetter(val[0]))
                        TypeTextTelex(val[0]);
                    else
                        TypeText(val);
                    if (_shifted && !_capsLock) { _shifted = false; Invalidate(); }
                    KeyPressed?.Invoke(this, val);
                    return;
            }
        }

        // ── Text-target helpers ───────────────────────────────────────────────

        private void TypeText(string text)
        {
            if (_target == null) return;

            if (_target is TextBox tb)
            {
                int s = tb.SelectionStart;
                tb.Text = tb.Text.Insert(s, text);
                tb.SelectionStart = s + text.Length;
            }
            else if (_target is Guna2TextBox g2)
            {
                int s = g2.SelectionStart;
                g2.Text = g2.Text.Insert(s, text);
                g2.SelectionStart = s + text.Length;
            }
            else if (_target is KzPasswordTextBox pwd)
            {
                int s = pwd.SelectionStart;
                pwd.Text = pwd.Text.Insert(s, text);
                pwd.SelectionStart = s + text.Length;
            }
            else if (_target is Guna2NumericUpDown nud)
            {
                if (text.Length == 1 && (char.IsDigit(text[0]) || text[0] == '-' || text[0] == '.'))
                {
                    string newStr = nud.Value.ToString() + text[0];
                    if (decimal.TryParse(newStr, System.Globalization.NumberStyles.Any,
                            System.Globalization.CultureInfo.InvariantCulture, out decimal val)
                        && val >= nud.Minimum && val <= nud.Maximum)
                        nud.Value = val;
                }
            }
            else if (_target is KzIPTextbox ip)
            {
                var focused = FindFocusedTextBox(ip);
                if (focused != null && text.Length == 1 && char.IsDigit(text[0]))
                {
                    int s = focused.SelectionStart;
                    focused.Text = focused.Text.Insert(s, text);
                    focused.SelectionStart = s + 1;
                }
            }
        }

        private void TypeTextTelex(char c)
        {
            if (_target == null) return;
            string before = GetTextBeforeCursor();
            var (del, ins) = KzTelexEngine.Process(before, c);
            for (int i = 0; i < del; i++) DoBackspace();
            TypeText(ins);
        }

        private string GetTextBeforeCursor()
        {
            if (_target is TextBox tb)
                return tb.Text.Substring(0, System.Math.Max(0, tb.SelectionStart));
            if (_target is Guna2TextBox g2)
                return g2.Text.Substring(0, System.Math.Max(0, g2.SelectionStart));
            if (_target is KzPasswordTextBox pwd)
                return pwd.Text.Substring(0, System.Math.Max(0, pwd.SelectionStart));
            if (_target is Guna2NumericUpDown nud)
                return nud.Value.ToString();
            if (_target is KzIPTextbox ip)
            {
                var focused = FindFocusedTextBox(ip);
                if (focused != null)
                    return focused.Text.Substring(0, System.Math.Max(0, focused.SelectionStart));
            }
            return "";
        }

        private void DoBackspace()
        {
            if (_target == null) return;

            if (_target is TextBox tb && tb.SelectionStart > 0)
            {
                int s = tb.SelectionStart;
                tb.Text = tb.Text.Remove(s - 1, 1);
                tb.SelectionStart = s - 1;
            }
            else if (_target is Guna2TextBox g2 && g2.SelectionStart > 0)
            {
                int s = g2.SelectionStart;
                g2.Text = g2.Text.Remove(s - 1, 1);
                g2.SelectionStart = s - 1;
            }
            else if (_target is KzPasswordTextBox pwd && pwd.SelectionStart > 0)
            {
                int s = pwd.SelectionStart;
                pwd.Text = pwd.Text.Remove(s - 1, 1);
                pwd.SelectionStart = s - 1;
            }
            else if (_target is Guna2NumericUpDown nud)
            {
                string str = nud.Value.ToString();
                if (str.Length > 0)
                {
                    string newStr = str.Substring(0, str.Length - 1);
                    if (string.IsNullOrEmpty(newStr))
                        nud.Value = 0m;
                    else if (decimal.TryParse(newStr, System.Globalization.NumberStyles.Any,
                                 System.Globalization.CultureInfo.InvariantCulture, out decimal val)
                             && val >= nud.Minimum && val <= nud.Maximum)
                        nud.Value = val;
                }
            }
            else if (_target is KzIPTextbox ip)
            {
                var focused = FindFocusedTextBox(ip);
                if (focused != null && focused.SelectionStart > 0)
                {
                    int s = focused.SelectionStart;
                    focused.Text = focused.Text.Remove(s - 1, 1);
                    focused.SelectionStart = s - 1;
                }
            }
        }

        private void FocusNextControl()
        {
            if (_target == null) return;
            _target.FindForm()?.SelectNextControl(_target, true, true, true, true);
        }

        private static TextBox FindFocusedTextBox(Control parent)
        {
            foreach (Control c in parent.Controls)
                if (c is TextBox tb && tb.Focused) return tb;
            return null;
        }

        // ── Rounded-rect helpers ──────────────────────────────────────────────

        private void FillRR(Graphics g, Brush b, RectangleF r)
        {
            using var p = RoundPath(r);
            g.FillPath(b, p);
        }

        private void DrawRR(Graphics g, Pen p, RectangleF r)
        {
            using var path = RoundPath(r);
            g.DrawPath(p, path);
        }

        private GraphicsPath RoundPath(RectangleF r)
        {
            float d     = _keyRadius * 2f;
            float safeR = Math.Min(r.Width, r.Height);
            if (d > safeR) d = safeR;

            var path = new GraphicsPath();
            path.AddArc(r.X,          r.Y,          d, d, 180, 90);
            path.AddArc(r.Right - d,  r.Y,          d, d, 270, 90);
            path.AddArc(r.Right - d,  r.Bottom - d, d, d,   0, 90);
            path.AddArc(r.X,          r.Bottom - d, d, d,  90, 90);
            path.CloseFigure();
            return path;
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing) _pressTimer?.Dispose();
            base.Dispose(disposing);
        }
    }
}
