---
step: "0.2"
title: "Business Analyst — User Stories + AC"
agent: business-analyst
status: done
completed_at: "2026-08-09 22:15"
deps: ["0.1"]
---

# STEP 0.2 — Business Analyst: User Stories + AC

## Nhiệm vụ

Chi tiết hóa FAIL-1..7 từ PRD v2.3 thành User Stories có AC đo được (Given/When/Then), liệt kê edge cases bắt buộc xử lý, vẽ business flow mermaid, đặt câu hỏi kỹ thuật cho Tech Lead.

## Đã làm

- Đọc PRD v2.3 (`docs/prd/PRD-agent-dashboard-autofailover.md`) toàn bộ, đặc biệt mục 5 (FAIL-1..7) và mục 7 (Q1-Q7 đã chốt).
- Đọc PLAN-MASTER.md để nắm context và bước tiếp theo.
- Đọc Handoff Payload từ STEP-0.1 (PM).
- Đọc code hiện có: `oauth_service.py` (activate_oauth_account, refresh_lock, in-memory backup mechanism) và `accounts.py` (AccountStore, XOR encryption, needs_relogin field) để viết AC sát thực tế kỹ thuật.
- Viết 7 User Stories (US-001..007), map 1-1 với FAIL-1..7:
  - US-001: Phát hiện tự động 429/quota 100% (FAIL-1)
  - US-002: Hot-swap credential < 100ms (FAIL-2)
  - US-003: Log đầy đủ mọi sự kiện failover (FAIL-3 + FAIL-7)
  - US-004: Dashboard realtime status (FAIL-4)
  - US-005: Cấu hình failover chain (FAIL-5)
  - US-006: Wait-and-retry khi hết toàn bộ quota (FAIL-6)
  - US-007: No silent failover — indicator trực quan (FAIL-7)
- Viết 27 AC scenarios (Given/When/Then), 21 business rules (BR1..BR21), 11 edge cases (EC1..EC11).
- Vẽ business flow mermaid tổng thể (failover detection → chọn account → swap → log → retry hoặc wait-and-retry).
- Đặt 4 câu hỏi kỹ thuật cho Tech Lead (Q-TL-1..4) — không block BA, chỉ cần Tech Lead trả lời khi viết TDD.
- Xuất DOCX: thành công. PDF: lỗi docx2pdf RPC trên Windows (lỗi đã biết, không block workflow).

## Artifact

- `docs/user-stories/US-agent-dashboard-autofailover.md` — User Stories + AC source Markdown
- `docs/user-stories/US-agent-dashboard-autofailover.docx` — Word document (KZTEK brand) ✅
- `docs/user-stories/US-agent-dashboard-autofailover.pdf` — ⚠️ thất bại do RPC Windows (DOCX đã có, không block)

## Quyết định quan trọng

- **Edge case EC4 (mid-flight request):** Dashboard không thể intercept request đã in-flight. Behavior: swap chỉ ảnh hưởng request tiếp theo. Request mid-flight tự handle kết quả từ Anthropic. Đây là limitation kỹ thuật, không phải bug.
- **Edge case EC5 (non-429 errors):** Auto-failover KHÔNG trigger với lỗi network timeout, 401, 403. Chỉ 429 và quota 100% mới trigger. 401 → mark needs_relogin (đã có cơ chế).
- **Edge case EC3 (API down toàn cầu):** Nếu 2+ account 429 trong < 60 giây → assume API issue, tạm dừng auto-failover. Threshold cụ thể cần Tech Lead xác nhận (Q-TL-2).
- **Buffer wait-and-retry:** T_retry = T_reset + 30s để tránh race condition với Anthropic propagation delay.
- **Manual beats auto (BR16):** Manual activation LUÔN hủy scheduled auto-retry — đây là nguyên tắc thiết kế rõ ràng.
- **DB schema failover_events:** 9 fields đề xuất (failover_id, occurred_at, from_account_id, from_account_name, to_account_id, to_account_name, trigger_reason, result, swap_latency_ms, next_retry_at). Tech Lead xác nhận khi viết TDD (Q-TL-3).

## Handoff Payload — bước sau đọc phần này

- **do_not_redo:**
  - KHÔNG thiết kế complex auth/login/session cho multi-user — scope v2.3 là 1 user local.
  - KHÔNG thêm Gemini/OpenAI vào failover chain — chỉ Anthropic-to-Anthropic.
  - KHÔNG cross-provider (BR17) — khi tất cả Anthropic hết quota, chỉ wait-and-retry, không chuyển provider.
  - Mã hoá credential vẫn là XOR (đã chốt Q4 trong PRD) — không mở lại.

- **watch_out:**
  - Bước tiếp theo là **UI/UX Designer (0.3)**: Auto-Failover là feature **chủ yếu backend**. UI chỉ cần THÊM VÀO Account Manager đã có (Sprint 6), không thiết kế màn hình mới phức tạp.
  - 4 component UI cần design: (1) Failover status indicator/badge trên Account Manager, (2) Failover chain config drag-and-drop order, (3) Wait-and-retry countdown banner, (4) Failover Log tab/view.
  - **Không cần wireframe phức tạp** — chỉ cần mockup mức low-fidelity cho 4 component trên, tích hợp vào Account Manager section đã có.
  - Tech Lead sẽ cần trả lời Q-TL-1..4 khi viết TDD (Phase 1.2) — BA đã ghi rõ trong US file.
  - failover_events là bảng DB mới — DevOps cần migration script (Phase 5.1).

- **next_inputs:**
  - US file đầy đủ: `docs/user-stories/US-agent-dashboard-autofailover.md`
  - 4 component UI cần design (từ US-002, US-003, US-004, US-005):
    1. **Failover status indicator** (US-004 Scenario 1 + US-007): badge "FAILOVER ACTIVE" + notification toast ở header
    2. **Failover chain config UI** (US-005 Scenario 1): ordered list có drag-and-drop / nút lên-xuống, checkbox bao gồm/không
    3. **Wait-and-retry countdown** (US-006 Scenario 3 + US-004 Scenario 3): banner cảnh báo màu cam + countdown timer
    4. **Failover Log view** (US-003 Scenario 4): tab/panel dạng table, sort mới nhất lên đầu, filter theo ngày
  - Account Manager UI hiện tại (Sprint 6): UX Designer đọc code frontend để biết layout đang có trước khi design component mới.
  - PRD v2.3: `docs/prd/PRD-agent-dashboard-autofailover.md` — đặc biệt mục 5 để hiểu FAIL-4 và FAIL-5.
