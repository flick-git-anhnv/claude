---
step: 7.2
plan: ../PLAN-MASTER.md
agent: Junior Developer
status: done
completed_at: 2026-08-06 21:15
deps: [7.1]
---

# STEP 7.2 — Frontend: Roster UI redesign (AgentRosterItem + PipelineCard)

## Input nhận
- Handoff Payload từ STEP-7.1 (Senior Developer):
  - `roster[]` thay thế hoàn toàn `steps[]` — cập nhật TypeScript types
  - `tokens` trong `history[]` entry có thể `null` → ẩn gracefully
  - `status: "active"` chỉ đúng khi child session cuối của vai trò đó đang Running
  - `result_summary` / `result_full` / `duration_ms` chưa có trong API (backend defer)
- API contract thật từ `curl http://localhost:7770/api/sessions/973154ca.../chain`:
  14 vai trò roster, `call_count` từ 1–11, token hợp lý (tech-lead: 132K out, senior-dev: 193K out)

## Nhiệm vụ
Redesign `PipelineCard.tsx` + tạo `AgentRosterItem.tsx` (thay `StepStation.tsx`) theo yêu cầu:
1. 1 ô/vai trò (gộp N lần gọi) — tên, model·description, token compact, badge active/done
2. `call_count > 1` → "(xN)" badge + nút "Xem lịch sử"
3. History panel inline bên dưới grid — liệt kê từng entry, ẩn result_summary nếu null
4. Giữ layout flex-wrap, brand màu Cam #F05922

## Definition of Done
- [x] TypeScript types: `RosterTokens`, `RosterHistoryEntry`, `RosterEntry`, `RosterResponse` thêm vào `types/index.ts`
- [x] `fmtTokensCompact()` thêm vào `utils/format.ts`
- [x] `AgentRosterItem.tsx` mới: active (196px, pulse), done (148px, hover-expand), token label, history button
- [x] `PipelineCard.tsx` redesign: dùng `roster[]`, `AgentRosterItem`, `HistoryPanel` state inline
- [x] `tsc -b` → 0 errors
- [x] `vite build` → pass

## Đã làm
1. **`types/index.ts`**: thêm Sprint 4 roster types (RosterTokens, RosterHistoryEntry, RosterEntry, RosterResponse); deprecate `ChainResponse.steps?` → `roster?[]` (optional cả hai để backward compat).
2. **`utils/format.ts`**: thêm `fmtTokensCompact(n: number): string | null` — trả null nếu n≤0, "1.5K" nếu ≥1000, "1.2M" nếu ≥1M.
3. **`AgentRosterItem.tsx`** (NEW, thay `StepStation.tsx`):
   - Active: 196px, `rgba(255,170,128,0.12)` bg, `border-left: 4px solid #F05922`, pulse dot cam, `shortModel()` rút gọn prefix "claude-", xN badge cam, token label nếu >0, nút "Xem lịch sử ▾"
   - Done: 148px, mờ 0.65, hover expand → 168px + opacity 1, checkmark xanh, xN badge mờ B8B3D6
   - Token null → ẩn hoàn toàn (không hiện "0")
4. **`PipelineCard.tsx`** redesign hoàn toàn:
   - Fetch `/chain` → parse `data.roster`
   - Dùng `AgentRosterItem` + `RosterConnector`
   - State `selectedHistory: RosterEntry | null` — khi click "Xem lịch sử" → set state
   - `HistoryPanel` component inline: list history entries; token null → ẩn; `result_summary` optional → hiển thị nếu có, nút "Xem thêm" mở `result_full`
   - Header label đổi thành "[N vai trò]" / "[N vai trò — kết thúc]"
5. **`code-graph/CODE-GRAPH.md`**: v1.6 cập nhật Sprint 4 changes + DOCX xuất OK.

## Quyết định quan trọng
1. **Không xóa `StepStation.tsx`**: giữ lại để tránh break nếu có import cũ nào còn tham chiếu — sẽ cleanup sau khi TL verify.
2. **History panel inline** (không modal/portal): đơn giản, không cần thư viện ngoài, không phá flex-wrap layout. Panel xuất hiện bên dưới toàn bộ grid.
3. **Token display = input + output**: bỏ qua cache_creation/cache_read cho số compact vì cache đôi khi rất lớn (ui-ux-designer: cache_read=3.9M) làm số hiển thị gây nhầm lẫn; meaningful cost là input+output.
4. **shortModel()**: strip prefix `claude-` để tiết kiệm space trong ô hẹp ("sonnet-4-6" thay vì "claude-sonnet-4-6").

## Artifact
- `tools/agent-dashboard/frontend/src/types/index.ts`
- `tools/agent-dashboard/frontend/src/utils/format.ts`
- `tools/agent-dashboard/frontend/src/components/sessions/AgentRosterItem.tsx` (NEW)
- `tools/agent-dashboard/frontend/src/components/sessions/PipelineCard.tsx`
- `code-graph/CODE-GRAPH.md` (v1.6)

## Handoff Payload — bước sau đọc phần này
- do_not_redo: types đã thêm RosterResponse/RosterEntry/etc.; fmtTokensCompact đã có trong format.ts; AgentRosterItem đã tạo; PipelineCard đã redesign; CODE-GRAPH v1.6 updated.
- watch_out:
  - `StepStation.tsx` vẫn còn file nhưng không còn được dùng trong PipelineCard — TL có thể xem xét xóa.
  - Token display dùng `input + output` (không dùng cache) — nếu TL muốn đổi thành tổng 4 loại → sửa `AgentRosterItem.tsx` dòng `const totalTokens = entry.total_tokens.input + entry.total_tokens.output`.
  - `result_summary` / `result_full` đã có UI handler (HistoryPanel) — chờ Senior Dev commit follow-up backend để hiện data thật.
  - chunk size warning (>500KB) là pre-existing, không phải do bước này tạo ra.
- next_inputs:
  - Commit hash: `53b2a18`
  - Demo: truy cập dashboard local port 5173 → click session "973154ca..." → xem roster 14 vai trò → click "Xem lịch sử" ở Tech Lead (11 lần) / Senior Dev (11 lần) để xem panel
  - Files cần review: `AgentRosterItem.tsx`, `PipelineCard.tsx`, `types/index.ts` (Sprint 4 types)

## Commit
- Hash: 53b2a18
- Đã push: không (branch research/skills-2026-08-05, ahead of origin)
