---
step: "9.6"
plan: ../PLAN-MASTER.md
agent: qa-engineer
status: done
completed_at: "2026-08-08 08:47"
deps: ["9.5"]
---

# STEP 9.6 — QA Smoke Test & Quality Verification Sprint 6

## Input nhận
- Báo cáo UX/UI review ở bước 9.5
- Toàn bộ source code frontend và backend sau tích hợp

## Nội dung Kiểm thử & Kết quả
1. **Kiểm thử tự động (Automated Testing):**
   - Chạy toàn bộ test suite backend: `pytest` → **251/251 test cases PASS**. Xác nhận test case mới `test_group_by_project` chạy thành công.
   - Chạy test suite frontend: `npm run test` → **23/23 tests PASS**. Xác nhận các hàm `decodeProjectSlug` và `getUsageErrorMsg` được bao phủ bởi test cases đầy đủ.
   - Biên dịch sản phẩm: `npm run build` → **Thành công 100%**, không có lỗi TypeScript (tsc -b) hay lỗi đóng gói (vite build).
2. **Kiểm thử tích hợp & Tái hiện (Integration & Smoke Tests):**
   - **Scenario 1 (Rate Limit 429):** API active usage trả về error code `'http_429'`. AppHeader vẫn giữ nguyên layout 80px, hiển thị `--` trên progress bar, rê chuột vào hiển thị tooltip giải thích đúng tiếng Việt. Thẻ tài khoản hiển thị *"Không lấy được quota ⓘ"* kèm tooltip tương ứng.
   - **Scenario 2 (Group by Project):** Truy cập view "Tổng hợp", click chuyển qua lại giữa 2 nút "Vai trò" và "Dự án". Khi chọn "Dự án", dữ liệu hiển thị chính xác (gộp token + số lần gọi của các subagents trong cùng dự án). Cột đầu tiên đổi thành "Dự án". Thư mục dự án Windows được hiển thị thân thiện (ví dụ `C:\Users\nguye\Desktop\Claude-Git\claude`). Tìm kiếm hoạt động chính xác theo đường dẫn đã hiển thị.

## Kết luận
- Chất lượng Sprint 6 đạt chuẩn tuyệt đối.
- Không phát hiện bất kỳ lỗi P0/P1 hay lỗi phát sinh (regressions).
- Quyết định: **SIGN-OFF** cho phép deploy và hoàn thành sprint.
