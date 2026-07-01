using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using Guna.UI2.WinForms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System dropdown select — Default, Error, Disabled states.")]
    public class KzCombobox : Guna2ComboBox
    {
        private KzInputState _state = KzInputState.Default;

        [Category("•KZTEK")]
        [Description("Input state (Default, Error, Disabled).")]
        [DefaultValue(KzInputState.Default)]
        public KzInputState InputState
        {
            get { return _state; }
            set { _state = value; ApplyStyle(); }
        }

        public KzCombobox()
        {
            ApplyBaseStyle();
            ApplyStyle();

            GotFocus  += (_, __) => { if (_state == KzInputState.Default) SetActiveBorder(true); };
            LostFocus += (_, __) => { if (_state == KzInputState.Default) SetActiveBorder(false); };
        }

        private void ApplyBaseStyle()
        {
            Height       = KzTokens.HeightMd;
            BorderRadius = KzTokens.RadiusMd;
            Font         = KzThemeHelper.GetFont(KzTokens.FontMd);
            ForeColor    = KzTokens.Ink;
            FillColor    = KzTokens.White;
            ItemHeight   = KzTokens.HeightSm;
            DropDownStyle = ComboBoxStyle.DropDownList;
        }

        private void SetActiveBorder(bool active)
        {
            BorderColor = active ? KzTokens.Orange500 : KzTokens.Divider;
            Invalidate();
        }

        private void ApplyStyle()
        {
            switch (_state)
            {
                case KzInputState.Default:
                    BorderColor      = KzTokens.Divider;
                    BorderThickness  = 1;
                    Enabled          = true;
                    FillColor        = KzTokens.White;
                    ForeColor        = KzTokens.Ink;
                    HoverState.BorderColor   = KzTokens.Navy700;
                    HoverState.FillColor     = KzTokens.White;
                    FocusedState.BorderColor = KzTokens.Orange500;
                    FocusedState.FillColor   = KzTokens.White;
                    break;

                case KzInputState.Focus:
                    BorderColor      = KzTokens.Orange500;
                    BorderThickness  = 1;
                    Enabled          = true;
                    FillColor        = KzTokens.White;
                    ForeColor        = KzTokens.Ink;
                    HoverState.BorderColor   = KzTokens.Orange500;
                    HoverState.FillColor     = KzTokens.White;
                    FocusedState.BorderColor = KzTokens.Orange500;
                    FocusedState.FillColor   = KzTokens.White;
                    break;

                case KzInputState.Error:
                    BorderColor      = KzTokens.Error;
                    BorderThickness  = 1;
                    Enabled          = true;
                    FillColor        = KzTokens.White;
                    ForeColor        = KzTokens.Ink;
                    HoverState.BorderColor   = KzTokens.Error;
                    HoverState.FillColor     = KzTokens.White;
                    FocusedState.BorderColor = KzTokens.Error;
                    FocusedState.FillColor   = KzTokens.White;
                    break;

                case KzInputState.Disabled:
                    BorderColor     = KzTokens.Border;
                    BorderThickness = 1;
                    Enabled         = false;
                    FillColor       = KzTokens.BgAlt;
                    ForeColor       = KzTokens.TextMuted;
                    break;
            }

            Invalidate();
        }
    }
}
