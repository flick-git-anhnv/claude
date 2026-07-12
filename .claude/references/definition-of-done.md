# Reference: Definition of Done (DoD) — KZTEK Workspace

> Gom từ các nơi rải rác: `CLAUDE.md` §11 (artifact bắt buộc), §15 (đồng bộ tài liệu), §15.3 (checklist PR), `qa-engineer.md` (tiêu chí sign-off). File này là nguồn tổng hợp — các agent khác **link tới đây** thay vì lặp lại. Ý tưởng tham khảo từ `references/definition-of-done.md` trong repo `addyosmani/agent-skills` (xem `docs/research/RESEARCH-agent-skills-2026-07-12.md`).

> **Phân biệt AC vs DoD:** Acceptance Criteria (AC) trả lời "Có xây đúng THỨ NÀY chưa?" — cụ thể theo từng task/user story. Definition of Done (DoD) trả lời "Đã SẴN SÀNG chưa?" — áp dụng chung cho MỌI task, không đổi theo từng feature. Một DoD bị thương lượng lại mỗi sprint không còn là DoD.

## 1. Correctness
- [ ] Acceptance Criteria của task/user story đã đạt đủ (đối chiếu `docs/user-stories/US-*.md`).
- [ ] Không có regression phát hiện được ở luồng liên quan.
- [ ] Edge case chính đã được xử lý (input rỗng, giá trị biên, lỗi mạng).

## 2. Quality
- [ ] Test có ý nghĩa (không chỉ viết để đạt coverage) — unit + integration cho logic mới.
- [ ] Code review đã qua đúng chain (Two-Eyes §8 CLAUDE.md) — không self-merge, không self-approve.
- [ ] Security audit đã chạy nếu đụng auth/payment/DB schema/dữ liệu nhạy cảm (`security-audit-stride`, xem `.claude/references/security-audit-checklist.md`).
- [ ] Không còn P0/P1 bug mở liên quan đến task này (QA có quyền VETO — §8, §9 CLAUDE.md).

## 3. Integration
- [ ] Build sạch (0 lỗi) ở môi trường đích.
- [ ] (Nếu C# migrate/Avalonia) Publish thử `linux-x64` pass — không chỉ build.
- [ ] Không phá vỡ pipeline CI/CD hiện có.

## 4. Documentation
- [ ] Tài liệu liên quan đã cập nhật theo bảng mapping §15.1 CLAUDE.md (PRD/US/TDD/DESIGN/ADR/Test case) — hoặc ghi rõ lý do không cần.
- [ ] `code-graph/CODE-GRAPH.md` + `.pdf` đã cập nhật nếu thay đổi structure/API (§17 CLAUDE.md).
- [ ] File `.md` mới/sửa đã xuất `.docx`/`.pdf` theo §19 CLAUDE.md (bỏ qua nếu đang chạy trên môi trường cloud không cần xuất, theo chỉ dẫn user tại thời điểm đó).

## 5. Ship-readiness
- [ ] DevOps Engineer đã deploy staging + smoke test pass.
- [ ] DevOps Lead đã approve trước khi lên production (§8 CLAUDE.md Two-Eyes).
- [ ] Sprint doc (`docs/planning/SPRINT-*.md`) đã cập nhật trạng thái task (§15.4 CLAUDE.md).
- [ ] Không có mục nào trong checklist đồng bộ tài liệu (§15.3 CLAUDE.md) bị bỏ trống mà không giải thích lý do.

---

**Cách dùng:** agent nào cần khai một task là "hoàn thành" (Senior/Junior Developer trước khi báo Tech Lead, Tech Lead trước khi báo EM, ...) nên tự đối chiếu nhanh 5 nhóm trên trước khi đánh dấu ✅. Không cần chép lại nội dung — chỉ cần tick tinh thần từng nhóm áp dụng cho task đó.
