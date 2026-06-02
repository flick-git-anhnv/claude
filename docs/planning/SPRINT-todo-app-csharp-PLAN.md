---
id: SPRINT-todo-app-csharp
product: To-Do App C# (.NET 8)
prd-ref: docs/prd/PRD-todo-app-csharp.md
us-ref: docs/user-stories/US-todo-app-csharp.md
author: Project Manager / Scrum Master
version: 1.0
created: 2026-06-02
updated: 2026-06-02
status: Planning
---

# SPRINT PLAN — To-Do App C# (.NET 8)
## Trạng thái: Planning

---

## 1. Thông tin chung

| Trường | Nội dung |
|--------|----------|
| **Dự án** | To-Do App C# Desktop/Console |
| **Sprint tổng cộng** | 3 Sprints |
| **Ngày bắt đầu** | 2026-06-03 (Thứ Tư) |
| **Ngày kết thúc dự kiến** | 2026-06-20 (Thứ Bảy) |
| **Tổng thời gian** | ~14 ngày làm việc (3 tuần) |
| **Velocity cơ sở** | 8–10 Story Points/ngày (cả team) |
| **Phương pháp** | Scrum nhẹ (Sprint 5–7 ngày, daily standup, sprint review) |

### Quy ước Story Points (SP)

| SP | Ý nghĩa |
|----|---------|
| 1 | Cực đơn giản, < 2 giờ |
| 2 | Đơn giản, ~half-day |
| 3 | Trung bình, ~1 ngày |
| 5 | Phức tạp, 1.5–2 ngày |
| 8 | Rất phức tạp, 2–3 ngày |
| 13 | Cần chia nhỏ thêm |

---

## 2. Thành viên team

| Vai trò | Tên/Ký hiệu | Thời gian | Ghi chú |
|---------|-------------|-----------|---------|
| Senior Developer | SD | Full-time | Code phức tạp, architecture, mentor |
| Junior Developer | JD | Full-time | CRUD, UI, unit test đơn giản |
| Tech Lead | TL | Part-time (~50%) | Review, design, unblock |
| QA Engineer | QAE | Part-time (~50%) | Test từ Sprint 2 trở đi |
| DevOps Engineer | DOE | Part-time (~30%) | Setup CI/CD, deploy Sprint 3 |

**Capacity tổng theo sprint (5 ngày làm việc):**
- SD: 5 ngày = ~40 giờ
- JD: 5 ngày = ~40 giờ
- TL (50%): ~20 giờ
- QAE (50%): ~20 giờ (Sprint 2–3)
- DOE (30%): ~12 giờ (Sprint 3)

---

## 3. Sprint Breakdown Tổng Quan

```
Sprint 1  |  06/03 – 06/11  |  7 ngày  |  F01–F07 (MVP Core)
Sprint 2  |  06/12 – 06/16  |  4 ngày  |  F08–F10 (Should Have)
Sprint 3  |  06/17 – 06/20  |  4 ngày  |  QA, Bug Fix, Polish, Deploy
```

---

## 4. Sprint 1 — MVP Core (F01–F07)

**Thời gian:** 2026-06-03 (T4) → 2026-06-11 (T4) — 7 ngày làm việc
**Sprint Goal:** Hoàn thành đầy đủ CRUD công việc + đánh dấu hoàn thành + lưu trữ local. Ứng dụng chạy được end-to-end.

### 4.1 Sprint 1 — Backlog

| Task ID | Mô tả | Assignee | Estimate | SP | Priority | Status | Phụ thuộc |
|---------|-------|----------|----------|----|----------|--------|-----------|
| S1-T001 | Setup project: tạo solution .NET 8, cấu trúc thư mục (Domain/Application/Infrastructure/UI) | SD | 2h | 1 | P0 | Todo | Không có |
| S1-T002 | Thiết kế data model: class `TodoItem` (Id, Title, Description, Status, CreatedAt, UpdatedAt, Priority, DueDate) | SD | 2h | 1 | P0 | Todo | S1-T001 |
| S1-T003 | Viết interface `ITodoRepository` + `ITodoService` | SD | 2h | 1 | P0 | Todo | S1-T002 |
| S1-T004 | Implement `JsonFileRepository` — lưu/đọc dữ liệu từ file JSON local | SD | 4h | 3 | P0 | Todo | S1-T003 |
| S1-T005 | Implement `TodoService`: CreateTask, UpdateTask, DeleteTask, GetAll, ToggleComplete | SD | 4h | 3 | P0 | Todo | S1-T003 |
| S1-T006 | Viết unit test cho `TodoService` (tối thiểu 80% coverage) | SD | 4h | 3 | P0 | Todo | S1-T005 |
| S1-T007 | Viết unit test cho `JsonFileRepository` | SD | 2h | 2 | P1 | Todo | S1-T004 |
| S1-T008 | Implement `ConsoleUI` — màn hình chính: hiển thị menu, danh sách task (US-002) | JD | 4h | 3 | P0 | Todo | S1-T005 |
| S1-T009 | Implement UI: Tạo task mới — form nhập liệu, validation (US-001) | JD | 4h | 3 | P0 | Todo | S1-T008 |
| S1-T010 | Implement UI: Sửa task — chọn task, form sửa, validation (US-003) | JD | 3h | 2 | P0 | Todo | S1-T008 |
| S1-T011 | Implement UI: Xóa task — confirm dialog, thực hiện xóa (US-004) | JD | 2h | 1 | P0 | Todo | S1-T008 |
| S1-T012 | Implement UI: Toggle hoàn thành / bỏ hoàn thành (US-005) | JD | 2h | 1 | P0 | Todo | S1-T008 |
| S1-T013 | Implement: Auto-save sau mỗi thao tác (US-006) — tích hợp service → repository | SD | 2h | 2 | P0 | Todo | S1-T004, S1-T005 |
| S1-T014 | Implement: Load dữ liệu khi khởi động (US-007) — xử lý file không tồn tại / corrupt | SD | 2h | 2 | P0 | Todo | S1-T004 |
| S1-T015 | Xử lý error state: storage lỗi, file corrupt, empty state UI | JD | 2h | 2 | P1 | Todo | S1-T008, S1-T014 |
| S1-T016 | Dependency Injection setup (Microsoft.Extensions.DependencyInjection) | SD | 1h | 1 | P1 | Todo | S1-T001 |
| S1-T017 | Integration test: end-to-end flow CRUD + persistence | SD | 3h | 2 | P1 | Todo | S1-T006, S1-T007 |
| S1-T018 | Code review Sprint 1 — TL review toàn bộ PR | TL | 4h | — | P0 | Todo | S1-T017 |
| S1-T019 | Fix review comments từ TL (nếu có) | SD + JD | 2h | — | P0 | Todo | S1-T018 |

**Tổng SP Sprint 1:** ~27 SP
**Capacity:** SD ~40h + JD ~40h + TL 20h = đủ để hoàn thành

### 4.2 Sprint 1 — Task Board

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SPRINT 1 TASK BOARD — MVP Core                           │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│      TODO        │   IN PROGRESS    │     REVIEW       │       DONE         │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ S1-T001 (SD)     │                  │                  │                    │
│ Setup project    │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T002 (SD)     │                  │                  │                    │
│ Data model       │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T003 (SD)     │                  │                  │                    │
│ Interfaces       │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T004 (SD)     │                  │                  │                    │
│ JsonRepository   │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T005 (SD)     │                  │                  │                    │
│ TodoService      │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T006 (SD)     │                  │                  │                    │
│ Unit test Svc    │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T007 (SD)     │                  │                  │                    │
│ Unit test Repo   │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T008 (JD)     │                  │                  │                    │
│ ConsoleUI main   │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T009 (JD)     │                  │                  │                    │
│ UI: Tạo task     │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T010 (JD)     │                  │                  │                    │
│ UI: Sửa task     │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T011 (JD)     │                  │                  │                    │
│ UI: Xóa task     │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T012 (JD)     │                  │                  │                    │
│ UI: Toggle done  │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T013 (SD)     │                  │                  │                    │
│ Auto-save        │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T014 (SD)     │                  │                  │                    │
│ Load on startup  │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T015 (JD)     │                  │                  │                    │
│ Error states     │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T016 (SD)     │                  │                  │                    │
│ DI setup         │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T017 (SD)     │                  │                  │                    │
│ Integration test │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T018 (TL)     │                  │                  │                    │
│ Code review      │                  │                  │                    │
├──────────────────┤                  │                  │                    │
│ S1-T019 (SD+JD)  │                  │                  │                    │
│ Fix review cmts  │                  │                  │                    │
└──────────────────┴──────────────────┴──────────────────┴────────────────────┘
```

---

## 5. Sprint 2 — Should Have Features (F08–F10)

**Thời gian:** 2026-06-12 (T6) → 2026-06-16 (T2) — 4 ngày làm việc (bao gồm T7 12/06 là ngày review Sprint 1)
**Sprint Goal:** Bổ sung lọc theo trạng thái, gán ưu tiên, gán ngày hạn. Ứng dụng có đủ tính năng "Should Have".

> **Lưu ý:** 2026-06-12 (T6) dành cho Sprint Review + Retrospective Sprint 1 + Sprint Planning Sprint 2. Coding Sprint 2 bắt đầu từ 2026-06-13 (T7).

### 5.1 Sprint 2 — Backlog

| Task ID | Mô tả | Assignee | Estimate | SP | Priority | Status | Phụ thuộc |
|---------|-------|----------|----------|----|----------|--------|-----------|
| S2-T001 | Implement filter theo trạng thái: All / Pending / Completed (US-008) | JD | 3h | 2 | P1 | Todo | Sprint 1 Done |
| S2-T002 | UI: hiển thị bộ lọc đang active, cập nhật danh sách khi đổi filter | JD | 2h | 1 | P1 | Todo | S2-T001 |
| S2-T003 | Implement Priority enum (Low/Medium/High) + gán priority khi tạo/sửa task (US-009) | SD | 2h | 2 | P1 | Todo | Sprint 1 Done |
| S2-T004 | UI: hiển thị priority trong danh sách + sắp xếp theo priority khi lọc | JD | 2h | 1 | P1 | Todo | S2-T003 |
| S2-T005 | Implement DueDate: parse/validate input ngày, gán vào task (US-010) | SD | 3h | 2 | P1 | Todo | Sprint 1 Done |
| S2-T006 | UI: hiển thị DueDate, highlight task quá hạn | JD | 2h | 2 | P1 | Todo | S2-T005 |
| S2-T007 | Cập nhật `JsonFileRepository` để persist Priority + DueDate | SD | 1h | 1 | P1 | Todo | S2-T003, S2-T005 |
| S2-T008 | Unit test: filter logic, priority sorting | SD | 3h | 2 | P1 | Todo | S2-T001, S2-T003 |
| S2-T009 | Unit test: DueDate validation và highlight logic | JD | 2h | 1 | P1 | Todo | S2-T005 |
| S2-T010 | Code review Sprint 2 — TL review | TL | 3h | — | P1 | Todo | S2-T009 |
| S2-T011 | Fix review comments (nếu có) | SD + JD | 2h | — | P1 | Todo | S2-T010 |
| S2-T012 | QA: Test Sprint 1 features (tạo test case, chạy manual test F01–F07) | QAE | 4h | — | P0 | Todo | Sprint 1 Done |
| S2-T013 | QA: Log bug Sprint 1 (nếu có), tạo BUG report | QAE | 2h | — | P1 | Todo | S2-T012 |

**Tổng SP Sprint 2:** ~14 SP
**Capacity:** SD ~32h + JD ~32h + TL ~16h + QAE ~20h = đủ

---

## 6. Sprint 3 — QA, Bug Fix, Polish, Deploy

**Thời gian:** 2026-06-17 (T3) → 2026-06-20 (T6) — 4 ngày làm việc
**Sprint Goal:** Đảm bảo chất lượng toàn bộ tính năng, fix bug, polish UI, deploy bản Release.

> **Lưu ý:** 2026-06-17 (T3) dành cho Sprint Review + Retrospective Sprint 2 + Sprint Planning Sprint 3. Coding/fix Sprint 3 từ 2026-06-17 chiều trở đi hoặc từ 2026-06-18.

### 6.1 Sprint 3 — Backlog

| Task ID | Mô tả | Assignee | Estimate | SP | Priority | Status | Phụ thuộc |
|---------|-------|----------|----------|----|----------|--------|-----------|
| S3-T001 | QA: Regression test toàn bộ F01–F10, chạy tất cả test case | QAE | 6h | — | P0 | Todo | Sprint 2 Done |
| S3-T002 | QA: Test edge cases: file corrupt, disk full, empty list | QAE | 3h | — | P0 | Todo | Sprint 2 Done |
| S3-T003 | Bug fix P0/P1 từ QA report (ước tính) | SD | 4h | — | P0 | Todo | S3-T001 |
| S3-T004 | Bug fix P2/P3 (polish, minor UI issues) | JD | 3h | — | P1 | Todo | S3-T001 |
| S3-T005 | Polish: cải thiện hiển thị console (căn lề, màu sắc, UX text) | JD | 2h | — | P3 | Todo | S3-T004 |
| S3-T006 | Viết README.md: hướng dẫn cài đặt, chạy, cấu hình | JD | 2h | — | P1 | Todo | Sprint 2 Done |
| S3-T007 | Setup CI: GitHub Actions — build + test tự động | DOE | 3h | — | P1 | Todo | Sprint 2 Done |
| S3-T008 | Publish bản Release: `dotnet publish` → tạo executable + zip | DOE | 2h | — | P0 | Todo | S3-T007 |
| S3-T009 | QA: Verify bug fix, re-test các case đã fail | QAE | 2h | — | P0 | Todo | S3-T003 |
| S3-T010 | QA Lead: Sign-off chất lượng — không còn bug P0/P1 | QAL | 1h | — | P0 | Todo | S3-T009 |
| S3-T011 | TL: Final code review, merge tất cả nhánh vào main | TL | 2h | — | P0 | Todo | S3-T010 |
| S3-T012 | Demo nội bộ cho stakeholder (nếu có) | TL + PM | 1h | — | P1 | Todo | S3-T011 |

**Capacity Sprint 3:** SD ~32h + JD ~32h + TL ~16h + QAE ~24h + DOE ~12h = đủ

---

## 7. Timeline / Gantt (Text-based)

```
                    JUNE 2026
     Wk1           Wk2              Wk3
  03 04 05 06 07 | 10 11 12 13 14 | 17 18 19 20
  W  T  F  S  S  | M  T  W  T  F  | M  T  W  T
  ─────────────────────────────────────────────
  SPRINT 1 ────────────────────►
  ├─ S1-T001..T007 (SD): Architecture + Service  ██████████
  │                                              (06/03-06/07)
  ├─ S1-T008..T015 (JD): UI Console             ████████████
  │                                              (06/04-06/10)
  ├─ S1-T016..T017 (SD): DI + Integration       ██████
  │                                              (06/09-06/11)
  └─ S1-T018..T019 (TL): Code Review            ██
                                                 (06/11)

  [MILESTONE 1: MVP Done] ──────────────────────► 2026-06-11

                            SPRINT 2 ──────────────────────►
                            ├─ Sprint Review S1 / Planning S2   █
                            │                                   (06/12)
                            ├─ S2-T001..T009 (SD+JD): Features  ████████
                            │                                   (06/13-06/16)
                            ├─ S2-T010..T011 (TL): Code Review  ██
                            │                                   (06/16)
                            └─ S2-T012..T013 (QAE): QA Sprint1  ████████
                                                                (06/13-06/16)

  [MILESTONE 2: Feature Complete] ─────────────────────────► 2026-06-16

                                            SPRINT 3 ──────────────►
                                            ├─ Review S2/Planning S3    █
                                            │                          (06/17 sáng)
                                            ├─ S3-T001..T002 (QAE): QA ██████
                                            │                          (06/17-06/18)
                                            ├─ S3-T003..T005 (SD+JD): Fix ████
                                            │                          (06/18-06/19)
                                            ├─ S3-T007..T008 (DOE): CI/CD ████
                                            │                          (06/17-06/18)
                                            ├─ S3-T009..T011 (QAE+TL): Final ██
                                            │                          (06/19)
                                            └─ S3-T012: Demo           █
                                                                       (06/20)

  [MILESTONE 3: QA Sign-off] ──────────────────────────────► 2026-06-19
  [MILESTONE 4: RELEASE v1.0] ─────────────────────────────► 2026-06-20
```

### Milestones chính

| # | Milestone | Ngày mục tiêu | Điều kiện |
|---|-----------|---------------|-----------|
| M1 | MVP Done | 2026-06-11 (T4) | F01–F07 pass tất cả AC, build thành công |
| M2 | Feature Complete | 2026-06-16 (T2) | F08–F10 hoàn thành, merge vào main |
| M3 | QA Sign-off | 2026-06-19 (T5) | Không còn bug P0/P1, regression pass |
| M4 | Release v1.0 | 2026-06-20 (T6) | Executable publish, CI xanh, README xong |

---

## 8. Definition of Done (DoD)

### DoD Sprint 1 — MVP Core

Mỗi tính năng F01–F07 được coi là DONE khi:

- [ ] Code được merge vào nhánh `develop` (không merge thẳng vào `main`)
- [ ] Unit test coverage >= 80% cho module liên quan
- [ ] Tất cả AC của US-001 đến US-007 được implement đúng
- [ ] Không có warning compiler nghiêm trọng
- [ ] TL đã review và approve PR
- [ ] Build thành công trên máy sạch (`dotnet build` không lỗi)
- [ ] Ứng dụng chạy được end-to-end: tạo task → lưu → đọc lại sau restart
- [ ] Error states đã xử lý (storage lỗi, file corrupt, empty list)
- [ ] Tài liệu code (XML comment) cho public interface

### DoD Sprint 2 — Should Have Features

Mỗi tính năng F08–F10 được coi là DONE khi:

- [ ] Tất cả DoD Sprint 1 áp dụng cho code mới
- [ ] Filter (F08), Priority (F09), DueDate (F10) hoạt động độc lập và kết hợp được
- [ ] Dữ liệu Priority và DueDate persist sau khi restart ứng dụng
- [ ] QAE đã chạy manual test F01–F07 trong Sprint 2 và không có P0 bug
- [ ] Bug P0/P1 từ Sprint 1 đã được fix và verify

### DoD Sprint 3 — Release

Bản Release v1.0 được coi là DONE khi:

- [ ] Tất cả test case (F01–F10) pass — không còn bug P0/P1
- [ ] Regression test toàn bộ hoàn thành
- [ ] QA Lead sign-off chính thức
- [ ] CI pipeline xanh (GitHub Actions: build + test)
- [ ] Executable đã publish (`dotnet publish -c Release`)
- [ ] README.md đầy đủ: cài đặt, chạy, yêu cầu hệ thống
- [ ] TL merge `develop` vào `main` sau QA sign-off
- [ ] Tag `v1.0.0` trên git

---

## 9. Meeting Schedule

### Daily Standup

| Trường | Nội dung |
|--------|----------|
| **Thời gian** | 09:15 sáng, mỗi ngày làm việc |
| **Thời lượng** | 15 phút (tối đa) |
| **Format** | Async (Slack/Teams) hoặc sync ngắn |
| **3 câu hỏi** | 1. Hôm qua làm gì? 2. Hôm nay làm gì? 3. Có blocker không? |
| **Ai tham gia** | SD, JD, TL (bắt buộc); QAE, DOE (từ Sprint 2) |
| **Người điều phối** | Project Manager |

**Quy tắc standup:**
- Không giải quyết vấn đề trong standup — blocker được note và giải quyết offline ngay sau
- Nếu TL không available → SD escalate qua Slack trong vòng 1h
- Blocker chưa gỡ được trong 24h → PJM escalate lên Engineering Manager

### Sprint Review / Demo

| Sprint | Ngày | Thời lượng | Nội dung |
|--------|------|-----------|---------|
| Sprint 1 Review | 2026-06-12 sáng | 1 giờ | Demo F01–F07, nhận phản hồi |
| Sprint 2 Review | 2026-06-17 sáng | 1 giờ | Demo F08–F10, nhận phản hồi |
| Sprint 3 Review (Release Demo) | 2026-06-20 chiều | 1.5 giờ | Demo toàn bộ, QA sign-off, release |

### Sprint Retrospective

| Sprint | Ngày | Thời lượng | Format |
|--------|------|-----------|--------|
| Sprint 1 Retro | 2026-06-12 chiều | 45 phút | Start/Stop/Continue |
| Sprint 2 Retro | 2026-06-17 chiều | 45 phút | Start/Stop/Continue |
| Sprint 3 Retro | 2026-06-20 cuối ngày | 30 phút | Quick lessons learned |

### Sprint Planning

| Sprint | Ngày | Thời lượng | Input cần có |
|--------|------|-----------|-------------|
| Sprint 1 Planning | 2026-06-02 (đã xong) | 2 giờ | PRD + US + RESOURCE |
| Sprint 2 Planning | 2026-06-12 chiều | 1 giờ | Kết quả Sprint 1 + bug report |
| Sprint 3 Planning | 2026-06-17 sáng (sau review) | 45 phút | Bug list + QA report S2 |

---

## 10. Dependencies

| ID | Dependency | Ảnh hưởng | Xác suất rủi ro |
|----|-----------|-----------|----------------|
| DEP-01 | TDD từ Tech Lead phải xong trước khi SD bắt đầu S1-T001 | Delay > 1 ngày nếu thiếu | Cao — cần resolve ngay |
| DEP-02 | S1-T003 (Interfaces) phải xong trước S1-T004, S1-T005 | Unblock parallel work | Thấp — SD tự làm |
| DEP-03 | S1-T008 (ConsoleUI main) phải xong trước S1-T009..T012 | JD blocked nếu delay | Trung bình |
| DEP-04 | Sprint 1 Done (M1) trước khi Sprint 2 bắt đầu feature | Sprint 2 chất lượng phụ thuộc vào Sprint 1 | Thấp |
| DEP-05 | QAE cần có Test Plan (từ QA Lead) trước khi test Sprint 2 | Thiếu test plan = test không có hướng | Trung bình |
| DEP-06 | CI/CD (DOE) phải xong trước khi publish Release | Không có CI = release thủ công, rủi ro | Thấp |

---

## 11. Scope bị đẩy ra khỏi v1.0 (Out of Scope)

Theo PRD Non-goals — các tính năng sau KHÔNG thuộc v1.0:

| # | Tính năng | Lý do | Phiên bản dự kiến |
|---|-----------|-------|-------------------|
| OOS-01 | Đồng bộ cloud / multi-device | Ngoài phạm vi MVP | v2.0 |
| OOS-02 | Hệ thống nhắc nhở / notification | Cần background service | v1.1 |
| OOS-03 | Chia sẻ task (collaboration) | Single-user MVP | v2.0 |
| OOS-04 | Recurring tasks | Logic phức tạp | v1.2 |
| OOS-05 | Sub-tasks | Tăng độ phức tạp data model | v1.1 |
| OOS-06 | Import/Export file bên ngoài | Để v1.1 | v1.1 |
| OOS-07 | Undo / Redo | Không trong AC MVP | v1.1 |

---

## 12. Risk & Blocker Tracking

### Format ghi nhận blocker tại Daily Standup

```
BLOCKER-[YYYY-MM-DD]-[NNN]
─────────────────────────────────────────────────
Người báo   : [SD / JD / QAE / DOE]
Task bị ảnh : [Task ID]
Mô tả       : [Mô tả blocker cụ thể]
Gặp từ      : [Ngày giờ]
Cần từ      : [TL / PM / EM / ...]
Deadline gỡ : [Ngày]
Trạng thái  : [Open / In Progress / Resolved]
Ghi chú     : [Cách giải quyết / kết quả]
```

### Risk Register

| ID | Rủi ro | Xác suất | Tác động | Biện pháp giảm thiểu |
|----|--------|----------|----------|----------------------|
| R-01 | TDD chưa sẵn → SD không có spec để code | Cao | Cao | PJM nhắc TL hoàn thành TDD trước 2026-06-03 sáng |
| R-02 | JD gặp khó khăn với ConsoleUI pattern | Trung bình | Trung bình | SD mentor JD trong 2 ngày đầu Sprint 1 |
| R-03 | File JSON corrupt edge case khó test | Thấp | Trung bình | SD viết test cụ thể cho trường hợp này (S1-T007) |
| R-04 | QA phát hiện nhiều P0 bug cuối Sprint 3 | Thấp | Rất cao | Bắt đầu QA sớm từ Sprint 2, không để dồn vào Sprint 3 |
| R-05 | Tech Lead không available đúng hạn review | Trung bình | Cao | Slot review đặt trước trong lịch, SD tự review chéo nếu cần |
| R-06 | Scope creep: team muốn thêm tính năng giữa sprint | Thấp | Cao | PJM từ chối mọi scope thay đổi giữa sprint, đưa vào backlog v1.1 |
| R-07 | DOE không setup được CI kịp | Thấp | Trung bình | DOE bắt đầu setup CI từ đầu Sprint 3; fallback: release thủ công |

### Quy trình xử lý blocker

```
Blocker phát hiện
    │
    ▼
Báo tại Daily Standup (09:15) hoặc ngay qua Slack
    │
    ▼
PJM ghi vào Blocker Log (file này)
    │
    ▼
Gỡ trong 24h?
    ├─ Có → Close blocker, cập nhật log
    └─ Không → PJM escalate lên Engineering Manager ngay
                (kèm: mô tả blocker, tác động, đề xuất giải quyết)
```

---

## 13. Báo cáo trạng thái sprint (Template — Daily)

```
DAILY SPRINT STATUS — [YYYY-MM-DD]
════════════════════════════════════════
Sprint hiện tại : Sprint [N]
Ngày thứ        : [X/7] (Sprint 1) | [X/4] (Sprint 2) | [X/4] (Sprint 3)
SP đã burn      : [X] / [Tổng]
SP còn lại      : [X]

HOÀN THÀNH HÔM QUA:
  ✅ [Task ID] — [mô tả ngắn] — [Assignee]

ĐANG LÀM HÔM NAY:
  🔄 [Task ID] — [mô tả ngắn] — [Assignee]

BLOCKER:
  🛑 [Blocker ID hoặc "Không có"]

DỰ BÁO:
  [On track / At risk / Delayed — lý do]
════════════════════════════════════════
```

---

## 14. Phê duyệt Sprint Plan

| Vai trò | Người duyệt | Trạng thái | Ngày |
|---------|-------------|-----------|------|
| Product Manager | PM | Chờ phê duyệt | — |
| Tech Lead | TL | Chờ phê duyệt | — |
| QA Lead | QAL | Chờ phê duyệt | — |
| Project Manager (chốt) | PJM | Đã soạn | 2026-06-02 |

---

## Lịch sử cập nhật

| Ngày | Phiên bản | Nội dung thay đổi |
|------|-----------|-------------------|
| 2026-06-02 | v1.0 | Khởi tạo Sprint Plan — 3 sprints, 14 ngày |
