---
step: "1.3"
plan: ../PLAN-MASTER.md
agent: ui-ux-designer
status: done
completed_at: 2026-08-05 23:05
deps: ["1.2"]
---

# STEP 1.3 — UX: Thiết kế Wireframe + Design Spec

## Input nhận
Output từ Bước 1.2 (BA): `docs/user-stories/US-agent-dashboard.md` — user stories, AC.
Output từ Bước 1.1 (PM): `docs/prd/PRD-agent-dashboard.md` — feature list.

## Nhiệm vụ
Thiết kế layout tổng thể dashboard (wireframe text-based hoặc ASCII), mô tả các màn hình chính, flow chuyển đổi giữa các view, và component list. Áp dụng brand KZTEK (Navy #251C53, Cam #F05922).

## Definition of Done
- [ ] `docs/design/DESIGN-agent-dashboard.md` được tạo với: layout tổng thể, mô tả từng màn hình (Agent Live View, Session History, Token Usage Chart, Account Manager), navigation flow
- [ ] Mô tả rõ trạng thái UI: loading, empty state, error state, WebSocket disconnected state
- [ ] Component list: liệt kê các component chính cần build (AgentCard, SessionRow, TokenChart, AccountSwitcher...)
- [ ] Màu sắc/style theo brand KZTEK
- [ ] `docs/design/DESIGN-agent-dashboard.docx` + `.pdf` được xuất

## Đã làm
- Đọc brand KZTEK (Navy #251C53, Cam #F05922) và toàn bộ 8 User Stories F-01..F-08
- Thiết kế layout tổng thể: Header cố định (56px, Navy bg) + Sidebar trái (220px, Navy bg) + Main content area
- Thiết kế 5 màn hình: Agent Status Panel, Token Analytics, Session History, Account Manager, Header Indicator
- Định nghĩa states đầy đủ cho mỗi màn hình: loading, empty, error, WebSocket disconnected
- Component list 13 components với props/states rõ ràng
- Design tokens đầy đủ (CSS variables)
- Quyết định 4 câu hỏi mở từ BA (Q1, Q2, Q3, Q7)
- Xuất DOCX thành công; PDF lỗi RPC (docx2pdf issue trên máy) — ghi chú ⚠️

## Artifact
- `docs/design/DESIGN-agent-dashboard.md` — Design spec đầy đủ
- `docs/design/DESIGN-agent-dashboard.docx` — DOCX (brand KZTEK) ✅
- `docs/design/DESIGN-agent-dashboard.pdf` — ⚠️ Lỗi docx2pdf RPC, DOCX có sẵn

## Quyết định quan trọng
1. Không có active account → KHÔNG block chức năng — chỉ warning banner trên header
2. Agent DONE giữ trong Status Panel <24h, sau đó chuyển vào Session History
3. Backend restart → reconnect WebSocket, không reload page
4. Ngưỡng 60s/300s giữ nguyên — nếu cần tuỳ chỉnh thêm vào F-12 (P2)
5. Account Manager dùng slide-in panel (không phải modal) để không block trang chính
6. Token Analytics: biểu đồ bar chart (input: Navy, output: Cam), summary cards 3 cột

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- do_not_redo: Wireframe 5 màn hình và 13 components đã xác định, không cần thiết kế lại
- watch_out: (1) Dashboard local-only → không thiết kế cho responsive mobile. (2) PDF chưa xuất được do docx2pdf RPC lỗi — EM có thể bỏ qua PDF hoặc yêu cầu chạy lại trên máy khác. (3) Account Switcher chỉ lưu/hiển thị account, KHÔNG inject API key vào Claude Code runtime.
- next_inputs: `docs/design/DESIGN-agent-dashboard.md` — layout, component list, design tokens để EM estimate resource và PM review

## Commit
- Hash: [điền sau khi commit]
- Đã push: không

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
