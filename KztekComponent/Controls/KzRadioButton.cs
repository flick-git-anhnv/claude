using System;
using System.ComponentModel;
using System.Drawing;
using Guna.UI2.WinForms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System radio button — Navy checked, border unchecked.")]
    public class KzRadioButton : Guna2RadioButton
    {
        public KzRadioButton()
        {
            Font   = KzThemeHelper.GetFont(KzTokens.FontMd);
            Cursor = System.Windows.Forms.Cursors.Hand;
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
                CheckedState.FillColor   = KzTokens.Navy900;
                CheckedState.BorderColor = KzTokens.Navy900;
                CheckedState.InnerColor  = KzTokens.White;

                UncheckedState.FillColor   = KzTokens.White;
                UncheckedState.BorderColor = KzTokens.Divider;
                UncheckedState.InnerColor  = KzTokens.White;
            }
            else
            {
                CheckedState.FillColor   = KzTokens.Navy100;
                CheckedState.BorderColor = KzTokens.Border;
                CheckedState.InnerColor  = KzTokens.Navy300;

                UncheckedState.FillColor   = KzTokens.Navy100;
                UncheckedState.BorderColor = KzTokens.Border;
                UncheckedState.InnerColor  = KzTokens.Navy100;
            }

            Invalidate();
        }
    }
}
