---
category: avalonia
tags: [migration, code-review, security, cross-platform, race-condition, memory-leak, checklist, process, code-migrator]
severity: critical
created: 2026-06-26
updated: 2026-07-01
project-origin: iPGSv4 CCU Avalonia migration — Wave 1–4 review found 18 issues
---

# WinForms→Avalonia Migration: Checklist bắt buộc — 18 issues điển hình bị bỏ sót

## Tình huống gặp phải

Sau khi migrate xong iPGSv4 (31 Views, WinForms → Avalonia), code review hậu kỳ phát hiện 18 issues: 4 Critical, 6 High, 4 Medium, 4 Low. Hầu hết đều **compile và run được trên Windows** — chỉ bị phát hiện qua review chủ động hoặc khi build linux-x64.

## Root Cause — Tại sao bỏ sót

| Nhóm | Root cause |
|---|---|
| SQL injection (TL-001, TL-005) | Không có security review step; compiler không cảnh báo string interpolation vào SQL |
| System.Drawing crash Linux (TL-002/003) | Windows build pass → CI không bắt; `UltilityManagement.cs` bị bỏ qua khi fix `Option.cs` |
| Dialog TCS deadlock (TL-004) | WinForms dùng `DialogResult` tự động; Avalonia yêu cầu TCS explicit — pattern mới không quen |
| Zone event không realtime (TL-006) | MVVM decoupling đúng nhưng wiring event chưa đủ — chỉ có timer tick, không push event |
| Memory leak timer (TL-007) | Unloaded event thường bị bỏ quên khi tập trung vào Loaded |
| UndoCap không enforce (TL-008) | Stack<T> không có RemoveFirst — LinkedList cần dùng nhưng reviewer không cân nhắc kỹ |
| WinExe cross-platform (TL-009) | Copy csproj từ WinForms không audit OutputType |
| Ghost project in sln (TL-010) | File bị xóa nhưng sln entry không được dọn |
| CashViewModel race (TL-011) | `IsRunning` set quá muộn (sau khi connect xong) → TOCTOU race khi double-click |
| DeviceStatusView anti-pattern (TL-012) | WinForms pattern "recreate form on refresh" → ViewModel; MVVM dùng Reload() thay thế |
| Redundant IsEnabled binding (TL-015) | `[RelayCommand(CanExecute=...)]` đã xử lý, vẫn bind thêm IsEnabled → double-bind |
| ShowImageWindow FindControl (TL-016) | Dùng magic string FindControl thay MVVM binding — code smell WinForms carried over |
| CODE-GRAPH stale (TL-017/018) | Code thay đổi nhưng không update docs trong cùng session |
| MsBox version sai (TL-014) | Reviewer đề xuất version không tồn tại trên NuGet — chưa verify trước |

## Checklist bắt buộc sau migrate

### 🔴 Security (CRITICAL — làm trước nhất)

- [ ] Grep toàn bộ `FillData\(` + `$"` → escape mọi string user/DB với `.Replace("'", "''")`
- [ ] Grep `string.Format` hoặc `+` trong SQL string → same fix
- [ ] Xem xét tất cả method nhận raw SQL string → đảm bảo parameterized hoặc escaped

### 🔴 Cross-platform (CRITICAL — build linux-x64 trước khi done)

```bash
dotnet build ProjectName.csproj -r linux-x64 --no-self-contained -c Release
```

- [ ] `System.Drawing.Color` → đổi thành hex string `"#RRGGBB"`; xóa `System.Drawing.Common` package
- [ ] Grep toàn bộ project: `using System.Drawing` → tìm file bị sót (không chỉ `Option.cs`)
- [ ] `OutputType` trong `.csproj` của cross-platform project: `WinExe` → `Exe`
- [ ] Xóa `.resx` files khỏi build nếu không dùng

### 🟠 Async/Threading (HIGH)

- [ ] `Task.Run(ConnectAndStart)` pattern: IsRunning/IsConnecting phải set TRƯỚC Task.Run, không sau
  ```csharp
  // WRONG:
  Task.Run(() => { ... IsRunning = true; }); // window of TOCTOU
  // RIGHT:
  _isConnecting = true; Task.Run(() => { try { ... } finally { _isConnecting = false; } });
  ```
- [ ] ConnectAndStart phải có try/catch — exception trên background thread crash app
- [ ] Field `_validator`/`_connection` dùng trong multi-thread: capture vào local var trước khi dùng
  ```csharp
  var v = _validator; // snapshot once
  if (v == null) return;
  // use v from here on
  ```
- [ ] Disconnect: null field TRƯỚC khi close (`var v = _field; _field = null; v?.Close()`)

### 🟠 Dialog / TaskCompletionSource (HIGH)

- [ ] `TaskCompletionSource` dialog PHẢI có `dlg.Closed` guard:
  ```csharp
  dlg.Closed += (_, _) => tcs.TrySetResult(false); // Alt+F4 / OS close
  ```
- [ ] Dùng `TrySetResult` thay `SetResult` để tránh exception khi race

### 🟠 Memory Leak (HIGH)

- [ ] Mọi `DispatcherTimer` tạo trong Loaded/constructor → PHẢI Stop trong `Unloaded`:
  ```csharp
  Unloaded += (_, _) => { _timer?.Stop(); _timer = null; };
  ```
- [ ] Event subscription trong View → unsubscribe trong Unloaded

### 🟡 Collections có giới hạn (MEDIUM)

- [ ] `Stack<T>` KHÔNG có `RemoveFirst` → **dùng `LinkedList<T>`** cho capped undo/redo:
  ```csharp
  if (_undoStack.Count >= Cap) _undoStack.RemoveFirst(); // O(1)
  _undoStack.AddLast(cmd);
  ```

### 🟡 MVVM Anti-patterns (MEDIUM)

- [ ] Không `DataContext = new ViewModel(...)` trong OnRefresh → gọi `vm.Reload()` thay thế
- [ ] Không `FindControl<T>("name")` trong code-behind → bind qua ViewModel property
- [ ] `[RelayCommand(CanExecute = nameof(X))]` đã disable button → xóa `IsEnabled="{Binding X}"` thừa
- [ ] Xóa `x:CompileBindings="False"` khi đã có DataType đúng → bật compiled bindings

### 🟡 .sln cleanup (MEDIUM)

- [ ] Sau khi xóa project → xóa entry trong `.sln` (tìm bằng `grep` project name)
- [ ] Verify tất cả `ProjectReference` thực sự tồn tại trên disk

### 🟢 Documentation (LOW)

- [ ] Update `CODE-GRAPH.md` sau mỗi session: services thêm/xóa, packages thêm/xóa
- [ ] Verify package version TỒN TẠI trên NuGet trước khi cập nhật csproj
- [ ] `CODE-GRAPH.md` và `CODE-GRAPH.pdf` phải cập nhật trong cùng session

## Thứ tự thực hiện review (ưu tiên)

```
1. Grep SQL injection → fix ngay (security)
2. Build linux-x64 → fix errors (System.Drawing, OutputType, resx)
3. Kiểm tra Task.Run pattern → fix race (threading)
4. Kiểm tra DispatcherTimer Unloaded (memory)
5. Kiểm tra Stack→LinkedList cho capped collections
6. Code style: redundant IsEnabled, FindControl, VM recreation
7. Documentation: CODE-GRAPH sync, sln cleanup
```

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Windows build pass **KHÔNG** có nghĩa là cross-platform safe. Luôn chạy `dotnet build -r linux-x64` trong cùng session migrate.
- ⚠️ MsBox.Avalonia chỉ có `3.0.0-rc2` trên NuGet (tính đến 2026-06). Không upgrade bừa.
- ⚠️ Khi fix `System.Drawing` trong file A, grep toàn project để tìm file B cùng pattern — không bỏ sót.
- ⚠️ `volatile bool _isConnecting` cần thiết cho double-click guard — `IsRunning` KHÔNG đủ vì nó được set ở cuối flow.

## Tham chiếu

- Project: iPGSv4 CCU, branch ccu-avalonia, 2026-06-25/26
- TL-001 đến TL-018: 18 issues phát hiện qua WF-REVIEW-CRIT
- Files đại diện: `LoginViewModel.cs`, `CashViewModel.cs`, `MapStatusView.axaml.cs`, `MapDetailWindow.axaml.cs`, `Option.cs`, `UltilityManagement.cs`, `DialogService.cs`

## Cập nhật 2026-07-01 — Root cause thực sự & fix ở tầng process (code-migrator)

**Vấn đề tái diễn:** Sau khi lesson này ra đời, `code-migrator` vẫn tiếp tục để lọt 2 dạng lỗi giống hệt ở các lần migrate sau:
1. **Bỏ sót tính năng** khi khảo sát class/Form/UI — inventory chỉ liệt kê "mẫu tiêu biểu" thay vì 100% (giống root cause TL-002/003: `UltilityManagement.cs` bị bỏ qua khi fix `Option.cs` cùng pattern).
2. **Thiếu thư viện cross-platform** cho build Windows + Linux — checklist "Cross-platform" ở trên chỉ được chạy như một **review hậu kỳ riêng** (WF-REVIEW-CRIT), không phải gate bắt buộc ngay trong quy trình migrate — nên dependency mới do Senior/Junior Dev thêm ở giai đoạn code (G5) không bị bắt lại trước khi sign-off.

**Fix đã áp dụng (trong `.claude/agents/code-migrator.md` của project "AI Agent Creator Workspace"):**
- Thêm **Cấp 0** vào §2A: bắt buộc `Glob`/`Grep` đếm số file/class/control/timer/event thực tế trong source TRƯỚC khi lập inventory — số dòng inventory phải khớp con số đếm được, thiếu = BLOCK, không cho sang G3.
- Thêm **G6 — re-check dependency lần cuối**: Grep lại toàn bộ csproj/`using` (kể cả code Senior/Junior Dev mới thêm ở G5) trước khi QA sign-off, không chỉ rà 1 lần ở G1/G4.
- `dotnet publish -r linux-x64 --self-contained` chuyển từ "tùy chọn nếu cần chắc chắn" → **BẮT BUỘC** ở G6 (build có thể pass nhưng publish thiếu runtime asset vẫn vỡ khi chạy thật).

**Áp dụng lại (How to reuse):** Nếu thấy code-migrator (hoặc agent tương tự) báo "migrate xong" mà chưa từng in ra số liệu `Tổng file nguồn: N | Tổng control/timer/event: M` khớp với bảng inventory, và chưa từng chạy lại `dotnet publish -r linux-x64` ở bước cuối (không phải bước đầu) → coi như CHƯA đạt gate, yêu cầu làm lại G6 trước khi nhận artifact.
