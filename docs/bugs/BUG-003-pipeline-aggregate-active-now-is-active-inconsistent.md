# [BUG-003] Pipeline aggregate active_now và is_active không đồng nhất với session thực tế

**Severity:** High | **Priority:** P2
**Môi trường:** Backend FastAPI uvicorn | URL: http://127.0.0.1:7770 | Build: branch feature/agent-dashboard-2026-08-06
**Phát hiện:** QA Engineer | Ngày: 2026-08-10

---

## Mô tả

`GET /api/pipeline/aggregate` trả về giá trị `active_now` và `is_active` không khớp với trạng thái session thực tế từ `GET /api/sessions/by-project`. Bug có hai dạng biểu hiện tuỳ theo `group_by` parameter:

- **group_by=agent**: `active_now=0` cho TẤT CẢ agents, dù có 2 sessions đang Running thật.
- **group_by=project**: Tổng `active_now` = 3, nhưng chỉ có 2 sessions Running thật (overcounting 1 từ project `c--Users-nguye-DecodeTools`). Thêm vào đó, `is_active` trong `project_roster` luôn là `false` cho mọi agent entry, kể cả trong project đang có session Running.

Bug tương tự đã được report trước đó (mô tả cũ: "active_now=4 nhưng is_active toàn false") nhưng chưa được fix hoàn toàn. Lần này biểu hiện khác chiều: group_by=agent undercount (0), group_by=project overcount (3 vs 2), is_active vẫn false.

## Các bước reproduce

1. Xác nhận có ít nhất 1 session đang Running:
   ```
   GET /api/sessions/by-project
   → Đếm sessions có state="Running" hoặc state="Idle"
   ```

2. Gọi pipeline aggregate group_by=agent:
   ```
   GET /api/pipeline/aggregate?group_by=agent
   → Kiểm tra active_now của từng agent trong roster
   ```

3. Gọi pipeline aggregate group_by=project:
   ```
   GET /api/pipeline/aggregate?group_by=project
   → Kiểm tra active_now của từng project, và is_active trong project_roster
   ```

4. So sánh với số Running sessions thực tế.

## Kết quả thực tế

```
GET /api/sessions/by-project:
  Sessions Running: 2 (session IDs: af4bacc5, d942db42)
  Sessions Idle: 0

GET /api/pipeline/aggregate?group_by=agent:
  Senior Developer: active_now=0
  Tech Lead: active_now=0
  QA Engineer: active_now=0
  ... (all 22 agents): active_now=0
  SUM active_now: 0   ← Sai, phải > 0

GET /api/pipeline/aggregate?group_by=project:
  c--Users-nguye-Desktop-Claude-Git-claude: active_now=2  ← đúng
  c--Users-nguye-DecodeTools: active_now=1  ← SAI (không có session Running ở đây)
  SUM active_now: 3   ← Sai, phải là 2

is_active trong project_roster của mọi project = false  ← Sai cho project có Running session
```

## Evidence (timestamp 2026-08-10 ~09:09 UTC+7)

```json
// group_by=agent — active_now=0 tất cả (trích đoạn)
{"role":"senior-developer","active_now":0,"status":"done"}
{"role":"qa-engineer","active_now":0,"status":"done"}

// group_by=project — active_now sai
{"display_name":"c--Users-nguye-Desktop-Claude-","active_now":2}  // có 2 Running — đúng
{"display_name":"c--Users-nguye-DecodeTools","active_now":1}      // không có Running — SAI

// is_active trong project_roster (trích đoạn dự án đang active)
{"role":"qa-engineer","is_active":false}   // Sai — qa-engineer đang Running trong af4bacc5
```

## Kết quả mong đợi

```
GET /api/pipeline/aggregate?group_by=agent:
  qa-engineer: active_now >= 1  (session af4bacc5 đang chạy qa-engineer)
  SUM active_now: 2

GET /api/pipeline/aggregate?group_by=project:
  c--Users-nguye-Desktop-Claude-Git-claude: active_now=2
  c--Users-nguye-DecodeTools: active_now=0
  SUM active_now: 2

is_active trong project_roster:
  (project c--Users-nguye-Desktop-Claude-Git-claude): qa-engineer.is_active=true
```

## Tần suất

100% reproducible — xuất hiện mỗi khi có session đang Running.

## Tác động

- Dashboard UI hiển thị số lượng active agents/sessions sai → người dùng mất trust vào dashboard.
- group_by=agent không phản ánh activity hiện tại → không dùng được để debug "ai đang chạy gì".
- is_active=false cho tất cả → filter "active only" không hoạt động.

## Phân tích sơ bộ

Hai biểu hiện (undercount ở agent-level, overcount ở project-level) gợi ý có thể có 2 bug riêng biệt:

1. **Undercount (group_by=agent)**: Logic tính `active_now` cho agent có thể không query đúng bảng session state, hoặc không join đúng với bảng agent calls.
2. **Overcount (group_by=project)**: Project `c--Users-nguye-DecodeTools` báo active_now=1 — có thể do session Idle/cũ không được mark Ended đúng, hoặc query không filter đúng state="Running".
3. **is_active false**: Field này có thể được tính tách biệt với `active_now` và có lỗi trong logic so sánh.

## Workaround

Dùng `GET /api/sessions/by-project` và tự đếm sessions có `state="Running"` hoặc `state="Idle"` để biết số lượng thật.

## Liên quan

- Bug cũ cùng loại: chưa có bug ticket cụ thể trước đó (chỉ được nhắc trong task description "active_now=4 nhưng is_active toàn false, đã phát hiện trước")
- File liên quan: `tools/agent-dashboard/backend/agent_dashboard/` (routes/pipeline.py hoặc tương đương)
