---
step: 6.4
title: "Track D Frontend: FR-003 session title, FR-002 %context badge, FR-001 pipeline view"
agent: Junior Developer
status: done
created: 2026-08-06
completed_at: 2026-08-06 15:08
deps: ["6.2"]
---

# STEP-6.4 — Track D Frontend Sprint 3

## Nhiệm vụ
Implement 3 tính năng Sprint 3 cho Agent Status Panel frontend, dùng mock data vì backend Track C đang chạy song song.

## Đã làm

### File mới tạo
- `src/components/sessions/ContextBadge.tsx` — FR-002: progress bar 48×8px + %text. Ngưỡng màu: navy 0–70%, cam nhạt 70–90%, đỏ >90%. Ẩn khi `context_pct === 0` hoặc null/undefined. `role="progressbar"` + aria-label đầy đủ.
- `src/components/sessions/StepStation.tsx` — FR-001: station active (164px, border-left 4px #F05922, `animate-ping` pulse dot, `line-clamp-3`) / done (96px, opacity 0.65, hover expand +16px, `line-clamp-2`). Dùng `data-station-active="true"` attr cho auto-scroll lookup.
- `src/components/sessions/PipelineCard.tsx` — FR-001: fetch `/api/sessions/{id}/chain` khi mount + khi `lastSubagentAt` thay đổi. Loading skeleton (animate-pulse), fail silently (empty/error → null). Scroll ngang `overflow-x:auto`, fade gradient 32px 2 bên (`pointer-events:none`). Auto-scroll active station `useEffect([chainData])`.
- `src/components/sessions/SessionCard.tsx` — SessionCard v2: title row FR-003 (null → không render, truncate 80 ký tự), ContextBadge cuối token row, PipelineCard bên dưới. Backward-compatible (session cũ không có Sprint 3 fields vẫn render bình thường).

### File cập nhật
- `src/types/index.ts`: ChainStep, ChainResponse interfaces; Session += title?/context_pct?/last_input_total?/max_context?; DeltaEvent += session_title_changed + session_context_updated
- `src/api/mockData.ts`: MOCK_SESSIONS với Sprint 3 fields đa dạng (low/warning/danger/0/null context, title/null); getMockChain() → sess-001 (5 bước active) + sess-003 (3 bước all done) + mặc định empty
- `src/api/interceptor.ts`: handler GET /api/sessions/:id/chain → getMockChain()
- `src/hooks/useApi.ts`: thêm getSessionChain(sessionId)
- `src/state/wsReducer.ts`: case session_title_changed + session_context_updated
- `src/components/agents/AgentStatusPanel.tsx`: import SessionCard thay AgentCard

### Build verification
- `tsc -b` → 0 errors
- `vite build` → 861 modules, built in 8.46s (chunk size warning: Recharts, pre-existing)
- Commit: `6673d3a`

## Quyết định quan trọng
- PipelineCard fetch data của chính nó (không phải parent truyền steps) để giảm coupling với SessionCard
- Dùng `current_subagent?.at` làm `lastSubagentAt` prop → PipelineCard tự re-fetch khi WS `subagent_changed` fires (không cần thêm event mới)
- Giữ `AgentCard.tsx` nguyên (không xóa) — SessionCard là component mới, backward-compatible
- `data-station-active="true"` thay vì forwardRef để auto-scroll đơn giản hơn

## Handoff Payload — bước sau đọc phần này

- **do_not_redo:** 4 component mới đã implement đầy đủ theo spec DESIGN §Sprint 3. Mock chain `sess-001`/`sess-003` đã có. TypeScript 0 errors, build thành công.
- **watch_out:**
  1. `ContextBadge` ẩn khi `context_pct === 0` — đây là intended behavior (không phải bug). Kiểm tra `sess-003` mock: context_pct=0 → badge không hiện.
  2. `PipelineCard` fail silently: session không có chain (sess-002/004/005/006) → fetch trả `steps:[]` → component render null — KHÔNG lỗi.
  3. `SessionCard` dùng `session.current_subagent?.at` làm refresh trigger cho PipelineCard — nếu backend Track C gửi `subagent_changed` event, PipelineCard tự re-fetch chain. Không cần logic thêm.
  4. `StepStation` active dùng `animate-ping` (Tailwind built-in) — cần Tailwind v3.3+. Package đang dùng v3.4.7 ✅.
  5. Chunk size warning (587KB) là Recharts library — tồn tại từ trước Sprint 3. Không cần xử lý.
- **next_inputs:** Commit `6673d3a`. Files Tech Lead cần review: 4 file mới + 7 file sửa (danh sách đầy đủ trong commit). Demo: `cd tools/agent-dashboard/frontend && VITE_MOCK=true npm run dev` → mở localhost:5173, tab "Agent Status" → thấy sess-001 có pipeline 5 bước + ContextBadge 4.5%, sess-002 có badge 72.3% warning màu cam. Backend Track C cần merge trước khi test với data thật.
