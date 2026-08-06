---
step: 5.2
agent: senior-developer
title: Track A — OAuth Account Support
status: done
created: 2026-08-06
completed_at: 2026-08-06 09:53
---

# STEP-5.2: Track A — OAuth Account Support

## Nhiệm vụ
Implement Track A: OAuth Session accounts cho Agent Dashboard Sprint 2.

- Data model migration: thêm `kind` discriminator vào `accounts.enc` (v1→v2), backup `accounts.v1.bak`, idempotent
- API: CRUD cho `oauth_session` accounts — POST import từ `%USERPROFILE%\.claude\.credentials.json`, plus `import-current-oauth` và `oauth-status` endpoints
- "Set Active" OAuth flow: backup credentials in-memory + file timestamped → re-snapshot prev active OAuth → write new account's OAuth → `finally` restore on failure
- Background auto-refresh scheduler: swap-and-invoke với `asyncio.Lock`, in-memory backup, `finally` restore, `needs_relogin` flag khi refresh token hết hạn
- Unit tests 33 cases: migration idempotent, mask token, backup/restore logic (mock file I/O)
- Frontend: 2-tab dialog (API Key | OAuth Session), BannerAlert security warning, AccountCard OAuth badges

## Đã làm

### Backend (Python/FastAPI)

**`agent_dashboard/config.py`** — Thêm OAuth constants:
- `CLAUDE_CREDENTIALS_FILE` → `~/.claude/.credentials.json`
- `OAUTH_REFRESH_INTERVAL_SEC` = 1800 (env override)
- `OAUTH_REFRESH_AHEAD_RATIO` = 0.20
- `OAUTH_REFRESH_MIN_AHEAD_MS` = 30 phút (ms)

**`agent_dashboard/accounts.py`** — Rewrite hoàn toàn cho v2:
- `mask_oauth_token(token)` → `sk-ant-****XXXX` (4 ký tự cuối)
- `REQUIRED_OAUTH_FIELDS = {"accessToken", "refreshToken", "expiresAt", "refreshTokenExpiresAt"}`
- `AccountStore._migrate_v1_to_v2()` — backup `accounts.v1.bak`, add `kind: "api_key"` to all, bump version 1→2, idempotent
- `list_accounts()` — trả về kind-aware entries (OAuth: `oauth_masked`, `needs_relogin`, `expires_in_sec`, `refresh_expires_in_sec`)
- `add_oauth_account(name, oauth_block, org_uuid)` — validate REQUIRED_OAUTH_FIELDS
- `update_oauth_snapshot(acc_id, oauth_block, org_uuid)` — replace oauth block, bump `last_refreshed_at`
- `set_needs_relogin(acc_id)` — flag account, persist
- `get_oauth_status(acc_id)` — `{expires_in_sec, refresh_expires_in_sec, needs_relogin, last_refreshed_at}`
- `reveal_key()` cho oauth → raise `ValueError("REVEAL_NOT_SUPPORTED_FOR_OAUTH")`
- `_safe_expires_in_sec(ms)` — ms timestamp → remaining seconds (clamped ≥ 0)

**`agent_dashboard/oauth_service.py`** — NEW FILE:
- `read_credentials(path)` / `write_credentials(path, data)` — atomic read/write
- `validate_oauth_block(block)` — kiểm tra REQUIRED_OAUTH_FIELDS
- `activate_oauth_account(acc_id, store, creds_path)`:
  - In-memory backup
  - Tạo `.credentials.backup.<timestamp>.json` (timestamped file backup)
  - Re-snapshot prev active OAuth account từ current file
  - Write new account's oauth vào credentials
  - On failure: `finally` restore in-memory backup
- `refresh_inactive_accounts(store, creds_path, refresh_lock)` — skip active, skip needs_relogin, RT expired → set_needs_relogin, else invoke `_do_swap_and_invoke`
- `_do_swap_and_invoke(acc_id, store, creds_path, refresh_lock)`:
  - Acquire `asyncio.Lock` (`refresh_lock`)
  - In-memory backup + `.credentials.backup.emergency.json`
  - Write account oauth → invoke `_run_claude_subprocess()`
  - Compare `expiresAt` before/after → `update_oauth_snapshot` if changed
  - `finally`: restore in-memory backup, delete emergency backup
- `_run_claude_subprocess()` — `claude -p ok --model claude-haiku-4-5`, `shell=True` (Windows .cmd), `asyncio.wait_for` 30s + `loop.run_in_executor`, return exit code
- `check_emergency_backup(creds_path)` — detect crash recovery backup

**`agent_dashboard/models.py`** — AccountCreate mở rộng:
- Field `kind: str = "api_key"` + validator `"api_key" | "oauth_session"`
- Method `validate_for_kind()` — api_key requires `api_key` field
- (Track B cũng sửa file này: SUBAGENT_DISPLAY, ParsedLine 2 new fields — không conflict)

**`agent_dashboard/routes/accounts.py`** — Full rewrite:
- POST `/api/accounts`: dispatch by `body.kind` — api_key → `store.add_account()`, oauth_session → read `.credentials.json` → `store.add_oauth_account()`
- POST `/{id}/import-current-oauth` — re-import OAuth snapshot
- GET `/{id}/oauth-status` — `store.get_oauth_status(acc_id)`
- POST `/{id}/activate` — api_key → `store.activate()`, oauth_session → `oauth_service.activate_oauth_account()`
- Error codes: CREDENTIALS_FILE_NOT_FOUND, OAUTH_SNAPSHOT_INVALID, OAUTH_NEEDS_RELOGIN, CREDENTIALS_WRITE_FAILED, REVEAL_NOT_SUPPORTED_FOR_OAUTH

**`agent_dashboard/main.py`** — OAuth scheduler wired:
- Global `_oauth_refresh_lock = asyncio.Lock()`
- Lifespan: `app.state.credentials_path = config.CLAUDE_CREDENTIALS_FILE`
- Start: `asyncio.create_task(_oauth_refresh_scheduler(store), name="oauth_refresh")`
- Startup: `check_emergency_backup()` → log warning nếu có crash backup
- Shutdown: `oauth_task.cancel()` + `await asyncio.sleep(0)`

**`tests/test_accounts_oauth.py`** — 33 tests, tất cả PASS:
- Migration (idempotent, backup, kind, version), mask_oauth_token, add_oauth_account (valid/invalid/no_org), list_accounts (no raw tokens, masked, expires), update_oauth_snapshot (replaces/wrong kind/persists), set_needs_relogin, get_oauth_status, validate_oauth_block, activate_oauth_account (writes/resnapshots/restores/not found/creates backup), refresh_inactive_accounts (skips active/needs_relogin/RT expired/invokes swap)

### Frontend (React/TypeScript)

**`frontend/src/types/index.ts`** — Extended Account type:
```typescript
type AccountKind = 'api_key' | 'oauth_session'
interface Account { kind: AccountKind; oauth_masked?; needs_relogin?; expires_in_sec?; refresh_expires_in_sec?; last_refreshed_at? }
```

**`frontend/src/hooks/useApi.ts`** — Added `addOAuthAccount(name)`, `importCurrentOAuth(id)`, `getOAuthStatus(id)`. Updated `addAccount` to send `kind: 'api_key'`.

**`frontend/src/components/accounts/AccountCard.tsx`** — Kind badges (API Key / OAuth), `fmtRemaining()`, `needs_relogin` badge, removed Copy for OAuth.

**`frontend/src/components/accounts/AddAccountPanel.tsx`** — 2-tab dialog (API Key | OAuth Session). OAuth tab shows import instructions. Props: `onSaveApiKey` + `onSaveOAuth`.

**`frontend/src/pages/AccountManagerPage.tsx`** — Security banner khi có OAuth account, split `handleSaveApiKey` + `handleSaveOAuth`.

### Verification thực tế

**pytest 118/118 PASS** (85 cũ + 33 OAuth mới):
```
tests/test_accounts_oauth.py  33 passed
tests/test_accounts.py        ...
tests/test_state_manager.py   ...
Total: 118 passed
```

**claude -p verification:**
```
expiresAt BEFORE: 1786011920567 (2026-08-06 17:25:20 UTC+7, ~456 min remaining)
expiresAt AFTER:  1786011920567  — UNCHANGED (correct — token NOT near-expiry threshold)
Exit code: 0
```
Xác nhận: subprocess exit 0, `claude -p ok --model claude-haiku-4-5` hoạt động đúng. Token chỉ refresh khi còn < 30 phút — đây là behavior đúng, không phải bug.

## Artifacts

- `tools/agent-dashboard/backend/agent_dashboard/config.py` — OAuth constants ✅
- `tools/agent-dashboard/backend/agent_dashboard/accounts.py` — v2 with kind discriminator ✅
- `tools/agent-dashboard/backend/agent_dashboard/oauth_service.py` — NEW: activate, scheduler, subprocess ✅
- `tools/agent-dashboard/backend/agent_dashboard/models.py` — AccountCreate with kind ✅
- `tools/agent-dashboard/backend/agent_dashboard/routes/accounts.py` — OAuth routes ✅
- `tools/agent-dashboard/backend/agent_dashboard/main.py` — scheduler wired ✅
- `tools/agent-dashboard/backend/tests/test_accounts_oauth.py` — 33 tests ✅
- `tools/agent-dashboard/frontend/src/types/index.ts` — Account type extended ✅
- `tools/agent-dashboard/frontend/src/hooks/useApi.ts` — OAuth hooks ✅
- `tools/agent-dashboard/frontend/src/components/accounts/AccountCard.tsx` — OAuth badges ✅
- `tools/agent-dashboard/frontend/src/components/accounts/AddAccountPanel.tsx` — 2-tab ✅
- `tools/agent-dashboard/frontend/src/pages/AccountManagerPage.tsx` — security banner ✅
- `code-graph/CODE-GRAPH.md` — v1.2 thêm oauth_service.py + env vars ✅

## Commit hash
`7dcae48`

## Quyết định quan trọng

1. **`shell=True` cho subprocess trên Windows**: `claude` là `.cmd` file → cần `shell=True` để cmd.exe resolve đúng trong PATH.
2. **In-memory backup (không file) cho auto-refresh**: Tránh tích lũy backup token files. File backup chỉ dùng cho manual activate (timestamped) và emergency crash recovery.
3. **`asyncio.run_in_executor` thay `asyncio.create_subprocess_exec`**: Tránh Windows asyncio subprocess limitations trong `ProactorEventLoop`.
4. **`organizationUuid` missing from credentials**: Machine's `.credentials.json` chỉ có `['mcpOAuth', 'claudeAiOauth']` — `organizationUuid` optional, code handle None đúng.
5. **Token refresh không xảy ra khi verify**: Đúng — 456 phút còn lại >> 30 phút threshold. Đây là expected behavior, không phải lỗi.

---

## Handoff Payload — bước sau đọc phần này

- **Đã làm**: Toàn bộ Track A OAuth: data model v2, AccountStore methods, oauth_service.py (activate+scheduler+subprocess), routes/accounts.py, main.py scheduler, frontend 2-tab+badge+banner, 33 unit tests. Tất cả 118 tests pass. `claude -p` subprocess verified exit 0.

- **do_not_redo**:
  - KHÔNG re-implement data migration v1→v2 (đã có backup `accounts.v1.bak`, idempotent)
  - KHÔNG viết lại oauth_service.py — đã complete
  - KHÔNG thêm test migration/mask/backup nữa — 33 tests đã cover
  - KHÔNG thêm `--max-turns` flag vào `claude -p` — flag này không tồn tại trong CLI version hiện tại

- **watch_out**:
  - Emergency backup `.credentials.backup.emergency.json`: nếu file này tồn tại khi khởi động server → main.py log warning. Xóa thủ công sau khi xác nhận `.credentials.json` đúng.
  - Frontend build (`tsc` + `vite build`) chưa verify trong session này — kiểm tra trước security audit nếu cần đảm bảo frontend không broken.
  - `organizationUuid` trong credentials là optional — code xử lý None nhưng `org_uuid` field trong store vẫn None nếu machine không có key này.
  - Backup timestamped files `credentials.backup.<ts>.json` tích lũy trong `~/.claude/` nếu user activate nhiều lần — không có auto-cleanup, cần document cho user.

- **next_inputs** (cho TL security-audit-stride):
  - Files cần audit: `oauth_service.py` (main threat surface), `accounts.py` (token storage XOR+base64), `routes/accounts.py` (endpoint validation), `main.py` (scheduler startup)
  - Threat surface: ghi đè `.credentials.json` (file credential thật của Claude Code), XOR+base64 không phải AES, subprocess shell=True, `refresh_token` expiry handling
  - STRIDE threats rõ nhất: S (token trong accounts.enc XOR+base64), T (concurrent write thiếu lock → đã fix với asyncio.Lock), R (audit trail chưa có), D (scheduler vẫn chạy khi tất cả accounts cần relogin), E (validate_oauth_block chỉ check fields, không check token format)
  - Security decision đã có: refresh_lock prevent concurrent write, in-memory backup + finally restore, mask_oauth_token never log full token, REVEAL_NOT_SUPPORTED_FOR_OAUTH
