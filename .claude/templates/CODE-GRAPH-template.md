# CODE-GRAPH.md — Bản đồ codebase: [Tên Dự Án]
**Cập nhật lần cuối:** YYYY-MM-DD | **Bởi:** [agent/user] | **Version:** 1.0

> File này được duy trì tự động bởi coding agents.
> **Đọc file này TRƯỚC khi đọc source code** để hiểu cấu trúc dự án mà không cần mở từng file.

---

## Tổng quan dự án
[Mô tả ngắn: mục đích hệ thống, đối tượng sử dụng, tech stack chính, môi trường chạy]

**Tech stack:** [vd: Python 3.11 + FastAPI + PostgreSQL + Redis]
**Deploy:** [vd: Docker + AWS ECS / Windows Service / Electron App]
**Môi trường:** [vd: Local dev → Staging → Production]

---

## Cấu trúc thư mục
```
[project-root]/
├── src/
│   ├── [module-A]/     ← [mục đích — vd: xử lý auth]
│   ├── [module-B]/     ← [mục đích — vd: business logic chính]
│   └── [module-C]/     ← [mục đích — vd: utils, helpers]
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── prd/
│   ├── user-stories/
│   └── tech-design/
├── infra/              ← IaC (Terraform/Docker)
├── scripts/            ← Helper scripts
└── .claude/            ← AI agent configs
```

---

## Module chính
| Module | Path | Mục đích | Files quan trọng |
|--------|------|----------|-----------------|
| [ModuleA] | `src/module-a/` | [mục đích] | `main.ts`, `types.ts` |
| [ModuleB] | `src/module-b/` | [mục đích] | `service.ts`, `model.ts` |

---

## Entry Points
| Tên | File | Mô tả |
|-----|------|-------|
| App start | `src/main.ts` | Khởi động ứng dụng |
| API Router | `src/routes/index.ts` | Điểm vào tất cả API routes |
| CLI | `scripts/cli.py` | Command-line interface (nếu có) |

---

## API / Interface chính
| Endpoint / Class / Function | File:Line | Mô tả |
|----------------------------|-----------|-------|
| `GET /api/v1/health` | `src/routes/health.ts:5` | Health check |
| `POST /api/v1/auth/login` | `src/routes/auth.ts:12` | Đăng nhập |
| `class UserService` | `src/services/user.ts:1` | Business logic user |

---

## Database Schema
| Table/Collection | Columns chính | Quan hệ |
|-----------------|--------------|---------|
| `users` | id, email, role, created_at | → orders (1:N), → sessions (1:N) |
| `orders` | id, user_id, status, total | → users (N:1), → order_items (1:N) |

---

## Dependencies quan trọng
| Package | Version | Dùng cho |
|---------|---------|---------|
| [package-name] | [x.y.z] | [mục đích sử dụng] |

---

## Config / Environment Variables
| Key | Default | Bắt buộc | Mô tả |
|-----|---------|---------|-------|
| `DATABASE_URL` | - | ✅ | PostgreSQL connection string |
| `JWT_SECRET` | - | ✅ | Secret key cho JWT tokens |
| `PORT` | `3000` | ❌ | Port ứng dụng chạy |

---

## Thay đổi gần đây
| Ngày | File/Module | Loại | Mô tả ngắn | Agent |
|------|------------|------|------------|-------|
| YYYY-MM-DD | `src/...` | Add/Update/Remove | [mô tả thay đổi] | [agent-name] |

---

## Lessons & Quyết định quan trọng (bộ nhớ bền vững — lấy cảm hứng từ GBrain của gstack)
> Ghi lại QUYẾT ĐỊNH + LÝ DO, không chỉ trạng thái code — giúp agent sau không suy luận lại từ đầu hoặc lặp lại sai lầm đã biết.

| Ngày | Quyết định / Bài học | Lý do (WHY) | Agent ghi nhận |
|------|----------------------|--------------|-----------------|
| YYYY-MM-DD | [vd: Chọn KzDataGrid thay vì DataGridView gốc] | [vd: đã thử DataGridView gốc, không hỗ trợ virtualization → lag với >10k dòng] | [agent-name] |

---

## Ghi chú đặc biệt
[Known issues, gotchas, constraints quan trọng không hiển nhiên từ code]

- **[Ghi chú 1]:** [mô tả]
- **[Ghi chú 2]:** [mô tả]
