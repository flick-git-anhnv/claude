---
step: "4.4"
plan: ../PLAN-MASTER.md
agent: devops-lead
status: todo
completed_at:
deps: ["4.3"]
---

# STEP 4.4 — DOL: Approve + Smoke Test Cuối

## Input nhận
Output từ Bước 4.3 (DOE): `docs/devops/DEPLOY-agent-dashboard.md` + script start/stop, app đang chạy.

## Nhiệm vụ
Approve deploy, chạy smoke test cuối (verify dashboard live, WebSocket kết nối, token data hiển thị đúng), confirm workflow hoàn thành.

## Definition of Done
- [ ] Chạy start-dashboard script → app khởi động thành công
- [ ] Truy cập `http://localhost:<port>` → dashboard load được
- [ ] WebSocket status hiển thị "Connected"
- [ ] Ít nhất 1 session hiển thị trong history (từ data đã có trước đó)
- [ ] Smoke test log nhúng vào DEPLOY doc hoặc ghi riêng
- [ ] Confirm workflow WF-FEATURE hoàn thành — ghi nhận vào PLAN-MASTER.md

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
