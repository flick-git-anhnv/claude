using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System label — typed typography (H1, H2, H3, Subheading, Body, Small, Caption, Muted).")]
    public class KzLabel : Label
    {
        private KzLabelType _labelType = KzLabelType.Body;

        [Category("•KZTEK")]
        [DefaultValue(KzLabelType.Body)]
        public KzLabelType LabelType
        {
            get => _labelType;
            set { _labelType = value; ApplyStyle(); }
        }

        public KzLabel()
        {
            BackColor = Color.Transparent;
            ApplyStyle();
        }

        private void ApplyStyle()
        {
            ForeColor = KzTokens.Ink;

            switch (_labelType)
            {
                case KzLabelType.H1:
                    Font = KzThemeHelper.GetFont(KzTokens.FontH1, FontStyle.Bold);
                    break;
                case KzLabelType.H2:
                    Font = KzThemeHelper.GetFont(KzTokens.FontH2, FontStyle.Bold);
                    break;
                case KzLabelType.H3:
                    Font = KzThemeHelper.GetFont(KzTokens.FontH3, FontStyle.Bold);
                    break;
                case KzLabelType.Subheading:
                    Font      = KzThemeHelper.GetFont(KzTokens.FontLg, FontStyle.Bold);
                    ForeColor = KzTokens.Navy700;
                    break;
                case KzLabelType.Small:
                    Font = KzThemeHelper.GetFont(KzTokens.FontSm);
                    break;
                case KzLabelType.Caption:
                    Font      = KzThemeHelper.GetFont(KzTokens.FontXs);
                    ForeColor = KzTokens.TextMuted;
                    break;
                case KzLabelType.Muted:
                    Font      = KzThemeHelper.GetFont(KzTokens.FontBody);
                    ForeColor = KzTokens.TextMuted;
                    break;
                default: // Body
                    Font = KzThemeHelper.GetFont(KzTokens.FontBody);
                    break;
            }
        }
    }
}
