---
description: "PHẢI dùng khi cần thực thi 1 bước (STEP-N.M) trong plan docs/plans/PLAN-*/ qua subagent theo session isolation §16.5 — trigger: 'chạy bước tiếp theo', 'tiếp tục plan', 'làm STEP-3.2', hoặc Dispatcher đến lượt thực thi 1 bước ⬜/🔄 trong plan đã duyệt. Skill tự đọc Handoff Log bước liền trước, phát hiện bước làm dở, dựng prompt chuẩn và verify artifact sau khi xong. KHÔNG dùng khi: chưa có plan được duyệt (→ task-planner), plan chỉ có 1 bước duy nhất, bước hiện tại là câu hỏi/xác nhận với user, hoặc user yêu cầu rõ chạy toàn bộ trong 1 session (các ngoại lệ §16.5)."
disable-model-invocation: true
---

# Skill: run-plan-step — Thực thi 1 bước plan qua subagent (§16.5)

> Chuẩn hóa khuôn prompt mà Dispatcher phải soạn tay lặp lại cho mỗi bước plan.
> Nguồn gốc: workflow tool-improvements 2026-07-26 (7.LinuxDeployTool) — 10+ prompt cùng khuôn, và sự cố STEP-5.2 làm dở suýt bị làm lại từ đầu.

## Quy trình

### 1. Xác định bước cần chạy
- Đọc `PLAN-MASTER.md` của plan (user chỉ định, hoặc plan in-progress duy nhất trong `docs/plans/`). Có ≥2 plan in-progress mà user không chỉ định → hỏi user bằng AskUserQuestion, không tự đoán.
- Bước mục tiêu = bước user chỉ định, hoặc bước ⬜/🔄 ĐẦU TIÊN theo thứ tự bảng Phases & Steps. User yêu cầu chạy lại bước đã ✅ → được phép, nhưng xác nhận lại với user trước (sẽ ghi đè Handoff Log/kết quả cũ).
- Bước 🛑 Blocked → DỪNG, hiển thị BLOCK format, không nhảy qua bước sau.
- Ghi nhận: số bước (N.M), tên, agent phụ trách (cột Agent), đường dẫn step file.

### 2. Kiểm tra ngoại lệ §16.5 (nếu dính → KHÔNG spawn subagent)
- Plan chỉ có 1 bước duy nhất → chạy trực tiếp trong session chính.
- Bước là câu hỏi/xác nhận với user (VD "User duyệt plan") → hỏi user, chờ trả lời.
- User đã yêu cầu rõ chạy toàn bộ trong 1 session → làm trực tiếp.
- Chưa có plan nào khớp → BLOCK, trỏ về `task-planner`. KHÔNG tự tạo plan.

### 3. Thu thập context
- Đọc step file của bước mục tiêu (nhiệm vụ, Definition of Done).
- Grep `## Handoff Log` trong step file của bước LIỀN TRƯỚC (chỉ bước liền trước — R11) → copy NGUYÊN VĂN. Bước đầu tiên → ghi "Không có Handoff Log".
- Chạy `git status --short` + `git log --oneline -1`. Nếu working tree có file code untracked/modified KHỚP phạm vi bước mục tiêu (đối chiếu theo danh sách file/module nêu trong step file hoặc mục Artifact) → đánh dấu **bước làm dở**.
- Kiểm tra khả năng push: đã biết từ memory/lần push fail trước, hoặc chạy `git push --dry-run` — fail vì credential → prompt ghi "KHÔNG git push".
- Lệnh build/test: lấy từ step file/PLAN-MASTER nếu có ghi; không có → dò từ project (solution/csproj/package.json) và ghi tường minh vào prompt.

### 4. Dựng prompt theo khuôn 8 phần (BẮT BUỘC đủ, không rút gọn)
```
1. Vai trò + bước:      "Bạn là [Agent] thực hiện STEP-N.M của plan <folder> trong repo <path>
                         (<mô tả 1 dòng project, solution file>)."
2. Handoff Log:         "**Handoff Log từ STEP liền trước (bối cảnh đã biết, KHÔNG nghiên cứu lại):**
                         <nguyên văn>"
3. Nhiệm vụ:            Chi tiết từ step file — đủ để subagent KHÔNG cần đọc lại lịch sử session.
4. Giới hạn scope:      "Đúng scope — KHÔNG làm [các mục thuộc bước sau, liệt kê ID]."
5. Gate build/test:     "Build sạch `<lệnh build>` + `<lệnh test>` — tất cả pass mới được coi là xong."
6. Cập nhật plan:       "Cập nhật step file (Đã làm, artifact, Handoff Log 4 dòng, status: done,
                         completed_at lấy giờ thật `Get-Date -Format "yyyy-MM-dd HH:mm"`);
                         cập nhật PLAN-MASTER (1 dòng status → ✅, updated:, +1 dòng Lịch sử);
                         chạy script md_to_docx cho MASTER (R1). Cập nhật CODE-GRAPH nếu đổi public API (R3); nếu thay đổi chỉ là logic nội bộ
                         không đổi interface, thêm dòng `no-codegraph: <lý do ngắn>` vào commit message
                         (§17.6 CLAUDE.md) thay vì cập nhật CODE-GRAPH."
7. Commit:              Format cố định:
                         [<plan-slug>] Bước N.M: <mô tả ngắn>
                         - <chi tiết>
                         Plan: <đường dẫn step file>
                         Co-Authored-By: Claude <model> <noreply@anthropic.com>
                         + "KHÔNG push" nếu không có credential.
                         Push: thử `git push` ĐÚNG 1 LẦN, giới hạn thời gian chờ ~15-20 giây
                         (`timeout 15 git push` trên Bash hoặc tương đương). Treo/timeout/lỗi credential
                         → KHÔNG retry, ghi nhận "đã commit local, push thất bại — cần xác thực/push
                         thủ công" và tiếp tục bước kế tiếp — KHÔNG để việc push chặn tiến độ.
8. Yêu cầu trả về:      "Trả về tóm tắt ≤5 dòng: đã làm gì, quyết định, build/test, commit hash."
```
**Nếu bước làm dở** → chèn thêm TRƯỚC phần Nhiệm vụ: "**QUAN TRỌNG — bước này ĐANG LÀM DỞ.** Working tree có: <danh sách file>. Nhiệm vụ đầu tiên: `git diff` từng file để hiểu phần đã làm, rồi HOÀN TẤT phần thiếu — KHÔNG làm lại từ đầu, KHÔNG vứt code dở trừ khi sai."

### 5. Gọi subagent
- `Agent` tool, `run_in_background: false`, `subagent_type` = tên cột Agent chuyển kebab-case ("Senior Developer" → `senior-developer`, "DevOps Engineer" → `devops-engineer`...; riêng "UX/UI Reviewer" → `ux-ui-reviewer`). Tên không có trong danh sách agent khả dụng → BLOCK hỏi user, không đoán agent thay thế.
- Commit `Co-Authored-By`: dùng model của session chính (dòng chuẩn harness đang cung cấp).
- Hiển thị header agent theo format §5 CORE.md trước khi gọi.

### 6. Verify sau khi subagent xong (không tin tóm tắt suông)
- Step file: frontmatter `status: done` + `completed_at` đã điền, mục Handoff Log không rỗng.
- PLAN-MASTER: dòng bước đó đã ✅ + giờ hoàn thành.
- `git log --oneline -1` có commit mới đúng format `[slug] Bước N.M:`.
- Thiếu bất kỳ mục nào → SendMessage cho subagent yêu cầu bổ sung (hoặc tự Edit phần .md nhỏ nếu subagent đã kết thúc), rồi verify lại. CHỈ báo hoàn thành khi đủ.

### 7. Báo cáo
- Hiển thị khối ✅ HOÀN THÀNH (format §5 CORE.md) với commit hash + artifact — tóm tắt ngắn, KHÔNG dán nguyên log subagent.

## Verification (done gate)
- [ ] Prompt gửi subagent đủ 8 phần khuôn (đối chiếu từng phần trước khi gọi)
- [ ] Handoff Log bước liền trước được nhúng NGUYÊN VĂN (hoặc ghi rõ "bước đầu tiên")
- [ ] Bước làm dở (nếu có) được phát hiện qua git status và chỉ thị audit-diff có trong prompt
- [ ] Sau khi xong: step file done + MASTER ✅ + commit đúng format đã verify bằng Read/Grep/git log
- [ ] Không spawn subagent cho case thuộc ngoại lệ §16.5

## Red Flags (lý do hay bỏ qua — dừng lại khi thấy)
| Thought | Reality |
|---------|---------|
| "Bước này nhỏ, soạn prompt tay nhanh hơn" | Prompt tay là nguồn gốc lỗi quên Handoff Log/quên MASTER — bước nhỏ càng dễ ẩu. Khuôn 8 phần tồn tại vì đã quên thật. |
| "Subagent báo xong rồi, verify làm gì" | STEP làm dở + MASTER lệch đã xảy ra thật (STEP-5.2, 2026-07-26). Tóm tắt của subagent không phải bằng chứng. |
| "Nhúng cả 5 Handoff Log cũ cho chắc" | R11 chỉ yêu cầu bước LIỀN TRƯỚC — nhúng nhiều gây phình prompt, subagent tự Read step xa hơn nếu cần. |
| "Git status có file lạ nhưng chắc không liên quan" | File code untracked khớp phạm vi bước = bước dở cho đến khi chứng minh ngược lại. Bỏ qua = làm lại từ đầu, mất công. |
| "Plan 1 bước nhưng cứ spawn cho đúng quy trình" | Ngoại lệ §16.5 là CÓ CHỦ ĐÍCH — spawn cho plan 1 bước chỉ tốn token/paraphrasing hop. |
