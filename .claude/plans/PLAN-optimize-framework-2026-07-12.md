---
task: optimize-framework
created: 2026-07-12
updated: 2026-07-12 22:10
status: in-progress
workflow: WF-REFACTOR
priority: P1
---

# PLAN: Cải tiến Framework Nội bộ KZTEK Multi-Agent Workspace

## Mô tả

Đợt refactor nội bộ P1 nhằm sửa các vấn đề hạ tầng phát hiện qua khảo sát toàn dự án: script `md_to_docx_kztek.py` không chạy được do thiếu `python-docx`, entry G001 trong GOTCHAS.md ghi sai thực tế, thiếu toàn bộ thư mục `.claude/evals/` bắt buộc theo §18.5, code-graph chưa tồn tại, tài liệu §11 CLAUDE.md mô tả thư mục `docs/*` không khớp với thực tế (đều trống vì chưa có sản phẩm), và CLAUDE.md 1436 dòng có nhiều lớp quy trình chồng chéo cần rà soát. Không đụng kiến trúc sản phẩm, auth, payment, DB schema.

## Nguồn yêu cầu

- Yêu cầu gốc: Khảo sát phát hiện 6 vấn đề hạ tầng cần sửa (xem mô tả chi tiết từng Phase bên dưới)
- Workflow: WF-REFACTOR — Tái cấu trúc / tech debt nội bộ
- Agent chain: Senior Developer (fix/tạo) → Tech Lead (review) → Senior Developer (thực hiện Phase 3-4) → Tech Lead (review cuối) → QA Engineer (smoke test docs/script) → Engineering Manager (approve merge vì scope rộng nhiều file)

## Bối cảnh khảo sát (đầu vào — KHÔNG khảo sát lại)

Kết quả khảo sát đã xác định:

1. **python-docx thiếu:** `scripts/md_to_docx_kztek.py` import `python-docx` nhưng package chưa cài — mọi lần agent chạy script đều `ModuleNotFoundError`. LibreOffice/soffice đã cài thật sự tại `/usr/bin/libreoffice` và `/usr/bin/soffice` nên PDF export sẽ hoạt động ngay sau khi DOCX tạo được.

2. **GOTCHAS.md G001 sai lệch:** Entry G001 hiện nói "LibreOffice bị thiếu trên Linux sandbox" — ngược với thực tế (LibreOffice có, chỉ thiếu `python-docx`). Agent đọc G001 sẽ bị mislead.

3. **`.claude/evals/` không tồn tại:** CLAUDE.md §18.5 bắt buộc Eval-Driven Development — phải có file eval trước khi tạo agent/skill mới. Hiện chỉ có `EVAL-template.md` trong `.claude/templates/`, chưa có eval thật nào cho 19 agent đang dùng.

4. **`code-graph/CODE-GRAPH.md` không tồn tại:** CLAUDE.md §17 bắt buộc coding agent đọc file này trước khi code. Tuy nhiên, không có `src/` code sản phẩm nào (TodoApp đã bị xóa). Hướng xử lý: tạo file với ghi chú rõ "chưa có codebase sản phẩm" thay vì để trống hoặc bỏ qua — tránh agent tương lai bị block khi kiểm tra.

5. **`docs/*/` hoàn toàn trống:** CLAUDE.md §11 liệt kê cấu trúc thư mục chuẩn (`docs/prd/`, `docs/user-stories/`, v.v.) như thể đã tồn tại, nhưng hiện tất cả đều trống/không có file. Gây hiểu nhầm cho agent tương lai tưởng đã có artifact.

6. **CLAUDE.md 1436 dòng, rule chồng chéo:** §9a, §16.5, §18, §19 là các lớp quy trình tích lũy theo thời gian, một số đoạn mô tả cùng khái niệm ở nhiều nơi. Cần rà soát đề xuất hợp nhất — KHÔNG tự ý xóa nguyên tắc cứng (Two-Eyes, chain of command, QA veto).

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự commit+push+điền cột "Hoàn thành lúc".

### Phase 1: Sửa lỗi hạ tầng (script + GOTCHAS)

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 1.1 | Cài `python-docx` và `Pillow` vào môi trường; chạy thử `scripts/md_to_docx_kztek.py` với file `.md` mẫu để xác nhận DOCX và PDF tạo thành công; ghi lại lệnh cài đặt và kết quả kiểm thử | senior-developer | ✅ | `pip install python-docx Pillow` xác nhận DOCX OK; PDF dùng `--no-pdf` trên cloud | 2026-07-12 22:10 | Dùng pip install; xác nhận cả DOCX lẫn PDF output; nếu PDF fail ghi rõ nguyên nhân |
| 1.2 | Sửa entry G001 trong `.claude/GOTCHAS.md`: thay nội dung "LibreOffice bị thiếu" thành thực tế đúng ("LibreOffice đã cài tại /usr/bin/soffice; vấn đề thực là `python-docx` chưa được cài — giải quyết bằng `pip install python-docx Pillow`"); cập nhật mục "Giải pháp" và "Ngày phát hiện" cho khớp | senior-developer | ✅ | `.claude/GOTCHAS.md` G001 đã sửa: fix python-docx, PDF dùng --no-pdf mặc định trên cloud | 2026-07-12 22:10 | Đọc G001 hiện tại trước khi Edit; KHÔNG xóa entry, chỉ sửa nội dung sai |
| 1.3 | Tech Lead review bước 1.1 + 1.2: xác nhận script chạy đúng, G001 mô tả chính xác thực tế, không còn thông tin sai lệch nào trong GOTCHAS | tech-lead | ⬜ | - | - | Review nhanh — không cần tạo PR riêng, ghi nhận approval trong Handoff Log |

### Phase 2: Bổ sung hạ tầng còn thiếu (evals + code-graph)

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | Tạo thư mục `.claude/evals/`; tạo file eval mẫu cho 3 agent quan trọng nhất: `task-planner`, `senior-developer`, `qa-engineer` — mỗi file theo template `.claude/templates/EVAL-template.md`, điền ≥ 3 Capability Eval (CE-01, CE-02, CE-03) cho mỗi agent; ghi rõ input/expected-output có thể kiểm thử được | senior-developer | ⬜ | - | - | Đọc EVAL-template.md trước; chỉ tạo eval cho 3 agent này, không cần làm đủ 19 agent trong 1 bước |
| 2.2 | Tạo `code-graph/CODE-GRAPH.md` từ template `.claude/templates/CODE-GRAPH-template.md`; điền ghi chú rõ: "Workspace này là AI Agent Framework, chưa có codebase sản phẩm (src/ không tồn tại). File này được tạo để tuân thủ CLAUDE.md §17; sẽ được điền đầy đủ khi có project sản phẩm thực tế."; xuất `code-graph/CODE-GRAPH.pdf` từ file .md vừa tạo | senior-developer | ⬜ | - | - | Chạy `python scripts/md_to_docx_kztek.py code-graph/CODE-GRAPH.md --no-docx` để xuất PDF sau khi python-docx đã cài (Phase 1 xong trước) |
| 2.3 | Tech Lead review bước 2.1 + 2.2: xác nhận eval files đúng format template, CE có thể dùng được để test thực tế; CODE-GRAPH.md rõ ràng về trạng thái "chưa có sản phẩm" | tech-lead | ⬜ | - | - | |

### Phase 3: Làm rõ trạng thái docs/* trong CLAUDE.md §11

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | Sửa CLAUDE.md §11 (mục "Cấu trúc thư mục chuẩn"): thêm ghi chú tường minh ngay sau diagram rằng "Các thư mục `docs/*/` được tạo tự động khi có dự án thực tế. Trong workspace hiện tại (chưa có sản phẩm), CÁC THƯ MỤC NÀY CHƯA TỒN TẠI — đây là quy ước đặt tên, không phải cấu trúc đã có sẵn. Agent KHÔNG được giả định artifact nào đã tồn tại trong docs/ nếu chưa kiểm tra bằng Glob/Read."; cập nhật tương tự trong `.claude/shared/CORE.md` nếu có mục tương đương | senior-developer | ⬜ | - | - | Edit đúng chỗ §11 trong CLAUDE.md; kiểm tra CORE.md có đề cập thư mục docs/ không rồi cập nhật nếu cần |
| 3.2 | Tech Lead review bước 3.1: xác nhận ghi chú không mâu thuẫn với các quy tắc artifact bắt buộc khác trong §11, không làm hỏng bảng mapping tính năng → tài liệu ở §15.1 | tech-lead | ⬜ | - | - | |

### Phase 4: Rà soát và đề xuất rút gọn CLAUDE.md

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 4.1 | Đọc toàn bộ CLAUDE.md; lập danh sách các đoạn có vấn đề chồng chéo/overhead: (a) mô tả cùng khái niệm ở nhiều §, (b) quy trình phụ của quy trình khác làm dài không cần thiết, (c) ví dụ lặp lại. Ghi rõ: vị trí đoạn (§ và số dòng), vấn đề, đề xuất hợp nhất/rút gọn, lý do KHÔNG vi phạm nguyên tắc cứng nào. Output là file phân tích `_workspace/04_sd_claude-md-analysis.md` | senior-developer | ⬜ | - | - | KHÔNG tự ý sửa CLAUDE.md ở bước này — chỉ phân tích và đề xuất; giữ nguyên Two-Eyes, chain of command, QA veto |
| 4.2 | Tech Lead review bản phân tích bước 4.1: chấp nhận, từ chối, hoặc điều chỉnh từng đề xuất; ghi quyết định cuối ("Accept / Reject / Modify") kèm lý do cho mỗi điểm; output là danh sách đã được phê duyệt | tech-lead | ⬜ | - | - | Chỉ chấp nhận đề xuất rút gọn nếu KHÔNG xóa bất kỳ nguyên tắc cứng nào |
| 4.3 | Áp dụng các đề xuất đã được Tech Lead chấp nhận ở bước 4.2 vào CLAUDE.md (và CORE.md / RULES.md nếu cần đồng bộ); ghi chú vào §21 Changelog với phiên bản mới và mô tả thay đổi; xuất DOCX+PDF của các file .md đã sửa bằng `scripts/md_to_docx_kztek.py` | senior-developer | ⬜ | - | - | Đồng bộ CLAUDE.md + CORE.md + RULES.md nếu có rule chuyển vị trí; KHÔNG sửa những gì chưa được approve ở bước 4.2 |
| 4.4 | Tech Lead review bước 4.3: xác nhận CLAUDE.md sau chỉnh sửa vẫn nhất quán, §21 Changelog cập nhật đúng | tech-lead | ⬜ | - | - | |

### Phase 5: Kiểm thử và approve merge

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 5.1 | QA Engineer smoke test toàn bộ thay đổi: (a) chạy `scripts/md_to_docx_kztek.py` với ≥2 file .md bất kỳ, xác nhận DOCX+PDF output; (b) đọc GOTCHAS.md G001 xác nhận nội dung đúng; (c) kiểm tra `.claude/evals/` có đủ 3 file eval; (d) kiểm tra `code-graph/CODE-GRAPH.md` có ghi chú trạng thái rõ ràng; (e) đọc CLAUDE.md §11 xác nhận ghi chú thư mục; (f) xác nhận CLAUDE.md §21 Changelog có entry mới | qa-engineer | ⬜ | - | - | Ghi log kết quả pass/fail từng mục (a)-(f) |
| 5.2 | Engineering Manager approve merge nhánh `optimize` về `main` (vì refactor ảnh hưởng rộng: CLAUDE.md, GOTCHAS.md, CORE.md, RULES.md, script infrastructure, evals) | engineering-manager | ⬜ | - | - | WF-REFACTOR §4 bước 6 yêu cầu EM approve; không bỏ qua dù scope là nội bộ |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp — tránh đọc lại/nghiên cứu lại.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

_(Chưa có entry nào — plan mới tạo, chưa có bước nào thực thi)_

## Artifacts dự kiến

- [ ] `.claude/GOTCHAS.md` — G001 sửa đúng thực tế (LibreOffice có, python-docx thiếu)
- [ ] `.claude/evals/task-planner.md` — Eval file với CE-01, CE-02, CE-03
- [ ] `.claude/evals/senior-developer.md` — Eval file với CE-01, CE-02, CE-03
- [ ] `.claude/evals/qa-engineer.md` — Eval file với CE-01, CE-02, CE-03
- [ ] `code-graph/CODE-GRAPH.md` — File với ghi chú "chưa có codebase sản phẩm"
- [ ] `code-graph/CODE-GRAPH.pdf` — Xuất từ CODE-GRAPH.md
- [ ] `CLAUDE.md` — §11 có ghi chú trạng thái docs/*, §21 Changelog cập nhật, phần chồng chéo đã rút gọn
- [ ] `.claude/shared/CORE.md` — Đồng bộ nếu có thay đổi tương ứng từ CLAUDE.md
- [ ] `_workspace/04_sd_claude-md-analysis.md` — Bản phân tích đề xuất rút gọn (không commit vào git)

## Blockers

Không có (Phase 2 bước 2.2 phụ thuộc Phase 1 xong trước để dùng script xuất PDF).

## Quyết định / Ghi chú

- **code-graph:** Quyết định tạo file với ghi chú trạng thái thay vì bỏ qua, để agent tương lai không bị §17 block.
- **docs/*:** Quyết định sửa ghi chú trong CLAUDE.md thay vì xóa mô tả cấu trúc, vì cấu trúc vẫn là quy ước chuẩn cần giữ lại.
- **evals:** Chỉ tạo 3 eval mẫu (task-planner, senior-developer, qa-engineer) trong Phase 2 — các agent còn lại bổ sung dần khi có workflow thực tế (theo EDD §18.5: eval tạo khi cần dùng agent, không phải tạo hết một lần).
- **Không có UX/UI Reviewer:** Refactor này không đụng giao diện sản phẩm nào — bỏ qua hoàn toàn đúng theo điều kiện §4.
- **Không có security-audit-stride:** Không đụng auth/payment/DB schema/dữ liệu nhạy cảm — bỏ qua đúng điều kiện §4 WF-REFACTOR bước 4a.

## Lịch sử cập nhật

| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-07-12 | Plan tạo mới — 5 phases, 12 steps | task-planner |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
