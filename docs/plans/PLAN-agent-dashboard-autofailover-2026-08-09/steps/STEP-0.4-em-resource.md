---
step: "0.4"
title: "Engineering Manager — Estimate effort, phân bổ team, quyết định priority & CTO review"
agent: engineering-manager
status: done
completed_at: "2026-08-09 23:10"
deps: ["0.3"]
---

# STEP 0.4 — Engineering Manager: Phân bổ Nhân sự & Quyết định Priority

## Input nhận

Từ STEP-0.3 (UX Designer):
- 4 component UI thiết kế xong: `FailoverStatusBadge`, `FailoverChainConfig` tab, `FailoverLogTable` tab, `WaitRetryBanner` global
- Backend cần: Failover engine service, 5 API endpoints mới, 5 WebSocket event types, DB migration (`failover_events`), hot-swap logic < 100ms, wait-and-retry scheduler
- Frontend cần: Tab bar mới (Account Manager), 4 React component, extend `ToastContext`, WebSocket client 5 events
- Design spec đầy đủ tại `docs/design/DESIGN-agent-dashboard-autofailover.md`

## Nhiệm vụ

Estimate effort SD/JD, xác nhận priority P2, quyết định có cần CTO review hay không, phân bổ team theo pattern Sprint 2.

## Đã làm

- Đọc PRD v2.3, US 7 stories + 11 EC, Design spec 4 component, Handoff Payload STEP-0.3.
- Tham chiếu `RESOURCE-agent-dashboard.md` (Sprint 1) để giữ nhất quán format và đơn vị ngày công.
- Estimate SD backend: 7.5 ngày (8 hạng mục — phần lớn mở rộng Sprint 2, không làm lại từ đầu).
- Estimate JD frontend: 7.5 ngày (7 hạng mục — tab bar mới + 4 component + toast extend + WS client).
- Quyết định Priority: **P2** (nhất quán toàn dự án — PRD ghi P1 nhưng EM điều chỉnh đúng tiêu chí).
- Quyết định CTO Review: **SKIP** — lý do ghi rõ trong RESOURCE file và mục "Quyết định quan trọng" dưới.
- Quyết định security audit: **BẮT BUỘC** `security-audit-stride` tại Bước 4.3 (TL review code).
- Viết `docs/planning/RESOURCE-agent-dashboard-autofailover.md`, xuất DOCX thành công.

## Artifact

- `docs/planning/RESOURCE-agent-dashboard-autofailover.md` — Phân bổ nhân sự đầy đủ ✅
- `docs/planning/RESOURCE-agent-dashboard-autofailover.docx` — Word document (KZTEK brand) ✅
- `docs/planning/RESOURCE-agent-dashboard-autofailover.pdf` — ⚠️ thất bại RPC Windows (DOCX đủ dùng)

## Quyết định quan trọng

**1. Priority: P2 (không phải P1 như PRD ghi)**
- PRD v2.3 ghi P1 nhưng đây là tool nội bộ 1 người, không production user-facing, không ảnh hưởng khách hàng.
- Nhất quán với Sprint 1–6: toàn bộ project agent-dashboard là P2.
- EM điều chỉnh P1 → P2 đúng tiêu chí thực tế.

**2. CTO Review: SKIP — lý do cụ thể:**
- Tính năng đụng credential Anthropic (`.credentials.json`, swap giữa account) nhưng đây là MỞ RỘNG của Sprint 2 đã có.
- Sprint 2 đã implement `activate_oauth_account()` + `refresh_lock` + XOR obfuscation mà không cần CTO review riêng.
- Auto-Failover chỉ gọi các hàm Sprint 2 theo trigger mới (429/quota) — không có cơ chế credential mới nào.
- Không có kiến trúc chiến lược nào đòi hỏi CTO sign-off ở cấp độ này.
- Bù đắp: `security-audit-stride` BẮT BUỘC tại Bước 4.3 — gate cứng trước merge.

**3. SD và JD song song (∥) sau khi TDD xong**
- JD dùng mock WebSocket + json-server trong giai đoạn song song.
- SD và JD chỉ bắt đầu Phase 4 SAU KHI TDD (Bước 1.2) được TL hoàn thành và duyệt.

## Handoff Payload — bước sau đọc phần này

- **do_not_redo:**
  - KHÔNG cần CTO review — đã quyết định và ghi lý do đầy đủ.
  - KHÔNG thay đổi priority P2 — đã chốt.
  - KHÔNG làm lại estimate — 7.5 ngày SD và 7.5 ngày JD là final (có thể điều chỉnh trong TDD nếu TL phát hiện scope lớn hơn).

- **watch_out:**
  - **Bước tiếp theo là Tech Lead viết TDD (Bước 1.2) — KHÔNG qua CTO.** TL bắt đầu ngay.
  - TL phải trả lời 4 câu Q-TL trong TDD trước khi SD bắt đầu: Q-TL-1 (cơ chế detect 429), Q-TL-2 (threshold API down), Q-TL-3 (DB schema failover_events), Q-TL-4 (tính T_reset).
  - **`security-audit-stride` BẮT BUỘC tại Bước 4.3 (TL review code)** — TL phải ghi rõ kết quả audit vào step file 4.3 trước khi approve merge. Fail nhóm rủi ro cao = BLOCK merge.
  - SD và JD chỉ bắt đầu Phase 4 SAU KHI TDD được TL duyệt — không bắt đầu trước.
  - PRD ghi P1 nhưng EM đã điều chỉnh P2 — không cần clarify lại với PM.

- **next_inputs:**
  - RESOURCE file đầy đủ: `docs/planning/RESOURCE-agent-dashboard-autofailover.md`
  - Design spec cho TL: `docs/design/DESIGN-agent-dashboard-autofailover.md` (mục "Hand-off cho Senior Developer" — API endpoint, WebSocket events, failover engine interface)
  - US file cho TL: `docs/user-stories/US-agent-dashboard-autofailover.md` — đặc biệt BR1–BR21, Q-TL-1..4, EC1..11
  - Existing code TL cần đọc: `oauth_service.py` (`activate_oauth_account`, `refresh_lock`), `db/` module, WebSocket server hiện tại
  - Effort đã estimate: SD 7.5nd backend, JD 7.5nd frontend — TL dùng để chia task trong TDD

## Commit

- Hash: (chưa commit — sẽ commit cùng với cập nhật PLAN-MASTER)
- Đã push: chờ commit

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
