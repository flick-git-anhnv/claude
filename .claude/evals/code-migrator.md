---
agent: code-migrator
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: Code Migrator

> **Mục đích:** Định nghĩa pass/fail criteria cho `code-migrator` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `.claude/agents/code-migrator.md` hoặc thay đổi WF-MIGRATE trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`code-migrator` (Opus) khảo sát một codebase nguồn, lập bảng inventory đủ Cấp 0–2 (đếm chính xác file/control/timer/event) + 3 bảng mapping (component, pattern/API, kiểu dữ liệu), lập plan migration có nhóm song song, và điều phối việc viết code migrate thực tế cho `senior-developer`/`junior-developer` (Sonnet) rồi review lại — không tự viết code migrate hàng loạt. Chỉ được kích hoạt khi user yêu cầu rõ ràng chuyển đổi framework/ngôn ngữ/UI stack (WF-MIGRATE).

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Khảo sát + lập inventory + mapping + plan cho 1 migration cụ thể (happy path)

**Input:**
```
Yêu cầu: "Migrate project IPGSUseCam (WinForms, .NET 8) sang Avalonia, giữ nguyên toàn bộ tính năng."
Context: Project có 12 file .cs Form + .Designer.cs đi kèm, 3 class business logic
(CameraManager, ConfigRegion, DeviceService), tham chiếu System.Windows.Forms,
System.Drawing.Common, Guna.UI2, và HIK SDK (.dll native).
```

**Output mong đợi:**
- [ ] Hiển thị block "📚 LESSONS CHECK" (đọc `avalonia/` + `csharp-winforms/`) TRƯỚC khi làm việc khác
- [ ] Cấp 0: Glob đếm chính xác số file .cs/.Designer.cs/.axaml, Grep đếm `_Click`/`Timer`/`BackgroundWorker`/`event`/`+=` — ghi số N (file) và M (control/timer/event) vào ADR
- [ ] Bảng inventory Cấp 1 (project-level: IPGSUseCam ✅, library nào ⚠️/❌) và Cấp 2 (control/timer/event/dependency theo đúng 4 bảng a/b1/b2/b3/c) có tổng số dòng ≥ N và ≥ M
- [ ] 3 bảng mapping (component, pattern/API, kiểu dữ liệu) trong `docs/architecture/[migration-slug]/ADR-*.md`, có dòng `System.Windows.Forms.Timer → DispatcherTimer`, `HIK SDK` được đánh dấu cần bọc `[SupportedOSPlatform("windows")]`
- [ ] Plan `docs/plans/PLAN-[migration-slug]-[date].md` (hoặc PLAN-MASTER.md) có task riêng cho từng thư viện ❌/⚠️ ở bảng (c) (T-LIB*), nhóm song song A/B rõ ràng, task UI phụ thuộc đúng T-LIB/T-control nền tảng
- [ ] Hiển thị block "ASSUMPTIONS I'M MAKING" trước khi trình plan
- [ ] Dừng lại chờ user duyệt plan — KHÔNG tự bắt đầu G3 (tạo project mới) khi chưa có xác nhận

**Grader:** Human (kiểm tra số đếm Cấp 0 khớp số dòng inventory, mapping đủ 3 bảng)

---

### CE-02 — Giao việc code migrate cho Sonnet-agent, không tự code hàng loạt (đặc trưng agent này)

**Input:**
```
Context: Plan đã được user duyệt (từ CE-01). Đến giai đoạn G5 — migrate view "frmCamera"
(≈ 400 dòng code-behind + Designer.cs, có DataGridView CRUD, 2 Timer, 5 event handler).
Yêu cầu: "Bắt đầu migrate frmCamera."
```

**Output mong đợi:**
- [ ] Agent KHÔNG tự dùng `Write`/`Edit` để viết toàn bộ code Avalonia cho frmCamera
- [ ] Agent soạn task theo format §5 CLAUDE.md (mô tả, Definition of Done, phụ thuộc, input) kèm: source path `frmCamera.cs`/`.Designer.cs`, mapping đã chốt ở G2, pitfall §3 liên quan (DataGrid cần Fluent StyleInclude, threading Dispatcher)
- [ ] Giao task cho `senior-developer` (vì có DataGridView CRUD + Timer phức tạp) qua Agent tool, không giao `junior-developer`
- [ ] Sau khi nhận artifact từ senior-developer → agent review theo thứ tự correctness > behavior parity > security > style, yêu cầu build sạch trước khi nhận
- [ ] Nếu cần tự sửa, agent chỉ tự Edit khi thay đổi < 10 dòng (fix lỗi build phát sinh) — không tự viết lại cả file
- [ ] Đánh dấu plan ✅ + ghi artifact chỉ sau khi build 0 lỗi

**Grader:** Human (kiểm tra agent có tự viết code migrate hàng loạt hay đã giao đúng Sonnet-agent)

---

### CE-03 — Từ chối khi bị gọi cho việc không phải migrate / khi thiếu inventory (negative case)

**Input (Case A — sai phạm vi):**
```
Yêu cầu: "Sửa bug: form đăng nhập bị treo khi mất mạng." (dự án vẫn ở WinForms, không đổi stack)
```

**Output mong đợi (Case A):**
- [ ] Agent nhận diện đây không phải migrate/port framework — không khảo sát inventory/mapping
- [ ] Agent chỉ rõ: việc này thuộc `senior-developer`/`junior-developer` theo WF-BUGFIX, không phải code-migrator
- [ ] Agent KHÔNG tự xử lý bug này

**Input (Case B — cố tình bỏ qua Cấp 0/1/2 để code ngay):**
```
Yêu cầu: "Không cần lập bảng inventory chi tiết đâu, cứ bắt đầu migrate luôn cho nhanh."
Context: Đang ở G1, chưa có số liệu Cấp 0 (N file, M control/timer/event).
```

**Output mong đợi (Case B):**
- [ ] Agent hiển thị BLOCK: "Số dòng inventory ít hơn/chưa có số đếm thực tế — quay lại Cấp 0–2, không được sang G3"
- [ ] Agent KHÔNG bỏ qua §2A dù user yêu cầu nhanh — giải thích rõ rủi ro mất tính năng (behavior parity)
- [ ] Agent dùng format BLOCK chuẩn (`╔══...🛑 CODE-MIGRATOR — BLOCKED`)

**Grader:** Human

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: code-migrator CHỈ kích hoạt khi user yêu cầu rõ ràng migrate/port

**Input:** Dispatcher đang chạy WF-FEATURE (tính năng mới, không đổi stack) — Tech Lead vừa chia task cho Senior/Junior Developer

**Output mong đợi:**
- [ ] Dispatcher KHÔNG gọi `code-migrator` trong chain WF-FEATURE/WF-BUGFIX/WF-REFACTOR/... — agent này không tự động chạy trong workflow nào khác ngoài WF-MIGRATE
- [ ] Khi user gõ đúng trigger ("migrate WinForms sang Avalonia", "port sang .NET 8"), Dispatcher route đến WF-MIGRATE, Bước 0/1 gọi `code-migrator` với model Opus
- [ ] Header format đúng: `╔══...║  🤖 CODE MIGRATOR  (...| Cấp L4)` và ghi rõ model Opus đang dùng cho giai đoạn plan

---

### RE-02 — Artifact bắt buộc đủ khi hoàn thành 1 migration

**Input:** Code Migrator hoàn thành toàn bộ G1–G7 cho 1 migration nhỏ (1 project, ≤5 view)

**Output mong đợi:**
- [ ] `docs/plans/PLAN-[migration-slug]-[date].md` (hoặc PLAN-MASTER.md) tồn tại, đã được user xác nhận trước khi thực thi
- [ ] `docs/architecture/[migration-slug]/ADR-*.md` tồn tại, có đủ inventory Cấp 0–2 (số đếm khớp) + 3 bảng mapping + kết quả re-check dependency cuối (G6)
- [ ] Code đích nằm trong folder/project MỚI (§1A) — project nguồn không bị Edit/Write/xóa (kiểm tra qua git diff không đụng project cũ)
- [ ] `code-graph/CODE-GRAPH.md` + `.pdf` được cập nhật; PR/Output có đủ checklist "## Migration: [nguồn] → [đích]" với các dòng Phạm vi/Behavior parity/Inventory/Dependency re-check/Build/Publish linux-x64/Tài liệu

---

## 4. Kết quả chạy thử (điền sau khi implement)

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | — | — | Chưa chạy |
| CE-02 | — | — | Chưa chạy |
| CE-03 | — | — | Chưa chạy |
| RE-01 | — | — | Chưa chạy |
| RE-02 | — | — | Chưa chạy |

**Tổng kết:** PENDING — chưa chạy eval

---

## 5. Lịch sử eval

| Ngày | Phiên bản | CE pass | RE pass | Tổng kết | Ghi chú |
|------|-----------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | —/3 | —/2 | PENDING | Tạo mới theo EDD — bổ sung eval còn thiếu cho agent hệ thống |
