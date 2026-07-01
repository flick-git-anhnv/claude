using System;
using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    // ── KzMenuStrip ───────────────────────────────────────────────────────────

    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System styled menu strip — NavyBar or LightBar style with KZTEK brand colors.")]
    public class KzMenuStrip : MenuStrip
    {
        public enum KzMenuBarStyle { NavyBar, LightBar }

        private KzMenuBarStyle      _menuStyle = KzMenuBarStyle.NavyBar;
        private KzMenuStripRenderer _kzRenderer;

        [Category("•KZTEK")]
        [Description("NavyBar = dark Navy background (default); LightBar = white background with Navy text.")]
        [DefaultValue(KzMenuBarStyle.NavyBar)]
        public KzMenuBarStyle MenuBarStyle
        {
            get => _menuStyle;
            set { _menuStyle = value; ApplyStyle(); }
        }

        public KzMenuStrip()
        {
            _kzRenderer = new KzMenuStripRenderer(this);
            Renderer    = _kzRenderer;   // sets RenderMode=Custom automatically
            Padding     = new Padding(4, 2, 0, 2);
            ApplyStyle();
        }

        private void ApplyStyle()
        {
            if (_menuStyle == KzMenuBarStyle.NavyBar)
            {
                BackColor = KzTokens.Navy900;
                ForeColor = Color.White;
            }
            else
            {
                BackColor = KzTokens.White;
                ForeColor = KzTokens.Navy900;
            }
            Font = new Font(KzTokens.FontFallback, KzTokens.FontSm, FontStyle.Regular);
            Invalidate();
        }
    }

    // ── Custom renderer ───────────────────────────────────────────────────────

    internal sealed class KzMenuStripRenderer : ToolStripRenderer
    {
        private readonly KzMenuStrip _strip;

        internal KzMenuStripRenderer(KzMenuStrip strip)
        {
            _strip = strip;
        }

        // Main bar / dropdown panel background
        protected override void OnRenderToolStripBackground(ToolStripRenderEventArgs e)
        {
            Color bg = (e.ToolStrip is ToolStripDropDown)
                ? KzTokens.White
                : _strip.BackColor;
            using var brush = new SolidBrush(bg);
            e.Graphics.FillRectangle(brush, e.AffectedBounds);
        }

        // Menu item hover / pressed highlight
        protected override void OnRenderMenuItemBackground(ToolStripItemRenderEventArgs e)
        {
            if (!e.Item.Enabled) return;
            if (e.Item.Selected || e.Item.Pressed)
            {
                using var brush = new SolidBrush(KzTokens.Orange500);
                e.Graphics.FillRectangle(brush, new Rectangle(Point.Empty, e.Item.Size));
            }
        }

        // Text color per context
        protected override void OnRenderItemText(ToolStripItemTextRenderEventArgs e)
        {
            bool hot = e.Item.Selected || e.Item.Pressed;

            Color color;
            if (e.ToolStrip is ToolStripDropDown)
                color = hot ? Color.White : KzTokens.Text;
            else
                color = _strip.MenuBarStyle == KzMenuStrip.KzMenuBarStyle.NavyBar
                    ? Color.White
                    : KzTokens.Navy900;

            if (!e.Item.Enabled) color = KzTokens.TextMuted;

            e.TextColor = color;
            base.OnRenderItemText(e);
        }

        // Dropdown arrow color
        protected override void OnRenderArrow(ToolStripArrowRenderEventArgs e)
        {
            bool hot = e.Item.Selected || e.Item.Pressed;
            if (e.Item.Owner is ToolStripDropDown)
                e.ArrowColor = hot ? Color.White : KzTokens.TextMuted;
            else
                e.ArrowColor = _strip.MenuBarStyle == KzMenuStrip.KzMenuBarStyle.NavyBar
                    ? Color.White
                    : KzTokens.Navy900;
            base.OnRenderArrow(e);
        }

        // Separator line in dropdown
        protected override void OnRenderSeparator(ToolStripSeparatorRenderEventArgs e)
        {
            int cy = e.Item.Height / 2;
            using var pen = new Pen(KzTokens.Divider, 1);
            e.Graphics.DrawLine(pen, 4, cy, e.Item.Width - 4, cy);
        }

        // Dropdown panel border
        protected override void OnRenderToolStripBorder(ToolStripRenderEventArgs e)
        {
            if (!(e.ToolStrip is ToolStripDropDown)) return;
            using var pen = new Pen(KzTokens.Border, 1);
            e.Graphics.DrawRectangle(pen, 0, 0,
                e.AffectedBounds.Width - 1, e.AffectedBounds.Height - 1);
        }

        // Left image margin in dropdown (light gray column)
        protected override void OnRenderImageMargin(ToolStripRenderEventArgs e)
        {
            if (!(e.ToolStrip is ToolStripDropDown)) return;
            using var brush = new SolidBrush(KzTokens.BgAlt);
            e.Graphics.FillRectangle(brush, e.AffectedBounds);
        }

        // Check mark for checked menu items
        protected override void OnRenderItemCheck(ToolStripItemImageRenderEventArgs e)
        {
            bool hot = e.Item.Selected || e.Item.Pressed;
            Color fg = hot ? Color.White : KzTokens.Orange500;
            var r    = e.ImageRectangle;
            using var pen = new Pen(fg, 2f);
            // Simple checkmark: two lines
            e.Graphics.DrawLines(pen, new[]
            {
                new Point(r.Left + 2,  r.Top  + r.Height / 2),
                new Point(r.Left + r.Width / 3, r.Bottom - 3),
                new Point(r.Right - 2, r.Top  + 3),
            });
        }
    }
}
