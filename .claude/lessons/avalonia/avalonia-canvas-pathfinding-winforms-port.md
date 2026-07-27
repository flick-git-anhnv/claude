---
name: avalonia-canvas-pathfinding-winforms-port
description: Port thuật toán tìm đường WinForms→Avalonia: dùng foot-on-edge thay vì nearest-vertex để path liên tục
metadata:
  type: feedback
category: avalonia
tags: [canvas, pathfinding, BFS, perpendicular-foot, WinForms-port, map]
severity: high
created: 2026-06-27
project-origin: iPGSv4 (branch ccu-avalonia) — MapDetailWindow
---

# Avalonia Canvas: Pathfinding Foot-on-Edge (port từ WinForms)

## Vấn đề

Khi port thuật toán tìm đường từ WinForms sang Avalonia, ban đầu dùng "nearest vertex" (tìm đỉnh gần nhất) để bắt đầu BFS. Kết quả:

- Đường đi **bị đứt đoạn** — connector entity→vertex trỏ vào *tâm vertex*, không trỏ vào điểm trên đường thực tế
- Đường đi **không liên tiếp** — thiếu đoạn nối từ entity đến điểm chân vuông góc trên road segment

## Root cause

WinForms (`frmMapDetail.cs`) dùng **"nearest edge"** (đoạn thẳng gần nhất), không phải nearest vertex:

```csharp
// WinForms đúng:
Tuple<ucItemInMap, ucItemInMap> shortestEdge = GetShortestEdge(entity, edges);
// → tìm edge gần nhất bằng khoảng cách từ entity đến foot của đường thẳng
Point closestPoint = FindClosestPoint(entity, shortestEdge);
// → foot = điểm gần nhất trên đoạn shortestEdge từ entity (perpendicular foot)
```

Port sai trong Avalonia:
```csharp
// ❌ SAI — tìm vertex gần nhất → path bị đứt
string? startV = GetNearestVertex(startId);
// Connector đến vertex.center → không khớp với điểm trên road
```

## Fix bắt buộc

Polyline hoàn chỉnh phải là:
```
entity.center → foot_on_nearest_edge → [intermediate vertex centers] → foot_on_end_edge → entity.center
```

### Các hàm cần có

```csharp
// 1. Tìm edge gần nhất theo foot distance
private int NearestEdgeIdx(Point p)
// → duyệt _edgeLines, gọi FootOnSegment() cho mỗi edge, lấy index có dist nhỏ nhất

// 2. Tính foot của entity lên edge (= FindClosestPoint WinForms)
private Point FootOnEdge(Point entityCenter, string v1Id, string v2Id)
// → gọi FootOnSegment() đã có sẵn

// 3. Build polyline (= FindShortestRoad WinForms)
private List<Point> BuildRoadPoints(startC, sFoot, sIdx, sV1, sV2, endC, eFoot, eIdx, eV1, eV2)
// Same edge → [start, sFoot, eFoot, end]
// Khác edge → thử 4 combo (sV1/sV2 × eV1/eV2), BFS từ sVInner đến eVGoal, chọn ngắn nhất

// 4. BFS qua _edgeLines (không chỉ vertex-to-vertex)
private List<string>? BfsPath(string from, string to)

// 5. Vẽ polyline xanh liên tục + arrowhead tại điểm cuối
private void DrawGreenPolyline(List<Point> pts)
// → StreamGeometry với nhiều LineTo, + BuildTipArrow tại pts[^1]
```

### Chiều traversal startEdge (quan trọng)

Khi edges khác nhau, path phải traverse startEdge trước rồi mới tiếp:
- `sFoot` nằm trên startEdge giữa sV1 và sV2
- Road đi từ `sFoot` về phía `sVInner` (một trong hai endpoint)
- `sVInner` trở thành đỉnh đầu tiên trong BFS

Phải thử **cả 2 chiều** (sV1→sV2 và sV2→sV1) và cả 2 endpoint của endEdge → 4 combo, chọn ngắn nhất.

## Pattern hoàn chỉnh (Avalonia)

```csharp
private void RunPathfinding(string startId, string endId)
{
    // 1. Tìm nearest edge (không phải vertex)
    int sIdx = NearestEdgeIdx(startC);
    Point sFoot = FootOnEdge(startC, sV1, sV2);

    // 2. Hide tất cả edges + ZoneConnTag
    foreach (var edge in _edgeLines) edge.path.IsVisible = false;

    // 3. Build polyline và vẽ 1 đường xanh liên tục
    var pts = BuildRoadPoints(...);
    DrawGreenPolyline(pts);  // KHÔNG highlight từng edge riêng lẻ
}
```

## Điểm khác biệt so với WinForms

| Aspect | WinForms | Avalonia |
|---|---|---|
| Path output | `List<List<Point>>` vẽ trong Paint | `StreamGeometry` thêm vào Canvas |
| ZoneConn arrows | Luôn vẽ trong Paint | Ẩn trong path check, restore khi clear |
| Edge highlight | Không ẩn edges | Ẩn tất cả `_edgeLines` khi check |
| Arrowhead | Custom DrawLine | `BuildTipArrow()` + filled Path |

## Dấu hiệu nhận biết lỗi

- Path vẽ ra bị đứt đoạn (không liên tiếp)
- Đường xanh có "gap" giữa entity và road
- Mũi tên đỏ (ZoneConnTag) vẫn hiện khi đang check path
