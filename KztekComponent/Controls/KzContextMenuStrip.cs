using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    // ── KzContextMenuStrip ────────────────────────────────────────────────────

    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System styled context menu — white background, Orange500 item highlight, branded separators and check marks.")]
    public class KzContextMenuStrip : ContextMenuStrip
    {
        public KzContextMenuStrip()
        {
            Renderer = new KzContextMenuRenderer();
            Font     = new Font(KzTokens.FontFallback, KzTokens.FontSm, FontStyle.Regular);
        }

        public KzContextMenuStrip(IContainer container) : base(container)
        {
            Renderer = new KzContextMenuRenderer();
            Font     = new Font(KzTokens.FontFallback, KzTokens.FontSm, FontStyle.Regular);
        }
    }

    // ── Custom renderer ───────────────────────────────────────────────────────

    internal sealed class KzContextMenuRenderer : ToolStripRenderer
    {
        // Panel background: always white
        protected override void OnRenderToolStripBackground(ToolStripRenderEventArgs e)
        {
            using var brush = new SolidBrush(KzTokens.White);
            e.Graphics.FillRectangle(brush, e.AffectedBounds);
        }

        // Item hover / pressed: Orange500 fill
        protected override void OnRenderMenuItemBackground(ToolStripItemRenderEventArgs e)
        {
            if (!e.Item.Enabled) return;
            if (e.Item.Selected || e.Item.Pressed)
            {
                using var brush = new SolidBrush(KzTokens.Orange500);
                e.Graphics.FillRectangle(brush, new Rectangle(Point.Empty, e.Item.Size));
            }
        }

        // Text: white on hover, Text normally, TextMuted when disabled
        protected override void OnRenderItemText(ToolStripItemTextRenderEventArgs e)
        {
            bool hot = e.Item.Selected || e.Item.Pressed;
            e.TextColor = !e.Item.Enabled ? KzTokens.TextMuted
                        : hot            ? Color.White
                        :                  KzTokens.Text;
            base.OnRenderItemText(e);
        }

        // Submenu arrow: white on hover, TextMuted normally
        protected override void OnRenderArrow(ToolStripArrowRenderEventArgs e)
        {
            bool hot = e.Item.Selected || e.Item.Pressed;
            e.ArrowColor = hot ? Color.White : KzTokens.TextMuted;
            base.OnRenderArrow(e);
        }

        // Separator line
        protected override void OnRenderSeparator(ToolStripSeparatorRenderEventArgs e)
        {
            int cy = e.Item.Height / 2;
            using var pen = new Pen(KzTokens.Divider, 1);
            e.Graphics.DrawLine(pen, 4, cy, e.Item.Width - 4, cy);
        }

        // Panel border
        protected override void OnRenderToolStripBorder(ToolStripRenderEventArgs e)
        {
            using var pen = new Pen(KzTokens.Border, 1);
            e.Graphics.DrawRectangle(pen, 0, 0,
                e.AffectedBounds.Width - 1, e.AffectedBounds.Height - 1);
        }

        // Left image margin column
        protected override void OnRenderImageMargin(ToolStripRenderEventArgs e)
        {
            using var brush = new SolidBrush(KzTokens.BgAlt);
            e.Graphics.FillRectangle(brush, e.AffectedBounds);
        }

        // Check mark: Orange500 normally, white on hover
        protected override void OnRenderItemCheck(ToolStripItemImageRenderEventArgs e)
        {
            bool hot = e.Item.Selected || e.Item.Pressed;
            Color fg = hot ? Color.White : KzTokens.Orange500;
            var r    = e.ImageRectangle;
            using var pen = new Pen(fg, 2f);
            e.Graphics.DrawLines(pen, new[]
            {
                new Point(r.Left + 2,  r.Top  + r.Height / 2),
                new Point(r.Left + r.Width / 3, r.Bottom - 3),
                new Point(r.Right - 2, r.Top  + 3),
            });
        }
    }
}
