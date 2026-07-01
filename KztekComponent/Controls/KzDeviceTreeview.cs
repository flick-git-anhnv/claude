using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Text;
using System.Windows.Forms;
using KztekComponent.Theme;

namespace KztekComponent.Controls
{
    // ── KzDeviceTreeview ──────────────────────────────────────────────────────

    [ToolboxItem(true)]
    [Category("•KZTEK")]
    [Description("KZTEK Design System device hierarchy tree — cameras, access control, IoT. "
               + "Shows online/offline status dots per node.")]
    public class KzDeviceTreeview : TreeView
    {
        // ── Public enums ──────────────────────────────────────────────────────

        public enum KzNodeType
        {
            Group,
            Camera,
            DoorController,
            Barrier,
            Sensor,
            Intercom,
            NVR,
            Generic,
        }

        public enum KzDeviceStatus
        {
            Unknown,
            Online,
            Offline,
            Warning,
        }

        // ── Events ────────────────────────────────────────────────────────────

        [Category("•KZTEK")]
        [Description("Fired when the user selects a node.")]
        public event System.EventHandler<TreeNode> DeviceSelected;

        // ── Node metadata (kept outside TreeNode to avoid coupling) ───────────

        private sealed class NodeMeta
        {
            public KzNodeType Type;
            public KzDeviceStatus Status;
            public string DeviceId;
        }

        private readonly Dictionary<TreeNode, NodeMeta> _meta = new Dictionary<TreeNode, NodeMeta>();

        // ── Layout constants ──────────────────────────────────────────────────

        private const int DotSize = 7;
        private const int DotPadRight = 8;
        private const int AccentBarW = 3;

        // ── Constructor ───────────────────────────────────────────────────────

        public KzDeviceTreeview()
        {
            DrawMode = TreeViewDrawMode.OwnerDrawText;
            FullRowSelect = true;
            HideSelection = false;
            HotTracking = true;
            ShowLines = true;
            ShowRootLines = false;
            ShowPlusMinus = true;
            BorderStyle = BorderStyle.None;
            BackColor = KzTokens.White;
            ForeColor = KzTokens.Text;
            Font = new Font(KzTokens.FontFallback, KzTokens.FontSm);
            ItemHeight = 28;
            Indent = 16;
            LineColor = KzTokens.Border;

            DrawNode += OnDrawNode;
            AfterSelect += (_, e) => DeviceSelected?.Invoke(this, e.Node);
        }

        // ── Public API ────────────────────────────────────────────────────────

        /// <summary>Add a group/folder node. <paramref name="parent"/> = null → root level.</summary>
        public TreeNode AddGroup(string name, TreeNode parent = null)
        {
            var node = new TreeNode(name);
            _meta[node] = new NodeMeta { Type = KzNodeType.Group, Status = KzDeviceStatus.Unknown };
            AddToCollection(node, parent);
            return node;
        }

        /// <summary>Add a device leaf node.</summary>
        public TreeNode AddDevice(
            string name,
            KzNodeType type,
            KzDeviceStatus status = KzDeviceStatus.Unknown,
            TreeNode parent = null,
            string deviceId = null)
        {
            var node = new TreeNode(name);
            _meta[node] = new NodeMeta { Type = type, Status = status, DeviceId = deviceId };
            AddToCollection(node, parent);
            return node;
        }

        /// <summary>Update the status dot of an existing node and refresh the row.</summary>
        public void SetStatus(TreeNode node, KzDeviceStatus status)
        {
            if (_meta.TryGetValue(node, out var m)) m.Status = status;
            Invalidate(GetNodeBounds(node, full: true));
        }

        public KzDeviceStatus GetStatus(TreeNode node)
            => _meta.TryGetValue(node, out var m) ? m.Status : KzDeviceStatus.Unknown;

        public KzNodeType GetNodeType(TreeNode node)
            => _meta.TryGetValue(node, out var m) ? m.Type : KzNodeType.Generic;

        public string GetDeviceId(TreeNode node)
            => _meta.TryGetValue(node, out var m) ? m.DeviceId : null;

        // ── Drawing ───────────────────────────────────────────────────────────

        private void OnDrawNode(object sender, DrawTreeNodeEventArgs e)
        {
            var g = e.Graphics;
            var node = e.Node;
            if (node == null) { e.DrawDefault = true; return; }

            bool selected = (e.State & TreeNodeStates.Selected) != 0;
            bool hot = (e.State & TreeNodeStates.Hot) != 0;
            bool focused = Focused;

            // Full-row bounds (override e.Bounds which is text-only in OwnerDrawText)
            int rowW = ClientSize.Width > 0 ? ClientSize.Width : 1;
            int rowH = e.Bounds.Height > 0 ? e.Bounds.Height : 1;
            var row = new Rectangle(0, e.Bounds.Y, rowW, rowH);

            // Guard: skip custom drawing until control has real dimensions
            if (ClientSize.Width <= 0 || e.Bounds.Height <= 0) { e.DrawDefault = true; return; }

            // Expand the Graphics clip to cover the full row
            g.SetClip(row, CombineMode.Replace);

            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.TextRenderingHint = TextRenderingHint.ClearTypeGridFit;

            // 1. Background
            Color bg = selected
                ? (focused ? KzTokens.Navy100 : KzTokens.BgAlt)
                : hot ? KzTokens.BgAlt
                : KzTokens.White;
            using (var bgBrush = new SolidBrush(bg))
                g.FillRectangle(bgBrush, row);

            // 2. Orange left-accent bar on selected row
            if (selected && focused)
            {
                using var accent = new SolidBrush(KzTokens.Orange500);
                g.FillRectangle(accent, new Rectangle(0, row.Y, AccentBarW, row.Height));
            }

            _meta.TryGetValue(node, out var meta);
            var nodeType = meta?.Type ?? KzNodeType.Generic;
            var status = meta?.Status ?? KzDeviceStatus.Unknown;

            // 3. Type icon + label
            string icon = TypeIcon(nodeType);
            string label = icon + "  " + node.Text;

            // Do NOT dispose: font is owned by the node or the TreeView
            Font font = node.NodeFont ?? Font;
            Color textColor = selected ? KzTokens.Navy900 : KzTokens.Text;
            if (!Enabled) textColor = KzTokens.TextMuted;
            using var textBrush = new SolidBrush(textColor);

            float ty = e.Bounds.Y + (e.Bounds.Height - font.GetHeight(g)) / 2f;
            g.DrawString(label, font, textBrush, (float)e.Bounds.X, ty);

            // 4. Status dot — only for non-group nodes
            if (nodeType != KzNodeType.Group)
            {
                Color dotColor = StatusColor(status);
                int dotX = row.Right - DotSize - DotPadRight;
                int dotY = row.Y + (row.Height - DotSize) / 2;
                using var dotBrush = new SolidBrush(dotColor);
                g.FillEllipse(dotBrush, dotX, dotY, DotSize, DotSize);

                // Thin outline for better visibility on white bg
                using var dotPen = new Pen(Color.FromArgb(40, 0, 0, 0), 0.5f);
                g.DrawEllipse(dotPen, dotX, dotY, DotSize, DotSize);
            }

            g.ResetClip();
        }

        // ── Static helpers ────────────────────────────────────────────────────

        private static string TypeIcon(KzNodeType t) => t switch
        {
            KzNodeType.Group => "▸",
            KzNodeType.Camera => "◉",
            KzNodeType.DoorController => "⬡",
            KzNodeType.Barrier => "⬛",
            KzNodeType.Sensor => "◈",
            KzNodeType.Intercom => "◑",
            KzNodeType.NVR => "▣",
            _ => "◦",
        };

        private static Color StatusColor(KzDeviceStatus s) => s switch
        {
            KzDeviceStatus.Online => KzTokens.Success,
            KzDeviceStatus.Offline => KzTokens.TextMuted,
            KzDeviceStatus.Warning => KzTokens.Warning,
            _ => KzTokens.Border,
        };

        // ── Private helpers ───────────────────────────────────────────────────

        private void AddToCollection(TreeNode node, TreeNode parent)
        {
            if (parent != null) parent.Nodes.Add(node);
            else Nodes.Add(node);
        }

        private Rectangle GetNodeBounds(TreeNode node, bool full)
        {
            if (node == null) return Rectangle.Empty;
            var b = node.Bounds;
            return full ? new Rectangle(0, b.Y, ClientSize.Width, b.Height) : b;
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing) _meta.Clear();
            base.Dispose(disposing);
        }
    }
}
