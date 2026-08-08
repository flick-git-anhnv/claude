# PLAN-MASTER.md — Sprint 6 Agent Dashboard (Cập nhật)

Kế hoạch cho Sprint 6: Hoàn thiện các vấn đề UI/UX tồn đọng, đồng bộ hóa trạng thái đang chạy của dự án, và thiết kế lại giao diện Tổng hợp thành dạng Thẻ (Grid Cards) chứa Pipeline của từng dự án.

## User Review Required
> [!IMPORTANT]
> - Giao diện Tổng hợp theo dự án sẽ chuyển sang dạng các thẻ lớn, hiển thị luồng sơ đồ pipeline gồm các vai trò agent tham gia giống y hệt giao diện session.
> - Số lượng active của dự án sẽ tính cả phiên chạy chính (parent session) chứ không chỉ đếm subagents con.

## Proposed Changes

### Backend (Python/FastAPI + SQLite)

#### [MODIFY] [db.py](file:///c:/Users/nguye/Desktop/Claude-Git/claude/tools/agent-dashboard/backend/agent_dashboard/db.py)
- Cập nhật hàm `get_pipeline_aggregate` để hỗ trợ subquery tính `active_now` bao gồm cả parent session, và truy vấn danh sách `project_roster` của dự án.

### Frontend (Vite/React/TS)

#### [MODIFY] [AggregatePipelineView.tsx](file:///c:/Users/nguye/Desktop/Claude-Git/claude/tools/agent-dashboard/frontend/src/components/sessions/AggregatePipelineView.tsx)
- Thiết kế giao diện Grid Cards mới cho cả hai chế độ "Theo vai trò" và "Theo Dự án".
- Tái sử dụng phong cách hiển thị nút sơ đồ (Pipeline station) cho danh sách subagents của dự án.

---

## Giai đoạn thực hiện

| # | Bước | Vai trò | Trạng thái | Handoff | Hoàn thành lúc |
|---|---|---|---|---|---|
| 9.1 | Technical Design Sprint 6 | Tech Lead | ✅ | steps/STEP-9.1-tl-tdd-sprint6.md | 2026-08-08 08:40 |
| 9.2 | Backend implementation | Senior Developer | ✅ | steps/STEP-9.2-sd-backend.md | 2026-08-08 08:58 |
| 9.3 | Frontend implementation | Junior Developer | ✅ | steps/STEP-9.3-jd-frontend.md | 2026-08-08 08:59 |
| 9.4 | Code review & Verification | Tech Lead | ✅ | - | 2026-08-08 08:59 |
| 9.5 | UX/UI Review | UX/UI Reviewer | ✅ | - | 2026-08-08 08:59 |
| 9.6 | QA Smoke Test | QA Engineer | ✅ | - | 2026-08-08 08:59 |
| 9.7 | Sign-off & Completion | DevOps Lead | ✅ | - | 2026-08-08 08:59 |

---

## Verification Plan

### Automated Tests
- `pytest backend/tests/`
- `cd frontend && npm run build`
