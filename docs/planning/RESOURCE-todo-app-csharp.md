---
id: RESOURCE-todo-app-csharp
feature: To-Do App C# Desktop/Console
prd-ref: docs/prd/PRD-todo-app-csharp.md
us-ref: docs/user-stories/US-todo-app-csharp.md
design-ref: docs/design/DESIGN-todo-app-csharp.md
author: Engineering Manager (L2)
version: 1.0
created: 2026-06-02
updated: 2026-06-02
priority: P2
status: Approved
---

# RESOURCE-todo-app-csharp: Phân bổ nhân sự — To-Do App C# Console

---

## 1. Tóm tắt quyết định

| Trường | Nội dung |
|---|---|
| **Tính năng** | To-Do App C# Console — quản lý công việc cá nhân offline |
| **Mức ưu tiên** | P2 — Không urgent, không critical; giá trị rõ ràng nhưng không ảnh hưởng hệ thống sản xuất |
| **Scope MVP** | Sprint 1: F01–F07 (Must Have); Sprint 2: F08–F10 (Should Have) |
| **Tổng timeline** | ~14 ngày làm việc (trong khung 12–17 ngày PRD ước tính) |
| **Cần CTO review** | Không — quy mô nhỏ, không liên quan kiến trúc chiến lược, bảo mật, hay hạ tầng production |
| **Engineering Manager approve** | Đinh Công Thành — 2026-06-02 |

---

## 2. Team Allocation

| Role | Tỉ lệ tham gia | Giai đoạn | Trách nhiệm chính |
|---|---|---|---|
| **Tech Lead** | Part-time (20–30%) | Toàn bộ dự án | Viết TDD, review code, approve merge, giải quyết blocker kỹ thuật |
| **Senior Developer** | Full-time (100%) | Phase 0–3 | Core layer: domain model, storage service, business logic, validation, error handling |
| **Junior Developer** | Full-time (100%) | Phase 1–3 | Console UI layer: màn hình, menu, input, rendering — theo spec DESIGN-todo-app-csharp.md |
| **QA Engineer** | Full-time (100%) | Phase 2–3 | Viết test case, thực thi, log bug, verify fix, smoke test |
| **QA Lead** | Part-time (15%) | Phase 3 | Sign-off chất lượng — bắt buộc cho P0/P1 bug trước khi release |
| **DevOps Engineer** | Part-time (10%) | Phase 4 | Build artifact, đóng gói `.exe`, verify chạy trên máy sạch |
| **DevOps Lead** | Part-time (5%) | Phase 4 | Approve artifact release cuối |

**Nguyên tắc phân công:**
- Senior Developer KHÔNG viết Console UI trực tiếp — Junior Developer phụ trách toàn bộ UI layer theo DESIGN spec.
- Junior Developer KHÔNG tự quyết định thay đổi UX — mọi sai lệch so với DESIGN-todo-app-csharp.md phải báo Tech Lead.
- Tech Lead giao việc qua format TASK chuẩn; không Engineering Manager giao thẳng cho Dev.

---

## 3. Phân bổ Effort — Sprint 1: MVP (F01–F07)

**Tổng sprint 1:** ~8 ngày làm việc

### 3.1 Phase 0 — Analysis & Design Kỹ Thuật (2 ngày)

| Task | Người thực hiện | Effort | Output bắt buộc |
|---|---|---|---|
| Viết TDD (Technical Design Doc) | Tech Lead | 1.5 ngày | `docs/tech-design/TDD-todo-app-csharp.md` |
| Xác nhận tech stack, storage format, project structure | Tech Lead | 0.5 ngày | Quyết định ghi trong TDD |
| Review TDD | Senior Developer + EM | 0.5 ngày | Comment, approve TDD |

**Phụ thuộc:** Tech Lead phải trả lời OQ1 (Console vs WPF), OQ2 (JSON vs SQLite), OQ4 (vị trí file) trước khi Phase 1 bắt đầu.

### 3.2 Phase 1 — Development MVP (F01–F07) (5 ngày)

**Senior Developer — Core/Service Layer (5 ngày):**

| Feature | Story Point | Effort ước tính | Mô tả công việc |
|---|---|---|---|
| F06 + F07: Storage Service (JSON/SQLite) | 5 SP | 1.5 ngày | IStorageService interface, JSON/SQLite implementation, write-then-rename pattern, error handling, startup load |
| Domain Model + Validation | 2 SP | 0.5 ngày | TodoItem model (Id, Title, Description, Status, Priority, DueDate, CreatedAt, UpdatedAt, CompletedAt), validation rules BR-GLOBAL-01/02 |
| F01: Create Task — Business Logic | 2 SP | 0.5 ngày | TodoService.CreateTask(), validate, persist, return result |
| F03: Edit Task — Business Logic | 2 SP | 0.5 ngày | TodoService.UpdateTask(), validate, persist |
| F04: Delete Task — Business Logic | 1 SP | 0.25 ngày | TodoService.DeleteTask(), confirm logic |
| F05: Toggle Status — Business Logic | 2 SP | 0.5 ngày | TodoService.ToggleStatus(), CompletedAt management |
| F02: Get List — Business Logic | 1 SP | 0.25 ngày | TodoService.GetAll(), sort by CreatedAt DESC |
| Unit Test (≥ 80% coverage business logic) | 3 SP | 1 ngày | Viết xNUnit/MSTest cho tất cả service + validation |

**Subtotal Senior Developer Sprint 1:** ~5 ngày

**Junior Developer — Console UI Layer (5 ngày):**

| Feature | Story Point | Effort ước tính | Mô tả công việc |
|---|---|---|---|
| AppShell + Navigation + ANSI setup | 2 SP | 0.5 ngày | ConsoleApp entry, ANSI enable, UTF-8, screen routing, keyboard handler |
| Screen 1: Màn hình chính + TaskRow rendering | 3 SP | 1 ngày | AppHeader, StatusBar, TaskRow list, MenuBar, EmptyState theo DESIGN spec |
| Screen 2: Tạo task mới (multi-step) | 3 SP | 1 ngày | 4 bước: Title → Desc → Priority → DueDate, validation inline, StepIndicator |
| Screen 3: Sửa task | 2 SP | 0.75 ngày | Hiển thị giá trị cũ, từng trường sửa riêng, [S] save |
| Screen 4: Xác nhận xóa | 1 SP | 0.25 ngày | ConfirmBox, Y/N handler, Enter mặc định = N |
| Screen 6: Toggle (inline) | 1 SP | 0.25 ngày | Nhập số task, toggle ngay, toast xác nhận |
| Screen 7: Toast Notification | 1 SP | 0.25 ngày | ToastNotification component, success/error/warning variants, 1.5s auto-dismiss |
| Unit Test UI helpers | 1 SP | 0.5 ngày | Test render helper, truncation, date display logic |
| Wire Up: kết nối UI ↔ Service | 2 SP | 0.5 ngày | Gọi đúng method từ TodoService, xử lý kết quả, hiển thị thông báo chuẩn MSG-* |

**Subtotal Junior Developer Sprint 1:** ~5 ngày

**Tổng Story Point Sprint 1:** 35 SP  
**Tổng ngày công Sprint 1:** ~12 ngày công (5 SD + 5 JD + 2 TL)

---

## 4. Phân bổ Effort — Sprint 2: Should Have (F08–F10)

**Tổng sprint 2:** ~4 ngày làm việc

| Feature | Người thực hiện | Story Point | Effort ước tính | Mô tả |
|---|---|---|---|---|
| F08: Lọc theo trạng thái (All/Pending/Completed) | Junior Developer | 3 SP | 0.75 ngày | Screen 5 Filter menu, filter logic trong service, update StatusBar |
| F09: Priority — Business Logic | Senior Developer | 2 SP | 0.5 ngày | Priority enum, default value (None), storage migration-safe read |
| F09: Priority — UI (Screen 2 Bước 3, Screen 3) | Junior Developer | 2 SP | 0.5 ngày | Priority selector, hiển thị symbol + màu trong TaskRow |
| F10: Due Date — Business Logic | Senior Developer | 3 SP | 0.75 ngày | DueDate parse/validate, overdue calculation, timezone local |
| F10: Due Date — UI (Screen 2 Bước 4, Screen 3) | Junior Developer | 3 SP | 0.75 ngày | DD/MM/YYYY input + parse, cảnh báo ngày quá khứ MSG-005, hiển thị trạng thái trong TaskRow |
| Unit test bổ sung F08–F10 | Senior + Junior | 2 SP | 0.5 ngày | Mỗi dev viết test cho phần mình |

**Subtotal Sprint 2:** ~3.75 ngày dev + 0.5 ngày TL review = ~4.25 ngày

**Tổng Story Point Sprint 2:** 15 SP

---

## 5. Phân bổ Effort — Phase 3: QA & Polish

**Tổng phase 3:** ~2 ngày

| Task | Người thực hiện | Effort |
|---|---|---|
| Viết test case chi tiết (TC-*) dựa trên US-001 đến US-010 | QA Engineer | 1 ngày |
| Thực thi manual test, log bug vào `docs/bugs/BUG-*.md` | QA Engineer | 0.5 ngày |
| Bug fix (ước tính 2–3 bug P2/P3) | Senior / Junior Developer | 0.5 ngày |
| Verify fix, regression test | QA Engineer | 0.25 ngày |
| Sign-off QA Lead | QA Lead | 0.25 ngày |

---

## 6. Phân bổ Effort — Phase 4: Release

**Tổng phase 4:** ~1 ngày

| Task | Người thực hiện | Effort |
|---|---|---|
| Build `dotnet publish` → single-file `.exe` | DevOps Engineer | 0.25 ngày |
| Verify chạy trên máy sạch (không cài VS/SDK) | DevOps Engineer | 0.25 ngày |
| Approve artifact, xác nhận DoD production | DevOps Lead | 0.25 ngày |
| Viết README cơ bản (cách chạy, yêu cầu hệ thống) | Junior Developer | 0.25 ngày |

---

## 7. Tổng Effort Toàn Dự Án

| Giai đoạn | Ngày làm việc |
|---|---|
| Phase 0 — Analysis & TDD | 2 ngày |
| Phase 1 — Development Sprint 1 (F01–F07) | 6 ngày |
| Phase 2 — Development Sprint 2 (F08–F10) | 4 ngày |
| Phase 3 — QA & Bug Fix | 2 ngày |
| Phase 4 — Release & Packaging | 1 ngày |
| **Tổng** | **~15 ngày làm việc** |

> Trong khung 12–17 ngày PRD ước tính. Buffer ~2 ngày nếu có bug phức tạp hoặc scope nhỏ thêm từ PM.

### Bảng Story Point tổng hợp

| Sprint | Must Have / Should Have | Story Points | Assignee chính |
|---|---|---|---|
| Sprint 1 | F01–F07 | 35 SP | SD (Core) + JD (UI) |
| Sprint 2 | F08–F10 | 15 SP | SD (Logic) + JD (UI) |
| **Tổng** | | **50 SP** | |

---

## 8. Priority — Quyết định Chính Thức

**Priority: P2**

**Lý do:**
- Ứng dụng phục vụ người dùng cá nhân (nội bộ hoặc demo), không phải hệ thống production nghiệp vụ.
- Không có SLA, không có user base thực tế cần phục vụ ngay.
- Không liên quan đến revenue, bảo mật, hoặc hạ tầng core của KZTEK.
- Timeline 12–17 ngày hoàn toàn khả thi với team 2 dev full-time.
- Không cần escalate lên CTO: feature không liên quan kiến trúc chiến lược, không có rủi ro bảo mật.

**Scope chốt:**
- Sprint 1 (MVP): **F01, F02, F03, F04, F05, F06, F07** — Must Have, bắt buộc hoàn thành.
- Sprint 2: **F08, F09, F10** — Should Have, làm sau Sprint 1 complete và QA sign-off Sprint 1.
- F11–F13 (Could Have): Không làm trong 2 sprint này. PM mở backlog ticket nếu cần ở v1.1.
- Mọi thay đổi scope phải qua PM, không self-scope.

---

## 9. Resource Constraints

| Constraint | Chi tiết |
|---|---|
| **Team size** | 2 developer full-time (1 Senior + 1 Junior). Nhỏ — không có buffer dev. |
| **Availability** | Tech Lead part-time (20–30%); không ảnh hưởng nếu Dev chủ động, TL review 1–2 lần/ngày |
| **Infrastructure** | Không cần cloud, CI/CD phức tạp, hay server. Build local + publish single-file `.exe` |
| **Dependency bên ngoài** | Không có — .NET 8 SDK, NuGet packages ổn định, không cần license bên thứ ba |
| **Parallel work risk** | Nếu Junior Developer bị pull sang task khác trong Sprint 1 → báo ngay EM để điều chỉnh |
| **No overtime policy** | P2 không justify overtime. Nếu có delay → cắt F08–F10 trước, giữ MVP |

---

## 10. Risk Assessment

| ID | Rủi ro | Xác suất | Ảnh hưởng | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | Junior Developer chưa quen ANSI console, mất thêm thời gian implement UI | Trung bình | Trung bình | Tech Lead tạo AppShell skeleton + ANSI helper trước; JD điền vào. Senior Dev review UI code lần 1. | Tech Lead |
| R2 | File JSON bị corrupt khi crash mid-write | Thấp | Cao | Senior Dev dùng write-then-rename pattern (BR2 trong US-006). Test crash scenario. | Senior Dev |
| R3 | Scope creep — PM thêm F11–F13 giữa Sprint 1 | Trung bình | Cao | PM đã lock scope MoSCoW. EM sẽ block mọi scope addition vào sprint đang chạy. | EM + PM |
| R4 | Test coverage < 80% khi TL review | Trung bình | Trung bình | TL yêu cầu coverage report trước khi merge. QA không sign-off nếu coverage chưa đủ. | Tech Lead + QA Lead |
| R5 | ANSI màu không hiển thị trên Windows 10 cũ | Thấp | Thấp | Design spec có fallback plaintext (DESIGN mục 12.3). JD implement kiểm tra OS version. | Junior Dev |

---

## 11. Quyết định Open Questions từ PRD

### OQ3: Có cần hỗ trợ Windows 10 trở xuống không?

**Quyết định của Engineering Manager: Hỗ trợ Windows 10 build 1511 trở lên (tối thiểu). Không hỗ trợ Windows 7/8.**

**Lý do:**
- Persona A (sinh viên) và Persona B (nhân viên văn phòng) đều đang dùng Windows 10 hoặc Windows 11 tại thời điểm 2026.
- Windows 10 build 1511 (November Update, 2015) là phiên bản đầu tiên hỗ trợ ANSI escape codes trong console — cần thiết cho color scheme đã được UX thiết kế.
- Hỗ trợ Windows 7/8 đòi hỏi fallback phức tạp, không tương xứng với quy mô P2.
- .NET 8 Runtime tối thiểu yêu cầu Windows 10 version 1607 — quyết định này align với tech stack.

**Hệ quả:**
- Ứng dụng sẽ require .NET 8 Runtime hoặc publish dưới dạng self-contained single-file (ưu tiên).
- Khi khởi động: kiểm tra `Console.WindowWidth` và version Windows; nếu ANSI không hỗ trợ → disable màu, chạy plaintext thuần (fallback đã có trong DESIGN spec mục 12.3).
- DevOps Engineer ghi rõ yêu cầu hệ thống trong README: "Windows 10 (1607 trở lên) hoặc Windows 11".

**Các OQ còn lại (OQ1, OQ2, OQ4):** Thuộc thẩm quyền Tech Lead, phải trả lời trong TDD trước khi Phase 1 bắt đầu.

---

## 12. Definition of Done — Cấp Resource

Engineering Manager xác nhận task resource allocation hoàn thành khi:

- [x] Team allocation được xác định rõ: ai làm gì, tỉ lệ tham gia
- [x] Effort estimate chi tiết theo feature (F01–F10) và phase
- [x] Priority P2 được chính thức confirm với lý do
- [x] Scope Sprint 1 / Sprint 2 được chốt
- [x] Resource constraints được ghi nhận
- [x] Risk assessment với mitigation plan
- [x] OQ3 được trả lời bằng quyết định có căn cứ
- [ ] Project Manager nhận bàn giao để lập sprint plan (`SPRINT-*-PLAN.md`)
- [ ] Tech Lead nhận brief để bắt đầu TDD

---

## 13. Bàn giao sang bước tiếp theo

**Bước tiếp theo trong WF-FEATURE:**
- **Bước 6 → Project Manager:** Lập sprint plan chi tiết, timeline, task board dựa trên resource allocation này.
- **Bước 7 → Tech Lead:** Viết TDD, chia task chi tiết cho Senior và Junior Dev, trả lời OQ1/OQ2/OQ4.

**Input Project Manager cần từ tài liệu này:**
- Team: 1 Senior Dev + 1 Junior Dev full-time; TL part-time 20–30%
- Sprint 1: 8 ngày, 35 SP, scope F01–F07
- Sprint 2: 4 ngày, 15 SP, scope F08–F10
- Phase 3 QA: 2 ngày; Phase 4 Release: 1 ngày
- Tổng: ~15 ngày làm việc

---

*Tài liệu này là đầu vào chính thức cho Project Manager (Sprint Plan) và Tech Lead (TDD).*
*Mọi thay đổi resource hoặc scope sau khi đã approve phải được Engineering Manager duyệt lại.*
