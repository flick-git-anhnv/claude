using KztekComponent.Theme;
using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK sidebar navigation panel — dark navy bg, KZTEK branding, nav items.")]
    public class KzSidebar : Panel
    {
        private string _brandName = "kztek";
        private readonly FlowLayoutPanel _itemsPanel;
        private int _activeIndex = 0;
        private int _itemCount = 0; // counts only KzSidebarItems, not section labels

        [Category("•KZTEK"), DefaultValue("kztek")]
        public string BrandName
        {
            get => _brandName;
            set { _brandName = value; Invalidate(); }
        }

        [Category("•KZTEK"), DefaultValue(0)]
        public int ActiveIndex
        {
            get => _activeIndex;
            set { SetActive(value); }
        }

        [Category("•KZTEK")]
        public event EventHandler<int> ItemSelected;

        public KzSidebar()
        {
            SetStyle(ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.ResizeRedraw, true);

            BackColor = KzTokens.Navy900;
            Padding = new Padding(0, 64, 0, 0); // space for brand header

            _itemsPanel = new FlowLayoutPanel
            {
                Dock = DockStyle.Fill,
                FlowDirection = FlowDirection.TopDown,
                WrapContents = false,
                BackColor = Color.Transparent,
                Padding = new Padding(0)
            };
            Controls.Add(_itemsPanel);
            Width = KzTokens.SidebarWidth;
        }

        // ── API ───────────────────────────────────────────────
        public void AddItem(string text, Image icon = null)
        {
            int itemIdx = _itemCount++; // 0-based, counting only items (not section labels)
            var item = new KzSidebarItem
            {
                Text = text,
                Icon = icon,
                Width = Width,
                IsActive = itemIdx == _activeIndex
            };
            item.ItemClicked += (s, e) =>
            {
                SetActive(itemIdx);
                ItemSelected?.Invoke(this, itemIdx);
            };
            _itemsPanel.Controls.Add(item);
        }

        public void AddSectionLabel(string label)
        {
            var lbl = new Label
            {
                Text = label.ToUpper(),
                ForeColor = Color.FromArgb(153, KzTokens.Navy300),
                Font = KzThemeHelper.GetFont(KzTokens.FontXs, FontStyle.Bold),
                Height = 28,
                Width = Width,
                Padding = new Padding(KzTokens.SidebarPadH, 10, 0, 0),
                BackColor = Color.Transparent
            };
            _itemsPanel.Controls.Add(lbl);
        }

        private void SetActive(int idx)
        {
            _activeIndex = idx;
            int itemIdx = 0;
            foreach (Control c in _itemsPanel.Controls)
            {
                if (c is KzSidebarItem si)
                {
                    si.IsActive = (itemIdx == idx);
                    itemIdx++;
                }
            }
        }

        // ── Paint brand header ────────────────────────────────
        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.ClearTypeGridFit;

            // Brand header area
            var headerRect = new Rectangle(0, 0, Width, 56);
            using (var bg = new SolidBrush(KzTokens.Navy900))
                g.FillRectangle(bg, headerRect);

            // Orange dot (rotated square)
            int dotX = KzTokens.SidebarPadH;
            int dotY = 23;
            int dotS = 10;
            var matrix = new Matrix();
            matrix.RotateAt(45, new PointF(dotX + dotS / 2f, dotY + dotS / 2f));
            g.Transform = matrix;
            using (var dotBrush = new SolidBrush(KzTokens.Orange500))
                g.FillRectangle(dotBrush, dotX, dotY, dotS, dotS);
            g.ResetTransform();

            // Brand text
            int textX = KzTokens.SidebarPadH + dotS + 10;
            using var brandFont = new Font("Manrope", 13f, FontStyle.Bold, GraphicsUnit.Pixel);
            using (var brush = new SolidBrush(KzTokens.White))
                g.DrawString(_brandName, brandFont, brush, new PointF(textX, 20));
        }

        protected override void OnResize(EventArgs e)
        {
            base.OnResize(e);
            if (_itemsPanel == null) return;
            foreach (Control c in _itemsPanel.Controls)
                c.Width = Width;
        }
    }
}

