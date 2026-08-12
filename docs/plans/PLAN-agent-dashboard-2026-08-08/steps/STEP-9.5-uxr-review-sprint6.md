---
step: "9.5"
plan: ../PLAN-MASTER.md
agent: ux-ui-reviewer
status: done
completed_at: "2026-08-08 08:45"
deps: ["9.4"]
---

# STEP 9.5 — UX/UI Review Sprint 6: Xác thực sửa lỗi UI-001/002 + Chế độ xem theo Dự án (FR-006)

## Input nhận
- Mã nguồn đã hoàn thiện và được Tech Lead review ở bước 9.4
- UI chỉnh sửa ở 3 vị trí:
  - AppHeader: UsageBar giữ nguyên chiều cao (80px), hiển thị `--` kèm tooltip lỗi khi API bị rate-limited hoặc lỗi khác (UI-001).
  - AccountCard: Hiển thị dòng chữ *"Không lấy được quota ⓘ"*, hover vào hiện tooltip tiếng Việt thân thiện (UI-002).
  - AggregatePipelineView: Thêm segmented control để chuyển chế độ "Vai trò" / "Dự án". Cột đầu tiên đổi thành "Dự án" và decode project slug sang dạng path Windows (FR-006).

## Đánh giá UX theo 7 tiêu chí (C1–C7)
- **C1: Bố cục:** Giao diện AppHeader không còn bị nhảy chiều cao khi xảy ra lỗi API quota (trước đây giật từ 80px về 56px). Segmented control nằm gọn gàng bên trái thanh tìm kiếm, giữ tỷ lệ và căn lề đồng bộ. Bảng tổng hợp hiển thị rõ ràng thông tin dự án.
- **C2: Màu/Brand:** Các nút trượt trong Segmented Control sử dụng màu Navy chủ đạo `#251C53` và chữ trắng khi active, đồng bộ hoàn hảo với brand KZTEK.
- **C3: Typography:** Tooltip hiển thị câu tiếng Việt rõ ràng, dễ đọc, không bị lỗi font hay dịch sai nghĩa. Đường dẫn dự án Windows được chuyển từ slug `c--Users--...` thành `C:\Users\...` có phân cấp rõ ràng.
- **C4: Consistency:** Segmented control có border radius (6px) và padding đồng nhất với các phần tử input/select kế bên.
- **C5: Interactivity:** Hiệu ứng hover và click chuyển đổi giữa "Vai trò" và "Dự án" diễn ra tức thì, không gây flicker bảng. Rê chuột vào biểu tượng `ⓘ` hiển thị tooltip ngay lập tức.
- **C6: Edge cases:** Khi tài khoản không lấy được quota (ví dụ rate limit 429), thanh UsageBar hiển thị `--` thay vì biến mất hoặc crash. Tìm kiếm hoạt động chính xác cả với đường dẫn Windows đã giải mã.
- **C7: Responsive:** Khi co giãn màn hình, cụm controls (Search + Segmented + Select) tự động xuống dòng mượt mà nhờ Flexbox layout.

## Kết luận
- **PASS** — 100% các lỗi UI-001 và UI-002 đã được khắc phục hoàn toàn. Tính năng FR-006 đạt chất lượng cao về mặt trải nghiệm người dùng.
- Sẵn sàng chuyển giao sang QA để chạy smoke test.
