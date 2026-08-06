---
step: 5.4
plan: ../PLAN-MASTER.md
agent: tech-lead
status: done
completed_at: 2026-08-06 10:02
deps: ["5.2"]
---

# STEP 5.4 — Security Audit STRIDE cho Track A (OAuth)

## Input nhận
Track A (5.2, commit `7dcae48`, 118/118 tests) đưa OAuth account support: `oauth_service.py`, `accounts.py` (XOR+base64), `routes/accounts.py` (import/activate/reveal), `main.py` (background refresh). Bước bắt buộc theo CLAUDE.md — đụng auth/credential nhạy cảm, không có điều kiện bỏ qua.

## Nhiệm vụ
Chạy security-audit-stride tập trung surface đã đổi. Verify 6 điểm rủi ro user chỉ ra (backup credential, race, log token, rate-limit endpoint, restore mid-swap, migration DB).

## Definition of Done
- [x] Đọc code 4 file thay đổi; đối chiếu STRIDE + OWASP Top 10
- [x] Chạy thử kịch bản exception mid-swap thật (không chỉ tin comment)
- [x] Kiểm tra log không lộ token
- [x] Quyết định BLOCK / PASS + known-issues

## Đã làm
Đọc trực tiếp 4 file (`oauth_service.py` 383 dòng, `accounts.py` 371 dòng, `routes/accounts.py` 307 dòng, `main.py` 376 dòng) + `tests/test_accounts_oauth.py`. Chạy toàn bộ 33 test oauth PASS. Chạy thêm 1 test tùy chỉnh: mock `store.activate` raise RuntimeError giữa lúc swap — file credential gốc được restore đúng (`accessToken`: NEW → ORIG, `expiresAt` 777 giữ nguyên). Kết luận: 1 High severity (race), 3 Medium, 2 Low. PASS có điều kiện với known-issues.

## Phát hiện chi tiết theo STRIDE

**H-1 [Tampering, HIGH] — Race giữa activate và auto-refresh (không chia sẻ lock):**
`_oauth_refresh_scheduler` chạy `refresh_inactive_accounts` mỗi 1800s, có `_oauth_refresh_lock`. Nhưng `activate_oauth_account()` (routes → oauth_service:58) KHÔNG nhận / KHÔNG acquire `refresh_lock`. Kịch bản race: user bấm Activate ngay lúc scheduler đang giữa swap-and-invoke của account khác → activate đọc credentials đã bị scheduler swap (không phải file gốc của active account) làm `in_memory_backup`; scheduler `finally` restore backup pre-swap của nó → **overwrite hoàn toàn credential vừa activate**. Người dùng thấy Activate "thành công" ở UI nhưng file trên disk là account cũ. Không mất khả năng login (vì scheduler backup vẫn valid) nhưng activate silently thất bại.
→ **REQUIRED FIX trước Sprint 3**: `activate_oauth_account` PHẢI nhận và `async with refresh_lock:` cùng lock với scheduler. Vì tần suất auto-refresh 30 phút / activate người dùng chỉ vài lần/ngày → xác suất thấp, chưa BLOCK merge cho Sprint 2, nhưng phải mở BUG P1 riêng.

**M-1 [Information Disclosure, MEDIUM] — API endpoint không rate-limit + không auth:**
`/activate`, `/import-current-oauth`, `/oauth-status` (routes/accounts.py) không có auth token, không rate-limit. Localhost binding (config port 7770) giảm rủi ro nhưng bất kỳ process cùng máy vẫn gọi được. Chỉ `/reveal` có rate limit 5/60s.
→ Sprint 3 nên thêm CSRF token đơn giản hoặc bearer local secret (đã ghi RESEARCH-config).

**M-2 [Repudiation/DoS, MEDIUM] — Backup file không có cleanup:**
`activate_oauth_account` tạo `.credentials.backup.<epoch>.json` mỗi lần → phình theo số lần switch. Với user switch 10 lần/ngày × 365 = 3650 file/năm. Không phải rủi ro bảo mật ngay nhưng lộ token cũ (đã hết hạn) không được xóa → tăng attack surface nếu attacker có filesystem access.
→ Sprint 3: keep-last-N (mặc định 5), xóa file cũ hơn 30 ngày.

**M-3 [Spoofing, MEDIUM] — Encryption XOR+base64 không chống chuyên gia:**
`_xor_key = SHA256(user+hostname)[:16]` là **obfuscation, không phải encryption thật**. Attacker biết username+hostname (dễ suy đoán) → decrypt trivial. Đã ghi rõ trong TDD là "mã hoá nhẹ, chấp nhận rủi ro nội bộ". Chấp nhận vì scope P2 dùng cá nhân — nhưng banner UI PHẢI nói rõ "không phải mã hoá cấp production" (kiểm tra frontend AddAccountPanel đã có banner này ở Track A).

**L-1 [Info Disclosure, LOW] — Log token: KHÔNG vi phạm.** Grep toàn bộ `logger.*` trong oauth_service.py + accounts.py: tất cả chỉ log `acc_id`, path, error message. Không có log raw `accessToken`/`refreshToken`/`api_key`. ✅

**L-2 [Tampering, LOW] — Migration v1→v2 mất dữ liệu:** `_migrate_v1_to_v2` tạo `.v1.bak` TRƯỚC khi ghi. Nếu crash mid-write → v1.bak vẫn còn, user có thể restore thủ công. `_load` chấp nhận file corrupted (log warning + start fresh) — không mất account cũ vì .v1.bak vẫn tồn tại. ✅

**Verify Point 5 mid-swap exception (đã chạy thật, không chỉ tin comment):**
```
Mock store.activate → raise RuntimeError('simulated mid-swap crash')
Kết quả: accessToken restored NEW→ORIG, expiresAt=777 giữ nguyên. PASS.
```
Cộng với test có sẵn `test_activate_oauth_restores_on_write_failure` → `finally` block đáng tin.

## Quyết định
**PASS có điều kiện — cho phép Bước 5.5 merge Sprint 2**, kèm known-issues:
- **BUG P1 mở mới**: H-1 race activate ↔ refresh (fix Sprint 3 đầu tiên, trước khi thêm feature OAuth mới).
- **Tech debt Sprint 3**: M-1 (auth endpoint), M-2 (backup cleanup).
- H-1 không BLOCK merge Sprint 2 vì: (a) xác suất thực tế thấp (auto-refresh 30 phút), (b) không gây mất login (chỉ activate silently fail), (c) fix cần refactor signature routes → nên nằm riêng PR Sprint 3.

## Artifact
- Không tạo file mới (audit-only). Rủi ro ghi trong step file này + Handoff Payload cho Bước 5.5.

## Handoff Payload — bước sau đọc phần này
- do_not_redo: Đã audit code + chạy test exception mid-swap. Bước 5.5 (TL code review cuối) KHÔNG cần audit lại STRIDE.
- watch_out: **H-1 race** — nếu Bước 5.5 review thấy có thể thêm 1 dòng `refresh_lock` vào `activate_oauth_account` mà không tăng scope quá — có thể inline fix; nếu không → mở BUG P1 Sprint 3.
- next_inputs: Kết luận PASS có điều kiện. 3 known-issues (H-1, M-1, M-2) — ghi vào PR description của Sprint 2 merge.

## Commit
- Hash: (chưa commit — sẽ push cùng cập nhật MASTER)
- Đã push: sẽ push
