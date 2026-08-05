---
name: sdk-crossplatform-eval
description: "PHẢI dùng khi cần đánh giá khả năng thay 1 SDK thiết bị native/Windows-only đang dùng (P/Invoke, DLL/.so cũ) bằng phiên bản SDK/API thay thế cross-platform (gRPC/REST/cloud gateway) TRƯỚC khi mở workflow migrate thật — phạm vi CHỈ 1 SDK/thiết bị đơn lẻ (VD: ZKTeco, BioBridge, Morpho đang native Windows-only giống Suprema, đã đánh giá 2026-07-31, xem docs/architecture/ADR-suprema-gsdk-eval.md làm mẫu). Output là ADR go/no-go, KHÔNG viết code migrate. KHÔNG dùng khi: user yêu cầu migrate code thật ngay (→ code-migrator/WF-MIGRATE); SDK hiện tại đã cross-platform sẵn (không có vấn đề gì để đánh giá); hoặc yêu cầu là migrate TOÀN BỘ UI/framework/codebase (dù có nhắc tên SDK thiết bị bên trong câu) — phạm vi đó vẫn thuộc code-migrator/WF-MIGRATE, KHÔNG phải đánh giá 1 SDK đơn lẻ."
disable-model-invocation: true
---

# SDK Cross-platform Eval (Đánh giá thay SDK native bằng bản cross-platform)

## Khi nào dùng
- Phát hiện 1 controller/module đang phụ thuộc SDK thiết bị **native, Windows-only** (P/Invoke `[DllImport]` tới `.dll`, hoặc thư viện `.so` chỉ build cho 1 nền tảng), và việc này đang chặn cross-platform (VD: app phải fallback `NullDeviceController`/stub trên Linux vì SDK không load được).
- Có tồn tại (hoặc user/Dispatcher nghi ngờ có) 1 phiên bản SDK MỚI của cùng vendor tuyên bố hỗ trợ đa nền tảng (gRPC/REST/cloud gateway...).
- User hoặc workflow đang ở giai đoạn **ĐÁNH GIÁ** (WF-ARCH), chưa quyết định migrate.

**KHÔNG dùng khi:**
- User đã quyết định migrate thật, muốn viết code ngay → dùng `code-migrator` (WF-MIGRATE).
- SDK hiện tại đã cross-platform, không có vấn đề kiến trúc cần đánh giá.

## Quy trình bắt buộc (5 bước)

1. **Xác định tính năng THỰC DÙNG** — grep/đọc đúng file controller đang gọi SDK (VD: `FSF2.cs`), KHÔNG dựa vào file khai báo API đầy đủ (VD: `SFApi.cs` có hàng trăm `[DllImport]` nhưng phần lớn không được gọi). Kết luận "SDK mới thiếu tính năng X" chỉ hợp lệ nếu X thực sự được controller gọi.
2. **WebSearch + verify SDK thay thế** — tìm tài liệu chính thức của vendor về SDK/API mới, xác nhận: hỗ trợ đúng model thiết bị đang dùng, hỗ trợ OS đích (Linux/ARM...), hạn chế tính năng (nếu có). Luôn trích nguồn (Sources). Nếu không tìm thấy SDK thay thế nào → kết luận NO-GO/KHÔNG ĐỦ DỮ LIỆU, không bịa.
3. **Lập bảng mapping API cũ → mới** — mỗi hàm SDK cũ đang dùng thật (từ Bước 1) đối chiếu hàm tương đương ở SDK mới, gắn nhãn Confidence `CONFIRMED` (đã đọc spec/proto chi tiết) hoặc `INFERRED` (suy luận từ tài liệu tổng quan, chưa đọc chi tiết).
4. **Ước lượng effort (S/M/L)** + đánh giá kiến trúc phụ trợ (VD: cần thêm gateway/service chạy ở đâu, ảnh hưởng gì đến tầng IPC/DeviceHost hiện có).
5. **Viết ADR go/no-go** tại `docs/architecture/ADR-[slug]-eval.md` (Context/Decision/Alternatives/Consequences), rồi giao **CTO review** (WF-ARCH: Tech Lead → CTO) — Tech Lead KHÔNG tự quyết GO cuối cùng. Nếu quyết định APPROVE có điều kiện, PHẢI nêu rõ gate (license, đọc spec/proto CONFIRMED, spike thử nghiệm ngắn) trước khi mở WF-MIGRATE thật.

## Output bắt buộc
```
docs/architecture/ADR-[slug]-eval.md (+ .docx/.pdf theo §19 CLAUDE.md)
```
Nếu chạy trong 1 plan có sẵn (`docs/plans/PLAN-*/`) → cập nhật step file + PLAN-MASTER theo §16.4.

## Verification (done gate)
- [ ] Mapping tính năng dựa trên file controller GỌI THẬT, không dựa trên file khai báo API đầy đủ.
- [ ] Mọi khẳng định về SDK mới có nguồn WebSearch trích dẫn, không bịa API.
- [ ] Confidence label CONFIRMED/INFERRED gắn cho từng dòng mapping.
- [ ] Quyết định cuối do CTO duyệt (WF-ARCH đầy đủ), không tự quyết ở cấp Tech Lead.
- [ ] Nếu APPROVE có điều kiện → gate cụ thể được ghi rõ, không mở WF-MIGRATE ngay khi chưa qua gate.

## Red Flags (lý do hay bỏ qua đúng bước — dừng lại khi thấy)

| Thought | Reality |
|---------|---------|
| "File API khai báo có hàm X, nên chắc đang dùng X" | File khai báo P/Invoke thường có SẴN toàn bộ SDK dù controller chỉ gọi 1 phần nhỏ — phải grep đúng file controller thực gọi, như case Suprema (SFApi.cs khai báo Wiegand/RS485 nhưng FSF2.cs không gọi). |
| "SDK mới nghe có vẻ tốt hơn, cứ đề xuất GO luôn" | GO kỹ thuật không đồng nghĩa nên làm ngay — phải kiểm tra có nhu cầu thật (ai đang cần) trước khi tốn effort, và luôn qua CTO duyệt gate. |
| "Không tìm thấy tài liệu chi tiết, thôi cứ giả định API tương đương" | Đây là bịa đặt — phải gắn nhãn INFERRED và yêu cầu bước sau (đọc spec/proto thật) trước khi cam kết effort đầy đủ. |
| "Đánh giá xong rồi, migrate luôn cho nhanh" | Đây là 2 workflow khác nhau (WF-ARCH đánh giá vs WF-MIGRATE thực thi) — ADR chỉ là input, không tự động mở migrate. |
