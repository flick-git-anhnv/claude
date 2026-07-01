using Guna.UI2.WinForms;
using KztekComponent.Theme;
using System;
using System.ComponentModel;
using System.Drawing;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System toggle switch — Navy on, Gray off, animated.")]
    public class KzToggleSwitch : Guna2ToggleSwitch
    {
        public KzToggleSwitch()
        {
            Size     = new Size(60, 30);
            Cursor   = System.Windows.Forms.Cursors.Hand;
            Animated = true;
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
                CheckedState.InnerColor  = KzTokens.White;
                CheckedState.BorderColor = KzTokens.Navy900;

                UncheckedState.FillColor   = KzTokens.Divider;
                UncheckedState.InnerColor  = KzTokens.White;
                UncheckedState.BorderColor = KzTokens.Divider;
            }
            else
            {
                CheckedState.FillColor   = KzTokens.Navy300;
                CheckedState.InnerColor  = KzTokens.White;
                CheckedState.BorderColor = KzTokens.Navy300;

                UncheckedState.FillColor   = KzTokens.Navy100;
                UncheckedState.InnerColor  = KzTokens.Navy300;
                UncheckedState.BorderColor = KzTokens.Border;
            }

            Invalidate();
        }
    }
}
