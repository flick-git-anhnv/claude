using Guna.UI2.WinForms;
using KztekComponent.Theme;
using System.ComponentModel;
using System.Windows.Forms;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System text input — Default, Focus, Error, Disabled states.")]
    public class KzTextBox : Guna2TextBox
    {
        private KzInputState _state = KzInputState.Default;

        [Category("•KZTEK")]
        [Description("Input state (Default, Focus, Error, Disabled).")]
        [DefaultValue(KzInputState.Default)]
        public KzInputState InputState
        {
            get { return _state; }
            set { _state = value; ApplyStyle(); }
        }

        public KzTextBox()
        {
            ApplyBaseStyle();
            ApplyStyle();
        }

        private void ApplyBaseStyle()
        {
            Height = KzTokens.HeightMd;
            BorderRadius = KzTokens.RadiusMd;
            Font = KzThemeHelper.GetFont(KzTokens.FontMd);
            ForeColor = KzTokens.Ink;
            PlaceholderForeColor = KzTokens.TextMuted;
            FillColor = KzTokens.White;
            Padding = new Padding(14, 0, 14, 0);
        }

        private void ApplyStyle()
        {
            switch (_state)
            {
                case KzInputState.Default:
                    BorderColor = KzTokens.Divider;
                    BorderThickness = 1;
                    Enabled = true;
                    FillColor = KzTokens.White;
                    ForeColor = KzTokens.Ink;
                    HoverState.BorderColor = KzTokens.Navy700;
                    HoverState.FillColor = KzTokens.White;
                    FocusedState.BorderColor = KzTokens.Orange500;
                    FocusedState.FillColor = KzTokens.White;
                    break;

                case KzInputState.Focus:
                    BorderColor = KzTokens.Orange500;
                    BorderThickness = 1;
                    Enabled = true;
                    FillColor = KzTokens.White;
                    ForeColor = KzTokens.Ink;
                    HoverState.BorderColor = KzTokens.Orange500;
                    HoverState.FillColor = KzTokens.White;
                    FocusedState.BorderColor = KzTokens.Orange500;
                    FocusedState.FillColor = KzTokens.White;
                    break;

                case KzInputState.Error:
                    BorderColor = KzTokens.Error;
                    BorderThickness = 1;
                    Enabled = true;
                    FillColor = KzTokens.White;
                    ForeColor = KzTokens.Ink;
                    HoverState.BorderColor = KzTokens.Error;
                    HoverState.FillColor = KzTokens.White;
                    FocusedState.BorderColor = KzTokens.Error;
                    FocusedState.FillColor = KzTokens.White;
                    break;

                case KzInputState.Disabled:
                    BorderColor = KzTokens.Border;
                    BorderThickness = 1;
                    Enabled = false;
                    FillColor = KzTokens.BgAlt;
                    ForeColor = KzTokens.TextMuted;
                    break;
            }

            Invalidate();
        }
    }
}
