---
step: "1.6"
plan: ../PLAN-MASTER.md
agent: project-manager
status: done
completed_at: 2026-08-05 23:59
deps: ["1.4"]
---

# STEP 1.6 — PJM: Lên Sprint Plan + Task Board

## Input nhận
Output từ Bước 1.4 (EM): `docs/planning/RESOURCE-agent-dashboard.md` — estimate effort, team assignment.
Output từ Bước 1.1–1.3: PRD, User Stories, Design Spec.

Handoff từ EM:
- do_not_redo: Estimate + phân bổ team đã chốt (SD 7nd backend, JD 9.5nd frontend, TL 4.5nd, QAE 1.5nd)
- watch_out: SD và JD chỉ bắt đầu SAU khi TDD (Bước 2.1) được Tech Lead duyệt xong; JD dùng mock server/mock data khi code song song với SD
- next_inputs: RESOURCE-agent-dashboard.md — effort từng role

## Nhiệm vụ
Lên sprint plan với task board, gắn story point, timeline, và task breakdown đủ chi tiết để TL viết TDD và dev bắt đầu code.

## Definition of Done
- [x] `docs/planning/SPRINT-agent-dashboard.md` được tạo với: sprint goal, backlog (task + SP + assignee + status), timeline ước tính
- [x] Task breakdown phân rõ: backend tasks (SD) vs frontend tasks (JD)
- [x] Milestone rõ: khi nào TDD xong → khi nào code xong → khi nào QA xong
- [x] `docs/planning/SPRINT-agent-dashboard.docx` được xuất

## Đã làm
Tạo sprint plan 1 sprint duy nhất cho Agent Dashboard. Velocity giả định 47 SP dựa trên capacity thực tế (SD 100% + JD 100% + TL 40%). Chia 21 task từ S1-T001 (TDD) đến S1-T021 (DevOps Lead smoke test), trong đó S1-T002..T007 (backend) và S1-T008..T015 (frontend) chạy song song sau khi TDD xong. Mốc hoàn thành: 2026-08-29. Xuất DOCX thành công; PDF lỗi docx2pdf RPC — ghi chú ⚠️ không block workflow. Phase 1 toàn bộ (Bước 1.1..1.6) đã hoàn thành, sẵn sàng chuyển Phase 2.

## Artifact
- `docs/planning/SPRINT-agent-dashboard.md`
- `docs/planning/SPRINT-agent-dashboard.docx` ✅
- `docs/planning/SPRINT-agent-dashboard.pdf` ⚠️ thất bại (docx2pdf RPC error — không block)

## Quyết định quan trọng
- 1 sprint duy nhất (~17 ngày lịch, 12 ngày làm việc thực sau TDD) — phù hợp project nhỏ
- Velocity 47 SP tính từ capacity (không có historical data — project mới, baseline lần đầu)
- S1-T012 (Session History) và S1-T014 (Toast/Banner) là P2 — có thể drop nếu sprint trễ > 20%
- JD dùng mock server (MSW hoặc json-server) trong giai đoạn parallel, tích hợp thật ở S1-T016

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: Sprint plan đã tạo tại `docs/planning/SPRINT-agent-dashboard.md`, 21 task đã liệt kê — không tạo lại; Phase 1 (1.1..1.6) hoàn thành toàn bộ
- watch_out: SD và JD PHẢI chờ TDD duyệt xong trước khi bắt đầu S1-T002/T008; S1-T012 và S1-T014 là P2 có thể drop; velocity 47 SP là giả định từ capacity, chưa có historical baseline
- next_inputs: `docs/planning/SPRINT-agent-dashboard.md` (sprint backlog để TL biết scope cần cover trong TDD); `docs/prd/PRD-agent-dashboard.md`; `docs/user-stories/US-agent-dashboard.md`; `docs/design/DESIGN-agent-dashboard.md` — 3 file này là input chính cho TDD (Bước 2.1)

## Commit
- Hash: (điền sau khi commit)
- Đã push: không

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
