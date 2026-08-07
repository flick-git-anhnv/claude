---
step: "8.1"
plan: ../PLAN-MASTER.md
agent: tech-lead
status: done
completed_at: 2026-08-06 22:50
deps: []
---

# STEP 8.1 — TDD ADDENDUM Sprint 5: Khảo sát CLI usage + Root cause BUG-004 + Thiết kế FR-004 + FR-005

## Input nhận
- PLAN-MASTER.md Phase 1-7 hoàn thành (Sprint 1-4 done)
- Yêu cầu gộp 4 hạng mục vào Sprint 5:
  1. **Usage Display:** hiển thị Session 5hr % + Weekly 7-day % ở AppHeader và AccountCard
  2. **BUG-004 (P2):** Card agent RUNNING không hiển thị model và token đã dùng — chỉ card ✅ mới có `model : tokens`
  3. **FR-004:** Thêm node "Claude" (Dispatcher/main loop) vào Pipeline view — hiện chỉ có subagent
  4. **FR-005:** Toggle 2 chế độ Pipeline view: (a) tách theo session, (b) gộp tất cả session thành 1 view aggregate
- Kiến trúc hiện tại: FastAPI backend (`tools/agent-dashboard/backend/`) + Vite/React/TS frontend (`tools/agent-dashboard/frontend/`)
- Key backend files: `backend/agent_dashboard/state_manager.py`, `backend/agent_dashboard/parser.py`, `backend/agent_dashboard/routes/sessions.py`, `backend/agent_dashboard/routes/accounts.py`
- Key frontend files: `frontend/src/components/pipeline/PipelineCard.tsx`, `frontend/src/components/pipeline/StepStation.tsx`, `frontend/src/components/sessions/SessionCard.tsx`, `frontend/src/components/layout/AppHeader.tsx`, `frontend/src/components/accounts/AccountCard.tsx`

## Nhiệm vụ
Viết TDD ADDENDUM Sprint 5 bao gồm 4 phần tách biệt:

**Phần A — Usage Display:** Nghiên cứu lệnh CLI `claude` (thử `--help`, `--status`, tương đương) để xác định lệnh chính xác lấy usage data, output format (text/JSON), có cần swap account không. Thiết kế `usage_service.py`, endpoint mới, cache 60s.

**Phần B — BUG-004 Root Cause:** Đọc `state_manager.py` và component hiển thị live card để xác định tại sao `model`/`tokens` không có khi session đang RUNNING. Xác định field nào trong JSONL/events available sớm nhất (ngay khi agent start, không đợi kết thúc). Đề xuất fix: cập nhật state_manager lưu model/token từ event sớm nhất + update component.

**Phần C — FR-004 Dispatcher Node:** Nghiên cứu cách nhận diện session gốc (Dispatcher/main loop) trong transcript — phân biệt với `agent-*.jsonl` (subagent). Session gốc: không có `parent_session_id` trong events, hoặc file transcript ở thư mục project chính (không phải file con). Thiết kế cách inject node "Claude (Dispatcher)" vào đầu chain trong `/api/sessions/{id}/chain` response — luôn là node đầu tiên, phân biệt với subagent nodes.

**Phần D — FR-005 Toggle 2 chế độ Pipeline:** Thiết kế API hỗ trợ 2 chế độ:
- Mode A (hiện tại): tách riêng theo session — endpoint `/api/sessions/{id}/chain` giữ nguyên
- Mode B (mới): aggregate — endpoint mới `/api/pipeline/aggregate` hoặc query param `?mode=aggregate` trả về tất cả agent đã chạy (mọi session), gộp theo vai trò (`subagent_type`), với tổng token + số lần gọi. Thiết kế state frontend cho toggle (local state hay URL param).

## Definition of Done
- [ ] **Phần A — CLI Usage:**
  - Đã chạy `claude --help` (và lệnh khác nếu cần) — ghi output thực tế
  - Xác định lệnh + output format + có cần swap account không
  - TDD §29: `usage_service.py` design (struct `UsageInfo`, endpoint, cache 60s, fallback null)
- [ ] **Phần B — BUG-004:**
  - Đọc `state_manager.py`: xác định khi nào `model`/`tokens` được set cho session (event nào trigger)
  - Đọc component live card (SessionCard hoặc tương đương): confirm field nào bị thiếu khi RUNNING
  - TDD §30: ghi root cause + fix plan (state_manager update event + component guard)
- [ ] **Phần C — FR-004:**
  - Xác nhận cách phân biệt session gốc vs subagent trong DB/JSONL hiện tại (field `parent_session_id` trong bảng `sessions` — xem schema TDD v1.0)
  - TDD §31: thiết kế "Claude Dispatcher" node — data shape (subagent_type="dispatcher", display_name="Claude (Dispatcher)", token_step từ session gốc), cách inject vào response `/chain`
- [ ] **Phần D — FR-005:**
  - TDD §32: thiết kế endpoint aggregate + response schema (mảng `{role, display, total_calls, total_tokens_in, total_tokens_out}`)
  - Thiết kế toggle state phía frontend (local state, không cần URL param)
- [ ] Task breakdown Sprint 5 (4 hạng mục): phân chia SD vs JD rõ ràng
- [ ] Append §29–32 vào `docs/tech-design/TDD-agent-dashboard.md`
- [ ] Xuất `docs/tech-design/TDD-agent-dashboard.docx` (`python scripts/md_to_docx_kztek.py`)

## Đã làm
- Khảo sát CLI `claude`: `claude --help`, `claude doctor`, thử `claude -p "/status"` — kết luận KHÔNG có subcommand CLI cho usage; `/status` và `/usage` chỉ là slash-command interactive. Grep binary `claude.exe` phát hiện endpoint REST thật: `GET https://api.anthropic.com/api/oauth/usage`, field trả về: `five_hour`, `seven_day`, `seven_day_opus`, `seven_day_sonnet`, `seven_day_overage_included`, `resets_at`, `resetsAt`, `rateLimitType`, `overageStatus`, `overageResetsAt`. Kết luận: dùng HTTP trực tiếp với Bearer token, KHÔNG cần subprocess `claude`, KHÔNG cần swap `.credentials.json`.
- Đọc `state_manager.py`, `parser.py:120-180`, `main.py:150-320`, `db.py:915-1180`, `AgentRosterItem.tsx`, `format.ts` — xác định root cause BUG-004: child transcript có dòng đầu là `user`/meta (không có `message.model`) → `agent_type=None` trong DB; `token_input/output=0` → `fmtTokensCompact(0)===null` → frontend ẩn cả dòng model+description và dòng tokens trên card ACTIVE. Race window kéo dài từ khi child transcript tạo đến khi assistant line đầu được ingest (1-5s).
- Đọc parser.py:52-77 (`is_subagent`, `parent_session_id`), `db.py` sessions table — xác nhận cách phân biệt session gốc (Dispatcher) vs subagent: file transcript ở `~/.claude/projects/<project>/<uuid>.jsonl` (parent dir không phải `subagents`) = Dispatcher; file trong `subagents/<parent>/agent-*.jsonl` = subagent. Parent's own model+tokens có sẵn trên chính row parent trong bảng `sessions`.
- Thiết kế endpoint aggregate `GET /api/pipeline/aggregate?project=&window=` — GROUP BY `attribution_agent`, JOIN `sessions` WHERE `parent_session_id IN (...)`. Toggle frontend chỉ dùng localStorage `pipelineMode`.
- Append §29-36 (~490 dòng) vào `docs/tech-design/TDD-agent-dashboard.md` — 4 phần A/B/C/D + task breakdown 12 task (6 SD + 6 JD) + 3 handoff payload (UX, SD, JD).
- Xuất DOCX qua `md_to_docx_kztek.py` — DOCX OK, PDF fail (docx2pdf RPC, non-blocking như các Sprint trước).
- Cập nhật TDD version `1.0` → `1.3` ở frontmatter.

## Artifact (đã tạo/cập nhật)
- `docs/tech-design/TDD-agent-dashboard.md` (append §29-36, +490 dòng, tổng 1544 dòng)
- `docs/tech-design/TDD-agent-dashboard.docx` (đã xuất lại)

## Quyết định quan trọng
- **CLI usage:** KHÔNG có subprocess. Gọi trực tiếp `GET https://api.anthropic.com/api/oauth/usage` với header `Authorization: Bearer <accessToken>` từ `.credentials.json` (active) hoặc từ `AccountStore` snapshot (inactive) — chỉ swap `.credentials.json` khi token gần hết hạn (< 60s) để refresh, không cần swap để đọc usage.
- **BUG-004 fix:** 2 lớp — (1) backend broadcast `chain_updated {session_id: parent_session_id}` khi CHILD session có event (main.py ingest loop), frontend PipelineCard listen delta này → refetch `/chain`; (2) frontend fallback UX — active card khi model=null → "đang khởi tạo…", tokens=0 → "— tokens" thay vì ẩn.
- **FR-004 Dispatcher node:** phân biệt bằng `is_subagent=0` và `parent_session_id=NULL` trong bảng `sessions`. Prepend 1 entry `{role:"__dispatcher__", is_dispatcher:true, display_name:"Claude (Dispatcher)", latest_model:parent.agent_type, total_tokens:parent's own tokens, history:[]}` vào đầu roster trong `get_session_chain`. Token của Dispatcher KHÔNG trừ children (parent's row chỉ chứa parent's own tokens).
- **FR-005 toggle:** endpoint MỚI `GET /api/pipeline/aggregate?project=&window=` (không dùng query param `?mode=` trên endpoint cũ, để tách concerns rõ ràng). Group BY `attribution_agent` từ tất cả child session của parent trong scope. Toggle state lưu localStorage `pipelineMode: 'session'|'aggregate'`, default `'session'`.

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- **do_not_redo:** Đã verify lệnh CLI (không có subcommand usage — dùng REST `/api/oauth/usage`). Đã đọc `state_manager.py`, `parser.py`, `db.py get_session_chain`, `AgentRosterItem.tsx` — không cần đọc lại. Đã xác nhận cách phân biệt session gốc (parent dir NOT `subagents`, `is_subagent=0`). Đã chốt schema 4 API mới (§30.3, §32.2, §33.1). Đã chốt localStorage key `pipelineMode`. Task breakdown 12 task chia SD (6) + JD (6) trong TDD §34.
- **watch_out:**
  1. Bước 8.2 (UX): design Dispatcher node phải phân biệt visually nhưng CÙNG SIZE với subagent card (196x100). UsageBar thresholds: < 80% xanh, ≥ 80% cam, ≥ 95% đỏ; tooltip có "resets in ...".
  2. Bước 8.3 (SD): `/api/oauth/usage` timeout 5s bằng SDK gốc. `_pct` handle cả scale 0..1 và 0..100 vì chưa verify runtime. Bearer token KHÔNG cần swap `.credentials.json` (khác `_do_swap_and_invoke`), chỉ swap khi expired < 60s. `chain_updated` broadcast target parent_session_id (KHÔNG child's session_id). Dispatcher entry LUÔN có `history=[]` (không thiếu key). Aggregate query bind `parent_ids` 2 lần (subquery + main WHERE), early return khi rỗng.
  3. Bước 8.4 (JD): `chain_updated.session_id` = parent — subscribe theo parent, không phải child. `is_dispatcher:true` → style Navy #251C53, KHÔNG dùng Cam của active. UsageBar polling 60s (không hơn — cache backend 60s). `AggregatePipelineView` empty state khi roster rỗng.
  4. Bước 8.5 (TL review): kiểm tra `_pct` scale bằng response thật (log data.get("five_hour") một lần khi test); verify `chain_updated` không gây refetch loop (frontend dedupe theo throttling ~500ms).
- **next_inputs:** TDD §29-36 (`docs/tech-design/TDD-agent-dashboard.md` dòng 1055-1544). Modules ưu tiên cho SD: `backend/agent_dashboard/usage_service.py` (mới), `backend/agent_dashboard/routes/accounts.py` (thêm 2 route), `backend/agent_dashboard/routes/sessions.py` (thêm route aggregate), `backend/agent_dashboard/db.py get_session_chain` (edit prepend dispatcher, thêm `get_pipeline_aggregate`), `backend/agent_dashboard/main.py` (thêm broadcast `chain_updated`). Modules ưu tiên cho JD: `frontend/src/components/UsageBar.tsx` (mới), `frontend/src/components/AggregatePipelineView.tsx` (mới), `frontend/src/hooks/usePipelineMode.ts` (mới), `frontend/src/components/sessions/AgentRosterItem.tsx` (edit `is_dispatcher` branch + active fallback), `frontend/src/components/layout/AppHeader.tsx` (edit), `frontend/src/components/accounts/AccountCard.tsx` (edit), `frontend/src/contexts/WsContext.tsx` (edit — handler `chain_updated`), `frontend/src/api/mockData.ts` (edit).

## Commit
- Hash: fc9e64d
- Đã push: chưa (session isolation — user chưa yêu cầu push)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
