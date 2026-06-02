# CODE-GRAPH.md — Bản đồ codebase: To-Do App C#
**Cập nhật lần cuối:** 2026-06-02 | **Bởi:** Tech Lead (code review S1-T018) | **Version:** 1.0

> File này được duy trì tự động bởi coding agents.
> **Đọc file này TRƯỚC khi đọc source code** để hiểu cấu trúc dự án mà không cần mở từng file.

---

## Tổng quan dự án
Ứng dụng quản lý công việc cá nhân (To-Do) chạy trên console, single-user, lưu trữ cục bộ bằng file JSON. Kiến trúc layered (Domain → Application → Infrastructure → Presentation), DI bằng `Microsoft.Extensions.DependencyInjection`.

**Tech stack:** C# / .NET 8 (Console App) + System.Text.Json (built-in, không dependency runtime ngoài)
**Deploy:** Self-contained / framework-dependent console executable (Windows)
**Môi trường:** Local → Staging (smoke test) → Production

---

## Cấu trúc thư mục
```
claude/
├── src/
│   ├── TodoApp.Domain/          ← Entity, enum, interface port, exception (không ref ai)
│   ├── TodoApp.Application/     ← Service nghiệp vụ, validation, request/result DTO
│   ├── TodoApp.Infrastructure/  ← JsonFileRepository, lưu trữ JSON atomic
│   └── TodoApp.ConsoleUI/       ← Presentation: AppRunner, Screens, Components, Rendering
├── tests/
│   ├── TodoApp.Application.Tests/      ← unit test service + validation (39 tests)
│   ├── TodoApp.Infrastructure.Tests/  ← unit test repository (12 tests)
│   └── TodoApp.Integration.Tests/     ← integration end-to-end (3 tests)
├── docs/
│   ├── prd/ user-stories/ design/ planning/ tech-design/
├── code-graph/                  ← bản đồ codebase (file này)
└── .claude/                     ← AI agent configs, plans, templates
```

---

## Module chính
| Module | Path | Mục đích | Files quan trọng |
|--------|------|----------|-----------------|
| Domain | `src/TodoApp.Domain/` | Entity + contract thuần, không phụ thuộc | `TodoItem.cs`, `ITodoRepository.cs`, `TodoStatus.cs`, `Priority.cs`, `StorageException.cs`, `TodoConstants.cs` |
| Application | `src/TodoApp.Application/` | Logic nghiệp vụ, điều phối validation + persist | `TodoService.cs`, `ITodoService.cs`, `Validation/TitleValidator.cs`, `OperationResult.cs`, `Requests.cs`, `TaskFilter.cs` |
| Infrastructure | `src/TodoApp.Infrastructure/` | Lưu trữ JSON, atomic write, recovery corrupt | `JsonFileRepository.cs`, `JsonStorageOptions.cs`, `StorageFileDto.cs` |
| ConsoleUI | `src/TodoApp.ConsoleUI/` | Giao diện console, vòng lặp tương tác | `AppRunner.cs`, `Program.cs`, `Screens/*`, `Components/*`, `Rendering/*`, `Messages.cs` |

---

## Entry Points
| Tên | File | Mô tả |
|-----|------|-------|
| App start | `src/TodoApp.ConsoleUI/Program.cs` | Wire DI, set UTF-8, gọi `AppRunner.Run()` |
| Vòng lặp chính | `src/TodoApp.ConsoleUI/AppRunner.cs:21` | Initialize + main loop điều phối các Screen |
| Menu chính | `src/TodoApp.ConsoleUI/Screens/MainScreen.cs:18` | Render danh sách + nhận lệnh người dùng |

---

## API / Interface chính
| Class / Method | File:Line | Mô tả |
|----------------------------|-----------|-------|
| `interface ITodoService` | `src/TodoApp.Application/ITodoService.cs:9` | Contract duy nhất Presentation được gọi; không throw, trả `OperationResult` |
| `TodoService.Initialize()` | `src/TodoApp.Application/TodoService.cs:15` | Nạp dữ liệu khi khởi động (US-007) |
| `TodoService.Create()` | `src/TodoApp.Application/TodoService.cs:29` | Tạo task, validate title/desc (US-001) |
| `TodoService.GetTasks()` | `src/TodoApp.Application/TodoService.cs:66` | Lọc + sort CreatedAt DESC, in-memory (US-002/008) |
| `TodoService.Update()` | `src/TodoApp.Application/TodoService.cs:87` | Sửa task + rollback nếu Storage fail (US-003/009/010) |
| `TodoService.Delete()` | `src/TodoApp.Application/TodoService.cs:134` | Xóa vĩnh viễn (US-004) |
| `TodoService.ToggleComplete()` | `src/TodoApp.Application/TodoService.cs:153` | Toggle Pending↔Completed (US-005) |
| `interface ITodoRepository` | `src/TodoApp.Domain/ITodoRepository.cs:7` | Port lưu trữ; in-memory source-of-truth |
| `JsonFileRepository.Save()` | `src/TodoApp.Infrastructure/JsonFileRepository.cs:176` | Ghi atomic write-temp → rename |

---

## Database Schema
Không dùng DB. Lưu trữ file JSON.

| File | Cấu trúc | Ghi chú |
|------|----------|---------|
| `todos.json` | `{ schemaVersion: 1, items: TodoItem[] }` | File dữ liệu chính (`StorageFileDto`) |
| `todos.tmp` | (file tạm khi ghi) | Dùng cho atomic write, xóa sau rename |
| `todos.bak.json` | (bản sao khi corrupt) | Backup tự động khi parse JSON lỗi |

**TodoItem:** `Id (Guid)`, `Title`, `Description?`, `Status`, `Priority`, `DueDate?`, `CreatedAt`, `UpdatedAt?`, `CompletedAt?`. `IsOverdue`/`IsDueToday` tính runtime, không persist.

---

## Dependencies quan trọng
| Package | Version | Dùng cho |
|---------|---------|---------|
| Microsoft.Extensions.DependencyInjection | (transitive .NET) | Wire DI trong `Program.cs` |
| System.Text.Json | built-in .NET 8 | Serialize/deserialize JSON storage |
| xUnit + coverlet.collector | (test) | Unit/integration test + coverage |

---

## Config / Environment Variables
| Key | Default | Bắt buộc | Mô tả |
|-----|---------|---------|-------|
| `TODOAPP_DATA_DIR` | `%LOCALAPPDATA%\KZTEK\TodoApp` | ❌ | Override thư mục lưu dữ liệu (phục vụ test). Path do người dùng tự sở hữu — không phải input từ mạng. |

---

## Thay đổi gần đây
| Ngày | File/Module | Loại | Mô tả ngắn | Agent |
|------|------------|------|------------|-------|
| 2026-06-02 | `src/TodoApp.Domain+Application+Infrastructure` | Add | Tạo Domain/Application/Infrastructure layer, 39+12 tests | Senior Developer |
| 2026-06-02 | `src/TodoApp.ConsoleUI/*` | Add | UI Screens + Components + Rendering, 3 integration tests | Junior Developer |
| 2026-06-02 | `src/TodoApp.Infrastructure/JsonFileRepository.cs` | Update | Làm rõ comment cấu hình JsonSerializerOptions (code review) | Tech Lead |

---

## Ghi chú đặc biệt
- **In-memory source-of-truth:** `JsonFileRepository._items` là nguồn dữ liệu duy nhất trong session. `GetTasks`/`GetAll`/`GetById` KHÔNG đọc lại đĩa — đáp ứng yêu cầu performance.
- **Atomic write:** Ghi `todos.tmp` rồi `File.Replace`/`File.Move` sang `todos.json` — gần atomic trên NTFS. Khi fail → cleanup temp + ném `StorageException`.
- **Rollback in-memory:** Mọi mutate (Add/Update/Delete/Toggle) rollback state in-memory nếu `Save()` ném, đảm bảo memory ↔ disk nhất quán.
- **No-crash policy (BR-GLOBAL-04):** Load với file corrupt/permission/IO lỗi → trả list rỗng + set flag (`CorruptionDetected`/`PermissionErrorOnLoad`), KHÔNG throw lên UI.
- **Logging an toàn:** Chỉ ghi `Debug.WriteLine` với `ex.Message` (không log nội dung task) — không lộ dữ liệu nhạy cảm.
- **Coverage:** Application 93.97% (TodoService 92.64%, TitleValidator/OperationResult/Requests 100%). Infrastructure ~62% (phần I/O lỗi hệ thống khó mô phỏng đầy đủ) — checklist TDD §14 chỉ yêu cầu Application ≥ 80%.
