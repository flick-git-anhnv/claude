---
step: 1.2
plan: ../PLAN-MASTER.md
agent: tech-lead
status: done
completed_at: 2026-08-09 23:45
deps: [0.2, 0.3, 0.4]
---

# STEP 1.2 — Tech Lead viết Technical Design Doc

## Input nhận
- PRD v2.3 `docs/prd/PRD-agent-dashboard-autofailover.md` (7 FAIL, scope FINAL chỉ Auto-Failover Anthropic).
- US `docs/user-stories/US-agent-dashboard-autofailover.md` (7 US, 27 scenarios, 21 BR, 11 EC, 4 Q-TL cần trả lời).
- DESIGN `docs/design/DESIGN-agent-dashboard-autofailover.md` (4 component UI + spec props).
- RESOURCE `docs/planning/RESOURCE-agent-dashboard-autofailover.md` (SD 7.5nd + JD 7.5nd; security-audit-stride bắt buộc tại 4.3).
- Handoff Payload từ STEP-0.4-em-resource.md.
- Code hiện có đã đọc: `oauth_service.py` (activate_oauth_account, refresh_lock), `usage_service.py` (resets_at + seven_day_resets_at có sẵn), `db/schema.py` (pattern migration idempotent).

## Nhiệm vụ
Viết TDD đầy đủ: trả lời dứt khoát 4 câu Q-TL, đề xuất kiến trúc (state machine + sequence), DB schema mới `failover_events`, API contract (5 REST + 8 WS event), task breakdown SD/JD, rủi ro kỹ thuật + mitigation.

## Definition of Done
- [x] TDD file tạo tại `docs/tech-design/TDD-agent-dashboard-autofailover.md`
- [x] 4 câu Q-TL trả lời dứt khoát (không né tránh, có số cụ thể)
- [x] Schema `failover_events` + migration idempotent nêu chi tiết
- [x] API contract 5 REST + 8 WS event types với payload
- [x] Task breakdown S7-T01..T09 (SD) + S7-T21..T27 (JD), tổng ước tính khớp 7.5nd + 7.5nd
- [x] Rủi ro RT-1..RT-9 kèm mitigation
- [x] Xuất DOCX (PDF fail RPC — non-blocking, giống các file khác trong plan)

## Đã làm
Viết TDD 11 mục: ASSUMPTIONS, bối cảnh, goals/non-goals, trả lời 4 Q-TL, kiến trúc (module tree + state machine mermaid + sequence mermaid + concurrency), DB migration (SQL + AccountStore v2→v3), API contract, rủi ro, backward compat, task breakdown, câu hỏi chờ user, metric. Điều chỉnh SLA thực tế: latency detection 15–90s (không 5s như US-001 nêu) — nêu rõ đây là giới hạn kiến trúc vì dashboard KHÔNG proxy CLI ↔ Anthropic; đề nghị BA/PM confirm chỉnh AC. Số 100ms trong PRD được reframe: chỉ mô tả file-write latency (đo qua `swap_latency_ms`).

## Artifact
- `docs/tech-design/TDD-agent-dashboard-autofailover.md` (v1.0)
- `docs/tech-design/TDD-agent-dashboard-autofailover.docx` (KZTEK brand)
- PDF: thất bại RPC (đã note; DOCX đủ dùng — nhất quán với PRD/US/DESIGN/RESOURCE cùng plan)

## Quyết định quan trọng
1. **Detection = usage_service poll 15s + JSONL parser opportunistic**, KHÔNG proxy. Latency thực tế P95 ≤ 90s. AC US-001 "5 giây" cần đàm phán chỉnh.
2. **Threshold API-wide = distinct ≥ 2 account trả 429 trong 60s → pause 5 phút** (áp dụng BA đề xuất, cụ thể hóa cấu hình).
3. **`failover_events` = 13 field** (9 BA đề xuất + `retry_attempt` + `error_message` + `chain_snapshot_json`). Purge 30 ngày.
4. **T_reset lấy trực tiếp từ `UsageInfo["resets_at"]` và `["seven_day_resets_at"]`** — Sprint 5 đã có, không cần endpoint mới.
5. **Concurrency = `failover_action_lock` bọc ngoài Engine + reuse `refresh_lock` Sprint 2** trong `activate_oauth_account` — không tạo race mới.
6. **Failover engine gọi thẳng `activate_oauth_account`, KHÔNG dùng `_do_swap_and_invoke`** — tránh subprocess 30s block chuỗi failover.
7. **AccountStore v2→v3 migration idempotent** thêm 2 field `priority` + `include_in_chain` mặc định khi load.
8. **Server KHÔNG push `wait_retry_tick` mỗi giây** — FE tự tick từ `next_retry_at` absolute time. Giữ event type để tương lai.

## Handoff Payload — bước sau đọc phần này
- **do_not_redo:**
  - Không cần khảo sát lại `oauth_service.py` — API `activate_oauth_account(acc_id, store, path, refresh_lock)` giữ nguyên chữ ký, chỉ gọi bởi engine.
  - Không cần thêm endpoint Anthropic — `usage_service.py` đã trả đủ `resets_at`/`seven_day_resets_at`.
  - Không tạo bảng SQLite cho failover chain config — dùng JSON AccountStore XOR (thêm 2 field per-account).
  - Migration pattern đã có mẫu tại `db/schema.py` `_migrate_result_columns` — copy y hệt, gọi sau nó trong `initialize()`.
  - Số 100ms trong PRD KHÔNG phải target detection latency — chỉ là swap file-write latency; đừng cố xây proxy để đạt 100ms detection.
- **watch_out:**
  - `refresh_lock` được share bởi `activate_oauth_account` + `_do_swap_and_invoke`. Failover engine chỉ được gọi `activate_oauth_account` — KHÔNG được gọi `_do_swap_and_invoke` (nó có subprocess 30s sẽ block chuỗi failover).
  - `chain_snapshot_json` PHẢI whitelist field — RT-6 là rủi ro security cao (lộ accessToken). Có unit test grep.
  - Nếu FE Sprint 6 hiện tại dùng `switch/case` trên WS event type mà `default: throw` → JD cần fix ignore unknown types (backward compat).
  - AC "5 giây" trong US-001 sẽ FAIL nếu QA verify strict — cần chỉnh trước khi QA Bước 4.5.
  - `usage_poll_loop` chạy 15s cho MỌI account included → nếu user thêm 10 account, 10 request/15s. Cache 60s giúp giảm còn ~10 request/60s = OK.
- **next_inputs:**
  - TDD: `docs/tech-design/TDD-agent-dashboard-autofailover.md` (§4 kiến trúc, §5 migration, §6 API contract, §9 task breakdown).
  - Backend module tree đề xuất: tạo package `tools/agent-dashboard/backend/agent_dashboard/failover/` với 4 file (engine.py, detector.py, scheduler.py, models.py) + `db/failover.py`.
  - Frontend: mở rộng `ToastContext` (variant `failover`, `failover-error`); giữ nguyên `AccountCard` (thêm badge), tab bar mới hoàn toàn.
  - **SD nhận:** danh sách S7-T01..T09 với dependency graph (T01 → T02 → T03 → T04 → T05 → T06/T07/T08 → T09).
  - **JD nhận:** danh sách S7-T21..T27; T21 làm trước (tab bar), 4 component có thể song song sau đó; T25 (WaitRetryBanner) phức tạp nhất — bắt đầu sớm.
  - **PM/BA nhận 2 câu §10 TDD:** (1) chỉnh AC US-001 5s → 90s? (2) `FAILOVER_THRESHOLD_PCT` mặc định 98.0 OK?
  - SD + JD chạy **∥ song song** sau khi 2 câu §10 được confirm; JD dùng mock backend theo contract §6 từ ngày 1.

## Commit
- Hash: (sẽ điền sau khi commit)
- Đã push: (điền sau)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
