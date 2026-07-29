// PostToolUse hook (Write|Edit) — nhắc cập nhật code-graph/CODE-GRAPH.md (CLAUDE.md §17)
// và ghi lesson (Global CLAUDE.md) sau khi chạm file source code.
// Chỉ NHẮC (additionalContext) — không bao giờ block.

let raw = "";
process.stdin.on("data", (c) => (raw += c));
process.stdin.on("end", () => {
  try {
    const input = JSON.parse(raw || "{}");
    const filePath =
      (input.tool_input && input.tool_input.file_path) ||
      (input.tool_response && input.tool_response.filePath) ||
      "";
    if (!filePath) return;

    const norm = filePath.replace(/\\/g, "/");

    // Loại trừ: tài liệu, lessons, chính code-graph, config nội bộ .claude
    const excludeRe = /\/(docs|lessons)\/|code-graph\/CODE-GRAPH\.md$|\/\.claude\//i;
    if (excludeRe.test(norm)) return;

    // Chỉ nhắc khi đụng vào file source code thật
    const srcRe = /\.(cs|ts|tsx|js|jsx|py|go|java|cpp|c|h|hpp)$/i;
    if (!srcRe.test(norm)) return;

    const msg =
      `Vừa sửa file source: ${filePath}. Nhắc theo CLAUDE.md: ` +
      `(1) Nếu đây là thay đổi structure/API/schema/dependency/env var → PHẢI cập nhật code-graph/CODE-GRAPH.md và xuất lại CODE-GRAPH.pdf (CLAUDE.md §17) — bỏ qua nếu chỉ sửa logic nội bộ không đổi interface. ` +
      `(2) Nếu vừa fix xong bug mất >5 phút hoặc phát hiện gotcha/hành vi bất ngờ → ghi lesson NGAY vào C:\\Users\\nguye\\.claude\\lessons\\ theo quy trình 8 bước (Global CLAUDE.md) — đừng đợi hết task.`;

    console.log(
      JSON.stringify({
        hookSpecificOutput: {
          hookEventName: "PostToolUse",
          additionalContext: msg,
        },
      })
    );
  } catch (e) {
    // Không bao giờ làm hỏng luồng chính vì lỗi hook
    return;
  }
});
