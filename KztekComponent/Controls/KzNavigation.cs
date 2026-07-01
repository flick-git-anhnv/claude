using KztekComponent.Theme;
using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace KztekComponent.Controls
{
    public class PageChangedEventArgs : EventArgs
    {
        public int NewPage { get; }
        public PageChangedEventArgs(int page) => NewPage = page;
    }

    [DefaultEvent("PageChanged")]
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK pagination bar — First, Prev, manual page input, Next, Last.")]
    public class KzNavigation : UserControl
    {
        // ── Inner: square icon button ─────────────────────────────────────────
        private sealed class NavBtn : Control
        {
            private readonly string _symbol;
            private bool _hovered;
            private bool _pressed;

            internal NavBtn(string symbol)
            {
                _symbol = symbol;
                SetStyle(
                    ControlStyles.UserPaint |
                    ControlStyles.OptimizedDoubleBuffer |
                    ControlStyles.AllPaintingInWmPaint |
                    ControlStyles.Selectable, true);
                Cursor  = Cursors.Hand;
                TabStop = false;
            }

            protected override void OnMouseEnter(EventArgs e)
            { _hovered = true;  Invalidate(); base.OnMouseEnter(e); }

            protected override void OnMouseLeave(EventArgs e)
            { _hovered = false; _pressed = false; Invalidate(); base.OnMouseLeave(e); }

            protected override void OnMouseDown(MouseEventArgs e)
            { if (e.Button == MouseButtons.Left) { _pressed = true; Invalidate(); } base.OnMouseDown(e); }

            protected override void OnMouseUp(MouseEventArgs e)
            { _pressed = false; Invalidate(); base.OnMouseUp(e); }

            protected override void OnPaint(PaintEventArgs e)
            {
                var g    = e.Graphics;
                g.SmoothingMode = SmoothingMode.AntiAlias;
                var rect = new Rectangle(0, 0, Width - 1, Height - 1);

                Color bg, fg;
                if (!Enabled)
                {
                    bg = KzTokens.BgAlt;
                    fg = KzTokens.TextMuted;
                }
                else if (_pressed)
                {
                    bg = KzTokens.Navy1000;
                    fg = KzTokens.White;
                }
                else if (_hovered)
                {
                    bg = KzTokens.Orange500;
                    fg = KzTokens.White;
                }
                else
                {
                    bg = KzTokens.Navy900;
                    fg = KzTokens.White;
                }

                using (var brush = new SolidBrush(bg))
                    KzThemeHelper.FillRoundedRect(g, brush, rect, KzTokens.RadiusSm);

                if (!Enabled)
                    using (var pen = new Pen(KzTokens.Border, 1f))
                        KzThemeHelper.DrawRoundedBorder(g, pen, rect, KzTokens.RadiusSm);

                using var fgBrush = new SolidBrush(fg);
                var fmt = new StringFormat
                {
                    Alignment     = StringAlignment.Center,
                    LineAlignment = StringAlignment.Center,
                };
                g.DrawString(_symbol,
                    KzThemeHelper.GetFont(KzTokens.FontSm, FontStyle.Bold),
                    fgBrush,
                    new RectangleF(0, 0, Width, Height), fmt);
            }

            protected override void OnEnabledChanged(EventArgs e)
            {
                base.OnEnabledChanged(e);
                Cursor = Enabled ? Cursors.Hand : Cursors.Default;
                Invalidate();
            }
        }

        // ── Inner: page-number input with KZTEK border ────────────────────────
        private sealed class PageInputPanel : Panel
        {
            private bool _focused;
            internal readonly TextBox Tb;

            internal PageInputPanel()
            {
                SetStyle(
                    ControlStyles.UserPaint |
                    ControlStyles.OptimizedDoubleBuffer |
                    ControlStyles.AllPaintingInWmPaint |
                    ControlStyles.ResizeRedraw, true);
                BackColor = KzTokens.White;

                Tb = new TextBox
                {
                    BorderStyle = BorderStyle.None,
                    TextAlign   = HorizontalAlignment.Center,
                    BackColor   = KzTokens.White,
                    ForeColor   = KzTokens.Ink,
                    MaxLength   = 6,
                    TabIndex    = 0,
                };
                Controls.Add(Tb);
                Tb.GotFocus  += (s, e) => { _focused = true;  Invalidate(); };
                Tb.LostFocus += (s, e) => { _focused = false; Invalidate(); };
            }

            internal void LayoutTb()
            {
                if (Tb == null) return;
                int textH = Tb.PreferredHeight;
                Tb.SetBounds(5, (Height - textH) / 2, Width - 10, textH);
            }

            protected override void OnSizeChanged(EventArgs e)
            { base.OnSizeChanged(e); LayoutTb(); }

            protected override void OnPaint(PaintEventArgs e)
            {
                var g = e.Graphics;
                g.SmoothingMode = SmoothingMode.AntiAlias;
                var rect = new Rectangle(0, 0, Width - 1, Height - 1);

                using (var brush = new SolidBrush(KzTokens.White))
                    KzThemeHelper.FillRoundedRect(g, brush, rect, KzTokens.RadiusSm);

                float bw = _focused ? 2f : 1f;
                Color bc = _focused ? KzTokens.Orange500 : KzTokens.Divider;
                using (var pen = new Pen(bc, bw))
                    KzThemeHelper.DrawRoundedBorder(g, pen, rect, KzTokens.RadiusSm);
            }
        }

        // ── Fields ────────────────────────────────────────────────────────────
        private NavBtn        _btnFirst, _btnPrev, _btnNext, _btnLast;
        private PageInputPanel _inputPanel;
        private Label          _lblSlash, _lblTotal;
        private bool           _layouting;

        private int    _currentPage = 1;
        private int    _totalPages  = 1;
        private KzSize _kzSize      = KzSize.Medium;

        public event EventHandler<PageChangedEventArgs> PageChanged;

        // ── Properties ────────────────────────────────────────────────────────

        [Category("•KZTEK")]
        [Description("Current page number (1-based). Clamped to [1, TotalPages].")]
        [DefaultValue(1)]
        public int CurrentPage
        {
            get => _currentPage;
            set
            {
                int c = Clamp(value);
                if (c == _currentPage) return;
                _currentPage = c;
                SyncUI();
            }
        }

        [Category("•KZTEK")]
        [Description("Total number of pages.")]
        [DefaultValue(1)]
        public int TotalPages
        {
            get => _totalPages;
            set
            {
                _totalPages  = Math.Max(1, value);
                _currentPage = Math.Min(_currentPage, _totalPages);
                SyncUI();
            }
        }

        [Category("•KZTEK")]
        [Description("Control size (Small / Medium / Large).")]
        [DefaultValue(KzSize.Medium)]
        public KzSize KzSize
        {
            get => _kzSize;
            set { _kzSize = value; ApplySize(); }
        }

        // ── Constructor ───────────────────────────────────────────────────────

        public KzNavigation()
        {
            SetStyle(
                ControlStyles.UserPaint |
                ControlStyles.OptimizedDoubleBuffer |
                ControlStyles.AllPaintingInWmPaint |
                ControlStyles.ResizeRedraw |
                ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;
            Build();
            ApplySize();
            SyncUI();
        }

        // ── Build ─────────────────────────────────────────────────────────────

        private void Build()
        {
            _btnFirst = new NavBtn("◀◀");
            _btnPrev  = new NavBtn("◀");
            _btnNext  = new NavBtn("▶");
            _btnLast  = new NavBtn("▶▶");

            _inputPanel = new PageInputPanel();
            _inputPanel.Tb.KeyPress += OnInputKeyPress;
            _inputPanel.Tb.KeyDown  += OnInputKeyDown;
            _inputPanel.Tb.Leave    += OnInputLeave;

            _lblSlash = new Label
            {
                Text      = "/",
                AutoSize  = false,
                TextAlign = ContentAlignment.MiddleCenter,
                BackColor = Color.Transparent,
                ForeColor = KzTokens.TextMuted,
            };

            _lblTotal = new Label
            {
                AutoSize  = false,
                TextAlign = ContentAlignment.MiddleLeft,
                BackColor = Color.Transparent,
                ForeColor = KzTokens.TextMuted,
            };

            _btnFirst.Click += (s, e) => GoToPage(1);
            _btnPrev.Click  += (s, e) => GoToPage(_currentPage - 1);
            _btnNext.Click  += (s, e) => GoToPage(_currentPage + 1);
            _btnLast.Click  += (s, e) => GoToPage(_totalPages);

            Controls.AddRange(new Control[]
            {
                _btnFirst, _btnPrev,
                _inputPanel, _lblSlash, _lblTotal,
                _btnNext, _btnLast,
            });
        }

        // ── Size + layout ─────────────────────────────────────────────────────

        private void ApplySize()
        {
            if (_btnFirst == null) return;

            int btnH; float fontSize;
            switch (_kzSize)
            {
                case KzSize.Small:  btnH = 28; fontSize = KzTokens.FontSm;   break;
                case KzSize.Large:  btnH = 40; fontSize = KzTokens.FontMd;   break;
                default:            btnH = 34; fontSize = KzTokens.FontBody; break;
            }

            var font = KzThemeHelper.GetFont(fontSize);
            foreach (var b in new[] { _btnFirst, _btnPrev, _btnNext, _btnLast })
                b.Size = new Size(btnH, btnH);

            _inputPanel.Tb.Font = font;
            _lblSlash.Font      = font;
            _lblTotal.Font      = font;

            Height = btnH;
            PositionControls();
        }

        private void PositionControls()
        {
            if (_btnFirst == null || _layouting) return;
            _layouting = true;
            try
            {
                int btnH    = _btnFirst.Height;
                const int gap    = 4;
                const int midGap = 8;   // extra gap between btn group and input group
                const int inputW = 52;
                const int slashW = 16;
                const int totalW = 52;

                int x = 0;

                _btnFirst.SetBounds(x, 0, btnH, btnH); x += btnH + gap;
                _btnPrev.SetBounds (x, 0, btnH, btnH); x += btnH + midGap;

                _inputPanel.SetBounds(x, 0, inputW, btnH); x += inputW + 2;
                _lblSlash.SetBounds  (x, 0, slashW, btnH); x += slashW + 2;
                _lblTotal.SetBounds  (x, 0, totalW, btnH); x += totalW + midGap;

                _btnNext.SetBounds(x, 0, btnH, btnH); x += btnH + gap;
                _btnLast.SetBounds(x, 0, btnH, btnH); x += btnH;

                Width = x;
            }
            finally
            {
                _layouting = false;
            }
        }

        // ── Navigation logic ──────────────────────────────────────────────────

        private void GoToPage(int page)
        {
            int c = Clamp(page);
            if (c == _currentPage) return;
            _currentPage = c;
            SyncUI();
            PageChanged?.Invoke(this, new PageChangedEventArgs(_currentPage));
        }

        private int Clamp(int p) => Math.Max(1, Math.Min(p, _totalPages));

        // ── Input handlers ────────────────────────────────────────────────────

        private static void OnInputKeyPress(object sender, KeyPressEventArgs e)
        {
            if (!char.IsDigit(e.KeyChar) && e.KeyChar != (char)Keys.Back)
                e.Handled = true;
        }

        private void OnInputKeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter || e.KeyCode == Keys.Return)
            {
                CommitInput();
                e.SuppressKeyPress = true;
            }
            else if (e.KeyCode == Keys.Escape)
            {
                _inputPanel.Tb.Text = _currentPage.ToString();
                e.SuppressKeyPress  = true;
            }
        }

        private void OnInputLeave(object sender, EventArgs e) => CommitInput();

        private void CommitInput()
        {
            if (int.TryParse(_inputPanel.Tb.Text, out int p) && p >= 1 && p <= _totalPages)
                GoToPage(p);
            else
                _inputPanel.Tb.Text = _currentPage.ToString();
        }

        // ── Sync UI ───────────────────────────────────────────────────────────

        private void SyncUI()
        {
            if (_inputPanel == null) return;
            _inputPanel.Tb.Text = _currentPage.ToString();
            _lblTotal.Text      = _totalPages.ToString();
            _btnFirst.Enabled   = _currentPage > 1;
            _btnPrev.Enabled    = _currentPage > 1;
            _btnNext.Enabled    = _currentPage < _totalPages;
            _btnLast.Enabled    = _currentPage < _totalPages;
        }

        // ── Paint / Resize ────────────────────────────────────────────────────

        protected override void OnPaint(PaintEventArgs e) { /* transparent — no outer border */ }

        protected override void OnSizeChanged(EventArgs e)
        {
            base.OnSizeChanged(e);
            PositionControls();
        }
    }
}
