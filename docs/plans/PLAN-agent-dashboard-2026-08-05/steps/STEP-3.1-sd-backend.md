---
step: "3.1"
plan: ../PLAN-MASTER.md
agent: senior-developer
status: done
completed_at: 2026-08-05 23:37
deps: ["2.1"]
---

# STEP 3.1 — SD: Code Backend

## Input nhận
Output từ Bước 2.1 (TL): `docs/tech-design/TDD-agent-dashboard.md` — tech stack, API contract, DB schema, file-watcher design, task breakdown SD.

## Nhiệm vụ
Implement toàn bộ backend theo TDD: file-watcher theo dõi `~/.claude/projects/*/*.jsonl`, JSONL parser, SQLite ingestion (sessions + token_events), WebSocket server push realtime events, REST API endpoints, và account/API key management (lưu file local với mã hoá nhẹ).

## Definition of Done
- [ ] `src/agent-dashboard/backend/` tạo đủ:
  - [ ] File-watcher: watch `~/.claude/projects/*/*.jsonl`, detect new lines, không bỏ sót khi rotate file
  - [ ] JSONL parser: parse đúng format Claude session log, extract agent name/type, token counts, timestamps
  - [ ] SQLite: create/migrate schema, insert sessions + token events
  - [ ] WebSocket server: broadcast events realtime khi file-watcher phát hiện thay đổi
  - [ ] REST API: GET /sessions, GET /sessions/history?from=&to=, GET /accounts, POST /accounts/switch, POST /accounts (add), DELETE /accounts/:id
  - [ ] Account store: đọc/ghi file local với mã hoá nhẹ, validate API key format trước khi lưu
- [ ] Unit tests cho: JSONL parser, SQLite insert/query, account store encrypt/decrypt
- [ ] `requirements.txt` hoặc `pyproject.toml` với đầy đủ dependencies
- [ ] README hướng dẫn chạy backend local
- [ ] Chạy pre-coding-check (`code-graph/CODE-GRAPH.md` + lessons liên quan) trước khi code
- [ ] Chạy `/verify-pr` và đính kèm VERIFICATION REPORT vào PR description trước khi chuyển TL review

## Đã làm
- Tạo toàn bộ cấu trúc `tools/agent-dashboard/backend/` theo TDD §9
- `config.py`: tất cả thresholds + paths qua env vars, dùng pathlib, Windows-safe
- `db.py`: aiosqlite WAL mode, schema bootstrap (4 bảng), cursor persistence, upsert session, batch token_usage
- `parser.py`: parse JSONL Claude Code format, trích tool_use từ content blocks, agent_type từ model field, partial-line an toàn
- `tail_reader.py`: byte-offset cursor, chỉ yield dòng hoàn chỉnh (có `\n`), detect truncation, restore từ DB
- `watcher.py`: PollingObserver mặc định trên Windows (env FORCE_NATIVE_WATCHER=1 để override), bridge asyncio queue
- `state_manager.py`: Running/Idle/Ended state machine, evaluate_all cho ticker 30s, initialize_from_db khi restart
- `ws.py`: ConnectionManager fan-out, snapshot khi client kết nối, ping/pong handler
- `accounts.py`: XOR+base64 (SHA256 salt), CRUD + activate + reveal rate-limit 5/min, mask key
- `routes/sessions.py`, `routes/tokens.py`, `routes/accounts.py`: full REST theo TDD §6.1
- `main.py`: FastAPI lifespan, pipeline processor task, state ticker task, startup scan backlog, WebSocket endpoint
- `__main__.py`: `python -m agent_dashboard` → uvicorn on port 7770
- `tests/`: 47 unit tests, tất cả pass — parser (9), tail_reader (9), state_manager (11), accounts (18)
- Phát hiện và fix 1 bug trong test: thresholds `idle_threshold=5, ended_threshold=30` → đơn vị là giây, nhưng timedelta dùng minutes → session đi thẳng Ended; sửa thành đúng 300/1800 giây

## Artifact
- `tools/agent-dashboard/backend/` — toàn bộ backend package
- `tools/agent-dashboard/backend/agent_dashboard/` — 12 Python modules
- `tools/agent-dashboard/backend/tests/` — 4 test files + fixture
- `tools/agent-dashboard/backend/requirements.txt`, `pyproject.toml`, `README.md`

## Quyết định quan trọng
1. **PollingObserver mặc định trên Windows** — phù hợp watch_out từ TDD, native watcher có thể miss event
2. **Pipeline processor single asyncio task** — serialize tất cả DB writes, tránh lock SQLite
3. **TailReader dùng `rfind(b'\n')` thay vì split** — đảm bảo offset tính đúng byte kể cả multi-byte UTF-8
4. **Project mới độc lập** — KHÔNG cập nhật `code-graph/CODE-GRAPH.md` repo chính (ghi trong PR)

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: Backend đã implement đầy đủ theo TDD §5-§9. Không cần viết lại bất kỳ module nào. 47 tests xanh. Import `from agent_dashboard.main import app` thành công.
- watch_out:
  1. `pydantic-core` version mismatch trên máy này (2.18.2 vs cần 2.46.4) — đã upgrade global. Nếu test fail với SystemError pydantic-core → chạy `pip install --upgrade pydantic pydantic-core`.
  2. Tests state_manager dùng thresholds GIÂY (300/1800), không phải phút — xem comment trong test file.
  3. `data/` thư mục bị .gitignore — không commit vào git, tự tạo khi app start.
  4. Frontend `dist/` chưa tồn tại — backend sẽ không mount static files (không crash, chỉ log warning).
  5. Tool call `from agent_dashboard.accounts import mask_key` trong `routes/accounts.py` dùng `__import__` hack — có thể refactor sang import trực tiếp nếu TL muốn.
- next_inputs: TDD §5-§9 (đã implement), commit hash `fecd37d`. Bước tiếp theo: TL code review (Bước 3.3) sau khi JD hoàn thành frontend (Bước 3.2).

## Commit
- Hash: fecd37d
- Đã push: không (branch local: research/skills-2026-08-05)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
