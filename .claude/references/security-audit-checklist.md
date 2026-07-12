# Reference: OWASP Top 10 + STRIDE Checklist chi tiết

> Tách từ `.claude/commands/security-audit-stride.md` (§5 đề xuất cải tiến — nghiên cứu `addyosmani/agent-skills`, xem `docs/research/RESEARCH-agent-skills-2026-07-12.md`). File này là nguồn chi tiết duy nhất — `security-audit-stride.md` link tới đây thay vì lặp lại nội dung.

## OWASP Top 10 — checklist đầy đủ

| # | Hạng mục | Kiểm tra cụ thể |
|---|---|---|
| A01 | Broken Access Control | Kiểm tra authorization mọi endpoint mới — user A không truy cập được resource của user B chỉ bằng đổi ID. |
| A02 | Cryptographic Failures | Không lưu secret/password plaintext; dùng hash có salt (bcrypt/argon2), TLS cho data in-transit. |
| A03 | Injection | Dùng parameterized query/ORM, không nối string SQL/shell/LDAP; escape output đúng context (HTML/JS/URL). |
| A04 | Insecure Design | Luồng nghiệp vụ có business logic bypass không (VD: bỏ qua bước thanh toán, sửa giá qua client)? |
| A05 | Security Misconfiguration | Config mặc định an toàn: CORS thu hẹp đúng origin, security headers (CSP/HSTS), debug mode tắt ở production. |
| A06 | Vulnerable Components | Dependency mới không có CVE nghiêm trọng đã biết — kiểm tra qua advisory database trước khi thêm. |
| A07 | Auth Failures | Session/token quản lý đúng (expiry, rotation, revoke khi logout), chống brute-force (rate limit login). |
| A08 | Data Integrity Failures | Deserialization/update có ký xác nhận nguồn gốc không (tránh insecure deserialization, CI/CD supply chain)? |
| A09 | Logging Failures | Log đủ security event (login fail, quyền thay đổi) — KHÔNG log secret/PII vào log thường. |
| A10 | SSRF | Validate URL/host trước khi request ra ngoài từ server (chặn truy cập nội bộ/metadata endpoint). |

## STRIDE threat modeling — checklist đầy đủ

Áp dụng cho mỗi luồng dữ liệu mới hoặc thay đổi trust boundary:

| Threat | Câu hỏi kiểm tra |
|---|---|
| Spoofing | Ai có thể giả danh identity trong luồng này (user, service, device)? |
| Tampering | Dữ liệu có thể bị sửa trái phép ở đâu (request, storage, message queue)? |
| Repudiation | Có audit log đủ để chứng minh ai đã làm gì, khi nào? |
| Information Disclosure | Dữ liệu nhạy cảm có lộ ra log/response/error message/URL không? |
| Denial of Service | Có endpoint nào không rate-limit, dễ bị lạm dụng gây quá tải? |
| Elevation of Privilege | User thường có thể leo quyền admin qua lỗ hổng nào không (IDOR, JWT chưa verify role)? |

## Cách dùng
1. Người thực hiện `security-audit-stride` copy 2 bảng trên thành checklist `- [ ]` khi audit thực tế (xem format ở `.claude/commands/security-audit-stride.md`).
2. Ghi Pass/Fail/N-A cho từng dòng — không được bỏ trống.
3. Fail ở A01/A02/A03/A07 (nhóm rủi ro cao) → BLOCK merge.

**Tái sử dụng:** `tech-lead.md`, `senior-developer.md` có thể link tới file này khi Code Review Checklist cần dẫn chi tiết bảo mật, thay vì nhân bản nội dung.
