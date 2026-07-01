namespace KztekComponent.Theme
{
    public enum KzButtonVariant
    {
        Primary,   // Navy bg, white text
        Accent,    // Orange bg, white text
        Secondary, // White bg, Navy border+text
        Ghost,     // Transparent, Navy text
        Danger     // Red bg, white text
    }

    public enum KzSize
    {
        Small,
        Medium,
        Large
    }

    public enum KzInputState
    {
        Default,
        Focus,
        Error,
        Disabled
    }

    public enum KzBadgeVariant
    {
        Success,
        Warning,
        Error,
        Info,
        Neutral,
        Accent
    }

    public enum KzBadgeType
    {
        StatusPill, // Rounded pill with optional dot
        Tag         // Small square badge (LPR, RFID style)
    }

    public enum KzNudVariant
    {
        Default, // White bg, Navy buttons
        Navy,    // Dark navy bg+buttons
        Accent   // Orange buttons
    }

    public enum KzNudLayout
    {
        Horizontal, // [−] | value | [+]
        Vertical    // [+] / value / [−]
    }

    public enum KzCardVariant
    {
        Default,    // White bg, border
        Dark,       // Navy bg (CTA)
        Feature     // White + icon header area
    }

    public enum KzDeltaDirection
    {
        Up,
        Down,
        Neutral
    }

    public enum KzLabelType
    {
        H1,          // 36px Bold — display heading
        H2,          // 28px Bold
        H3,          // 20px Bold
        Subheading,  // 16px Bold, Navy700
        Body,        // 13px Regular — default
        Small,       // 12px Regular
        Caption,     // 11px Regular, Muted
        Muted        // 13px Regular, Muted color
    }

    public enum KzGroupBoxVariant
    {
        Default,   // White bg, light border
        Filled,    // Gray-100 bg, light border
        Outlined   // Transparent bg, 2px border
    }

    public enum KzPictureSizeMode
    {
        Zoom,     // Preserve aspect ratio, fit within bounds (letterbox)
        Stretch,  // Fill bounds, ignore aspect ratio
        Center,   // Natural size, centered, clip if larger
        Fill,     // Preserve aspect ratio, cover entire area (crop)
        Tile      // Tile the image
    }

    public enum KzPictureShape
    {
        Rectangle, // Sharp corners
        Rounded,   // Rounded corners (CornerRadius property)
        Circle     // Clipped to min(Width, Height) circle
    }

    public enum KzPictureBorderVariant
    {
        None,    // No border
        Default, // Light gray, turns orange on hover
        Navy,    // Navy brand color
        Accent   // Orange accent
    }

    public enum KzCaptionPosition
    {
        None,   // No caption
        Top,    // Semi-transparent overlay bar at top
        Bottom  // Semi-transparent overlay bar at bottom
    }

    public enum KzCountDownVariant
    {
        Default,  // Navy bg, white text — primary branding
        Accent,   // Orange bg, white text
        Success,  // Green bg, white text
        Danger,   // Red bg, white text
        Light     // Light Navy bg, dark text
    }

    public enum KzCountDownMode
    {
        Full,      // DD : HH : MM : SS
        TimeOnly,  // Total HH : MM : SS (hours can exceed 23)
        Compact    // Total MM : SS (minutes can exceed 59)
    }
}
