---
name: scope-check
description: "PHẢI dùng khi: yêu cầu user có thể map vào ≥2 workflow khác nhau, mô tả chỉ 1-2 câu không rõ priority, scope ảnh hưởng không rõ bao nhiêu module, hoặc chưa biết có cần CTO/EM duyệt kiến trúc không. Dùng ngay cả khi user tưởng đã rõ — 3 câu hỏi đúng lúc tiết kiệm 3 vòng sửa sau. Hỏi tối đa 5 câu để chốt scope, P0-P3 và workflow áp dụng TRƯỚC khi tạo Plan file. KHÔNG dùng khi: yêu cầu đã rõ workflow + priority (VD: SEV1 production down → thẳng WF-INCIDENT) hoặc user đã cung cấp đủ AC/constraint rõ ràng."
---

# Scope Check (Chốt phạm vi nhanh)

## Khi nào dùng
- Yêu cầu user có thể map vào ≥ 2 workflow khác nhau (VD: vừa giống bug vừa giống feature nhỏ).
- Không rõ mức độ ưu tiên (P0-P3) hoặc không rõ có cần CTO/EM duyệt kiến trúc không.
- Task có vẻ lớn nhưng user mô tả bằng 1-2 câu, chưa có AC/constraint rõ.

**KHÔNG dùng khi:** yêu cầu đã rõ ràng workflow + priority (VD: "SEV1 production down" → thẳng WF-INCIDENT, không cần hỏi lại).

## Quy trình bắt buộc

1. Hỏi user trực tiếp (KHÔNG tự đoán) các câu sau — chỉ hỏi câu còn thiếu thông tin, tối đa 5 câu:
   - **Mục tiêu cuối:** Kết quả mong đợi là gì (feature hoạt động, bug hết, tài liệu, quyết định kiến trúc...)?
   - **Phạm vi:** Chỉ 1 module/màn hình, hay ảnh hưởng nhiều phần?
   - **Mức ưu tiên:** P0 (chặn release) / P1 (quan trọng) / P2 (bình thường) / P3 (nhỏ)?
   - **Rủi ro:** Có đụng auth/payment/DB schema/kiến trúc lớn không?
   - **Ràng buộc thời gian:** Có deadline cụ thể không?
2. Từ câu trả lời, xác định **Workflow ID** phù hợp theo bảng routing CLAUDE.md §2.
3. Chuyển kết quả (workflow + priority + scope tóm tắt) làm input cho Bước Pre-0 (`task-planner`) — KHÔNG tự tạo Plan file ở bước này, chỉ chốt scope.

## Output bắt buộc
Một khối tóm tắt ngắn:
```
Scope đã chốt:
- Mục tiêu       : ...
- Phạm vi         : ...
- Priority        : P[0-3]
- Rủi ro kiến trúc: [Có/Không] — [chi tiết nếu có]
- Workflow đề xuất: WF-XXX
```

## Verification (done gate)
- [ ] Đã hỏi đủ các câu còn thiếu thông tin (không tự đoán thay user).
- [ ] Workflow đề xuất khớp với bảng routing CLAUDE.md §2.
- [ ] Priority đã chốt rõ P0-P3, không để mơ hồ.
- [ ] Kết quả đã chuyển giao đúng format cho Bước Pre-0 (`task-planner`).

## Red Flags (lý do hay bỏ qua scope-check — dừng lại nhìn nhận khi thấy)

| Thought | Reality |
|---------|---------|
| "Yêu cầu đã rõ rồi, không cần scope check" | Bỏ scope check là lý do phổ biến nhất dẫn đến plan sai workflow, tốn công làm lại từ đầu. |
| "Cứ làm đi, chốt scope sau nếu cần" | Chốt sau khi đã implement nghĩa là trả chi phí sửa cao hơn 5–10 lần so với hỏi trước. |
| "User nói là WF-BUGFIX rồi" | User mô tả triệu chứng, không phải root cause. Triage vẫn cần để phân biệt bug thật với feature request hay config issue. |
| "Hỏi thêm sẽ làm phiền user" | 3 câu hỏi đúng lúc tiết kiệm 3 vòng sửa sau. User muốn kết quả đúng, không phải nhanh mà sai workflow. |
