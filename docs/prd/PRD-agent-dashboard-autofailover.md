# PRD: Agent Dashboard v2 — Auto-Failover Anthropic (Xoay Tài Khoản Tự Động)

**Phiên bản:** 2.3 (scope cuối cùng)
**Ngày:** 2026-08-09
**PM:** Product Manager (KZTEK)
**Ưu tiên:** P1 — Công cụ nội bộ chiến lược
**Trạng thái:** Draft — chờ BA chi tiết hóa AC

---

> **Lịch sử scope (tóm tắt):**
> - v2.0: Hiểu nhầm "Multi-User" là nhiều người dùng chung LAN → thiết kế Auth/RBAC. Đã sửa.
> - v2.1: Scope correction đúng (1 máy, 1 người, nhiều account AI). Còn giả định OpenAI trong Vault.
> - v2.2: Sau spike kỹ thuật TL — Loại OpenAI (user quyết định), loại Antigravity (không khả thi kỹ thuật), loại Gemini Advanced. Vault còn lại: Gemini CLI piggyback OAuth.
> - **v2.3 (file này):** Google đã ngừng hỗ trợ OAuth cá nhân cho Gemini CLI — thông báo lỗi khi đăng nhập: **"This client is no longer supported for Gemini Code Assist for individuals — migrate to Antigravity suite"**. Piggyback OAuth cho Gemini CLI không còn khả thi. User quyết định: **"Tạm thời xây dựng luồng cho nhiều tài khoản Claude trước, xong rồi sẽ phát triển Gemini và ChatGPT sau."** Scope thu gọn: CHỈ còn Auto-Failover Anthropic.

---

## 1. Tổng quan

### 1.1 Bối cảnh

Agent Dashboard (v1) được xây dựng qua 6 sprint (2026-08-05 → 2026-08-08) với scope cố ý giới hạn: **1 user, 1 máy local, bảo mật đơn giản, không cloud**. Quyết định này đúng ở thời điểm đó — rủi ro thấp, ra nhanh, phủ được pain point cấp bách (observability agent + chuyển account Anthropic thủ công).

Tuy nhiên user (vietanh, KZTEK) đang gặp vấn đề thực tế cụ thể và đo được:

**Claude Code CLI bị gián đoạn do hết quota Anthropic:** Khi chạy pipeline agent dài, account Anthropic hiện tại bị 429/hết quota → toàn bộ pipeline dừng đột ngột, phải restart thủ công. User có nhiều account Anthropic (hiện tối thiểu 2: `vietanh` và `OAuth Imported`) nhưng việc chuyển vẫn phải làm tay.

### 1.2 Vấn đề cần giải quyết

| Vấn đề | Hiện trạng (v1) | Tác động thực tế |
|--------|----------------|-----------------|
| **Claude Code CLI bị dừng do quota Anthropic** | Chuyển account Anthropic thủ công — click "Kích hoạt" và restart CLI | Pipeline dừng đột ngột, mất context, phải restart từ đầu — xảy ra 2–3 lần/tuần |

### 1.3 Business justification

**Tại sao làm ngay:**

1. **Mất năng suất đo được:** Claude Code dừng giữa pipeline = mất toàn bộ context subagent đang chạy. Với pipeline phức tạp (10+ bước), restart tốn 30–60 phút/lần. Xảy ra 2–3 lần/tuần.
2. **Account Manager v1 đã có nền móng tốt:** Không làm lại từ đầu — thêm failover engine vào module Account Manager đã có, cộng thêm monitoring + failover chain config.
3. **Scope nhỏ, giá trị ngay:** Ước tính 1 sprint là đủ. Không cần kiến trúc phức tạp.

---

## 2. Scope Decision — v2.3

> **Đây là mở rộng phạm vi có chủ ý** — không phải scope creep. PRD v1 ghi rõ Account Manager chỉ hỗ trợ chuyển account thủ công. PRD v2.3 thêm tự động hóa failover cho Anthropic.

| Tính năng | Quyết định | Lý do |
|---|---|---|
| Chuyển account Anthropic thủ công | **Thay bằng Auto-Failover tự động** | Pain point trực tiếp: pipeline bị dừng lúc đang chạy |
| Gemini CLI Vault | **Backlog tương lai** (xem mục 8) | Google đã ngừng hỗ trợ OAuth cá nhân cho Gemini CLI — không thể piggyback OAuth nữa |
| OpenAI/ChatGPT Vault | **Backlog tương lai** (xem mục 8) | Chưa nghiên cứu; user quyết định làm sau Anthropic failover |

**Giữ nguyên từ v1 (không thay đổi):**
- Không cloud — vẫn chạy local/on-premise, 1 máy của user
- Không multi-user/multi-tenant — vẫn chỉ 1 người dùng
- Không auth/login screen
- Không kiểm soát agent từ dashboard (read-only)

---

## 3. Đối tượng người dùng (User Persona)

### Persona duy nhất: Power-User KZTEK

| Thuộc tính | Chi tiết |
|---|---|
| Người dùng | vietanh@kztek.vn — người vận hành dashboard duy nhất |
| Bối cảnh | 1 máy tính cá nhân Windows, chạy Claude Code CLI local |
| Tài khoản AI | Tối thiểu 2 account Anthropic: `vietanh` và `OAuth (Imported)` — có thể thêm thêm sau |
| Pain point chính | Pipeline Claude Code bị dừng đột ngột khi Anthropic account hết quota |
| Kỳ vọng | Khi Anthropic hết quota → tự động chuyển sang account Anthropic khác trong chuỗi ưu tiên, Claude Code CLI không bị ngắt |

---

## 4. Mục tiêu (Goals)

### 4.1 Goals chính

- **G1 — Auto-Failover Anthropic:** Khi account Anthropic đang active bị 429 hoặc đạt 100% quota (5h/7d), hệ thống tự động hot-swap sang account Anthropic khác trong chuỗi ưu tiên đã cấu hình — Claude Code CLI không bị gián đoạn, không cần can thiệp thủ công. Khi hết toàn bộ account Anthropic trong chuỗi → cảnh báo rõ ràng, tự động chờ và retry khi quota reset.
- **G2 — Backward compatible với v1:** Mọi tính năng đã có trong Sprint 1–6 (session view, token analytics, pipeline view, session history, Account Manager Anthropic thủ công) tiếp tục hoạt động sau upgrade.

### 4.2 Non-goals (TUYỆT ĐỐI KHÔNG làm trong đợt này)

> Ghi rõ để tránh scope creep. Phân biệt với Backlog tương lai (mục 8) — Non-goals là tính năng không làm trong đợt này và không có timeline cụ thể; Backlog tương lai là "chưa tới lượt, sẽ làm sau".

| Tính năng | Lý do không làm |
|---|---|
| **Multi-user/multi-tenant thật (nhiều người dùng khác nhau)** | User đã xác nhận KHÔNG cần — đây là tool cá nhân 1 máy |
| **Hệ thống auth/login/RBAC** | Không cần vì chỉ 1 user |
| **Dashboard accessible qua LAN/nhiều máy** | Không cần — user chỉ dùng trên 1 máy local |
| **Auto-Failover cross-provider (Anthropic → Gemini/OpenAI)** | Claude Code CLI chỉ nói chuyện với Anthropic API — cross-provider failover không có ý nghĩa kỹ thuật |
| **Runaway Loop Guard** | Tính năng riêng — backlog |
| **Ollama Offloading / Local LLM** | Scope creep — đòi hỏi GPU/VRAM monitoring — backlog |
| **MCP Manager** | Tính năng riêng biệt — backlog |
| **Chat Playground / Side-by-side** | Hướng sản phẩm khác — từ chối |
| **Webhook alerts (Telegram/Discord)** | Có thể thêm sau khi Auto-Failover ổn định — backlog |
| **Export báo cáo (PDF/CSV/HTML)** | Không phải MVP — backlog |
| **Health Check / Latency Ping** | Có thể thêm ở sprint sau — backlog |
| **Rate Limit Policy per project** | Phức tạp, cần thêm data — backlog |
| **Cloud deploy / container hóa** | Vẫn giữ local/on-premise như v1 |
| **Agent kill / control từ dashboard** | Non-goal từ v1, giữ nguyên |

---

## 5. Feature Requirements — Auto-Failover Anthropic

**Mô tả:** Giám sát liên tục trạng thái quota của account Anthropic đang active. Khi phát hiện 429 hoặc quota 100% (5h/7d), tự động hot-swap sang account Anthropic tiếp theo trong chuỗi ưu tiên — tất cả trong dưới 100ms, Claude Code CLI không bị gián đoạn. Khi hết toàn bộ account: tự động chờ và retry khi quota reset.

**Acceptance-level requirements (mức cao — BA chi tiết hóa):**

- [ ] **FAIL-1:** Hệ thống tự động phát hiện khi account Anthropic active bị HTTP 429 hoặc đạt 100% quota (5h hoặc 7d rolling window).
- [ ] **FAIL-2:** Thực hiện hot-swap credential sang account Anthropic tiếp theo trong chuỗi ưu tiên trong < 100ms — không yêu cầu restart CLI hay can thiệp thủ công.
- [ ] **FAIL-3:** Mọi sự kiện failover PHẢI được log đầy đủ: thời gian, account nào bị swap, lý do (429/quota), account mới được kích hoạt. Log này hiển thị rõ trên dashboard.
- [ ] **FAIL-4:** Dashboard hiển thị trạng thái failover realtime: account đang active, thời gian reset quota dự kiến, số lần failover trong 24h.
- [ ] **FAIL-5:** User có thể cấu hình chuỗi ưu tiên failover (account nào ưu tiên trước, account nào là backup cuối) — thực hiện qua giao diện Account Manager trên dashboard.
- [ ] **FAIL-6:** Khi hết toàn bộ account Anthropic trong chuỗi (tất cả đều bị quota): (a) Cảnh báo rõ ràng trên dashboard; (b) Hệ thống **tự động chờ và retry** khi quota reset (dựa trên thời gian reset được tính toán từ quota window 5h/7d); (c) KHÔNG tự ý cross-provider sang bất kỳ provider nào khác.
- [ ] **FAIL-7:** Không có "silent failover" — mọi swap phải có indicator trực quan trên dashboard và được ghi vào log FAIL-3.

---

## 6. Metric đo lường thành công

| Metric | Target | Cách đo |
|---|---|---|
| **Failover latency** | < 100ms từ lúc phát hiện 429 đến khi account mới được kích hoạt | Log timestamp: `detection_at` và `swap_completed_at` |
| **CLI interruption rate** | 0 lần CLI bị dừng do Anthropic quota sau khi triển khai (so với baseline v1: 2–3 lần/tuần) | Đếm số incident "CLI dừng do quota" trong 2 tuần sau go-live |
| **Backward compat** | 100% tính năng v1 hoạt động sau upgrade | Regression test suite Sprint 1–6 pass toàn bộ |
| **Failover log completeness** | Mọi event failover có đủ: timestamp, account cũ, account mới, lý do | QA spot-check 10 failover events trong môi trường test |
| **Wait-and-retry correctness** | Khi hết toàn bộ quota, hệ thống tự động retry đúng sau thời điểm reset quota — không sớm hơn, không quá 5 phút muộn | QA simulate toàn bộ account hết quota, kiểm tra retry timing |

---

## 7. Câu hỏi mở — Đã chốt toàn bộ

> **KHÔNG còn câu hỏi mở nào chặn BA.** Toàn bộ Q1–Q7 đã được chốt. BA có thể bắt đầu viết User Stories + AC ngay.

| ID | Câu hỏi | Quyết định đã chốt |
|---|---|---|
| **Q1 (đã chốt)** | Gemini API có usage endpoint công khai không? | **Không còn liên quan** — Gemini CLI Vault đã bị loại khỏi scope v2.3. |
| **Q2 (đã chốt)** | Behavior khi hết toàn bộ Anthropic quota? | **Tự động chờ và retry khi quota reset** — user xác nhận. Dashboard cảnh báo + hiển thị thời gian reset dự kiến + tự động thử lại khi cửa sổ quota mở lại. Không cross-provider. |
| **Q3 (đã chốt)** | Số lượng account Anthropic hiện có? | **Tối thiểu 2 account:** `vietanh` và `OAuth (Imported)` — xác nhận từ Account Manager v1. Failover chain thiết kế hỗ trợ mở rộng thêm account dễ dàng. |
| **Q4 (đã chốt)** | Mã hoá credential Anthropic: giữ XOR hay nâng AES-256? | **Giữ XOR obfuscation** — user xác nhận. 1 user local, overhead AES-256 không xứng đáng. |
| **Q5 (đã chốt)** | OpenAI có vào scope không? | **Chưa scope** — user quyết định làm sau (xem Backlog tương lai mục 8). |
| **Q6 (đã chốt)** | Google Antigravity IDE piggyback có khả thi không? | **Không** — TL xác nhận: Electron/Chromium, token mã hoá DPAPI trong SQLite, không có file JSON đọc được. |
| **Q7 (đã chốt)** | Gemini CLI OAuth còn khả thi không? | **Không** — Google đã chặn OAuth cá nhân cho Gemini CLI. Thông báo lỗi: "This client is no longer supported for Gemini Code Assist for individuals — migrate to Antigravity suite". Cả 2 hướng piggyback Gemini (CLI OAuth + Antigravity IDE) đều bị blocked. |

---

## 8. Backlog tương lai (Sprint 8+, chưa scope)

> **Phân biệt quan trọng:** Mục này là "chưa tới lượt, sẽ làm sau" — KHÔNG phải Non-goals. Non-goals (mục 4.2) là tính năng QUYẾT ĐỊNH không làm (không có timeline). Backlog tương lai là tính năng có ý định làm nhưng chưa prioritize vào đây.

### Gemini — Tạm hoãn vì kỹ thuật bị blocked

**Tình trạng:** Cả 2 hướng piggyback đều không khả thi:
- **Gemini CLI OAuth** (đã nghiên cứu trong v2.2): Google đã ngừng hỗ trợ OAuth cá nhân — thông báo lỗi khi user thử đăng nhập: *"This client is no longer supported for Gemini Code Assist for individuals — migrate to Antigravity suite"*. Token OAuth mới không thể được tạo.
- **Google Antigravity IDE piggyback** (đã nghiên cứu trong spike v2.2): Không khả thi — Electron/Chromium app, token mã hoá bằng Windows DPAPI trong SQLite, không có file JSON đọc được.

**Hướng khả thi nếu làm sau:** Dùng API key thông thường của Google AI Studio (Gemini API key). Không piggyback được quota cá nhân như đã mong muốn, nhưng có thể quản lý nhiều API key. Cần spike kỹ thuật riêng trước khi commit.

**Không phải "sẽ không bao giờ làm"** — chỉ là hiện tại bị blocked và user ưu tiên Anthropic failover trước.

### OpenAI / ChatGPT — Chưa nghiên cứu

**Tình trạng:** Chưa có spike kỹ thuật nào xác định cơ chế credential phù hợp (API key flow, có CLI không, credential lưu ở đâu trên Windows). User đã quyết định làm sau Anthropic failover.

**Hướng cần spike khi làm:** Xác định xem OpenAI CLI (nếu có) lưu credential ở đâu, cơ chế nào phù hợp để piggyback hoặc quản lý API key.

**Không phải "sẽ không bao giờ làm"** — cần spike kỹ thuật riêng để xác định khả thi và scope.

---

## 9. Rủi ro chính

### R1 — Auto-Failover silent / khó debug (TRUNG BÌNH)

**Mô tả:** Failover tự động có thể gây nhầm lẫn khi debug: "tại sao session này dùng account A lúc đầu nhưng account B ở cuối?" Nếu không log đầy đủ sẽ rất khó trace cost và pinpoint lỗi.

**Biện pháp giảm thiểu:**
- FAIL-3 và FAIL-7 bắt buộc: mọi swap phải có log timestamp đầy đủ và indicator trực quan trên dashboard.
- QA test case: simulate failover và verify log có đủ thông tin để reconstruct timeline hoàn chỉnh.

### R2 — Scope creep tiếp tục phình to (THẤP)

**Mô tả:** Sau khi Auto-Failover ra, các tính năng trong Backlog tương lai (Gemini, OpenAI) có thể được request đưa vào cùng sprint.

**Biện pháp giảm thiểu:**
- Mục 8 (Backlog tương lai) ghi rõ lý do kỹ thuật tại sao chưa làm — PM dùng làm tài liệu tham chiếu khi có request mới.
- Gemini: chỉ làm được khi có giải pháp kỹ thuật thay thế OAuth cá nhân (cần spike riêng).

---

## 10. Ước tính phạm vi sơ bộ

> Đây là ước tính sơ bộ của PM — KHÔNG phải cam kết. EM xác nhận, PJM chốt timeline.

**Mở rộng module Account Manager có sẵn — không làm lại từ đầu:**

- Failover engine: logic phát hiện 429/quota + hot-swap credential + retry khi quota reset. Ước tính 0.5–0.7 sprint.
- Failover chain config UI: giao diện cấu hình thứ tự ưu tiên account. Ước tính 0.1–0.2 sprint.
- Failover status dashboard: realtime indicator + log hiển thị. Ước tính 0.1–0.2 sprint.
- Backward compat + regression test: ước tính 0.1–0.2 sprint.

**Ước tính tổng: ~1 sprint (~1 tuần).** Nhỏ hơn đáng kể so với v2.2 (1–1.5 sprint) nhờ loại hoàn toàn Gemini CLI Vault. Engineering Manager xác nhận sau khi Tech Lead viết TDD.

---

## 11. Dependencies & Điều kiện bắt đầu

| Điều kiện | Trạng thái | Chặn bước |
|---|---|---|
| Có ít nhất 2 account Anthropic trong Account Manager v1 | **Đã xác nhận** — `vietanh` + `OAuth (Imported)` | Không block — đủ để implement và test failover chain |
| Behavior khi hết toàn bộ Anthropic quota (FAIL-6) | **Đã chốt** — tự động chờ và retry khi quota reset | BA có thể viết AC cho FAIL-6 ngay |
| Không có câu hỏi mở nào còn chặn BA | **Xác nhận** — tất cả Q1–Q7 đã được chốt | BA bắt đầu ngay, không cần chờ gì thêm |

---

## 12. Tài liệu liên quan

- PRD v1 (gốc): `docs/prd/PRD-agent-dashboard.md`
- Plan Sprint 1–6: `docs/plans/PLAN-agent-dashboard-2026-08-05/` và `docs/plans/PLAN-agent-dashboard-2026-08-08/`
- Plan initiative này: `docs/plans/PLAN-agent-dashboard-autofailover-2026-08-09/PLAN-MASTER.md`
- Account Manager hiện tại: `tools/agent-dashboard/backend/agent_dashboard/db/` + account management module

---

## Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi | Lý do |
|---|---|---|---|
| v2.0 | 2026-08-09 | PRD ban đầu — scope sai: giả định "Multi-User" là nhiều người dùng chung LAN, thiết kế Auth/RBAC | Hiểu nhầm yêu cầu ban đầu |
| v2.1 | 2026-08-09 | Scope correction: bỏ Auth/RBAC; giữ 2 trụ cột (Vault OpenAI+Gemini + Auto-Failover); vẫn giả định OpenAI vào scope | User xác nhận: 1 máy, 1 người, nhiều account AI |
| v2.2 | 2026-08-09 | Sau spike kỹ thuật TL: (1) Loại OpenAI hoàn toàn; (2) Loại Gemini Advanced + Antigravity IDE; (3) Vault thu gọn thành "Gemini CLI Vault" (piggyback OAuth đọc `~/.gemini/oauth_creds.json`) | Spike TL xác nhận giới hạn kỹ thuật từng cơ chế |
| **v2.3** | **2026-08-09** | **Scope cuối cùng:** Loại hoàn toàn Gemini CLI Vault (Google chặn OAuth cá nhân cho Gemini CLI — cả 2 hướng đều chết). Chỉ còn **Auto-Failover Anthropic**. Q2 chốt: tự động chờ retry khi quota reset. Q3 chốt: tối thiểu 2 account. Gemini + OpenAI chuyển sang Backlog tương lai (không phải Non-goals). Không còn câu hỏi mở nào chặn BA. | Google tắt Gemini CLI OAuth cá nhân; user quyết định ưu tiên Anthropic failover trước |

---

*PRD v2.3 — Product Manager KZTEK — 2026-08-09*
*Bước tiếp theo: Business Analyst chi tiết hóa User Stories + AC cho Auto-Failover Anthropic (FAIL-1..7). Không có câu hỏi mở nào cần trả lời trước — BA bắt đầu ngay.*
