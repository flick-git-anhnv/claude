---
category: python-tkinter
tags: [state-machine, monitoring, fastapi, dashboard, jsonl, session-state]
severity: medium
created: 2026-08-06
updated: 2026-08-06
project-origin: agent-dashboard
---

# Session state "Idle" vẫn có thể đang thực thi — đừng coi là "done"

## Tình huống gặp phải

Đang debug roster status trong Agent Dashboard (FastAPI + JSONL file-watcher).
Roster entry của Junior Developer hiện `status: "done"` (dấu ✓ màu xám) dù agent
đang thực sự coding (file vẫn đang được ghi).

## Triệu chứng / Lỗi

```
GET /api/sessions/{id}/chain
→ roster[junior-developer].status = "done"   ← SAI
   (expected: "active")

DB: child session state = "Idle"
    parent session state = "Idle"
```

UI hiển thị tất cả role là "done" dù session cha vẫn `state=Running/Idle` trong DB.

## Nguyên nhân gốc rễ (Root Cause)

Hai pattern bị bỏ sót trong điều kiện `is_active`:

**1. Child session → Idle khi chờ LLM inference**
Agent đang thực thi KHÔNG viết event JSONL liên tục. Giữa 2 lần gọi tool
(đặc biệt khi chờ Claude API trả lời), file JSONL im lặng. Sau
`IDLE_THRESHOLD_SEC` (5 phút mặc định), state machine đánh dấu child là "Idle"
dù agent hoàn toàn đang chạy. Điều kiện cũ `last_child_state == "Running"` → False.

**2. Parent session → Idle khi đang chờ child**
Sau khi parent gọi Agent tool, nó cũng không ghi event mới cho đến khi
child trả kết quả. Parent cũng trở thành "Idle". Điều kiện cũ
`session_state == "Running"` → False.

**3. Child session chưa được index (child_state = None)**
File transcript của child chưa được watcher quét kịp (file vừa tạo / lag
vài giây). Không có child session trong DB → child_state = None → fallback
về "done" sai.

## Giải pháp

```python
# TRƯỚC (sai):
is_active = session_state == "Running" and last_child_state == "Running"

# SAU (đúng):
is_active = session_state in ("Running", "Idle") and (
    last_child_state in ("Running", "Idle") or last_child_state is None
)
```

Mapping:
| parent_state | child_state | is_active |
|---|---|---|
| Running | Running | True |
| Running | Idle | True |
| Running | None (chưa có) | True |
| Idle | Running | True |
| Idle | Idle | True |
| Idle | None (chưa có) | True |
| Running/Idle | Ended | False |
| Ended | bất kỳ | False |

## Áp dụng lại (How to reuse)

- Bất cứ khi nào xây state machine 3-level (Running/Idle/Ended) cho subprocess:
  đừng chỉ check `Running`, phải check `in ("Running", "Idle")` cho cả parent
  lẫn child.
- Khi parent gọi child process/agent: parent NGỪNG ghi event → đương nhiên
  trở thành Idle. Đây là behavior bình thường, không phải done.
- Luôn có fallback `None` (child chưa index) → coi là active nếu parent còn sống.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Fallback `None → active` chỉ an toàn khi kết hợp với `parent in ("Running","Idle")`.
  Nếu parent đã `Ended`, `None` child cũng phải là "done".
- ⚠️ "Idle" trên child SESSION (state machine 5-30 phút) KHÁC với Idle trên child PROCESS
  (process ngủ). State machine chỉ track khi nào JSONL được ghi lần cuối.
- ⚠️ Threshold IDLE_THRESHOLD_SEC = 5 phút: nếu LLM inference lâu hơn 5 phút
  (context lớn, model chậm) → child luôn chuyển Idle trong khi đang chạy — đây
  là behavior thiết kế, không phải bug.

## Tham chiếu

- Fix commit: `db3fe78` branch `research/skills-2026-08-05`
- File: `tools/agent-dashboard/backend/agent_dashboard/db.py` — `get_session_chain` Step 6
- Tests: `tests/test_sprint4_token_step.py` — 4 case mới
