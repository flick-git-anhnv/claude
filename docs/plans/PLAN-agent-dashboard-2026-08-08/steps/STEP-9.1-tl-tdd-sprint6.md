---
step: "9.1"
plan: ../PLAN-MASTER.md
agent: tech-lead
status: done
completed_at: "2026-08-08 08:56"
deps: []
---

# STEP 9.1 — Technical Design Sprint 6: Redesign Aggregate view + Sync active status

## Input nhận
- Ảnh phản hồi từ người dùng chỉ ra sự khác biệt về trạng thái hoạt động giữa session view và aggregate view.
- Yêu cầu thiết kế giao diện Aggregate view dạng Thẻ (Cards) giống session view.

## Nhiệm vụ & Giải pháp thiết kế

### 1. Đồng bộ trạng thái Đang chạy (Active Status Sync)
- **Vấn đề:** Giao diện Session báo `RUNNING` vì parent session đang chạy, nhưng Aggregate view báo `—` hoạt động vì chỉ đếm child sessions (subagents) đang `Running`.
- **Giải pháp:** Trong `get_pipeline_aggregate` ([db.py](file:///c:/Users/nguye/Desktop/Claude-Git/claude/tools/agent-dashboard/backend/agent_dashboard/db.py)), khi `group_by == "project"`, `active_now` sẽ được đếm thông qua subquery:
  ```sql
  (SELECT COUNT(*) FROM sessions s3 WHERE s3.project = sessions.project AND s3.state = 'Running') AS active_now
  ```
  Điều này đảm bảo dự án được báo "đang chạy" nếu phiên chính (Dispatcher) hoặc bất kỳ subagent nào thuộc dự án đó đang chạy.

### 2. Thiết kế API Roster Dự án (Project Pipeline Roster)
- Khi `group_by == "project"`, mỗi dự án cần trả kèm thông tin danh sách subagents đã tham gia để frontend render chuỗi pipeline.
- Thêm thuộc tính `project_roster` trong mỗi entry dự án trả về từ backend:
  ```json
  "project_roster": [
    {
      "role": "senior-developer",
      "display_name": "Senior Developer",
      "call_count": 5,
      "total_tokens": {"input": 100, "output": 200}
    }
  ]
  ```

### 3. Thiết kế lại Giao diện Tổng hợp (Aggregate View Cards Layout)
- Bỏ bảng `<table>` cũ trong `AggregatePipelineView.tsx`.
- Thiết lập CSS Grid layout 3 cột: `display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16`.
- Xây dựng component `AggregateCard` với:
  - Header: Tên vai trò hoặc đường dẫn dự án giải mã.
  - Badge trạng thái: `✓ Hoàn thành` (xám/xanh) hoặc `● X đang chạy` (nhấp nháy màu cam).
  - Body: Grid thông số (Lần gọi, Số Sessions, Token IN/OUT).
  - Footer Pipeline: Nếu là dự án, hiển thị chuỗi các trạm agent dạng sơ đồ liên kết (linear chain nodes) như màn hình session.

## Definition of Done
- [x] Tài liệu thiết kế hoàn tất, sẵn sàng chuyển tiếp sang lập trình.
