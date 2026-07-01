using System;
using System.ComponentModel;
using System.Drawing;
using Guna.UI2.WinForms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System numeric up-down — multiple variants/sizes.")]
    public class KzNumericUpDown : Guna2NumericUpDown
    {
        private KzNudVariant _variant = KzNudVariant.Default;
        private KzSize       _kzSize  = KzSize.Medium;
        private bool         _hasError;
        private string       _suffix  = string.Empty;

        [Category("•KZTEK"), Description("Visual variant."), DefaultValue(KzNudVariant.Default)]
        public KzNudVariant NudVariant
        {
            get => _variant;
            set { _variant = value; ApplyStyle(); }
        }

        [Category("•KZTEK"), Description("Control size."), DefaultValue(KzSize.Medium)]
        public KzSize KzSize
        {
            get => _kzSize;
            set { _kzSize = value; ApplySize(); }
        }

        [Category("•KZTEK"), DefaultValue(false)]
        public bool HasError
        {
            get => _hasError;
            set { _hasError = value; ApplyStyle(); }
        }

        [Category("•KZTEK"), Description("Increment per click."), DefaultValue(typeof(decimal), "1")]
        public decimal Step
        {
            get => Increment;
            set => Increment = Math.Max(1, value);
        }

        // Accepted for API compatibility; not rendered — Guna2NumericUpDown layout is fixed.
        [Category("•KZTEK"), DefaultValue(""), Browsable(false)]
        public string Suffix
        {
            get => _suffix;
            set => _suffix = value;
        }

        public KzNumericUpDown()
        {
            BorderRadius           = KzTokens.RadiusMd;
            BorderThickness        = 1;
            UpDownButtonBorderVisible = false;
            IndicateFocus          = true;
            Increment              = 1;
            Minimum                = 0;
            Maximum                = 999999;
            ApplySize();
        }

        private void ApplySize()
        {
            switch (_kzSize)
            {
                case KzSize.Small:
                    Height = KzTokens.HeightSm;
                    Font   = KzThemeHelper.GetFont(KzTokens.FontBody);
                    break;
                case KzSize.Large:
                    Height = KzTokens.HeightLg;
                    Font   = KzThemeHelper.GetFont(KzTokens.FontLg);
                    break;
                default:
                    Height = KzTokens.HeightMd;
                    Font   = KzThemeHelper.GetFont(KzTokens.FontMd);
                    break;
            }
            ApplyStyle();
        }

        private void ApplyStyle()
        {
            Color borderNormal  = _hasError ? KzTokens.Error : KzTokens.Divider;
            Color borderFocused = _hasError ? KzTokens.Error : KzTokens.Orange500;

            BorderColor               = borderNormal;
            FocusedState.BorderColor  = borderFocused;

            switch (_variant)
            {
                case KzNudVariant.Navy:
                    FillColor              = KzTokens.Navy900;
                    ForeColor              = KzTokens.White;
                    UpDownButtonFillColor  = KzTokens.Navy700;
                    UpDownButtonForeColor  = KzTokens.White;

                    FocusedState.FillColor             = KzTokens.Navy900;
                    FocusedState.ForeColor             = KzTokens.White;
                    FocusedState.UpDownButtonFillColor = KzTokens.Navy1000;
                    FocusedState.UpDownButtonForeColor = KzTokens.White;

                    DisabledState.BorderColor          = KzTokens.Navy700;
                    DisabledState.FillColor            = KzTokens.Navy900;
                    DisabledState.ForeColor            = KzTokens.Navy300;
                    DisabledState.UpDownButtonFillColor = KzTokens.Navy700;
                    DisabledState.UpDownButtonForeColor = KzTokens.Navy300;
                    break;

                case KzNudVariant.Accent:
                    FillColor              = KzTokens.White;
                    ForeColor              = KzTokens.Ink;
                    UpDownButtonFillColor  = KzTokens.Orange500;
                    UpDownButtonForeColor  = KzTokens.White;

                    FocusedState.FillColor             = KzTokens.White;
                    FocusedState.ForeColor             = KzTokens.Ink;
                    FocusedState.UpDownButtonFillColor = KzTokens.Orange600;
                    FocusedState.UpDownButtonForeColor = KzTokens.White;

                    DisabledState.BorderColor          = KzTokens.Border;
                    DisabledState.FillColor            = KzTokens.BgAlt;
                    DisabledState.ForeColor            = KzTokens.TextMuted;
                    DisabledState.UpDownButtonFillColor = KzTokens.Orange300;
                    DisabledState.UpDownButtonForeColor = KzTokens.White;
                    break;

                default: // Default
                    FillColor              = KzTokens.White;
                    ForeColor              = KzTokens.Ink;
                    UpDownButtonFillColor  = KzTokens.Navy100;
                    UpDownButtonForeColor  = KzTokens.Navy700;

                    FocusedState.FillColor             = KzTokens.White;
                    FocusedState.ForeColor             = KzTokens.Ink;
                    FocusedState.UpDownButtonFillColor = KzTokens.Navy300;
                    FocusedState.UpDownButtonForeColor = KzTokens.Navy900;

                    DisabledState.BorderColor          = KzTokens.Border;
                    DisabledState.FillColor            = KzTokens.BgAlt;
                    DisabledState.ForeColor            = KzTokens.TextMuted;
                    DisabledState.UpDownButtonFillColor = KzTokens.Navy100;
                    DisabledState.UpDownButtonForeColor = KzTokens.Navy300;
                    break;
            }
        }
    }
}
