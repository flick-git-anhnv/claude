using System;
using System.ComponentModel;
using System.Drawing;
using Guna.UI2.WinForms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System checkbox — Navy checked, border unchecked, animated.")]
    public class KzCheckBox : Guna2CheckBox
    {
        public KzCheckBox()
        {
            Font     = KzThemeHelper.GetFont(KzTokens.FontMd);
            Cursor   = System.Windows.Forms.Cursors.Hand;
            Animated = true;
            this.AutoSize = true;
            ApplyColors();
        }

        protected override void OnEnabledChanged(EventArgs e)
        {
            base.OnEnabledChanged(e);
            ApplyColors();
        }

        private void ApplyColors()
        {
            if (Enabled)
            {
                CheckMarkColor = KzTokens.White;

                CheckedState.FillColor       = KzTokens.Navy900;
                CheckedState.BorderColor     = KzTokens.Navy900;
                CheckedState.BorderThickness = 0;
                CheckedState.BorderRadius    = KzTokens.RadiusSm;

                UncheckedState.FillColor       = KzTokens.White;
                UncheckedState.BorderColor     = KzTokens.Divider;
                UncheckedState.BorderThickness = 2;
                UncheckedState.BorderRadius    = KzTokens.RadiusSm;
            }
            else
            {
                CheckMarkColor = KzTokens.Navy300;

                CheckedState.FillColor       = KzTokens.Navy100;
                CheckedState.BorderColor     = KzTokens.Border;
                CheckedState.BorderThickness = 0;
                CheckedState.BorderRadius    = KzTokens.RadiusSm;

                UncheckedState.FillColor       = KzTokens.Navy100;
                UncheckedState.BorderColor     = KzTokens.Border;
                UncheckedState.BorderThickness = 2;
                UncheckedState.BorderRadius    = KzTokens.RadiusSm;
            }

            Invalidate();
        }
    }
}
