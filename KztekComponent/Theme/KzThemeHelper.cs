using System;
using System.Drawing;
using System.Drawing.Drawing2D;

namespace KztekComponent.Theme
{
    public static class KzThemeHelper
    {
        // ── Font helpers ──────────────────────────────────────
        public static Font GetFont(float size, FontStyle style = FontStyle.Regular)
        {
            // Note: FontStyle.Bold does not exist in WinForms — use Bold for semi-bold weight
            try { return new Font(KzTokens.FontSans, size, style, GraphicsUnit.Pixel); }
            catch { return new Font(KzTokens.FontFallback, size, style, GraphicsUnit.Pixel); }
        }

        public static Font GetFontPt(float pt, FontStyle style = FontStyle.Regular)
        {
            try { return new Font(KzTokens.FontSans, pt, style, GraphicsUnit.Point); }
            catch { return new Font(KzTokens.FontFallback, pt, style, GraphicsUnit.Point); }
        }

        // ── Rounded rectangle ─────────────────────────────────
        public static GraphicsPath RoundedRect(Rectangle r, int radius)
        {
            radius = Math.Min(radius, Math.Min(r.Width, r.Height) / 2);
            var path = new GraphicsPath();
            if (radius <= 0) { path.AddRectangle(r); return path; }
            path.AddArc(r.X, r.Y, radius * 2, radius * 2, 180, 90);
            path.AddArc(r.Right - radius * 2, r.Y, radius * 2, radius * 2, 270, 90);
            path.AddArc(r.Right - radius * 2, r.Bottom - radius * 2, radius * 2, radius * 2, 0, 90);
            path.AddArc(r.X, r.Bottom - radius * 2, radius * 2, radius * 2, 90, 90);
            path.CloseFigure();
            return path;
        }

        // ── Fill rounded rect ─────────────────────────────────
        public static void FillRoundedRect(Graphics g, Brush brush, Rectangle r, int radius)
        {
            using var path = RoundedRect(r, radius);
            g.FillPath(brush, path);
        }

        // ── Draw rounded border ───────────────────────────────
        public static void DrawRoundedBorder(Graphics g, Pen pen, Rectangle r, int radius)
        {
            using var path = RoundedRect(r, radius);
            g.DrawPath(pen, path);
        }

        // ── Focus ring (orange glow) ──────────────────────────
        public static void DrawFocusRing(Graphics g, Rectangle r, int radius)
        {
            var ringColor = Color.FromArgb(64, KzTokens.Orange500);
            using var pen1 = new Pen(ringColor, 3f);
            var outer = Rectangle.Inflate(r, 3, 3);
            DrawRoundedBorder(g, pen1, outer, radius + 3);
        }

        // ── Shadow (soft card shadow) ─────────────────────────
        public static void DrawCardShadow(Graphics g, Rectangle r, int radius, bool elevated = false)
        {
            int layers = elevated ? 6 : 2;
            int alpha = elevated ? 28 : 12;
            for (int i = layers; i >= 1; i--)
            {
                var shadowRect = Rectangle.Inflate(r, i, i);
                shadowRect.Offset(0, elevated ? i : 1);
                int a = Math.Max(4, alpha - i * 3);
                using var pen = new Pen(Color.FromArgb(a, KzTokens.Navy900));
                DrawRoundedBorder(g, pen, shadowRect, radius + i);
            }
        }

        // ── Measure text centered ─────────────────────────────
        public static void DrawCenteredText(Graphics g, string text, Font font, Color color,
            Rectangle bounds, StringAlignment h = StringAlignment.Center)
        {
            using var brush = new SolidBrush(color);
            var fmt = new StringFormat
            {
                Alignment = h,
                LineAlignment = StringAlignment.Center,
                Trimming = StringTrimming.EllipsisCharacter
            };
            g.DrawString(text, font, brush, bounds, fmt);
        }

        // ── Sidebar item gradient helper ──────────────────────
        public static void DrawSidebarItemHoverBg(Graphics g, Rectangle r)
        {
            using var brush = new LinearGradientBrush(
                r, Color.FromArgb(26, KzTokens.Orange500), Color.Transparent,
                LinearGradientMode.Horizontal);
            g.FillRectangle(brush, r);
        }
    }
}

