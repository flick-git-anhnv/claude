---
step: "3.1"
plan: ../PLAN-MASTER.md
agent: senior-developer
status: todo
completed_at:
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
[Điền sau khi hoàn thành]

## Artifact
[Điền sau khi hoàn thành]

## Quyết định quan trọng
[Điền sau khi hoàn thành]

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: Không có
- watch_out: Không có
- next_inputs: Không có

## Commit
- Hash: [điền sau khi commit]
- Đã push: [có/không]

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
