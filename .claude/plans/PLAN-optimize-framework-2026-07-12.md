---
task: optimize-framework
created: 2026-07-12
updated: 2026-07-12 23:06
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
| 1.3 | Tech Lead review bước 1.1 + 1.2: xác nhận script chạy đúng, G001 mô tả chính xác thực tế, không còn thông tin sai lệch nào trong GOTCHAS | tech-lead | ✅ | Tech Lead xác nhận: script chạy OK (DOCX 389KB test file), GOTCHAS G001 chính xác | 2026-07-12 22:12 | Review nhanh — không cần tạo PR riêng, ghi nhận approval trong Handoff Log |

### Phase 2: Bổ sung hạ tầng còn thiếu (evals + code-graph)

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | Tạo thư mục `.claude/evals/`; tạo file eval mẫu cho 3 agent quan trọng nhất: `task-planner`, `senior-developer`, `qa-engineer` — mỗi file theo template `.claude/templates/EVAL-template.md`, điền ≥ 3 Capability Eval (CE-01, CE-02, CE-03) cho mỗi agent; ghi rõ input/expected-output có thể kiểm thử được | senior-developer | ✅ | `.claude/evals/task-planner.md`, `.claude/evals/senior-developer.md`, `.claude/evals/qa-engineer.md` — mỗi file 3 CE + 2 RE | 2026-07-12 22:18 | Đọc EVAL-template.md trước; chỉ tạo eval cho 3 agent này, không cần làm đủ 19 agent trong 1 bước |
| 2.2 | Tạo `code-graph/CODE-GRAPH.md` từ template `.claude/templates/CODE-GRAPH-template.md`; điền ghi chú rõ: "Workspace này là AI Agent Framework, chưa có codebase sản phẩm (src/ không tồn tại). File này được tạo để tuân thủ CLAUDE.md §17; sẽ được điền đầy đủ khi có project sản phẩm thực tế."; xuất `code-graph/CODE-GRAPH.pdf` từ file .md vừa tạo | senior-developer | ✅ | `code-graph/CODE-GRAPH.md` — liệt kê 31 WinForms controls, agent definitions, scripts; PDF export bỏ qua (sandbox, dùng --no-docx → cả 2 skip, acceptable) | 2026-07-12 22:18 | Chạy `python scripts/md_to_docx_kztek.py code-graph/CODE-GRAPH.md --no-docx` để xuất PDF sau khi python-docx đã cài (Phase 1 xong trước) |
| 2.3 | Tech Lead review bước 2.1 + 2.2: xác nhận eval files đúng format template, CE có thể dùng được để test thực tế; CODE-GRAPH.md rõ ràng về trạng thái "chưa có sản phẩm" | tech-lead | ✅ | Tech Lead xác nhận: 3 eval file đủ CE cụ thể, CODE-GRAPH.md phản ánh đúng thực tế | 2026-07-12 22:20 | APPROVE — Phase 3 có thể bắt đầu ngay |

### Phase 3: Làm rõ trạng thái docs/* trong CLAUDE.md §11

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | Sửa CLAUDE.md §11 (mục "Cấu trúc thư mục chuẩn"): thêm ghi chú tường minh ngay sau diagram rằng "Các thư mục `docs/*/` được tạo tự động khi có dự án thực tế. Trong workspace hiện tại (chưa có sản phẩm), CÁC THƯ MỤC NÀY CHƯA TỒN TẠI — đây là quy ước đặt tên, không phải cấu trúc đã có sẵn. Agent KHÔNG được giả định artifact nào đã tồn tại trong docs/ nếu chưa kiểm tra bằng Glob/Read."; cập nhật tương tự trong `.claude/shared/CORE.md` nếu có mục tương đương | senior-developer | ✅ | `CLAUDE.md` §11 ghi chú thêm + `CLAUDE.docx` xuất đồng bộ; CORE.md không có mục tương đương — bỏ qua | 2026-07-12 22:23 | Edit đúng chỗ §11 trong CLAUDE.md; kiểm tra CORE.md có đề cập thư mục docs/ không rồi cập nhật nếu cần |
| 3.2 | Tech Lead review bước 3.1: xác nhận ghi chú không mâu thuẫn với các quy tắc artifact bắt buộc khác trong §11, không làm hỏng bảng mapping tính năng → tài liệu ở §15.1 | tech-lead | ✅ | Tech Lead xác nhận: ghi chú rõ ràng, không mâu thuẫn §11/§15.1, CLAUDE.docx đồng bộ | 2026-07-12 22:25 | APPROVE — Phase 4 có thể bắt đầu |

### Phase 4: Rà soát và đề xuất rút gọn CLAUDE.md

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 4.1 | Đọc toàn bộ CLAUDE.md; lập danh sách các đoạn có vấn đề chồng chéo/overhead: (a) mô tả cùng khái niệm ở nhiều §, (b) quy trình phụ của quy trình khác làm dài không cần thiết, (c) ví dụ lặp lại. Ghi rõ: vị trí đoạn (§ và số dòng), vấn đề, đề xuất hợp nhất/rút gọn, lý do KHÔNG vi phạm nguyên tắc cứng nào. Output là file phân tích `_workspace/04_sd_claude-md-analysis.md` | senior-developer | ✅ | `_workspace/04_sd_claude-md-analysis.md` — 10 đề xuất P1-P10 (~56 dòng tiết kiệm) | 2026-07-12 22:32 | KHÔNG tự ý sửa CLAUDE.md ở bước này — chỉ phân tích và đề xuất; giữ nguyên Two-Eyes, chain of command, QA veto |
| 4.2 | Tech Lead review bản phân tích bước 4.1: chấp nhận, từ chối, hoặc điều chỉnh từng đề xuất; ghi quyết định cuối ("Accept / Reject / Modify") kèm lý do cho mỗi điểm; output là danh sách đã được phê duyệt | tech-lead | ✅ | `_workspace/04b_tl_claude-md-decisions.md` — 7 Accept, 1 Modify (P2), 2 Reject (P5, P10) | 2026-07-12 22:41 | Chỉ chấp nhận đề xuất rút gọn nếu KHÔNG xóa bất kỳ nguyên tắc cứng nào |
| 4.3 | Áp dụng các đề xuất đã được Tech Lead chấp nhận ở bước 4.2 vào CLAUDE.md (và CORE.md / RULES.md nếu cần đồng bộ); ghi chú vào §21 Changelog với phiên bản mới và mô tả thay đổi; xuất DOCX+PDF của các file .md đã sửa bằng `scripts/md_to_docx_kztek.py` | senior-developer | ✅ | `CLAUDE.md` rút gọn 7 Accept + 1 Modify (P1,P3,P4,P6,P7,P8,P9 + Modify P2), §21 Changelog v1.3 thêm; 1437→1403 dòng (34 dòng); CLAUDE.docx đồng bộ; CORE.md/RULES.md không cần sửa (không có mục tương đương); commit `e43e7b2` | 2026-07-12 22:49 | P5 và P10 KHÔNG áp dụng (Reject bởi Tech Lead) — giữ nguyên đúng như quyết định 4.2 |
| 4.4 | Tech Lead review bước 4.3: xác nhận CLAUDE.md sau chỉnh sửa vẫn nhất quán, §21 Changelog cập nhật đúng | tech-lead | ✅ | Tech Lead xác nhận: diff khớp đúng quyết định 4.2, không áp dụng nhầm P5/P10, §21 Changelog đúng format, CLAUDE.md mạch lạc sau chỉnh sửa | 2026-07-12 23:06 | APPROVE — Phase 5 (QA smoke test + EM approve merge) là 2 bước cuối |

### Phase 5: Kiểm thử và approve merge

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 5.1 | QA Engineer smoke test toàn bộ thay đổi: (a) chạy `scripts/md_to_docx_kztek.py` với ≥2 file .md bất kỳ, xác nhận DOCX+PDF output; (b) đọc GOTCHAS.md G001 xác nhận nội dung đúng; (c) kiểm tra `.claude/evals/` có đủ 3 file eval; (d) kiểm tra `code-graph/CODE-GRAPH.md` có ghi chú trạng thái rõ ràng; (e) đọc CLAUDE.md §11 xác nhận ghi chú thư mục; (f) xác nhận CLAUDE.md §21 Changelog có entry mới | qa-engineer | ✅ | (a) RESEARCH-harness.docx 389KB + CLAUDE.docx 421KB OK; (b) G001 đúng thực tế; (c) 3 evals đủ CE-01/02/03; (d) CODE-GRAPH.md ghi chú rõ; (e) §11 dòng 755 "KHÔNG TỒN TẠI" OK; (f) v1.3 dòng 1401 OK; (g) settings.json JSON VALID; (h) code fence balanced, 1 H1 thật — TẤT CẢ 8/8 PASS | 2026-07-12 23:08 | Ghi log kết quả pass/fail từng mục (a)-(h) — TẤT CẢ PASS |
| 5.2 | Engineering Manager approve merge nhánh `optimize` về `main` (vì refactor ảnh hưởng rộng: CLAUDE.md, GOTCHAS.md, CORE.md, RULES.md, script infrastructure, evals) | engineering-manager | ⬜ | - | - | WF-REFACTOR §4 bước 6 yêu cầu EM approve; không bỏ qua dù scope là nội bộ |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp — tránh đọc lại/nghiên cứu lại.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

### Bước 1.1-1.2 — Cài python-docx, sửa GOTCHAS G001

- Đã làm: Xác nhận `pip install python-docx Pillow` thành công, DOCX export hoạt động. Sửa G001 trong GOTCHAS.md: thay thế nội dung sai ("LibreOffice không được cài") bằng thực tế đúng — python-docx thiếu là vấn đề chính (đã fix), soffice có ở /usr/bin/soffice nhưng không convert được trong sandbox (hiện tượng đã biết, không debug thêm).
- File/module đã đọc hoặc đổi: `.claude/GOTCHAS.md` (sửa G001), `.claude/plans/PLAN-optimize-framework-2026-07-12.md` (cập nhật status)
- Quyết định quan trọng: Theo chỉ đạo user — PDF không cần thiết trên cloud/sandbox. Không điều tra thêm lỗi soffice. Dùng `--no-pdf` làm mặc định khi chạy trên cloud.
- Bước sau cần biết: Phase 2 bước 2.2 tạo code-graph nên dùng `--no-pdf` mặc định (không chờ PDF export thành công). DOCX export hoạt động bình thường sau khi python-docx đã cài. KHÔNG cần chạy `pip install` lại — đã cài rồi.

### Bước 2.1-2.2 — Tạo .claude/evals/ (3 file) và code-graph/CODE-GRAPH.md

- Đã làm: Tạo `.claude/evals/task-planner.md`, `.claude/evals/senior-developer.md`, `.claude/evals/qa-engineer.md` — mỗi file theo EVAL-template, 3 CE + 2 RE, input/expected-output cụ thể testable. Tạo `code-graph/CODE-GRAPH.md` mô tả workspace agent framework (không có src/ sản phẩm), liệt kê 31 KztekComponent WinForms controls, agent definitions, scripts. PDF export bỏ qua (--no-docx trên sandbox → cả DOCX lẫn PDF đều skip — acceptable vì task chỉ yêu cầu thử).
- File/module đã đọc hoặc đổi: `.claude/templates/EVAL-template.md` (đọc), `.claude/templates/CODE-GRAPH-template.md` (đọc), `.claude/agents/task-planner.md` / `senior-developer.md` / `qa-engineer.md` (đọc để lấy scope thật), `KztekComponent/Controls/*.cs` (Glob để liệt kê controls), `.claude/evals/*.md` (tạo mới), `code-graph/CODE-GRAPH.md` (tạo mới)
- Quyết định quan trọng: CE của task-planner tập trung 3 kịch bản lifecycle: tạo plan mới (chờ xác nhận trước khi Write), tiếp tục plan dở (không tạo lại), BLOCK khi thiếu thông tin. CE senior-developer: code+test phức tạp, review PR Junior đúng priority (correctness trước style), escalate khi vượt thẩm quyền (DB schema change). CE qa-engineer: Given/When/Then+CRUD, reproduce có evidence, từ chối khi app chưa chạy + VETO P0.
- Bước sau cần biết: Bước 2.3 là Tech Lead review — cần đọc 3 file eval vừa tạo và CODE-GRAPH.md để xác nhận (a) CE có testable không, (b) CODE-GRAPH có ghi chú trạng thái "chưa có sản phẩm" rõ ràng không, (c) không có eval nào vi phạm Two-Eyes hay nguyên tắc cứng. Commit hash bước này: `d3a06b9`.

### Bước 2.3 — Tech Lead review Phase 2

- Đã làm: Đọc `.claude/evals/task-planner.md`, `.claude/evals/senior-developer.md`, `.claude/evals/qa-engineer.md` — mỗi file đủ 3 CE + 2 RE, input/expected-output cụ thể testable (CE-01 task-planner có Glob path + format block xác nhận cụ thể; CE-01 senior-dev có artifact path + số test case tối thiểu; CE-01 qa-engineer có AC + CRUD coverage cụ thể). Đọc `code-graph/CODE-GRAPH.md` — phản ánh đúng thực tế: nêu rõ workspace không có `src/`, liệt kê đúng 31 KztekComponent controls thật + agents/skills/scripts thật, có ghi chú "sẽ điền đầy đủ khi có sản phẩm thực".
- File/module đã đọc hoặc đổi: `.claude/evals/task-planner.md`, `.claude/evals/senior-developer.md`, `.claude/evals/qa-engineer.md`, `code-graph/CODE-GRAPH.md` (read-only); `.claude/plans/PLAN-optimize-framework-2026-07-12.md` (cập nhật status 2.3)
- Quyết định quan trọng: **APPROVE Phase 2** — không có eval mơ hồ, không có sai lệch trong CODE-GRAPH. Không phát hiện vi phạm Two-Eyes hay nguyên tắc cứng nào.
- Bước sau cần biết: Phase 3 (làm rõ trạng thái docs/* trong CLAUDE.md §11) có thể bắt đầu ngay. Khi sửa CLAUDE.md §11 cần đồng bộ CORE.md nếu có mục tương đương — kiểm tra Grep "docs/prd" trước khi Edit. Không sửa bảng mapping §15.1 (không nằm trong scope Phase 3).

### Bước 3.1 — Làm rõ trạng thái docs/* trong CLAUDE.md §11

- Đã làm: Glob kiểm tra toàn bộ `docs/**` — chỉ `docs/research/` (10 file) tồn tại. `docs/user-manuals/`, `docs/prd/` và tất cả thư mục docs con khác KHÔNG tồn tại. CORE.md không có mục nào đề cập thư mục docs/ (Grep không khớp). Thêm 1 đoạn ghi chú tường minh vào CLAUDE.md §11 ngay sau khối code "Cấu trúc thư mục chuẩn", nêu rõ: đây là quy ước đặt tên, hầu hết thư mục KHÔNG TỒN TẠI, chỉ `docs/research/` có nội dung, agent phải Glob/Read kiểm tra thực tế. Xuất CLAUDE.docx thành công (389KB dạng).
- File/module đã đọc hoặc đổi: `CLAUDE.md` (Edit thêm ghi chú §11), `CLAUDE.docx` (tạo mới bởi script), `.claude/shared/CORE.md` (read-only, không sửa)
- Quyết định quan trọng: CORE.md không có section tương đương về cấu trúc thư mục — không cần sửa. Không xóa bảng cấu trúc, chỉ thêm ghi chú trạng thái thực tế.
- Bước sau cần biết: Bước 3.2 là Tech Lead review — cần đọc CLAUDE.md §11 (dòng ~771-775 sau khối code thư mục), xác nhận ghi chú mới không mâu thuẫn với §15.1 (bảng mapping tính năng → tài liệu). Ghi chú mới KHÔNG thay đổi bảng mapping, chỉ làm rõ trạng thái hiện tại. Commit hash: `fd22ba2`.

### Bước 1.3 — Tech Lead review Phase 1

- Đã làm: Đọc lại GOTCHAS.md G001 (đã đúng thực tế: python-docx là root cause, PDF optional trên cloud, `--no-pdf` mặc định). Chạy `md_to_docx_kztek.py --help` + smoke test với `docs/research/RESEARCH-harness-2026-07-12.md --no-pdf --output-dir /tmp/tl-review-test/` → DOCX 389KB tạo OK. Xác nhận plan file bước 1.1 + 1.2 đánh dấu ✅ đúng thực tế.
- File/module đã đọc hoặc đổi: `.claude/GOTCHAS.md` (read-only), `scripts/md_to_docx_kztek.py` (smoke test), `.claude/plans/PLAN-optimize-framework-2026-07-12.md` (cập nhật status 1.3)
- Quyết định quan trọng: **APPROVE Phase 1** — hạ tầng script đã sạch, GOTCHAS G001 không còn gây hiểu nhầm. Phase 2 (evals + code-graph) có thể bắt đầu ngay.
- Bước sau cần biết: Khi Phase 2 cần xuất PDF/DOCX cho code-graph → dùng `--no-pdf` (theo G001) — chỉ tạo DOCX. Nếu bước sau cần cả PDF thật, phải chạy trên máy local có LibreOffice GUI (không phải sandbox này). Không cần chạy lại `pip install`.

### Bước 4.1 — Phân tích đề xuất rút gọn CLAUDE.md

- Đã làm: Đọc toàn bộ CLAUDE.md (1438 dòng) và CORE.md. Phát hiện 10 vấn đề overhead cụ thể, sắp xếp theo impact giảm dần (P1–P10). Tổng ước tính tiết kiệm ~56 dòng (3,9%). Phân tích ghi vào `_workspace/04_sd_claude-md-analysis.md` — file này KHÔNG commit (đã gitignore _workspace/).
- File/module đã đọc hoặc đổi: `CLAUDE.md` (toàn bộ, read-only), `.claude/shared/CORE.md` (read-only), `.claude/plans/PLAN-optimize-framework-2026-07-12.md` (cập nhật status 4.1 + Handoff Log)
- Quyết định quan trọng: Không có đề xuất nào xóa nguyên tắc cứng (Two-Eyes, chain of command, QA veto, security-audit-stride WF-REVIEW-CRIT, plan file §16, code graph §17, Git Safety Protocol — đều giữ nguyên). Các đề xuất chỉ xóa prose summary trùng lặp, ví dụ quá hiển nhiên, và rút ngắn text giải thích lặp lại.
- Bước sau cần biết: Tech Lead (bước 4.2) đọc `_workspace/04_sd_claude-md-analysis.md` — file có bảng summary 10 đề xuất + chi tiết từng mục + bảng xác nhận nguyên tắc cứng. Phân loại "Nên Accept ngay" gồm P1/P3/P7/P9 (rõ ràng nhất). P2/P5/P6 cần xác nhận thêm. Bước 4.3 (Senior Developer) chỉ sửa những mục được Tech Lead Accept ở 4.2.

### Bước 4.2 — Tech Lead duyệt 10 đề xuất rút gọn CLAUDE.md

- Đã làm: Đọc `_workspace/04_sd_claude-md-analysis.md`, đối chiếu 10 vị trí trong CLAUDE.md (dòng 41, 191–200, 229–235, 315–327, 670–685, 890–905, 980–1000, 1085–1160) để tự xác nhận. Quyết định: **7 Accept (P1/P3/P4/P6/P7/P8/P9), 1 Modify (P2 — giữ bullet Bước 9 vì Bước 9 không có annotation trong dòng bước), 2 Reject (P5 — không xác nhận được SPRINT-template có đủ 6 vị trí, tránh đẩy rủi ro sang file chưa verify; P10 — annotations ∥ cung cấp thông tin bước cha cụ thể, tiết kiệm 2 dòng không đáng đánh đổi độ rõ ràng).** Ghi quyết định + hướng dẫn chi tiết cho Bước 4.3 vào `_workspace/04b_tl_claude-md-decisions.md`.
- File/module đã đọc hoặc đổi: `CLAUDE.md` (read-only, 10 vị trí), `_workspace/04_sd_claude-md-analysis.md` (đọc), `_workspace/04b_tl_claude-md-decisions.md` (tạo mới), plan file (cập nhật status 4.2 + Handoff Log)
- Quyết định quan trọng: Không có đề xuất nào vi phạm nguyên tắc cứng (Two-Eyes, chain of command, QA veto, security-audit-stride WF-REVIEW-CRIT, Plan file §16, Code Graph §17). P2 sửa thành Modify vì Bước 9 (Junior Dev skip) không có annotation trong dòng bước — nếu Accept nguyên bản sẽ mất thông tin. P5/P10 Reject theo nguyên tắc "không đánh đổi rõ ràng lấy độ ngắn".
- Bước sau cần biết: Bước 4.3 (Senior Developer) PHẢI đọc `_workspace/04b_tl_claude-md-decisions.md` — file có checklist 10 mục hướng dẫn CHÍNH XÁC làm gì với từng đề xuất. **TUYỆT ĐỐI KHÔNG áp dụng P5 và P10 (Reject).** P2 chỉ xóa 3 bullets, giữ bullet Bước 9. Ước tính sau chỉnh sửa: ~44 dòng tiết kiệm. Sau khi áp dụng, cập nhật §21 Changelog (v1.3), đồng bộ CORE.md/RULES.md nếu có mục liên quan, xuất `CLAUDE.docx` bằng `--no-pdf`.

### Bước 3.2 — Tech Lead review Phase 3

- Đã làm: Đọc CLAUDE.md dòng 755-775 (§11 khối "Cấu trúc thư mục chuẩn" + ghi chú mới thêm ngay sau ```). Xác nhận ghi chú (a) rõ ràng nêu đây là QUY ƯỚC đặt tên, (b) liệt kê đúng các thư mục chưa tồn tại, (c) chỉ `docs/research/` có nội dung — khớp thực tế Glob của bước 3.1, (d) yêu cầu agent Glob/Read trước khi giả định. Không phủ định bảng "Bảng tổng hợp artifact bắt buộc theo workflow" (§11 dòng 779+) — workflow tương lai vẫn tạo thư mục khi cần. Không mâu thuẫn §15.1 (mapping tính năng → tài liệu vẫn nguyên). CLAUDE.docx timestamp 22:23 khớp CLAUDE.md → đồng bộ.
- File/module đã đọc hoặc đổi: `CLAUDE.md` §11 (read-only), `CLAUDE.docx` (kiểm tra timestamp), `.claude/plans/PLAN-optimize-framework-2026-07-12.md` (cập nhật status 3.2 + Handoff Log)
- Quyết định quan trọng: **APPROVE Phase 3** — ghi chú làm rõ trạng thái hiện tại, không xóa/phủ định quy ước cấu trúc chuẩn. Phase 4 có thể bắt đầu.
- Bước sau cần biết: Phase 4 bước 4.1 (Senior Developer) chỉ PHÂN TÍCH CLAUDE.md và đề xuất rút gọn vào `_workspace/04_sd_claude-md-analysis.md` — KHÔNG tự sửa CLAUDE.md ở bước này. Tech Lead sẽ review từng đề xuất ở bước 4.2 (Accept/Reject/Modify) trước khi bước 4.3 áp dụng. Nguyên tắc cứng phải giữ: Two-Eyes (§8), chain of command (§1), QA veto, chain nhảy cấp cấm (§1).

### Bước 4.4 — Tech Lead review cuối Phase 4

- Đã làm: Đọc `_workspace/04b_tl_claude-md-decisions.md` (checklist gốc 7 Accept + 1 Modify + 2 Reject). Xem diff commit `e43e7b2` — xác nhận từng thay đổi khớp đúng quyết định 4.2: P8 (§0 blockquote rút gọn), P4 (xóa code block fan-out §4 P7, giữ text + ref WORKFLOW.md Ví dụ 9), P2 Modify (xóa 3 bullets Bước 5/10a/10b, GIỮ Bước 9), P3 (xóa "Ví dụ hành động nhỏ hợp lệ" §9a), P1 (xóa toàn bộ §13.2), P6 (§16.5 Bước 2b WEB rút về 2 điểm khác biệt), P9 (xóa blockquote Handoff Log §16.5 Bước 4), P7 (gộp "KHÔNG gợi ý compact" thành 1 câu). Không phát hiện P5/P10 bị áp dụng nhầm. §21 Changelog có entry v1.3 đúng format bảng 5 cột, mô tả rõ đối tượng và lý do. CLAUDE.md 1404 dòng, cấu trúc heading/bảng/code block nguyên vẹn, không có đoạn cắt dở.
- File/module đã đọc hoặc đổi: `_workspace/04b_tl_claude-md-decisions.md` (đọc), `CLAUDE.md` (đọc §21 + tổng thể), `git show e43e7b2` (xem diff), `.claude/plans/PLAN-optimize-framework-2026-07-12.md` (cập nhật status 4.4 + Handoff Log)
- Quyết định quan trọng: **APPROVE Phase 4** — refactor CLAUDE.md hoàn tất, không có nguyên tắc cứng nào bị ảnh hưởng, không có regression cấu trúc.
- Bước sau cần biết: Phase 5 là 2 bước CUỐI của toàn bộ plan. Bước 5.1 QA Engineer smoke test 6 mục: (a) chạy `md_to_docx_kztek.py` với ≥2 file `.md` bất kỳ — có thể dùng `--no-pdf` (theo G001, PDF không cần trên cloud); (b) đọc GOTCHAS.md G001 xác nhận nội dung đúng thực tế python-docx; (c) `.claude/evals/` đủ 3 file (task-planner, senior-developer, qa-engineer); (d) `code-graph/CODE-GRAPH.md` có ghi chú "chưa có codebase sản phẩm"; (e) CLAUDE.md §11 có ghi chú trạng thái docs/*/; (f) CLAUDE.md §21 có entry v1.3. Ghi log pass/fail từng mục. Bước 5.2 Engineering Manager approve merge nhánh `optimize` → `main` (WF-REFACTOR §4 bước 6 yêu cầu).

### Bước 4.3 — Áp dụng rút gọn CLAUDE.md (đã được duyệt ở 4.2)

- Đã làm: Đọc `_workspace/04b_tl_claude-md-decisions.md` để lấy checklist chính xác. Áp dụng 7 Accept + 1 Modify (P2 — chỉ xóa 3 bullets "Điều kiện bỏ qua" Bước 5/10a/10b trong WF-FEATURE, giữ bullet Bước 9 vì không có annotation tương đương). Xóa §13.2 trùng lặp (P1), xóa code block pseudocode fan-out §4 P7 (P4), gộp 3 bullets "KHÔNG gợi ý compact" (P7), xóa "Ví dụ hành động nhỏ hợp lệ" §9a (P3), rút gọn Bước 2b WEB §16.5 (P6), xóa blockquote lý do Handoff Log §16.5 (P9), rút gọn blockquote trade-off Dispatcher §0 (P8). Thêm entry v1.3 vào §21 Changelog. Xuất `CLAUDE.docx` bằng `--no-pdf` (theo G001 — PDF không cần trên cloud). KHÔNG áp dụng P5 (danh sách vị trí SPRINT-*.md) và P10 (ký hiệu ∥) — đúng như Tech Lead Reject ở bước 4.2. Kiểm tra CORE.md/RULES.md bằng Grep — không có mục tương đương cần đồng bộ.
- File/module đã đọc hoặc đổi: `CLAUDE.md` (Edit 8 vị trí), `CLAUDE.docx` (xuất lại), `_workspace/04b_tl_claude-md-decisions.md` (đọc), `.claude/shared/CORE.md` + `RULES.md` (Grep kiểm tra, không sửa)
- Quyết định quan trọng: Số dòng giảm từ 1437 → 1403 (34 dòng, khớp ước tính ~44 dòng của Tech Lead — chênh lệch nhỏ do cách đếm dòng trống). Không có nguyên tắc cứng nào bị ảnh hưởng (Two-Eyes, chain of command, QA veto, security-audit-stride, Plan §16, Code Graph §17 đều nguyên vẹn).
- Bước sau cần biết: Bước 4.4 (Tech Lead review cuối) cần đọc lại CLAUDE.md ở các vị trí đã sửa (dùng commit `e43e7b2` để xem diff) để xác nhận không mâu thuẫn, và xác nhận §21 Changelog có entry v1.3 đúng format. Sau đó Phase 5 (QA smoke test + EM approve merge) là bước cuối cùng của toàn bộ plan.

### Bước 5.1 — QA Engineer smoke test toàn bộ thay đổi

- Đã làm: Test 8 mục (a)-(h): (a) chạy `md_to_docx_kztek.py` với `docs/research/RESEARCH-harness-2026-07-12.md` và `CLAUDE.md` (`--no-pdf`) — cả 2 DOCX tạo thành công (389KB, 421KB); (b) đọc GOTCHAS.md G001 — đúng thực tế (python-docx là root cause đã fix, PDF optional trên cloud); (c) `.claude/evals/` có đủ 3 file, mỗi file ≥3 CE; (d) `code-graph/CODE-GRAPH.md` có ghi chú rõ "chưa có codebase sản phẩm"; (e) CLAUDE.md §11 dòng 755 có ghi chú "KHÔNG TỒN TẠI" đúng; (f) CLAUDE.md §21 dòng 1401 có entry v1.3; (g) `.claude/settings.json` vẫn là JSON hợp lệ sau khi thêm Edit/Write; (h) code fence cân bằng, chỉ 1 H1 thật (9 dòng bắt đầu bằng "# " nhưng 8 dòng nằm trong code block minh họa, không phải heading thật). **KẾT QUẢ: 8/8 PASS.**
- File/module đã đọc hoặc đổi: `scripts/md_to_docx_kztek.py` (chạy test), `.claude/GOTCHAS.md`, `.claude/evals/*.md`, `code-graph/CODE-GRAPH.md`, `CLAUDE.md`, `.claude/settings.json` (đều read-only/test), `.claude/plans/PLAN-optimize-framework-2026-07-12.md` (cập nhật status 5.1)
- Quyết định quan trọng: Không phát hiện regression nào từ toàn bộ Phase 1-4. Framework sẵn sàng để merge.
- Bước sau cần biết: Bước 5.2 (Engineering Manager) là bước CUỐI CÙNG của plan — approve merge nhánh `optimize` → `main`. Toàn bộ artifact đã pass smoke test, không có blocker nào tồn đọng.

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
| 2026-07-12 22:10 | Bước 1.1 Done, Bước 1.2 Done — python-docx xác nhận hoạt động, G001 sửa đúng thực tế, PDF không cần trên cloud | Senior Developer |
| 2026-07-12 22:18 | Bước 2.1 Done (3 eval files), Bước 2.2 Done (CODE-GRAPH.md) — commit d3a06b9 | Senior Developer |
| 2026-07-12 22:20 | Bước 2.3 Done — Tech Lead APPROVE Phase 2 (evals đủ CE testable, CODE-GRAPH đúng thực tế) | Tech Lead |
| 2026-07-12 22:23 | Bước 3.1 Done — CLAUDE.md §11 ghi chú thêm trạng thái docs/*, CORE.md không cần sửa, DOCX export OK, commit fd22ba2 | Senior Developer |
| 2026-07-12 22:25 | Bước 3.2 Done — Tech Lead APPROVE Phase 3 (ghi chú không mâu thuẫn §11/§15.1, CLAUDE.docx đồng bộ) | Tech Lead |
| 2026-07-12 22:32 | Bước 4.1 Done — Phân tích 10 đề xuất P1-P10, ~56 dòng tiết kiệm, file `_workspace/04_sd_claude-md-analysis.md` (không commit) | Senior Developer |
| 2026-07-12 22:41 | Bước 4.2 Done — Tech Lead duyệt: 7 Accept, 1 Modify (P2), 2 Reject (P5, P10); ~44 dòng tiết kiệm sau điều chỉnh | Tech Lead |
| 2026-07-12 22:49 | Bước 4.3 Done — Áp dụng rút gọn CLAUDE.md (1437→1403 dòng), §21 Changelog v1.3, CLAUDE.docx đồng bộ, commit e43e7b2 | Senior Developer |
| 2026-07-12 23:06 | Bước 4.4 Done — Tech Lead APPROVE review cuối Phase 4: diff khớp quyết định 4.2, không nhầm P5/P10, §21 v1.3 đúng format, cấu trúc CLAUDE.md mạch lạc | Tech Lead |
| 2026-07-12 23:08 | Bước 5.1 Done — QA smoke test 8/8 PASS (script DOCX, GOTCHAS G001, evals, code-graph, CLAUDE.md §11/§21, settings.json, Markdown structure) | QA Engineer |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
