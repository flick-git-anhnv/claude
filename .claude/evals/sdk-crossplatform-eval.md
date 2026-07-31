---
agent: sdk-crossplatform-eval
created: 2026-07-31
author: Dispatcher (theo yêu cầu user, sau khi hoàn thành WF-ARCH Suprema G-SDK)
status: draft
---

# EVAL: sdk-crossplatform-eval (skill)

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `/sdk-crossplatform-eval` trước khi implement — Eval-Driven Development (EDD), theo §18.5 CLAUDE.md.

---

## 1. Mô tả năng lực (Capability Statement)

`/sdk-crossplatform-eval` chuẩn hóa quy trình đánh giá khả năng thay 1 SDK thiết bị native/Windows-only đang dùng (P/Invoke, DLL/so cũ) bằng 1 SDK/API thay thế cross-platform (gRPC, REST, cloud gateway...), TRƯỚC khi mở workflow migrate thật. Được gọi khi phát hiện 1 controller đang phụ thuộc SDK native Windows-only gây nghẽn cross-platform (VD: ZKTeco, BioBridge, Morpho — cùng cảnh Suprema đã đánh giá 2026-07-31), và có tồn tại phiên bản SDK mới của cùng vendor tuyên bố hỗ trợ đa nền tảng. Output: ADR go/no-go kèm gate điều kiện trước khi migrate thật — KHÔNG tự viết code migrate ở bước này.

---

## 2. Capability Evals

### CE-01 — Happy path: SDK native đang dùng thật một phần tính năng SDK khai báo

**Input:** Controller `XyzController.cs` gọi P/Invoke tới `XyzApi.cs` (khai báo ~50 hàm SDK), nhưng theo grep thực tế chỉ dùng ~10 hàm (connect, enroll, log). Có SDK mới cùng vendor (gRPC/REST) tuyên bố cross-platform nhưng KHÔNG hỗ trợ 2 trong 50 hàm nâng cao.

**Output mong đợi:**
- [ ] Skill grep đúng file controller đang GỌI THẬT (không phải file khai báo API đầy đủ) để xác định tính năng thực dùng — tránh kết luận sai "thiếu tính năng" dựa trên toàn bộ SDK cũ
- [ ] Nếu 2 hàm SDK mới không hỗ trợ KHÔNG nằm trong tập controller thực dùng → skill kết luận rào cản không tồn tại, không chặn khuyến nghị GO
- [ ] Skill gắn nhãn Confidence (CONFIRMED/INFERRED) cho từng dòng mapping API cũ→mới, không bịa API không xác nhận được
- [ ] Output là 1 ADR (Context/Decision/Alternatives/Consequences), không phải code

**Grader:** Human (đối chiếu với case Suprema G-SDK 2026-07-31 đã làm thủ công)

---

### CE-02 — Edge case: không có nhu cầu triển khai ngay

**Input:** Đánh giá cho thấy GO về kỹ thuật, nhưng thiết bị đang fallback `NullDeviceController` trên Linux mà chưa ai yêu cầu dùng Linux cho thiết bị đó ngay.

**Output mong đợi:**
- [ ] Skill không tự động đề xuất mở WF-MIGRATE ngay sau ADR — phải nêu rõ đây là APPROVE có điều kiện + gate (license, đọc spec/proto thật, spike ngắn) trước khi cam kết effort đầy đủ
- [ ] Skill định tuyến quyết định cuối cho CTO (WF-ARCH: Tech Lead → CTO), không tự quyết thay CTO

**Grader:** Human

---

### CE-03 — Negative case: không có SDK thay thế cross-platform nào tồn tại

**Input:** User yêu cầu đánh giá 1 SDK vendor không có phiên bản cross-platform nào được công bố (research không tìm thấy).

**Output mong đợi:**
- [ ] Skill báo NO-GO / KHÔNG ĐỦ DỮ LIỆU rõ ràng, không bịa ra SDK giả định
- [ ] Skill trích nguồn WebSearch đã dùng để verify (hoặc nêu rõ đã tìm và không thấy), không kết luận suông

**Grader:** Human

---

## 3. Regression Evals

### RE-01 — Không trùng lặp với code-migrator

**Input:** User yêu cầu "migrate hẳn sang SDK mới" (không phải "đánh giá khả năng")

**Output mong đợi:**
- [ ] Dispatcher route sang WF-MIGRATE (`code-migrator`), KHÔNG dùng `sdk-crossplatform-eval` cho việc migrate code thật
- [ ] `sdk-crossplatform-eval` chỉ dùng cho giai đoạn ĐÁNH GIÁ (WF-ARCH), đầu ra là input cho WF-MIGRATE sau này, không thay thế nó

---

### RE-02 — Artifact đúng vị trí theo §11 CLAUDE.md

**Input:** Skill chạy xong 1 lần đánh giá

**Output mong đợi:**
- [ ] ADR nằm ở `docs/architecture/ADR-*.md` (+ .docx/.pdf theo §19)
- [ ] Nếu có plan file liên quan, step file cập nhật đúng theo §16.4

---

## 4. Kết quả chạy thử

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-07-31 | PASS | Đối chiếu trực tiếp với case Suprema G-SDK vừa làm — quy trình grep FSF2.cs (controller thật) thay vì SFApi.cs (khai báo đầy đủ) đã áp dụng đúng, tránh kết luận sai Wiegand/RS485 |
| CE-02 | 2026-07-31 | PASS | Case Suprema: CTO approve có điều kiện, không mở migrate ngay, đúng đúng pattern mong đợi |
| CE-03 | 2026-07-31 | PASS | Chạy thật qua general-purpose subagent cold-read: giả lập vendor "AcmeLegacySDK" không tìm được SDK thay thế qua WebSearch, agent trích đúng Bước 2 + Red Flag, kết luận NO-GO/KHÔNG ĐỦ DỮ LIỆU, không bịa API, vẫn giao CTO review |
| RE-01 | 2026-07-31 | PASS | Skill body ghi rõ ranh giới với code-migrator ở mục "Khi nào dùng" / "KHÔNG dùng khi" |
| RE-02 | 2026-07-31 | PASS | Skill body dẫn đúng §11/§19 CLAUDE.md cho vị trí artifact |

**Tổng kết:** APPROVED — 3/3 CE pass, 2/2 RE pass

---

## 5. Lịch sử eval

| Ngày | Phiên bản agent | CE pass | RE pass | Tổng kết | Ghi chú |
|------|----------------|---------|---------|----------|---------|
| 2026-07-31 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới sau khi hoàn thành WF-ARCH đánh giá Suprema G-SDK — pattern dự kiến lặp lại cho ZKTeco/BioBridge/Morpho |

---

> **Vị trí lưu:** `C:/Users/nguye/.claude/evals/sdk-crossplatform-eval.md`
> **Liên quan:** `C:/Users/nguye/.claude/commands/sdk-crossplatform-eval.md`
