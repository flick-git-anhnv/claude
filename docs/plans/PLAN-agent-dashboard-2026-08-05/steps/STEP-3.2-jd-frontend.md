---
step: "3.2"
plan: ../PLAN-MASTER.md
agent: junior-developer
status: todo
completed_at:
deps: ["2.1"]
---

# STEP 3.2 — JD: Code Frontend

## Input nhận
Output từ Bước 2.1 (TL): `docs/tech-design/TDD-agent-dashboard.md` — tech stack, API contract, WebSocket events, task breakdown JD.
Output từ Bước 1.3 (UX): `docs/design/DESIGN-agent-dashboard.md` — wireframe, component list, brand colors.

## Nhiệm vụ
Implement frontend dashboard theo design spec và TDD: Agent Live View (hiển thị agent đang chạy realtime qua WebSocket), Session History (danh sách session đã kết thúc), Token Usage Chart (biểu đồ xu hướng từ SQLite), và Account Switcher.

## Definition of Done
- [ ] `src/agent-dashboard/frontend/` tạo đủ:
  - [ ] Agent Live View: connect WebSocket, hiển thị AgentCard realtime (agent name, status, current task, token count live update)
  - [ ] Session History: fetch REST GET /sessions/history, hiển thị danh sách session theo ngày, có lọc theo date range
  - [ ] Token Usage Chart: hiển thị biểu đồ đường/cột token usage theo ngày/tuần/tháng (dùng Chart.js hoặc lightweight lib)
  - [ ] Account Switcher: dropdown/modal để xem danh sách account, chọn account active, thêm/xóa account
  - [ ] WebSocket reconnect tự động khi mất kết nối + hiển thị trạng thái connection
  - [ ] Empty state rõ ràng khi không có session/data
  - [ ] Màu sắc/style theo brand KZTEK (Navy #251C53, Cam #F05922)
- [ ] Responsive cơ bản (hoạt động tốt trên màn hình desktop 1080p+)
- [ ] Chạy pre-coding-check trước khi code
- [ ] Chạy `/verify-pr` và đính kèm VERIFICATION REPORT vào PR description trước khi chuyển TL review

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
