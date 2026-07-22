---
name: security-audit-stride
description: Chạy checklist bảo mật OWASP Top 10 + STRIDE trước bước review cuối của Tech Lead trong WF-REVIEW-CRIT (luôn chạy) và trong WF-FEATURE/WF-REFACTOR khi thay đổi đụng auth/payment/DB schema/dữ liệu nhạy cảm (có điều kiện).
---

# Security Audit (OWASP + STRIDE)

## Khi nào dùng (điều kiện bắt buộc — thỏa ≥ 1 mới chạy)
- PR/thay đổi đụng: authentication, authorization, payment, DB schema, dữ liệu cá nhân/nhạy cảm, file upload, hoặc input từ user chưa validate.
- WF-REVIEW-CRIT (luôn chạy — vì định nghĩa critical path đã bao gồm auth/payment/schema).
- WF-FEATURE / WF-REFACTOR khi Tech Lead xác định có rủi ro bảo mật ở Bước Technical Design.

## Khi nào KHÔNG dùng
- Thay đổi UI thuần (màu sắc, spacing, text tĩnh).
- Config không ảnh hưởng logic bảo mật (VD: đổi log level, timeout hiển thị).
- Task nội bộ không có input từ bên ngoài, không đụng auth/payment/schema/dữ liệu nhạy cảm.

## Common Rationalizations (lý do thường gặp để bỏ qua bước — PHẢI bác bỏ, không được chấp nhận)

| Lý do đưa ra | Thực tế |
|---|---|
| "Đây là tool nội bộ, không ai tấn công đâu" | Tool nội bộ vẫn bị compromise — kẻ tấn công nhắm vào mắt xích yếu nhất trong hệ thống. |
| "Deadline gấp, để security sau" | Vá bảo mật sau khi ship khó hơn 10 lần làm đúng từ đầu — không có "sau" thực sự an toàn. |
| "Code này đã chạy ổn nhiều năm, chắc không có lỗ hổng" | Chạy ổn không đồng nghĩa an toàn — lỗ hổng cũ chỉ chưa bị khai thác, không phải không tồn tại. |
| "Chỉ là thay đổi nhỏ, không cần audit đầy đủ" | Thay đổi nhỏ vẫn có thể mở access control hoặc injection point mới — quy mô thay đổi không tỷ lệ với rủi ro. |
| "Đã có WAF/firewall chặn rồi" | Kiểm soát ở tầng hạ tầng không thay thế được validate đúng ở tầng ứng dụng — đây là lớp phòng thủ bổ sung, không phải duy nhất. |

## Người thực hiện
`tech-lead` (mặc định) hoặc `senior-developer` khi Tech Lead giao lại — KHÔNG downshift sang model thấp hơn (đây là bước REVIEW, vi phạm §13.1b nguyên tắc 4 nếu downshift).

## Quy trình bắt buộc

> **Xem thêm:** checklist chi tiết đầy đủ (mô tả từng hạng mục) tại `.claude/references/security-audit-checklist.md` — dùng bảng rút gọn dưới đây khi audit nhanh.

### Bước 1 — OWASP Top 10 checklist
Với mỗi PR/diff liên quan, kiểm tra và ghi Pass/Fail/N-A:
```
- [ ] A01 Broken Access Control      : kiểm tra authorization mọi endpoint mới
- [ ] A02 Cryptographic Failures     : không lưu secret/password plaintext
- [ ] A03 Injection                  : dùng parameterized query, không nối string SQL/shell
- [ ] A04 Insecure Design            : luồng nghiệp vụ có business logic bypass không?
- [ ] A05 Security Misconfiguration  : config mặc định an toàn (CORS, headers, debug mode off)
- [ ] A06 Vulnerable Components      : dependency mới không có CVE nghiêm trọng đã biết
- [ ] A07 Auth Failures              : session/token quản lý đúng (expiry, rotation)
- [ ] A08 Data Integrity Failures    : deserialization/update có ký xác nhận nguồn không?
- [ ] A09 Logging Failures           : log đủ event bảo mật, KHÔNG log secret/PII
- [ ] A10 SSRF                       : validate URL/host trước khi request ra ngoài
```

### Bước 2 — STRIDE threat modeling (chỉ cho thay đổi kiến trúc/luồng dữ liệu mới)
Với mỗi luồng dữ liệu mới hoặc thay đổi trust boundary:
```
- [ ] Spoofing        : ai có thể giả danh identity trong luồng này?
- [ ] Tampering       : dữ liệu có thể bị sửa trái phép ở đâu?
- [ ] Repudiation       : có audit log để chứng minh ai đã làm gì?
- [ ] Information Disclosure : dữ liệu nhạy cảm có lộ ra log/response/error message không?
- [ ] Denial of Service : có endpoint nào không rate-limit, dễ bị lạm dụng?
- [ ] Elevation of Privilege : user thường có thể leo quyền admin qua lỗ hổng nào không?
```

### Bước 3 — Kết luận
```
Kết quả Security Audit:
- OWASP: [N/10 Pass] — mục Fail: [...]
- STRIDE: [áp dụng/không áp dụng] — rủi ro phát hiện: [...]
- Quyết định: [✅ Đủ điều kiện merge / 🛑 BLOCK — cần fix trước]
```

Nếu có mục **Fail** ở A01/A02/A03/A07 (nhóm rủi ro cao) → BẮT BUỘC block merge, trả lại Senior/Junior Developer sửa trước khi Tech Lead review lại.

## Output bắt buộc
Nhúng bảng kết quả Bước 3 vào PR description / Technical Design Doc — KHÔNG tạo file riêng trừ khi phát hiện lỗ hổng nghiêm trọng (khi đó tạo `docs/architecture/ADR-security-*.md` ghi quyết định khắc phục).

## Verification (done gate — PHẢI tick đủ trước khi báo hoàn thành)
- [ ] Cả 10 mục OWASP đã ghi Pass/Fail/N-A, không còn mục trống.
- [ ] STRIDE đã áp dụng cho mọi luồng dữ liệu mới/thay đổi trust boundary (hoặc ghi rõ "không áp dụng" kèm lý do).
- [ ] Không có mục Fail nào ở nhóm rủi ro cao (A01/A02/A03/A07) còn tồn tại chưa fix.
- [ ] Kết quả đã nhúng vào PR description / TDD — không chỉ nói miệng "đã audit".
