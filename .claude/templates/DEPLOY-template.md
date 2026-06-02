# DEPLOY-[feature-slug]: Kế hoạch deploy

## Thông tin
- Feature: ...
- Version: ...
- Deploy window: [ngày giờ]
- Strategy: [Blue-Green / Canary / Rolling / Direct]

## Pre-deploy checklist
- [ ] PR approved bởi Tech Lead
- [ ] CI/CD pass
- [ ] QA sign-off (TEST-PLAN-[feature-slug].md)
- [ ] DevOps Lead approve
- [ ] Engineering Manager approve (nếu cần)
- [ ] Rollback plan sẵn sàng
- [ ] On-call standby xác nhận

## Rollback plan
- Trigger rollback khi: [điều kiện]
- Cách rollback: [lệnh / steps cụ thể]
- Thời gian rollback ước tính: ...

## Monitor sau deploy (30 phút)
- Dashboard: ...
- Alert cần theo dõi: ...
- Chỉ số healthy: ...

## Approvers
- DevOps Lead: [tên] — [ngày]
- Engineering Manager: [tên] — [ngày]
