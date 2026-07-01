using System.Drawing;

namespace KztekComponent.Theme
{
    public static class KzTokens
    {
        // ── Brand palette ─────────────────────────────────────
        public static readonly Color Navy900  = Color.FromArgb(0x25, 0x1C, 0x53); // #251C53 — primary
        public static readonly Color Navy1000 = Color.FromArgb(0x1A, 0x13, 0x40); // #1A1340 — hover
        public static readonly Color Navy700  = Color.FromArgb(0x4A, 0x3F, 0x8C); // #4A3F8C — sub-heading
        public static readonly Color Navy300  = Color.FromArgb(0xB8, 0xB3, 0xD6); // #B8B3D6 — disabled/soft
        public static readonly Color Navy100  = Color.FromArgb(0xF5, 0xF3, 0xFA); // #F5F3FA — hover wash

        public static readonly Color Orange500 = Color.FromArgb(0xF0, 0x59, 0x22); // #F05922 — accent/CTA
        public static readonly Color Orange600 = Color.FromArgb(0xD9, 0x48, 0x17); // #D94817 — hover
        public static readonly Color Orange300 = Color.FromArgb(0xFF, 0xAA, 0x80); // #FFAA80 — soft hover

        // ── Neutrals ──────────────────────────────────────────
        public static readonly Color White     = Color.FromArgb(0xFF, 0xFF, 0xFF);
        public static readonly Color BgDefault = Color.FromArgb(0xFF, 0xFF, 0xFF);
        public static readonly Color BgAlt     = Color.FromArgb(0xFA, 0xFA, 0xFA);
        public static readonly Color Border    = Color.FromArgb(0xE5, 0xE5, 0xE5);
        public static readonly Color Divider   = Color.FromArgb(0xCB, 0xCB, 0xCB);
        public static readonly Color Text      = Color.FromArgb(0x4A, 0x4A, 0x4A);
        public static readonly Color TextMuted = Color.FromArgb(0x6B, 0x6B, 0x6B);
        public static readonly Color Ink       = Color.FromArgb(0x1A, 0x1A, 0x1A);

        // ── Status ────────────────────────────────────────────
        public static readonly Color Success   = Color.FromArgb(0x16, 0xA3, 0x4A);
        public static readonly Color SuccessBg = Color.FromArgb(0xDC, 0xFC, 0xE7);
        public static readonly Color SuccessFg = Color.FromArgb(0x16, 0x65, 0x34);

        public static readonly Color Warning   = Color.FromArgb(0xF5, 0x9E, 0x0B);
        public static readonly Color WarningBg = Color.FromArgb(0xFE, 0xF3, 0xC7);
        public static readonly Color WarningFg = Color.FromArgb(0x92, 0x40, 0x0E);

        public static readonly Color Error     = Color.FromArgb(0xDC, 0x26, 0x26);
        public static readonly Color ErrorBg   = Color.FromArgb(0xFE, 0xE2, 0xE2);
        public static readonly Color ErrorFg   = Color.FromArgb(0x99, 0x1B, 0x1B);

        public static readonly Color Info      = Color.FromArgb(0x25, 0x63, 0xEB);
        public static readonly Color InfoBg    = Color.FromArgb(0xDB, 0xEA, 0xFE);
        public static readonly Color InfoFg    = Color.FromArgb(0x1E, 0x40, 0xAF);

        // ── Radius ────────────────────────────────────────────
        public const int RadiusSm   = 4;
        public const int RadiusMd   = 8;
        public const int RadiusLg   = 12;
        public const int RadiusXl   = 16;
        public const int RadiusPill = 999;

        // ── Control heights by size ───────────────────────────
        public const int HeightSm   = 32;
        public const int HeightMd   = 40;
        public const int HeightLg   = 48;

        // ── Button padding (H) by size ────────────────────────
        public const int BtnPadSmH  = 14;
        public const int BtnPadMdH  = 22;
        public const int BtnPadLgH  = 28;

        // ── Font sizes ────────────────────────────────────────
        public const float FontXs   = 11f;
        public const float FontSm   = 12f;
        public const float FontBody  = 13f;
        public const float FontMd   = 14f;
        public const float FontLg   = 16f;
        public const float FontH3   = 20f;
        public const float FontH2   = 28f;
        public const float FontH1   = 36f;
        public const float FontDisplay = 40f;

        // ── Font family ───────────────────────────────────────
        public const string FontSans = "Inter";
        public const string FontFallback = "Segoe UI";

        // ── Sidebar ───────────────────────────────────────────
        public const int SidebarWidth     = 220;
        public const int SidebarItemH     = 40;
        public const int SidebarPadH      = 20;
        public const int SidebarActiveBar = 3;

        // ── KPI accent bar ────────────────────────────────────
        public const int KpiBarW = 32;
        public const int KpiBarH = 3;

        // ── NUD ───────────────────────────────────────────────
        public const int NudBtnWidthSm = 30;
        public const int NudBtnWidthMd = 36;
        public const int NudBtnWidthLg = 44;
        public const int NudValueWidthSm = 60;
        public const int NudValueWidthMd = 72;
        public const int NudValueWidthLg = 80;

        // ── Opacity for badge hover ───────────────────────────
        public const int BadgeHoverElevation = 1; // px translateY analog (unused in WinForms, kept for docs)
    }
}
