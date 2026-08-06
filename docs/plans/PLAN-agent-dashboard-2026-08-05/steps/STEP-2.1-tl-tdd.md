---
step: "2.1"
plan: ../PLAN-MASTER.md
agent: tech-lead
status: done
completed_at: 2026-08-06 00:15
deps: ["1.3", "1.6"]
---

# STEP 2.1 — TL: Technical Design Document

## Input nhận
Output từ Bước 1.3 (UX): `docs/design/DESIGN-agent-dashboard.md` — wireframe, component list.
Output từ Bước 1.6 (PJM): `docs/planning/SPRINT-agent-dashboard-01-PLAN.md` — task breakdown.
Output từ Bước 1.1 (PM): `docs/prd/PRD-agent-dashboard.md` — feature list + scope.
Output từ Bước 1.2 (BA): `docs/user-stories/US-agent-dashboard.md` — AC chi tiết.

## Nhiệm vụ
Viết Technical Design Document: chọn tech stack, thiết kế kiến trúc tổng thể (backend + frontend + storage), định nghĩa API contract (WebSocket events + REST endpoints), DB schema SQLite, file-watcher mechanism, account store design, và chia task cụ thể cho SD (backend) và JD (frontend).

## Definition of Done
- [ ] `docs/tech-design/TDD-agent-dashboard.md` được tạo đầy đủ các mục:
  - [ ] Tech stack quyết định (VD: Python/FastAPI + SQLite + vanilla HTML/JS hoặc React)
  - [ ] Kiến trúc tổng thể (sơ đồ text: file-watcher → parser → SQLite → WebSocket server → browser UI)
  - [ ] File-watcher design: watch `~/.claude/projects/*/*.jsonl`, parse JSONL, detect new lines, push events
  - [ ] API contract: WebSocket events (agent_started, agent_update, agent_ended, token_update), REST endpoints (GET /sessions, GET /sessions/history, GET /accounts, POST /accounts/switch)
  - [ ] SQLite schema: tables sessions, token_events, accounts
  - [ ] Account store design: format file lưu accounts/API keys (mã hoá nhẹ — VD: base64 + local salt, không cần AES đầy đủ với tool cá nhân)
  - [ ] Task breakdown chi tiết cho SD và JD (input/output rõ từng task)
- [ ] `docs/tech-design/TDD-agent-dashboard.docx` + `.pdf` được xuất

## Đã làm
Viết TDD đầy đủ 14 mục cho Agent Dashboard: assumptions, goals/non-goals, tech stack (Python/FastAPI + Vite/React/TS), kiến trúc pipeline (mermaid) + 8 module backend, state machine session (Running/Idle/Ended với threshold 5m/30m), xử lý partial-write JSONL (offset persist + chỉ parse dòng end \n), API contract 11 REST endpoints + WebSocket envelope + 6 event types, SQLite schema 4 tables + index, account store XOR+base64, cấu trúc thư mục `tools/agent-dashboard/backend|frontend/`, task breakdown khớp 21 task Sprint, rủi ro + mitigation, Handoff Payload riêng cho SD (backend) và JD (frontend).

## Artifact
- `docs/tech-design/TDD-agent-dashboard.md` (~430 dòng)
- `docs/tech-design/TDD-agent-dashboard.docx` (KZTEK brand)
- PDF: ✗ thất bại do Word RPC lỗi (docx2pdf) — DOCX vẫn OK, workflow không block theo §19.4

## Quyết định quan trọng
1. Backend: Python 3.10+/FastAPI/watchdog/aiosqlite — khớp Sprint đã chốt, không đổi sang Node.
2. Frontend: Vite + React 18 + TypeScript + Tailwind + Recharts + native WebSocket (không Redux).
3. State machine: Running (event ≤ 5m) → Idle (5-30m) → Ended (>30m), ticker asyncio 30s.
4. Partial JSONL: `tail_reader` chỉ commit offset qua dòng end `\n`, dòng dở giữ RAM đợi tick sau; offset persist `file_cursors` table survive restart.
5. Account key: XOR + base64 với salt = SHA256(username+hostname), reveal endpoint rate-limit 5/phút, KHÔNG inject runtime.
6. Cấu trúc project: `tools/agent-dashboard/` (backend + frontend), không đụng `.claude/` hệ thống.
7. Port 7770, backend serve luôn frontend build ở production (mount StaticFiles).
8. SQLite WAL mode + 1 writer serialize asyncio queue tránh lock.

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")

### → Senior Developer (Bước 3.1 / S1-T002..T007 — Backend)
- **do_not_redo:** Đã chốt Python/FastAPI + watchdog + aiosqlite + SQLite; module layout §5.1, DB schema §7, API contract §6, state machine §5.2, partial-write handling §5.3 đã thiết kế xong — implement theo TDD, không design lại.
- **watch_out:**
  1. JSONL dòng cuối có thể chưa `\n` → PHẢI check `endswith("\n")` trước parse, không commit offset qua dòng dở.
  2. watchdog Windows đôi khi miss event khi file grow nhanh → chuẩn bị fallback PollingObserver 500ms.
  3. SQLite: bật WAL + 1 writer duy nhất qua asyncio queue → tránh lock.
  4. Threshold state machine (`IDLE=300s`, `ENDED=1800s`) đặt trong `config.py`, không hardcode.
  5. KHÔNG log plaintext API key ở đâu cả — mask tại boundary `GET /api/accounts`.
  6. Dùng `pathlib.Path.home() / ".claude" / "projects"` — không hardcode `~`.
- **next_inputs:** `docs/tech-design/TDD-agent-dashboard.md` (§5, §6, §7, §8, §9 backend, §11 backend), `docs/design/DESIGN-agent-dashboard.md` §Design System (chỉ token names). Implement path: `tools/agent-dashboard/backend/`.

### → Junior Developer (Bước 3.2 / S1-T008..T015 — Frontend)
- **do_not_redo:** Chốt Vite + React 18 + TS + Tailwind + Recharts + native WebSocket (không Redux). API contract §6 đã có → viết MSW mock chính xác từ đầu. Scaffold bằng skill `vite-react-setup` hoặc `npm create vite@latest`.
- **watch_out:**
  1. JD chạy **song song** SD → PHẢI dùng MSW mock toàn bộ REST + WS từ S1-T008, KHÔNG chờ backend.
  2. Design token BẮT BUỘC qua Tailwind config custom theme — KHÔNG hardcode màu hex trong JSX.
  3. WS envelope `{type: "snapshot|delta", ts, payload}` — reducer phân biệt snapshot (replace) vs delta (merge).
  4. Recharts stacked bar 4 series đúng thứ tự color: input=Navy dark, output=Cam, cache_creation=Navy mid, cache_read=Navy light.
  5. Copy API key: gọi `GET /api/accounts/{id}/reveal`, Toast "Đã copy", auto-clear clipboard sau 30s.
  6. 4 page phải chịu được state "Chưa có active account" (BannerAlert warning nhưng vẫn render).
- **next_inputs:** `docs/tech-design/TDD-agent-dashboard.md` (§6, §11 frontend), `docs/design/DESIGN-agent-dashboard.md` (toàn bộ). Implement path: `tools/agent-dashboard/frontend/`.

## Commit
- Hash: (session in-progress — sẽ commit bởi orchestrator)
- Đã push: chưa

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
