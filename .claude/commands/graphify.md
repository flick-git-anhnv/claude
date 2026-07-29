---
name: graphify
description: "PHẢI dùng khi user muốn thiết lập, cài đặt, cập nhật graph, hoặc tra cứu bằng công cụ Graphify (package PyPI `graphifyy`) cho 1 project cụ thể — ví dụ: '/graphify <path>', 'thiết lập graphify cho dự án này', 'chạy graphify update', 'tra cứu ai gọi hàm X bằng graphify', hoặc user hỏi có nên cài graphify cho project cụ thể của họ không (skill sẽ tư vấn kèm cảnh báo quy mô ở Bước 1). Skill tự phát hiện project đã cài graphify chưa rồi chạy đúng quy trình tương ứng (§17.6/§17.3 CLAUDE.md). KHÔNG dùng khi: (1) user chỉ hỏi thông tin chung về graphify là gì/hoạt động ra sao mà KHÔNG nhắc đến project cụ thể nào của họ (trả lời trực tiếp bằng text, không chạy lệnh); (2) user muốn migrate framework/ngôn ngữ (→ code-migrator, không liên quan graphify); (3) user muốn cập nhật `CODE-GRAPH.md` thủ công mà KHÔNG nhắc đến graphify/công cụ tự động (→ quy trình thủ công §17.1-17.5 CLAUDE.md, không tự ý kích hoạt skill này); (4) user chỉ muốn nâng cấp version package `graphifyy` không liên quan đến build/update graph (→ hướng dẫn trực tiếp `pip install --upgrade graphifyy`, không cần chạy toàn bộ quy trình skill)."
---

# Skill: `/graphify` — Thiết lập & sử dụng Graphify cho 1 project

> **Mục đích:** Tự động hóa đúng trình tự lệnh của công cụ Graphify (xem `docs/research/RESEARCH-graphify-2026-07-29.md` + §17.6 CLAUDE.md), tránh lặp lại gotcha đã phát hiện thực tế: **tên package PyPI thật là `graphifyy` (2 chữ y) — KHÔNG phải `graphify`**. `pip install graphify` sẽ báo lỗi "No matching distribution found".
>
> **Khi nào gọi:** User gõ `/graphify [path]`, hoặc mô tả rõ muốn cài đặt/cập nhật/tra cứu bằng graphify cho 1 project. Nếu user chỉ hỏi graphify là gì / hoạt động ra sao mà không có ý định chạy lệnh ngay → trả lời trực tiếp, không cần gọi skill này.

---

## Bước 0 — Xác định project target

- Nếu `args` có path → dùng path đó.
- Nếu không có `args` → dùng working directory hiện tại, nhưng **xác nhận lại với user** path đang thao tác trước khi cài đặt bất cứ gì (tránh cài nhầm project).

---

## Bước 1 — Pre-check môi trường (BẮT BUỘC trước khi cài đặt)

1. Kiểm tra Python: thử `python --version` trước, nếu không có/lỗi thì thử `python3 --version` (thứ tự này áp dụng cho mọi OS — Windows thường có `python`, Linux/macOS thường có `python3`). Yêu cầu **>= 3.10**.
   - Thiếu Python hoặc version < 3.10 → **DỪNG NGAY**, báo user cần cài Python 3.10+ trước. KHÔNG cố chạy `pip install` rồi nhận lỗi mập mờ. KHÔNG chạy tiếp Bước 2 trở đi.
2. Ước lượng quy mô project: Glob **tổng cộng dồn** số file theo mọi ngôn ngữ graphify hỗ trợ tốt nhất cho KZTEK (`.cs` + `.xaml` + `.razor` + `.cshtml` + `.ps1` + `.psm1` + `.psd1` + `.sql`), không tính riêng từng loại.
   - Nếu tổng < 50 file → cảnh báo: "Project nhỏ, giá trị graphify có thể thấp (theo §17.6 CLAUDE.md, graphify hữu ích nhất khi >50 file)". Hỏi user xác nhận có muốn tiếp tục không — **KHÔNG tự ý quyết định bỏ qua hoặc tự ý cài mà không hỏi**.
   - Bước 1 (cả 2 mục) luôn chạy trước Bước 2, **bất kể sau đó phát hiện Trạng thái A, B hay C** — pre-check không phụ thuộc trạng thái cài đặt.

---

## Bước 2 — Detect trạng thái graphify trong project

Chạy 2 kiểm tra:
```bash
python -m pip show graphifyy
```
```bash
# Kiểm tra đã build graph lần nào chưa (thư mục output mặc định của graphify)
ls graphify-out/graph.json 2>/dev/null
```

Từ đó xác định 1 trong 3 trạng thái:

| Trạng thái | `pip show graphifyy` | `graphify-out/graph.json` | → Nhánh xử lý |
|---|---|---|---|
| **A — Chưa cài** | Not found | — | Bước 3A |
| **B — Đã cài, chưa build** | Found | Không tồn tại | Bước 3A (bỏ qua bước cài, chạy thẳng build) |
| **C — Đã cài, đã build** | Found | Tồn tại | Bước 3B |

---

## Bước 3A — Cài đặt + build lần đầu (Trạng thái A/B)

1. Cài đặt (bỏ qua nếu đã ở Trạng thái B):
   ```bash
   python -m pip install graphifyy
   ```
   (Chỉ thêm `"graphifyy[leiden]"` nếu user yêu cầu rõ community detection nâng cao — không tự ý thêm extras.)
2. Build graph lần đầu tại root project:
   ```bash
   python -m graphify .
   ```
   → Sinh ra `graphify-out/graph.json`, `graphify-out/GRAPH_REPORT.md`, `graphify-out/graph.html`.
3. Đối chiếu với `code-graph/CODE-GRAPH.md`:
   - **Nếu đã tồn tại:** Đọc `GRAPH_REPORT.md` vừa sinh ra, so sánh với nội dung thủ công — liệt kê module/quan hệ nào graphify phát hiện mà CODE-GRAPH.md chưa có. **Dùng Edit để BỔ SUNG — TUYỆT ĐỐI KHÔNG Write đè hoặc xóa nội dung thủ công đã có.**
   - **Nếu CHƯA tồn tại:** Tạo mới `code-graph/CODE-GRAPH.md` từ `.claude/templates/CODE-GRAPH-template.md`, điền dữ liệu nền từ `GRAPH_REPORT.md`, rồi bổ sung thủ công phần mô tả nghiệp vụ mà graphify không tạo ra được.
   - Cả 2 trường hợp: phần bổ sung PHẢI kèm Confidence label (`CONFIRMED`/`INFERRED`/`UNCERTAIN` theo §17.2 CLAUDE.md) — graphify tự sinh dùng `EXTRACTED/INFERRED/AMBIGUOUS`, map lại: `EXTRACTED → CONFIRMED`, `INFERRED → INFERRED`, `AMBIGUOUS → UNCERTAIN`.
   - Xuất lại `CODE-GRAPH.pdf` theo §17.4 CLAUDE.md sau khi `.md` có thay đổi (tạo mới hoặc bổ sung).
4. Hỏi user xác nhận trước khi chạy always-on injection (thao tác này **sửa file `CLAUDE.md` của project**, cần xác nhận rõ ràng — theo nguyên tắc "Executing actions with care"):
   ```bash
   python -m graphify claude install
   ```

---

## Bước 3B — Sử dụng graphify đã sẵn sàng (Trạng thái C)

Xác định ngữ cảnh user đang cần gì:

| Ngữ cảnh | Lệnh chạy |
|---|---|
| Tra cứu trước khi đọc/sửa code (VD: "ai gọi hàm X", "module này phụ thuộc gì") | `python -m graphify query "<câu hỏi>"` |
| Vừa sửa code xong, chuẩn bị `/verify-pr` (theo §17.3 CLAUDE.md) | `python -m graphify update --diff` |
| Cần đường đi/quan hệ giữa 2 khái niệm cụ thể | `python -m graphify path A B` |
| Cần xem subgraph 1-hop quanh 1 node | `python -m graphify explain X` |
| Xem PR dashboard / graph impact của 1 PR | `python -m graphify prs` hoặc `python -m graphify prs <N>` |

**Sau khi chạy `update --diff`:** PHẢI nhắc rõ bước tiếp theo — bổ sung thủ công mô tả nghiệp vụ + Confidence label vào `CODE-GRAPH.md`. Graphify **không tự viết phần nghiệp vụ này** — chỉ chạy xong `update --diff` KHÔNG coi là hoàn thành nghĩa vụ cập nhật CODE-GRAPH theo §17.3.

---

## Bước 4 — Báo cáo kết quả

Tổng hợp cho user:
```
## GRAPHIFY — Kết quả thực thi
Project        : [path]
Trạng thái đầu : [A / B / C]
Lệnh đã chạy    : [danh sách lệnh thực tế đã chạy, theo đúng thứ tự]
Kết quả         : [tóm tắt output — số node/edge phát hiện, hoặc kết quả query]
CODE-GRAPH.md   : [Đã bổ sung X mục / Không cần thay đổi]
Bước tiếp theo  : [gợi ý cụ thể — VD: "Xem code-graph/CODE-GRAPH.md để duyệt các mục UNCERTAIN"]
```

**KHÔNG được bịa kết quả** — nếu lệnh nào fail, ghi rõ lỗi thực tế thay vì báo "thành công".

---

## Red Flags (lý do hay bỏ qua — nhìn nhận lại khi thấy)

| Thought | Reality |
|---------|---------|
| "`pip install graphify` chắc đúng rồi, thử luôn" | **Đã xảy ra thực tế và gây lỗi** — tên package đúng là `graphifyy` (2 chữ y). Luôn dùng đúng tên này; nếu nghi ngờ, chạy `python -m pip index versions graphifyy` để xác nhận trước |
| "Project nhỏ nhưng user đã gõ `/graphify` rồi, chắc muốn dùng luôn" | Vẫn phải cảnh báo giá trị thấp + hỏi xác nhận (Bước 1.2) — user gõ lệnh không có nghĩa đã cân nhắc trade-off |
| "Đã chạy `update --diff` xong, vậy là CODE-GRAPH.md đã cập nhật rồi" | Graphify KHÔNG tự viết mô tả nghiệp vụ + Confidence label — luôn phải nhắc bổ sung thủ công (Bước 3B) |
| "User không nói rõ path, dùng CWD luôn cho nhanh" | Phải xác nhận lại path với user trước khi cài đặt — tránh cài nhầm project (Bước 0) |
| "`graphify claude install` chỉ là lệnh nhỏ, chạy luôn cho tiện" | Đây là thao tác sửa `CLAUDE.md` của project — PHẢI hỏi xác nhận trước, không tự ý chạy |
| "CODE-GRAPH.md đã có nội dung graphify tương tự, ghi đè lại cho gọn" | TUYỆT ĐỐI không Write đè — chỉ Edit bổ sung, giữ nguyên nội dung thủ công đã có |
| "Máy này chắc có Python rồi, khỏi check" | Luôn kiểm tra version cụ thể (>=3.10) trước — tránh lỗi cài đặt nửa chừng khó debug |

---

## Verification (done gate)

- [ ] Đã kiểm tra Python >= 3.10 trước khi cài đặt
- [ ] Dùng đúng tên package `graphifyy` (không phải `graphify`)
- [ ] Đã xác nhận path project với user trước khi cài đặt (nếu dùng CWD mặc định)
- [ ] Không ghi đè/xóa nội dung thủ công trong `code-graph/CODE-GRAPH.md` — chỉ bổ sung qua Edit
- [ ] Đã xác nhận user trước khi chạy `graphify claude install`
- [ ] Báo cáo đúng kết quả thực tế của từng lệnh (không bịa PASS khi lệnh fail)
- [ ] Nếu có sửa `CODE-GRAPH.md` → đã xuất lại `.pdf` theo §17.4 CLAUDE.md

---

## Ghi chú

- Đây là CLI phải được **chủ động gọi** — không có watcher/daemon tự chạy ngầm (đúng theo §17.6 CLAUDE.md).
- KHÔNG tự ý cài pip package trên project production/staging khi chưa được Tech Lead duyệt.
- Output của graphify là input để điền vào CODE-GRAPH.md — không dùng raw output thay thế file template.
- Nguồn tham khảo đầy đủ: `docs/research/RESEARCH-graphify-2026-07-29.md`, §17.6 CLAUDE.md.
