using System;
using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using Guna.UI2.WinForms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System button — Primary, Accent, Secondary, Ghost, Danger variants.")]
    public class KzButton : Guna2Button
    {
        private KzButtonVariant _variant = KzButtonVariant.Primary;
        private KzSize _kzSize = KzSize.Medium;
        private Keys _shortcutKeys = Keys.None;
        private Form _parentForm;

        [Category("•KZTEK")]
        [Description("Visual variant of the button.")]
        [DefaultValue(KzButtonVariant.Primary)]
        public KzButtonVariant Variant
        {
            get { return _variant; }
            set { _variant = value; ApplyStyle(); }
        }

        [Category("•KZTEK")]
        [Description("Size of the button (Small=32px, Medium=40px, Large=48px).")]
        [DefaultValue(KzSize.Medium)]
        public KzSize KzSize
        {
            get { return _kzSize; }
            set { _kzSize = value; ApplyStyle(); }
        }

        [Category("•KZTEK")]
        [Description("Keyboard shortcut that triggers this button click (e.g. Keys.Control | Keys.S).")]
        [DefaultValue(Keys.None)]
        public Keys ShortcutKeys
        {
            get => _shortcutKeys;
            set => _shortcutKeys = value;
        }

        public KzButton()
        {
            ApplyStyle();
        }

        private void ApplyStyle()
        {
            // ── Size ─────────────────────────────────────────
            int h, padH;
            float fontSize;
            if (_kzSize == KzSize.Small)  { h = KzTokens.HeightSm; padH = KzTokens.BtnPadSmH; fontSize = KzTokens.FontBody; }
            else if (_kzSize == KzSize.Large) { h = KzTokens.HeightLg; padH = KzTokens.BtnPadLgH; fontSize = KzTokens.FontLg; }
            else                           { h = KzTokens.HeightMd; padH = KzTokens.BtnPadMdH; fontSize = KzTokens.FontMd; }

            Height = h;
            Padding = new Padding(padH, 0, padH, 0);

            // ── Shared ────────────────────────────────────────
            BorderRadius = KzTokens.RadiusMd;
            Font = KzThemeHelper.GetFont(fontSize, FontStyle.Bold);
            TextAlign = HorizontalAlignment.Center;
            ImageAlign = HorizontalAlignment.Left;
            BorderThickness = 0;
            ShadowDecoration.Enabled = false;

            // ── Variant-specific ──────────────────────────────
            switch (_variant)
            {
                case KzButtonVariant.Primary:
                    FillColor = KzTokens.Navy900;
                    ForeColor = KzTokens.White;
                    HoverState.FillColor = KzTokens.Navy1000;
                    HoverState.ForeColor = KzTokens.White;
                    HoverState.BorderColor = Color.Transparent;
                    BorderColor = Color.Transparent;
                    break;

                case KzButtonVariant.Accent:
                    FillColor = KzTokens.Orange500;
                    ForeColor = KzTokens.White;
                    HoverState.FillColor = KzTokens.Orange600;
                    HoverState.ForeColor = KzTokens.White;
                    HoverState.BorderColor = Color.Transparent;
                    BorderColor = Color.Transparent;
                    break;

                case KzButtonVariant.Secondary:
                    FillColor = KzTokens.White;
                    ForeColor = KzTokens.Navy900;
                    BorderColor = KzTokens.Navy900;
                    BorderThickness = 2;
                    HoverState.FillColor = KzTokens.Navy100;
                    HoverState.ForeColor = KzTokens.Navy900;
                    HoverState.BorderColor = KzTokens.Navy700;
                    break;

                case KzButtonVariant.Ghost:
                    FillColor = Color.Transparent;
                    ForeColor = KzTokens.Navy900;
                    BorderColor = Color.Transparent;
                    HoverState.FillColor = KzTokens.Navy100;
                    HoverState.ForeColor = KzTokens.Navy900;
                    HoverState.BorderColor = Color.Transparent;
                    break;

                case KzButtonVariant.Danger:
                    FillColor = KzTokens.Error;
                    ForeColor = KzTokens.White;
                    BorderColor = Color.Transparent;
                    HoverState.FillColor = Color.FromArgb(0xB9, 0x1C, 0x1C);
                    HoverState.ForeColor = KzTokens.White;
                    HoverState.BorderColor = Color.Transparent;
                    break;
            }

            // ── Disabled ──────────────────────────────────────
            if (!Enabled)
            {
                DisabledState.FillColor = KzTokens.Navy300;
                DisabledState.ForeColor = KzTokens.White;
                DisabledState.BorderColor = Color.Transparent;
            }

            Invalidate();
        }

        protected override void OnEnabledChanged(EventArgs e)
        {
            base.OnEnabledChanged(e);
            ApplyStyle();
        }

        protected override void OnHandleCreated(EventArgs e)
        {
            base.OnHandleCreated(e);
            AttachToParentForm();
        }

        protected override void OnParentChanged(EventArgs e)
        {
            base.OnParentChanged(e);
            if (IsHandleCreated) AttachToParentForm();
        }

        private void AttachToParentForm()
        {
            Form newForm = FindForm();
            if (newForm == _parentForm) return;

            if (_parentForm != null)
            {
                _parentForm.KeyDown -= ParentFormKeyDown;
                _parentForm = null;
            }

            if (newForm != null)
            {
                _parentForm = newForm;
                newForm.KeyPreview = true;
                newForm.KeyDown += ParentFormKeyDown;
            }
        }

        private void ParentFormKeyDown(object sender, KeyEventArgs e)
        {
            if (_shortcutKeys != Keys.None && e.KeyData == _shortcutKeys && Enabled && Visible)
            {
                PerformClick();
                e.Handled = true;
                e.SuppressKeyPress = true;
            }
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && _parentForm != null)
            {
                _parentForm.KeyDown -= ParentFormKeyDown;
                _parentForm = null;
            }
            base.Dispose(disposing);
        }
    }
}
