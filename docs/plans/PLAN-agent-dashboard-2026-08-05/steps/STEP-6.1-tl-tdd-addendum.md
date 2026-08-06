---
step: 6.1
plan: ../PLAN-MASTER.md
agent: Tech Lead
status: done
completed_at: 2026-08-06 11:05
deps: ["5.5"]
---

# STEP 6.1 — TDD Addendum Sprint 3 (BUG-003 + FR-001 + FR-002 + FR-003)

## Input nhận
- Backlog Sprint 3 từ PLAN-MASTER: BUG-003 (Invalid Date), FR-001 (Pipeline view), FR-002 (% context window), FR-003 (tên session thân thiện).
- PRD `docs/prd/PRD-agent-dashboard.md` §"Rủi ro / Câu hỏi mở" — Q-FR-002, Q-FR-003, FR-001 chưa thiết kế.
- Root cause sơ bộ Sprint 2 (Bước 5.5): `parser.py:55` fallback `timestamp = ""`.

## Nhiệm vụ
Xác minh dữ kiện thật từ code + `.jsonl`, chốt kiến trúc, viết TDD addendum §22–26 vào cuối `docs/tech-design/TDD-agent-dashboard.md`, chia task cho SD (Track C backend) + JD (Track D frontend).

## Đã làm

**Xác minh dữ kiện (không đoán):**

1. **BUG-003 — root cause chính xác:** Đọc `parser.py:55` (`timestamp = data.get("timestamp") or data.get("ts") or ""`) + `db.py:140` (`INSERT OR IGNORE ... VALUES (..., timestamp, timestamp, ...)`). Grep `.jsonl` thật: các dòng type `ai-title` và `last-prompt` KHÔNG có field `timestamp`. Khi 1 trong 2 dòng đó là dòng ĐẦU TIÊN được ingest cho một session mới → session được INSERT với `started_at=""`. Fix chọn: **backend fix tận gốc** — parser return `None` khi timestamp rỗng cho các dòng non-content (bổ sung early-return sau khi extract xong ai-title, xem FR-003).

2. **FR-003 — field có sẵn:** Grep type-value uniq trên `.jsonl` thật (file `6e5dfc13...`), phát hiện type `ai-title` với payload `{"type":"ai-title","aiTitle":"...","sessionId":"..."}` — **Claude Code tự đặt tên session**. KHÔNG cần tự trích từ user message. Có multi-line ai-title (Claude update tiêu đề nhiều lần) → lấy dòng CUỐI CÙNG. Fallback nếu session không có ai-title: `message.content[0].text` của dòng đầu tiên type `user` (đã verify tồn tại: `{"type":"user","message":{"content":[{"type":"text","text":"..."}]}}`), truncate 60 chars, skip nếu block đầu là `image`/`tool_result`. Cache trong DB cột mới `sessions.title` (idempotent migration giống Sprint 2).

3. **FR-002 — snapshot usage lượt gần nhất:** Hiện `db.py:145` cộng dồn `token_input += ?` — sai cho tính %context. Thêm 4 cột mới snapshot lượt CUỐI: `last_input_tokens`, `last_cache_creation`, `last_cache_read`, `last_usage_at` (không cộng dồn, GHI ĐÈ mỗi lần assistant message có `usage`). Cache `max_input_tokens` per-model: **giá trị tĩnh** đã xác minh trước đây (Sonnet 5/Opus 5/Fable 5 = 1_000_000; Haiku 4.5 = 200_000) hard-code trong `config.py` dict `MODEL_CONTEXT_WINDOW`, fallback 200_000 cho model lạ. Không gọi `GET /v1/models/{id}` runtime — tránh dependency mạng + rate-limit + không có API key OAuth. Nếu tương lai cần dynamic, bọc 1 hàm `resolve_max_tokens(model)` — dễ swap.

4. **FR-001 — chain identification:** Xác nhận Sprint 2 gap: subagent con ghi log ở nơi khác (không truy được đầy đủ). Chốt phương án **đơn giản khả thi Sprint 3**: coi 1 session cha (1 file `.jsonl` chính) = 1 chain. Pipeline = danh sách các `tool_use` Agent trong session đó theo thứ tự thời gian (`events` table đã lưu, có `tool_name='Agent'` + `payload_json` chứa `subagent_type`+`description`). Bước "đang active" = Agent call GẦN NHẤT trong chain của session có `state='Running'` và session chưa có Agent call mới hơn nó. Bước "đã qua" = có Agent call sau nó, hoặc session Ended/Idle. KHÔNG lần theo transcript agent con. Đủ dùng cho MVP pipeline view.

**Kiến trúc chốt trong TDD Addendum §22–26** (đã append vào `docs/tech-design/TDD-agent-dashboard.md`):

- §22 Assumptions Sprint 3 + Goals/Non-goals.
- §23 BUG-003 fix: parser guard `if not timestamp: return None` (ngoại trừ nhánh ai-title đã capture xong); DB defensive `INSERT ... WHERE ? != ''`; migration cleanup 1 lần đầu (`UPDATE sessions SET started_at = last_event_at WHERE started_at = ''`).
- §24 FR-003: cột `sessions.title`, parser extract `ai_title` + `first_user_text`, ingest logic: `title = ai_title if not null else truncate(first_user_text, 60) else null`. WS delta mới `session_title_changed`.
- §25 FR-002: 4 cột `last_*` mới, GHI ĐÈ mỗi assistant message có `usage.input_tokens > 0`, config `MODEL_CONTEXT_WINDOW`, endpoint mở rộng `/api/sessions` trả thêm `last_input_total` + `max_context` + `context_pct`. WS delta thêm `context_pct`.
- §26 FR-001: endpoint MỚI `GET /api/sessions/{id}/chain` → `[{step_index, subagent_type, description, started_at, ended_at?, status: "done"|"active"|"pending"}]`. Query từ `events` WHERE `session_id=? AND tool_name='Agent'` ORDER BY `ts`. `status` tính runtime từ session.state + thứ tự. WS delta `chain_step_changed` gộp vào WS hiện có (broadcast khi có Agent tool_use mới).
- §27 Task breakdown 8 task (S3-T01..T08).
- §28 Handoff Payload cho SD/JD.

## Artifact
- `docs/tech-design/TDD-agent-dashboard.md` — Addendum §22–28 (Sprint 3) đã append.
- `docs/tech-design/TDD-agent-dashboard.docx` + `.pdf` — xuất lại (§19).

## Quyết định quan trọng
1. **BUG-003 fix ở backend, KHÔNG frontend safe-guard** — tránh 244 session legacy tiếp tục invalid; parser guard + migration cleanup 1 lần. Frontend vẫn giữ `fmtDateTime` fallback "—" phòng edge case tương lai (đã có từ UI-001 fix).
2. **FR-002 dùng giá trị tĩnh** thay Models API — tránh network dependency cho tool local, đủ chính xác cho 4 model dùng thật, dễ swap sau. Ghi rõ nguồn (`skill claude-api` đã verify Sprint 2).
3. **FR-001 chain = 1 session cha** — không R&D thêm về agent con transcript. Đủ giá trị dashboard, làm được trong 1 sprint.
4. **FR-003 ưu tiên `aiTitle` native > user text trích** — chính xác hơn, đỡ xử lý edge case (image/tool_result block).

## Handoff Payload — bước sau đọc phần này

- **do_not_redo:** Đã xác minh `ai-title` là type native trong `.jsonl`. Đã xác minh chỉ `ai-title`+`last-prompt` thiếu timestamp. Đã chốt giá trị tĩnh `MODEL_CONTEXT_WINDOW`. Đã chốt chain = 1 session cha. Đã chốt fix BUG-003 ở backend. JD (6.4) KHÔNG cần tự trích user message cho FR-003 trừ khi session không có aiTitle (fallback).
- **watch_out:**
  1. `ai-title` xuất hiện NHIỀU LẦN trong 1 file — LUÔN lấy dòng cuối cùng (Claude update tiêu đề dần).
  2. Snapshot `last_input_tokens` GHI ĐÈ không cộng dồn — khác hoàn toàn `token_input` hiện tại. Đừng xóa cột cũ.
  3. `title` cột mới nullable (session chưa có aiTitle + không có user text hợp lệ → null; UI fallback hiển thị session_id thô như hiện tại).
  4. Chain endpoint chỉ trả Agent tool_use (KHÔNG trả Read/Bash/Grep) — filter `tool_name='Agent'` bắt buộc.
  5. `status: "active"` chỉ có TỐI ĐA 1 step trong 1 chain (là step cuối nếu session Running).
  6. Migration BUG-003 cleanup chạy 1 lần khi startup — check `count(*) WHERE started_at=''` > 0 mới chạy, không bao giờ chạy lại.
  7. FR-002 công thức: `context_pct = last_input_tokens + last_cache_creation + last_cache_read) / max_context * 100` — dùng SNAPSHOT lượt cuối, KHÔNG cộng dồn.
- **next_inputs:** `docs/tech-design/TDD-agent-dashboard.md` §22–28. Modules chạm: `parser.py`, `db.py`, `state_manager.py`, `routes/sessions.py`, `main.py` (ingest loop), `config.py` (thêm dict `MODEL_CONTEXT_WINDOW`), `frontend/src/pages/AgentStatus.tsx`, `frontend/src/components/*` (thêm PipelineCard). UX/UI Designer (Bước 6.2) dùng §26 chain endpoint schema làm cơ sở wireframe pipeline. SD (Bước 6.3) làm S3-T01..T05 (backend). JD (Bước 6.4) làm S3-T06..T08 (frontend, chờ 6.2 xong mới bắt đầu PipelineCard UI). Sau code: `graphify update --diff` (nếu có) → `/verify-pr` → PR.

## Commit
- Hash: [điền sau commit]
- Đã push: có (subagent tự push)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
