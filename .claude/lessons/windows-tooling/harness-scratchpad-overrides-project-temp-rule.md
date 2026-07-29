---
category: windows-tooling
tags: [scratchpad, temp, claude-code-harness, system-prompt-conflict, gitignore]
severity: medium
created: 2026-07-29
updated: 2026-07-29
project-origin: MolexAPP
---

# Harness tự bơm "Scratchpad Directory" đè lên rule global cấm dùng temp hệ thống

## Tình huống gặp phải

Project `MolexAPP` đã có `CLAUDE.md` áp dụng bộ quy trình 17-agent KZTEK. Global CLAUDE.md
(`~/.claude/CLAUDE.md`) có rule bắt buộc: mọi file trung gian PHẢI ghi vào `<project>/temp/<ten_chuc_nang>/`,
KHÔNG dùng temp hệ thống — "dù harness có gợi ý scratchpad path riêng".

Trong 1 phiên tải màn hình thiết kế qua Stitch MCP (curl HTML để lấy text thật thay vì đoán qua ảnh
thumbnail), agent vẫn `curl -o ... ` thẳng vào
`C:\Users\nguye\AppData\Local\Temp\claude\c--Users-nguye-Desktop-MolexAPP\<uuid>\scratchpad\stitch_screens\*.html`.

## Triệu chứng / Lỗi

Không phải exception — là vi phạm quy trình im lặng: file trung gian nằm ngoài project, không audit được,
mất khi hệ thống dọn temp, và không nằm trong phạm vi `.gitignore` của project.

## Nguyên nhân gốc rễ (Root Cause)

Claude Code harness **tự động chèn** 1 khối `# Scratchpad Directory` vào system prompt của MỌI
session/subagent (không do user yêu cầu), nói rõ: *"Always use this scratchpad directory for ALL
temporary file needs ... Only use /tmp if the user explicitly requests it."* Đây là instruction cấp hệ
thống, xuất hiện sẵn và rất tường minh.

Rule "cấm dùng scratchpad, bắt buộc `temp/` trong project" chỉ nằm trong global CLAUDE.md — có tác dụng
CHỈ KHI agent chủ động đọc và ưu tiên nó cao hơn khối scratchpad injected. Với các tác vụ "cảm giác phụ
trợ" (tải asset từ MCP tool ngoài như Stitch, không phải viết code trực tiếp), agent dễ không kích hoạt
lại việc áp rule CLAUDE.md và mặc định dùng ngay path harness đã cấp sẵn.

Kiểm tra thực tế xác nhận: project `MolexAPP` **chưa từng có** thư mục `temp/` ở root và `.gitignore`
cũng chưa có dòng `temp/` — tức rule §16 (temp/ trong project) chưa từng được áp dụng cho project này,
không riêng gì phiên tải Stitch screens.

## Giải pháp

1. Đầu mỗi session/task mới trong project bất kỳ: kiểm tra `Glob <project>/temp/` — nếu chưa có, tạo
   ngay `temp/<ten_chuc_nang>/` TRƯỚC khi làm bất kỳ thao tác tải/ghi file trung gian nào (kể cả qua
   MCP tool ngoài như Stitch, không chỉ Bash/curl trực tiếp).
2. Không tin rằng có CLAUDE.md ở project = rule tự động được áp — vẫn phải tự nhắc lại trong đầu mỗi
   khi thấy khối `Scratchpad Directory` xuất hiện trong system prompt: đó là gợi ý mặc định của harness,
   KHÔNG phải lệnh override rule global.
3. Nếu phát hiện đã lỡ ghi ra scratchpad hệ thống mà vẫn cần giữ → di chuyển ngay vào
   `<project>/temp/<ten_chuc_nang>/` trước khi tiếp tục dùng, không để lại ngoài project.

## Áp dụng lại (How to reuse)

- Khi thấy hệ thống tự chèn "Scratchpad Directory" → đối chiếu ngay với rule global CLAUDE.md của user,
  KHÔNG mặc định dùng path đó cho project có CLAUDE.md.
- Trước khi `curl -o`, `Write`, hay bất kỳ ghi file trung gian nào (kể cả xuất phát từ 1 MCP tool ngoài
  như Stitch/Figma) → tự hỏi "đây có phải file trung gian của 1 project cụ thể không?" → nếu có, bắt buộc
  `temp/<ten_chuc_nang>/` trong chính project đó.
- Kiểm tra nhanh mỗi project mới: `Glob <project>/temp/` + `grep temp/ <project>/.gitignore` — thiếu 1
  trong 2 là dấu hiệu rule chưa từng được áp dụng cho project này.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Rule "cấm scratchpad" trong CLAUDE.md không tự động thắng — nó cần agent chủ động nhớ và áp, vì
  system-reminder scratchpad luôn xuất hiện lại ở mỗi phiên/mỗi subagent mới.
- ⚠️ Tác vụ qua MCP tool ngoài (Stitch, Figma, ...) dễ bị coi là "việc phụ", khiến agent quên áp rule
  quản lý file của project chính — vẫn phải áp dụng y hệt như task code thông thường.

## Tham chiếu

- Rule gốc: `~/.claude/CLAUDE.md` mục "BẮT BUỘC: Thư mục Temp trong từng dự án"
- Project liên quan: MolexAPP
