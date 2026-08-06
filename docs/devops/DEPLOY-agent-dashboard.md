# DEPLOY-agent-dashboard — Hướng dẫn Deploy Local

> **Môi trường:** Local only (Windows 11, máy tính cá nhân)
> **Phiên bản:** 0.1.0 — commit ff0bd2e (QA sign-off 2026-08-06)
> **Cập nhật:** 2026-08-06

---

## 1. Yêu cầu môi trường

| Phần mềm | Phiên bản tối thiểu | Ghi chú |
|---|---|---|
| Python | 3.10+ | Thêm vào PATH khi cài |
| pip | đi kèm Python | Để cài backend dependencies |
| Node.js | 18+ | **Chỉ cần lần đầu** nếu `frontend/dist/` chưa có |
| npm | đi kèm Node.js | **Chỉ cần lần đầu** để build frontend |

> `frontend/dist/` đã được build sẵn và commit vào repo — **thường không cần Node.js**.
> Chỉ cần Node.js nếu bạn checkout một commit chưa có `dist/` hoặc muốn rebuild frontend.

### Backend dependencies (pip)

File: `tools/agent-dashboard/backend/requirements.txt`

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
watchdog==4.0.1
aiosqlite==0.20.0
pydantic==2.7.1
python-multipart==0.0.9
```

Cài thủ công (nếu không dùng `start.bat`):

```powershell
pip install -r tools/agent-dashboard/backend/requirements.txt
```

---

## 2. Cách khởi động (một lệnh)

### Cách A — Dùng `start.bat` (khuyến nghị, Windows)

```bat
tools\agent-dashboard\start.bat
```

Script tự động:
1. Kiểm tra Python và backend dependencies (cài nếu thiếu).
2. Kiểm tra `frontend/dist/` (build nếu thiếu, cần Node.js).
3. Khởi động server uvicorn trên cổng **7770**.
4. Mở trình duyệt tới `http://127.0.0.1:7770` sau 2 giây.

### Cách B — Thủ công (PowerShell / CMD)

```powershell
# Từ thư mục gốc project
cd tools\agent-dashboard\backend
python -m agent_dashboard
```

Dashboard sẽ khả dụng tại: **http://127.0.0.1:7770**

---

## 3. Cách dừng

- **Nếu dùng `start.bat`:** nhấn `Ctrl+C` trong cửa sổ terminal đang chạy script.
- **Kill theo cổng** (nếu terminal bị đóng mà process vẫn còn):

```powershell
# Tìm PID đang dùng cổng 7770
netstat -ano | findstr :7770

# Kill process (thay <PID> bằng số tìm được)
taskkill /F /PID <PID>
```

---

## 4. Cách xem log

Log được in ra terminal ngay khi server chạy. Định dạng:

```
2026-08-06 10:00:00  INFO      agent_dashboard.main  Agent Dashboard started on port 7770
2026-08-06 10:00:01  INFO      agent_dashboard.watcher  Watching: C:\Users\nguye\.claude\projects
```

Nếu cần lưu log ra file:

```bat
tools\agent-dashboard\backend\python -m agent_dashboard > dashboard.log 2>&1
```

---

## 5. Vị trí dữ liệu (SQLite DB + accounts)

| File | Đường dẫn |
|---|---|
| SQLite database | `tools/agent-dashboard/backend/data/dashboard.db` |
| Accounts (encrypted) | `tools/agent-dashboard/backend/data/accounts.enc` |
| JSONL nguồn (chỉ đọc) | `%USERPROFILE%\.claude\projects\*\*.jsonl` |

> **Lưu ý:** `data/` được tạo tự động khi khởi động lần đầu. Không cần tạo thủ công.

---

## 6. Backup và Restore SQLite DB

### Backup

```powershell
# Copy DB ra nơi an toàn (trong khi server KHÔNG chạy, hoặc đang chạy OK — SQLite hỗ trợ hot copy)
Copy-Item "tools\agent-dashboard\backend\data\dashboard.db" `
          "tools\agent-dashboard\backend\data\dashboard.db.bak-$(Get-Date -Format 'yyyyMMdd-HHmm')"
```

### Restore

```powershell
# Dừng server trước
# Copy bản backup về
Copy-Item "tools\agent-dashboard\backend\data\dashboard.db.bak-20260806-1000" `
          "tools\agent-dashboard\backend\data\dashboard.db"
# Khởi động lại server
```

---

## 7. Rollback (quay lại commit trước)

Nếu phiên bản mới gặp lỗi nghiêm trọng:

```powershell
# Xem danh sách commit gần nhất
git log --oneline -10

# Checkout commit ổn định trước đó (thay <HASH> bằng hash commit)
git checkout <HASH> -- tools/agent-dashboard/

# Khởi động lại
tools\agent-dashboard\start.bat
```

> Hoặc dùng `git stash` / `git revert` theo Git Safety Protocol nếu muốn giữ working tree sạch.

---

## 8. Known Issues (phiên bản 0.1.0 — build ff0bd2e)

Hai bug P2 sau đây được QA Lead xác nhận và cho phép deploy. Sẽ được fix trong iteration tiếp theo.

### BUG-001 — DELETE account trả HTTP 500 thay vì 204

| Trường | Nội dung |
|---|---|
| Endpoint | `DELETE /api/accounts/{id}` |
| Mô tả | Khi xóa account không active, API trả về HTTP 500 nhưng **account đã được xóa thành công**. Data không bị mất. |
| Ảnh hưởng | Frontend hiện thông báo lỗi mặc dù operation thành công. Làm mới trang sẽ xác nhận account đã biến mất. |
| Workaround | Sau khi thấy lỗi 500, làm mới danh sách account để xác nhận xóa đã thành công. |
| Priority | P2 |

### BUG-002 — Tạo account với tên trùng lặp không bị từ chối

| Trường | Nội dung |
|---|---|
| Endpoint | `POST /api/accounts` |
| Mô tả | API cho phép tạo hai account cùng tên. Validation trùng tên bị thiếu. |
| Ảnh hưởng | Danh sách account có thể có nhiều mục cùng tên, gây nhầm lẫn khi quản lý. Không gây mất dữ liệu hay crash. |
| Workaround | Kiểm tra tên trước khi tạo account mới. Nếu tạo nhầm, xóa account dư thừa. |
| Priority | P2 |

---

## 9. Deploy Checklist (Local)

```
[x] Python 3.10+ có sẵn, thêm vào PATH
[x] pip install requirements.txt chạy thành công
[x] frontend/dist/index.html tồn tại (đã build sẵn hoặc npm run build)
[x] Cổng 7770 trống (không có process khác chiếm)
[x] start.bat chạy không lỗi
[x] http://127.0.0.1:7770 mở được trong trình duyệt
[x] Dashboard hiển thị agent sessions từ ~/.claude/projects/
[x] Known issues (BUG-001, BUG-002) đã thông báo tới user
```
