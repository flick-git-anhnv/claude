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
    [Description("KZTEK Design System checked list box — multi-select list với checkbox Navy/Orange styling.")]
    public class KzCheckedListBox : UserControl
    {
        private readonly CheckedListBox _inner;
        private int  _hoveredIdx    = -1;
        private bool _borderFocused;

        public event ItemCheckEventHandler ItemChecked;

        public KzCheckedListBox()
        {
            SetStyle(
                ControlStyles.UserPaint |
                ControlStyles.OptimizedDoubleBuffer |
                ControlStyles.AllPaintingInWmPaint |
                ControlStyles.ResizeRedraw |
                ControlStyles.SupportsTransparentBackColor,
                true);

            BackColor = Color.Transparent;
            Padding   = new Padding(2);
            Size      = new Size(220, 160);

            _inner = new CheckedListBox
            {
                DrawMode       = DrawMode.OwnerDrawFixed,
                BorderStyle    = BorderStyle.None,
                CheckOnClick   = true,
                SelectionMode  = SelectionMode.None,
                Font           = KzThemeHelper.GetFont(KzTokens.FontMd),
                BackColor      = KzTokens.White,
                ForeColor      = KzTokens.Ink,
                ItemHeight     = KzTokens.HeightSm,
                IntegralHeight = false,
                Dock           = DockStyle.Fill,
                TabStop        = false,
            };

            _inner.DrawItem  += OnInnerDrawItem;
            _inner.MouseMove += (_, e) =>
            {
                int idx = _inner.IndexFromPoint(e.Location);
                if (idx != _hoveredIdx) { _hoveredIdx = idx; _inner.Invalidate(); }
            };
            _inner.MouseLeave  += (_, __) => { _hoveredIdx = -1; _inner.Invalidate(); };
            _inner.ItemCheck   += (_, e)  => ItemChecked?.Invoke(this, e);
            _inner.GotFocus    += (_, __) => { _borderFocused = true;  Invalidate(); };
            _inner.LostFocus   += (_, __) => { _borderFocused = false; Invalidate(); };

            Controls.Add(_inner);
        }

        // ── Focus passthrough ─────────────────────────────────
        protected override void OnGotFocus(EventArgs e)
        {
            base.OnGotFocus(e);
            _inner.Focus();
        }

        // ── Properties — delegate to inner ───────────────────

        [DesignerSerializationVisibility(DesignerSerializationVisibility.Content)]
        public CheckedListBox.ObjectCollection Items => _inner.Items;

        [Browsable(false)]
        public CheckedListBox.CheckedItemCollection CheckedItems => _inner.CheckedItems;

        [Browsable(false)]
        public CheckedListBox.CheckedIndexCollection CheckedIndices => _inner.CheckedIndices;

        [Category("•KZTEK"), DefaultValue(true)]
        public bool CheckOnClick
        {
            get => _inner.CheckOnClick;
            set => _inner.CheckOnClick = value;
        }

        [Category("•KZTEK"), DefaultValue(false)]
        public bool Sorted
        {
            get => _inner.Sorted;
            set => _inner.Sorted = value;
        }

        // ── Public API ────────────────────────────────────────
        public bool GetItemChecked(int index) => _inner.GetItemChecked(index);
        public void SetItemChecked(int index, bool value) => _inner.SetItemChecked(index, value);
        public CheckState GetItemCheckState(int index) => _inner.GetItemCheckState(index);
        public void SetItemCheckState(int index, CheckState value) => _inner.SetItemCheckState(index, value);

        public void SelectAll()
        {
            for (int i = 0; i < _inner.Items.Count; i++)
                _inner.SetItemChecked(i, true);
        }

        public void DeselectAll()
        {
            for (int i = 0; i < _inner.Items.Count; i++)
                _inner.SetItemChecked(i, false);
        }

        // ── Painting ──────────────────────────────────────────
        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;

            var r = new Rectangle(1, 1, Width - 2, Height - 2);

            using var fillBrush = new SolidBrush(Enabled ? KzTokens.White : KzTokens.BgAlt);
            KzThemeHelper.FillRoundedRect(g, fillBrush, r, KzTokens.RadiusMd);

            Color borderColor = !Enabled       ? KzTokens.Border
                              : _borderFocused  ? KzTokens.Orange500
                              : KzTokens.Divider;
            using var borderPen = new Pen(borderColor, 1f);
            KzThemeHelper.DrawRoundedBorder(g, borderPen, r, KzTokens.RadiusMd);
        }

        // ── Item drawing ──────────────────────────────────────
        private void OnInnerDrawItem(object sender, DrawItemEventArgs e)
        {
            if (e.Index < 0) return;

            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;

            bool isChecked  = _inner.GetItemChecked(e.Index);
            bool isDisabled = !Enabled;
            bool isHovered  = e.Index == _hoveredIdx;

            // Row background
            Color bgColor = isDisabled ? KzTokens.BgAlt
                          : isHovered  ? KzTokens.Navy100
                          : KzTokens.White;
            using (var bgBrush = new SolidBrush(bgColor))
                g.FillRectangle(bgBrush, e.Bounds);

            // Checkbox box
            const int checkSize = 16;
            const int padLeft   = 10;
            int checkTop = e.Bounds.Y + (e.Bounds.Height - checkSize) / 2;
            DrawCheckBox(g, new Rectangle(padLeft, checkTop, checkSize, checkSize), isChecked, isDisabled);

            // Item text
            const int gap  = 8;
            int textX      = padLeft + checkSize + gap;
            var textRect   = new Rectangle(textX, e.Bounds.Y, e.Bounds.Width - textX - 4, e.Bounds.Height);
            Color textColor = isDisabled ? KzTokens.Navy300 : KzTokens.Ink;
            using (var textBrush = new SolidBrush(textColor))
            using (var fmt = new StringFormat
            {
                LineAlignment = StringAlignment.Center,
                Trimming      = StringTrimming.EllipsisCharacter,
                FormatFlags   = StringFormatFlags.NoWrap,
            })
            {
                g.DrawString(_inner.Items[e.Index]?.ToString() ?? string.Empty,
                             _inner.Font, textBrush, textRect, fmt);
            }

            // Row divider (between items)
            if (e.Index < _inner.Items.Count - 1)
            {
                using var divPen = new Pen(Color.FromArgb(40, KzTokens.Divider));
                g.DrawLine(divPen, e.Bounds.Left, e.Bounds.Bottom - 1, e.Bounds.Right, e.Bounds.Bottom - 1);
            }
        }

        private static void DrawCheckBox(Graphics g, Rectangle r, bool isChecked, bool isDisabled)
        {
            Color fill   = isChecked  ? (isDisabled ? KzTokens.Navy300 : KzTokens.Navy900)
                                      : (isDisabled ? KzTokens.Navy100 : KzTokens.White);
            Color border = isChecked  ? (isDisabled ? KzTokens.Navy300 : KzTokens.Navy900)
                                      : (isDisabled ? KzTokens.Border   : KzTokens.Divider);

            using (var fillBrush = new SolidBrush(fill))
                KzThemeHelper.FillRoundedRect(g, fillBrush, r, KzTokens.RadiusSm);

            if (!isChecked)
            {
                // Inset border slightly so 2px pen stays inside the box
                var br = new Rectangle(r.X + 1, r.Y + 1, r.Width - 2, r.Height - 2);
                using var borderPen = new Pen(border, 2f);
                KzThemeHelper.DrawRoundedBorder(g, borderPen, br, KzTokens.RadiusSm);
            }

            if (isChecked)
            {
                Color markColor = isDisabled ? KzTokens.White : KzTokens.White;
                using var pen = new Pen(markColor, 2f)
                {
                    StartCap = LineCap.Round,
                    EndCap   = LineCap.Round,
                    LineJoin = LineJoin.Round,
                };
                g.DrawLine(pen, r.X + 3, r.Y + 9,  r.X + 6, r.Y + 12);
                g.DrawLine(pen, r.X + 6, r.Y + 12, r.X + 13, r.Y + 4);
            }
        }

        protected override void OnEnabledChanged(EventArgs e)
        {
            base.OnEnabledChanged(e);
            _inner.BackColor = Enabled ? KzTokens.White : KzTokens.BgAlt;
            _inner.Invalidate();
            Invalidate();
        }
    }
}
