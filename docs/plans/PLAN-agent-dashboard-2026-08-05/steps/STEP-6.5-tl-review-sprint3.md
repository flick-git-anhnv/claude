---
step: "6.5"
name: "TL Review Sprint 3 — Track C + Track D + merge decision"
agent: "Tech Lead"
plan: "PLAN-agent-dashboard-2026-08-05"
status: done
started_at: "2026-08-06 15:20"
completed_at: "2026-08-06 15:55"
deps: ["6.3","6.4"]
---

# STEP 6.5 — Tech Lead Review Sprint 3

## Nhiệm vụ
Review cuối Track C (backend, de4fbe8) + Track D (frontend, 6673d3a+158be36), tích hợp thật, quyết định merge — rút kinh nghiệm Sprint 2 lệch mock↔backend.

## Đã làm

### 1. Static verify
- Backend `pytest tests/ -q`: **170 passed** ✅
- Frontend `tsc -b` + `vite build`: **0 errors**, 861 modules, dist/index-*.js 587KB ✅

### 2. Đối chiếu API contract mock↔backend thật
Đọc `db.get_session_chain` (backend) vs `types/index.ts` + `mockData.getMockChain` (frontend). **Phát hiện 1 lệch schema** (lặp lại pattern Sprint 2):
- Backend trả `subagent_type/subagent_display/description` **Optional[str]** (có thể null) — logic đúng: khi Agent tool_use không có `subagent_type` field trong input.
- Frontend TS types khai báo required non-null `string`. Mock luôn cung cấp giá trị → TS không bắt được.
- **FIX:** `types/index.ts` đổi 3 field sang `string | null`; `StepStation.tsx` dùng fallback `displayName = subagent_display || subagent_type || 'Agent'`, `title={description || undefined}`.

### 3. Tích hợp thật (kill port 7770 cũ → uvicorn mới → curl thật)
| Hạng mục | Kết quả | Bằng chứng |
|----------|---------|-----------|
| BUG-003 | ✅ PASS | `GET /api/sessions` → 0/6 session có `started_at=""` |
| FR-002  | ✅ PASS | session `agent-ac7082…` ctx_pct=50.1% (200K); session `973154ca…` ctx_pct=78.8% (1M, sonnet-5) — max_context resolve đúng theo model |
| FR-003  | ✅ PASS (sau backfill) | 72/100 session history có `title` từ ai-title; ví dụ "Add Lovable MCP HTTP transport" |
| FR-001  | ✅ PASS (sau backfill) | `GET /api/sessions/{sid}/chain` trả 32 step với 14 distinct subagent_types (task-planner, product-manager, business-analyst, tech-lead, senior-developer, junior-developer, qa-engineer, devops-lead, ux-ui-reviewer, ui-ux-designer, project-manager, qa-lead, devops-engineer, engineering-manager) |

### 4. Phát hiện & fix bug nghiêm trọng thứ 2 — FR-001 hỏng trên session thật
- **Root cause:** `parser.py` truncate `raw_json = line[:2000]` → Agent tool_use lines (thường >2000 chars vì chứa prompt dài cho subagent) bị cắt giữa JSON. `get_session_chain` `_json.loads(payload_json)` raise → catch silent → toàn bộ steps trả `subagent_type=None` → UI pipeline không hiển thị được tên vai trò.
- **Verify:** DB session hiện tại 973154ca có 32/32 Agent events với `LENGTH(payload_json)=2000` (đều truncate max).
- **FIX (schema-level, cùng class bug với Sprint 2):**
  1. `db._SCHEMA_SQL`: thêm 2 cột `subagent_type TEXT`, `subagent_description TEXT` vào events table.
  2. `db._migrate_events_subagent_columns()`: idempotent ALTER TABLE cho DB cũ.
  3. `db.insert_event()`: thêm 2 param optional, INSERT vào 2 cột mới.
  4. `main._process_file()`: pipe `parsed.subagent_type` + `parsed.subagent_activity` (chỉ khi tool_name='Agent') vào insert_event.
  5. `db.get_session_chain()`: SELECT 2 cột mới, prefer stored value; fallback parse payload_json cho legacy row (chỉ có tác dụng nếu payload <2000).
- **Backfill 1 lần từ JSONL:** 1013 events (95 sessions) + 333 titles cập nhật cho data đã có sẵn trong DB — script chạy trực tiếp, không đưa vào code base.
- **Tests:** 170/170 vẫn pass sau khi sửa (`_SCHEMA_SQL` include cột mới nên test dùng `executescript` cũng có cột).

### 5. Quyết định merge
**APPROVED** ✅ — Cả Track C + Track D pass tích hợp thật 4/4 hạng mục. Lệch schema #1 (TS null) + bug schema #2 (events truncation) đã fix trong review này.

## Artifact
- Backend: `db.py` (schema+migration+insert_event+get_session_chain), `main.py` (insert_event call site)
- Frontend: `types/index.ts` (ChainStep nullable), `StepStation.tsx` (null-safe display)
- Verified: `pytest 170 passed`, `tsc 0 errors`, `vite build 861 modules`, `curl` 4/4 hạng mục pass

## Handoff Payload — bước sau đọc phần này (UXR — Bước 6.6)

- **do_not_redo:**
  - Không cần chạy lại pytest/tsc/build — đã pass toàn bộ.
  - Không cần restart backend cho lần đầu chạy UI review — server tại port 7770 đã chứa data đã backfill (32 steps chain thật cho session 973154ca, 333 sessions có title).
  - Không cần kiểm tra lại field name mock↔backend — đã sync xong.

- **watch_out:**
  1. **Legacy events truncation:** DB rows ghi TRƯỚC fix này có payload_json = 2000 chars max → không parse được. Chỉ 2 cột mới `subagent_type`/`subagent_description` dùng được cho chain. Sau restart, dữ liệu backfill vẫn còn (đã UPDATE trực tiếp).
  2. **Title backfill chưa full:** Sessions không có ai-title event trong JSONL → title vẫn null. UI phải hiển thị fallback session_id thô (đúng behavior thiết kế FR-003).
  3. **StepStation null-safe:** khi subagent_display null → fallback subagent_type raw slug → 'Agent'. Test UI nên bao gồm case Agent tool call với subagent_type null (hiếm, nhưng có thể).
  4. **PipelineCard fetch trigger:** re-fetch khi `current_subagent?.at` đổi. Session Idle không re-fetch — UXR test cần chọn 1 session đang Running (hoặc session 973154ca có 32 steps sẵn dù đang Idle).
  5. **Backend truncation limit vẫn 2000** — chưa tăng lên, tương lai vẫn có thể lệch nếu Agent input rất lớn. Đã workaround bằng cột riêng. Nếu muốn debug JSON đầy đủ → tăng limit là task riêng.

- **next_inputs:**
  - Frontend build production sẵn tại `tools/agent-dashboard/frontend/dist/`.
  - Backend chạy: `cd tools/agent-dashboard/backend && python -m uvicorn agent_dashboard.main:app --host 127.0.0.1 --port 7770`.
  - Frontend chạy: `cd tools/agent-dashboard/frontend && npm run dev` (dev server 5173) hoặc serve `dist/` qua static server.
  - Session giàu data để test pipeline view: `973154ca-dd2a-4b42-ae24-6bc8a2930a27` (32 steps, 14 subagent types khác nhau — đây là session dispatcher đang orchestrate agent-dashboard).
  - Session có title thật để test FR-003: xem history 30d — ~72% sessions có title.
  - Session có context_pct >70% để test FR-002 màu warning: `973154ca…` (78.8%).
  - Kịch bản UXR: C1 tổng quan → C2 pipeline layout 32 stations (scroll ngang + fade gradient + auto-scroll active) → C3 ContextBadge màu 3 ngưỡng → C4 fallback title null → C5 responsive mobile → C6 accessibility (aria-label pipeline steps) → C7 error state (session không có chain).
