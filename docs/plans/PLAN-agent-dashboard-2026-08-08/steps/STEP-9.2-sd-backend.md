---
step: "9.2"
plan: ../PLAN-MASTER.md
agent: senior-developer
status: done
completed_at: "2026-08-08 08:58"
deps: ["9.1"]
---

# STEP 9.2 — Backend Implementation Sprint 6 (Aggregate Update)

## Input nhận
- Yêu cầu và thiết kế kỹ thuật từ bước 9.1

## Nhiệm vụ & Kết quả thực hiện
1. **Đồng bộ đếm đang chạy (active_now):**
   - Đã cập nhật truy vấn `get_pipeline_aggregate` trong `db.py`. Khi `group_by == "project"`, `active_now` được tính thông qua subquery đếm toàn bộ các session (bao gồm cả phiên chạy Dispatcher chính và các subagents) có `state == 'Running'`.
   - Kết quả: Dự án sẽ được báo trạng thái "đang chạy" (Active) đồng bộ chuẩn xác với trạng thái session view.
2. **Hỗ trợ API Project Roster:**
   - Khi `group_by == "project"`, thực hiện thêm câu lệnh SQL phụ truy vấn tất cả các subagent từng chạy trong dự án đó (bao gồm vai trò, số lần gọi, tokens tiêu thụ) để gán vào `project_roster` của dự án.
3. **Unit Tests:**
   - Chạy `pytest` thành công với **251/251 test cases PASS**.
