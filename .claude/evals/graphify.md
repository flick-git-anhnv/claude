---
agent: graphify
created: 2026-07-29
author: Dispatcher (theo yêu cầu user)
status: draft
---

# EVAL: graphify (skill)

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `/graphify` trước khi implement — Eval-Driven Development (EDD), theo §18.5 CLAUDE.md.

---

## 1. Mô tả năng lực (Capability Statement)

`/graphify` tự động hóa việc thiết lập và sử dụng công cụ Graphify (package PyPI: `graphifyy`) cho 1 project C#/.NET hoặc bất kỳ codebase nào graphify hỗ trợ, theo §17.3/§17.6 CLAUDE.md. Skill tự phát hiện project đã cài graphify chưa, rồi chạy đúng lệnh tương ứng (cài đặt + build lần đầu, hoặc query/update cho project đã có sẵn), không đè lên `code-graph/CODE-GRAPH.md` thủ công hiện có.

---

## 2. Capability Evals

### CE-01 — Happy path: project lớn, chưa cài graphify

**Input:** User gõ `/graphify E:\KZTEK\...\App-Access-V2` — project C# 523 file `.cs`, Python 3.10 đã có sẵn, chưa cài `graphifyy`, đã có `code-graph/CODE-GRAPH.md` viết tay.

**Output mong đợi:**
- [ ] Skill kiểm tra Python version (>=3.10) TRƯỚC khi cài, không giả định có sẵn
- [ ] Skill dùng đúng tên package `graphifyy` (2 chữ y) khi cài — KHÔNG gõ `pip install graphify`
- [ ] Skill build graph lần đầu (`python -m graphify .`) sau khi cài xong
- [ ] Skill đối chiếu output (`graphify-out/GRAPH_REPORT.md`) với `code-graph/CODE-GRAPH.md` hiện có, đề xuất bổ sung — KHÔNG tự ý ghi đè/xóa nội dung thủ công đã có
- [ ] Skill hỏi xác nhận trước khi chạy `graphify claude install` (vì thao tác này sửa CLAUDE.md của project)

**Grader:** Human (đọc lại trình tự lệnh được đề xuất/thực thi)

---

### CE-02 — Edge case: project đã cài, dùng trong lúc code

**Input:** User gõ `/graphify update` (hoặc mô tả "vừa sửa code xong, chuẩn bị verify-pr") trong project đã cài graphify và đã build trước đó.

**Output mong đợi:**
- [ ] Skill chạy `graphify update --diff` (incremental) — KHÔNG build lại toàn bộ từ đầu (`graphify .`)
- [ ] Skill nhắc rõ: sau khi update, PHẢI bổ sung thủ công mô tả nghiệp vụ + Confidence label (CONFIRMED/INFERRED/UNCERTAIN) vào `CODE-GRAPH.md` — graphify không tự viết phần này
- [ ] Nếu ngữ cảnh là "tra cứu trước khi đọc code" thay vì "sau khi sửa code" → skill chạy `graphify query "..."` thay vì `update --diff`

**Grader:** Human

---

### CE-03 — Negative case: thiếu điều kiện tiên quyết

**Input:** User gõ `/graphify` trong (a) máy chưa cài Python, hoặc (b) project rất nhỏ (<10 file, không phải ngôn ngữ graphify hỗ trợ tốt).

**Output mong đợi:**
- [ ] Trường hợp (a): Skill phát hiện thiếu Python 3.10+ → dừng lại, hướng dẫn cài Python trước — KHÔNG cố chạy `pip install` rồi nhận lỗi mập mờ
- [ ] Trường hợp (b): Skill cảnh báo giá trị thấp cho project nhỏ, hỏi xác nhận user có thực sự muốn tiếp tục không — KHÔNG tự ý quyết định bỏ qua hoặc tự ý cài mà không hỏi

**Grader:** Human

---

## 3. Regression Evals

### RE-01 — Routing đúng khi user gõ `/graphify`

**Input:** User gõ `/graphify` hoặc mô tả rõ ý muốn thiết lập/dùng graphify cho 1 project.

**Output mong đợi:**
- [ ] Description của skill trigger đúng (không bị agent khác giành routing)
- [ ] Skill không tự kích hoạt khi user chỉ hỏi thông tin chung về graphify mà không yêu cầu thực thi (câu hỏi thuần túy nên trả lời trực tiếp, không chạy lệnh)

---

### RE-02 — Không phá hỏng CODE-GRAPH.md hiện có

**Input:** Project đã có `code-graph/CODE-GRAPH.md` với nội dung thủ công từ trước.

**Output mong đợi:**
- [ ] Sau khi chạy skill, nội dung cũ trong CODE-GRAPH.md vẫn còn nguyên (chỉ được bổ sung, không bị ghi đè/xóa)
- [ ] `code-graph/CODE-GRAPH.pdf` được xuất lại nếu `.md` có thay đổi (theo §17.4 CLAUDE.md)

---

## 4. Kết quả chạy thử

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-07-29 | PASS | Reader-test subagent (cold-read) mô phỏng đúng: kiểm tra Python trước, dùng `graphifyy`, build rồi mới đối chiếu CODE-GRAPH.md, hỏi xác nhận trước `claude install` |
| CE-02 | 2026-07-29 | PASS | Subagent phân biệt đúng ngữ cảnh "query" (tra cứu) vs "update --diff" (sau khi sửa code) và nhắc bổ sung Confidence label thủ công |
| CE-03 | 2026-07-29 | PASS | Subagent dừng đúng lúc thiếu Python, hỏi xác nhận cho project nhỏ thay vì tự quyết |
| RE-01 | 2026-07-29 | PASS | Description phân biệt rõ "thực thi" vs "chỉ hỏi thông tin" |
| RE-02 | 2026-07-29 | PASS | Skill quy định rõ chỉ Edit (bổ sung), không Write đè `CODE-GRAPH.md` |

**Tổng kết:** APPROVED — 3/3 CE pass, 2/2 RE pass

---

## 5. Lịch sử eval

| Ngày | Phiên bản agent | CE pass | RE pass | Tổng kết | Ghi chú |
|------|----------------|---------|---------|----------|---------|
| 2026-07-29 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới theo yêu cầu user, sau khi phát hiện gotcha tên package `graphifyy` |

---

> **Vị trí lưu:** `C:/Users/nguye/.claude/evals/graphify.md`
> **Liên quan:** `C:/Users/nguye/.claude/commands/graphify.md`
