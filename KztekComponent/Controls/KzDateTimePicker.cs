using System;
using System.ComponentModel;
using System.Drawing;
using Guna.UI2.WinForms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System date/time picker — bordered, focus-orange.")]
    public class KzDateTimePicker : Guna2DateTimePicker
    {
        public KzDateTimePicker()
        {
            Size             = new Size(240, KzTokens.HeightMd);
            Font             = KzThemeHelper.GetFont(KzTokens.FontMd);
            Cursor           = System.Windows.Forms.Cursors.Hand;

            FillColor        = KzTokens.White;
            ForeColor        = KzTokens.Ink;
            BorderColor      = KzTokens.Border;
            BorderThickness  = 1;
            BorderRadius     = KzTokens.RadiusMd;
            FocusedColor     = KzTokens.Orange500;
            IndicateFocus    = true;

            Format           = System.Windows.Forms.DateTimePickerFormat.Custom;
            CustomFormat     = "dd/MM/yyyy";

            HoverState.BorderColor = KzTokens.Navy700;
            HoverState.FillColor   = KzTokens.White;
        }

        protected override void OnEnabledChanged(EventArgs e)
        {
            base.OnEnabledChanged(e);
            FillColor   = Enabled ? KzTokens.White    : KzTokens.Navy100;
            ForeColor   = Enabled ? KzTokens.Ink      : KzTokens.Navy300;
            BorderColor = Enabled ? KzTokens.Border   : KzTokens.Border;
            Invalidate();
        }
    }
}
