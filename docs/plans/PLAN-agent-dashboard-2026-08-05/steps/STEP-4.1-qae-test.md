---
step: "4.1"
plan: ../PLAN-MASTER.md
agent: qa-engineer
status: todo
completed_at:
deps: ["3.4"]
---

# STEP 4.1 — QAE: Thực thi Test Plan

## Input nhận
Output từ Bước 3.4 (UXR): app đã pass UX review, issues blocker đã được fix.
Output từ Bước 1.2 (BA): `docs/user-stories/US-agent-dashboard.md` — AC để map test cases.

## Nhiệm vụ
Viết test cases và thực thi trên app chạy thật local. Bao phủ happy path, edge cases, và các AC đã định nghĩa trong User Stories. Log bug nếu phát hiện.

## Definition of Done
- [ ] `docs/test-cases/TC-agent-dashboard.md` được tạo với test cases đầy đủ
- [ ] Test cases bao phủ:
  - [ ] Realtime: khi có agent chạy mới, dashboard cập nhật trong ~2s
  - [ ] History: session lịch sử hiển thị đúng sau khi app khởi động lại (data từ SQLite)
  - [ ] Token chart: biểu đồ hiển thị đúng dữ liệu lịch sử
  - [ ] Account switch: chuyển account → dashboard reload với API key mới
  - [ ] WebSocket disconnect/reconnect: mất kết nối → hiển thị badge disconnect → tự reconnect
  - [ ] Empty state: khi chưa có session nào
  - [ ] File-watcher: watch đúng path `~/.claude/projects/*/*.jsonl`
- [ ] Chạy thật trên app local (KHÔNG test trên mockup)
- [ ] Bug log nếu có: `docs/bugs/BUG-agent-dashboard-*.md` cho mỗi bug P0/P1
- [ ] `docs/test-cases/TC-agent-dashboard.docx` + `.pdf` được xuất

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
