# MyClaude — tự viết lại 1 phiên bản mini của Claude (C#)

Dự án học tập cá nhân (không phải sản phẩm KZTEK), tiếp nối `learning/mygithub` và
`learning/design-patterns`. Gọi thẳng **Claude API thật** (Anthropic SDK cho C#) — không phải mô
phỏng — để hiểu cơ chế bên trong 1 chatbot và 1 coding agent như Claude Code.

## Yêu cầu

- .NET 8 SDK trở lên (sandbox hiện tại không có sẵn — build/chạy trên máy local).
- 1 Anthropic API key thật, đặt vào biến môi trường:
  ```bash
  export ANTHROPIC_API_KEY="sk-ant-..."
  ```
  Lấy key tại https://console.anthropic.com/ (mục API Keys). **Đây là bước bắt buộc** — không
  có key thì không gọi được API thật.

## Build & chạy

```bash
cd learning/myclaude
dotnet add src/MyClaude.Cli package Anthropic   # cài SDK chính thức của Anthropic
dotnet build

# Phase 1 — chat CLI đơn giản
dotnet run --project src/MyClaude.Cli -- chat

# Phase 2 — agentic loop có tool-use (đọc/ghi file, chạy bash) trong ./workspace
dotnet run --project src/MyClaude.Cli -- agent
```

Đổi model (mặc định `claude-opus-5`, đắt hơn nhưng mạnh nhất — có thể đổi sang
`claude-sonnet-5` cho rẻ hơn khi thử nghiệm):

```bash
export MYCLAUDE_MODEL="claude-sonnet-5"
```

## Phase 1 — Chat CLI (`ChatSession.cs`)

Cơ chế cốt lõi của MỌI chatbot dùng LLM:

1. **API stateless** — Claude không "nhớ" gì giữa các lần gọi. Mỗi request phải gửi lại
   **toàn bộ lịch sử hội thoại** (`_history` trong code) — đó là lý do chi phí token tăng dần
   theo độ dài cuộc trò chuyện.
2. **Streaming** — thay vì chờ toàn bộ câu trả lời rồi in 1 lần, server gửi từng mẩu nhỏ
   (`content_block_delta`) ngay khi model sinh ra — giống hiệu ứng "gõ chữ" bạn thấy trên
   claude.ai.
3. Sau khi stream xong, gộp lại thành 1 tin nhắn `assistant` và lưu vào lịch sử để lượt hỏi
   tiếp theo có đủ ngữ cảnh.

## Phase 2 — Agentic Loop (`AgentLoop.cs` + `Tools/`)

Khác biệt cốt lõi so với Phase 1: model có thể **yêu cầu gọi tool** thay vì trả lời trực tiếp.
Đây chính là cơ chế đứng sau Claude Code, Cursor, và mọi "AI agent" viết code:

```
User hỏi → gửi lên Claude kèm danh sách tool khả dụng
         → Claude trả lời "tool_use" (muốn đọc file X)
         → code CỦA BẠN (không phải Claude) thực thi việc đọc file
         → gửi kết quả lại cho Claude dưới dạng "tool_result"
         → Claude đọc kết quả, quyết định: trả lời luôn hay gọi tiếp tool khác
         → lặp lại đến khi Claude trả lời xong (stop_reason = end_turn)
```

3 tool đã cài (`Tools/ToolDefinitions.cs` + `Tools/ToolExecutor.cs`):

| Tool | Làm gì |
|---|---|
| `read_file` | Đọc nội dung 1 file trong thư mục làm việc |
| `write_file` | Tạo/ghi đè 1 file |
| `run_bash` | Chạy 1 lệnh shell (có timeout 10s) |

**Cảnh báo bảo mật (đọc kỹ trước khi chạy):**
- Mọi path đều được resolve về canonical path và kiểm tra nằm trong `workspace/` trước khi
  đọc/ghi — chặn path traversal (`../../etc/passwd`).
- `run_bash` **không có sandbox thật** — không container, không giới hạn CPU/RAM. Model có thể
  gợi ý bất kỳ lệnh nào; code hiện tại **không lọc lệnh nguy hiểm**. Chỉ chạy trong 1 thư mục
  thử nghiệm cô lập, không phải trên máy có dữ liệu quan trọng.
- Đây là bản học tập tối giản — Claude Code thật có thêm: permission prompt trước khi chạy lệnh,
  allowlist/denylist, sandbox container, và nhiều lớp bảo vệ khác.

## Đã học được gì

- API-first: mọi "AI app" đều là lớp mỏng gọi `POST /v1/messages`, phần khó là ở harness
  (vòng lặp, quản lý lịch sử, thực thi tool) chứ không phải bản thân model.
- Tool use không phải "phép màu" — chỉ là model trả về JSON có cấu trúc (`{"name": "...",
  "input": {...}}`), code của bạn tự quyết định làm gì với nó.
- Vì sao agent càng làm việc lâu càng tốn tiền: mỗi vòng lặp gửi lại TOÀN BỘ lịch sử
  (bao gồm cả tool result cũ) — đây là động lực của prompt caching và context editing trong
  Claude API thật (xem thêm trong skill `claude-api` nếu muốn đào sâu).

## Việc tiếp theo (đề xuất, chưa làm)

| Việc | Học được gì |
|---|---|
| Thêm prompt caching (`cache_control`) cho system prompt | Giảm chi phí khi lặp lại system prompt mỗi turn |
| Giới hạn `run_bash` bằng allowlist lệnh | Nguyên tắc "promote to dedicated tool" khi cần security boundary |
| Thêm streaming cho Phase 2 (agent loop) | Kết hợp UX mượt của Phase 1 với khả năng hành động của Phase 2 |
| Thêm `web_search` (server-side tool có sẵn) | Không cần code — chỉ khai báo tool, Claude tự chạy trên server Anthropic |
