---
description: Chạy TRƯỚC khi deploy production cho thay đổi phạm vi hẹp (WF-HOTFIX/WF-FASTTRACK/WF-BUGFIX) — fan-out song song Tech Lead (code review) + Security Audit + QA Engineer (smoke check), tổng hợp thành quyết định GO/NO-GO kèm rollback plan bắt buộc. KHÔNG thay thế đầy đủ WF-FEATURE cho thay đổi lớn.
---

# /ship — Pre-deploy Go/No-Go Gate

> Lấy cảm hứng từ pattern "parallel fan-out with merge" trong `commands/ship.toml` của repo `addyosmani/agent-skills` (xem `docs/research/RESEARCH-agent-skills-2026-07-12.md`, đề xuất #8).

## Khi nào dùng
- Thay đổi đã đủ điều kiện WF-HOTFIX, WF-FASTTRACK, hoặc WF-BUGFIX (scope hẹp, đã qua code review cơ bản) và cần 1 điểm quyết định GO/NO-GO nhanh trước khi DevOps deploy.
- Muốn rút ngắn wall-clock time bằng cách chạy review + security audit + smoke check ĐỘC LẬP đồng thời thay vì tuần tự (điều kiện song song hoá — RULES.md §3.4).

## Khi nào KHÔNG dùng
- Thay đổi thuộc WF-FEATURE quy mô lớn, đụng kiến trúc/CTO cần duyệt — vẫn phải đi đủ chain PM→BA→...→DOL, `/ship` không thay thế các bước đó.
- Diff quá nhỏ (≤ 2 file, < 50 dòng, không đụng auth/payment/data/config) → có thể bỏ qua fan-out đầy đủ, chỉ cần Tech Lead review nhanh (WF-FASTTRACK bình thường), không cần chạy `/ship`.
- PR chưa qua code review cơ bản (Senior Dev/Tech Lead review lần đầu) — `/ship` là gate CUỐI, không thay thế review đầu tiên.

## Quy trình bắt buộc

### Phase A — Fan-out song song (1 lời gọi Agent tool, 3 nhánh độc lập)
```
∥ Tech Lead        : Code review theo Code Review Checklist + severity label (tech-lead.md)
∥ Security Audit    : Chạy security-audit-stride NẾU đụng auth/payment/schema/dữ liệu nhạy cảm — nếu không đụng, ghi "N/A — không áp dụng"
∥ QA Engineer       : Smoke test path bị ảnh hưởng (không cần regression đầy đủ)
```
Điều kiện song song hoá: cả 3 nhánh cùng nhận input là PR/diff hiện tại, không nhánh nào cần kết quả của nhánh khác trước khi bắt đầu (đủ điều kiện RULES.md §3.4).

### Phase B — Tổng hợp (merge kết quả 3 nhánh)
- Thu thập kết quả cả 3 nhánh — KHÔNG merge/quyết định khi thiếu bất kỳ nhánh nào.
- Nếu Tech Lead request changes HOẶC Security Audit Fail nhóm rủi ro cao HOẶC QA phát hiện P0/P1 → NO-GO ngay, không cần đợi phân tích thêm.

### Phase C — Quyết định GO/NO-GO
```
## /ship — Kết quả

Tech Lead review     : [✅ Approve / ⚠️ Có Nit/Optional / 🛑 Request changes]
Security Audit        : [✅ Pass / N/A — không áp dụng / 🛑 Fail: [mục nào]]
QA Smoke test          : [✅ Pass / 🛑 Fail: [bug nào]]

Quyết định: [🟢 GO / 🔴 NO-GO]
Blockers (nếu NO-GO): [danh sách cụ thể]

Rollback plan (BẮT BUỘC, kể cả khi GO):
- Cách revert: [git revert <commit> / feature flag off / rollback migration]
- Người thực hiện nếu cần rollback: [DevOps Lead]
- Thời gian ước tính để rollback: [X phút]
```

## Verification (done gate)
- [ ] Cả 3 nhánh Phase A đã có kết quả — không quyết định khi thiếu nhánh nào.
- [ ] Rollback plan đã viết cụ thể, không để trống kể cả khi quyết định là GO.
- [ ] NO-GO đã được báo lại cho Dispatcher/Tech Lead để quay lại đúng workflow gốc (WF-HOTFIX/WF-FASTTRACK/WF-BUGFIX) sửa tiếp — không tự ý deploy khi NO-GO.

## Escalate khi
- Security Audit phát hiện lỗ hổng nghiêm trọng ngoài dự kiến → Engineering Manager + CTO (theo §7 CLAUDE.md).
- Bất đồng giữa Tech Lead và QA về mức độ nghiêm trọng của 1 bug → QA Lead phân xử (QA có quyền VETO — §8 CLAUDE.md).
