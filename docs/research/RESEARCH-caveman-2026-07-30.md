---
title: "Báo cáo nghiên cứu — juliusbrussee/caveman"
repo_url: https://github.com/juliusbrussee/caveman
research_date: 2026-07-30
researcher: github-repo-researcher
branch: claude/caveman-research-nzhhnc
mode: A (Cải tiến KZTEK)
status: draft — chờ user chọn đề xuất áp dụng (Bước 4)
---

# Nghiên cứu repo: juliusbrussee/caveman

> Bước 3 WF-GITHUB-RESEARCH — Phân tích trung lập. Đề xuất áp dụng KZTEK (Mode A) hoặc tài liệu học tập (Mode B) sẽ viết riêng sau khi user xác nhận mục đích.

> **Ghi chú kỹ thuật:** Không thể `add_repo`/clone `juliusbrussee/caveman` trực tiếp vào phiên này vì session đang gắn với owner `flick-git-anhnv` (không hỗ trợ cross-owner add trong v1). Phân tích dưới đây dựa trên nội dung GitHub công khai (trang repo + README qua WebFetch), không phải bản clone đầy đủ source code — nên không thể đánh giá chi tiết logic implementation trong `/src`.

---

## 1. Tổng quan repo

**Tên:** caveman
**URL:** https://github.com/juliusbrussee/caveman
**License:** MIT
**Loại:** Skill/plugin cho AI coding agent (Claude Code, Gemini, Cursor và 30+ agent khác)

### Mục đích cốt lõi

Caveman là một skill nén **output token** của AI agent — bắt agent trả lời ngắn gọn kiểu "người tiền sử" (bỏ lời thừa, giữ fragment câu) nhưng giữ nguyên độ chính xác kỹ thuật (code/lệnh/lỗi giữ nguyên byte-for-byte). Slogan: *"Why use many token when few token do trick"*.

**Kết quả công bố:** Giảm trung bình **65% output tokens** trên 10 task benchmark, không đổi độ chính xác.

### Vấn đề giải quyết

AI agent thường trả lời dài dòng, lặp lại ngữ cảnh, thêm câu dẫn/kết luận không cần thiết — tốn output token (ảnh hưởng tốc độ phản hồi và chi phí). Caveman inject 1 skill/prompt buộc agent nói súc tích ngay từ tin nhắn đầu.

---

## 2. Ngôn ngữ & cấu trúc thư mục

**Ngôn ngữ chính:** JavaScript/TypeScript (dựa trên `package.json`, `bin/`, `src/`)

```
caveman/
├── src/          <- logic chính (cài đặt, hook)
├── skills/       <- định nghĩa skill cho từng agent
├── agents/       <- định nghĩa hỗ trợ 30+ agent platform khác nhau
├── docs/         <- tài liệu chi tiết
├── benchmarks/   <- số liệu benchmark tiết kiệm token
├── evals/        <- bộ eval kiểm chứng
└── plugins/      <- extension cho từng platform (Claude Code, Gemini, ...)
```

---

## 3. Cơ chế hoạt động

1. **Prompt-based compression** — Skill chỉ đạo agent: xóa filler, giữ substance, dùng câu rời rạc (fragment), KHÔNG BAO GIỜ sửa nội dung code/command/error message.
2. **Hook architecture** — Trên Claude Code, một flag file khiến agent nói "kiểu caveman" ngay từ tin nhắn đầu tiên của session (không cần user nhắc lại mỗi lần).
3. **Session logging** — Lệnh `/caveman-stats` đọc log session, tính token đã tiết kiệm và quy đổi ra số tiền cụ thể.

### 6 mức compression

| Level | Ví dụ |
|---|---|
| `lite` | "Wrap object in `useMemo`. New ref every render." |
| `full` (mặc định) | "New ref each render. Wrap in `useMemo`." |
| `ultra` | "New ref/render. `useMemo` it." |
| `wenyan` | Nén bằng tiếng Trung cổ (tối ưu token ở mức ký tự) |
| *(2 mức khác)* | Không lấy được chi tiết từ WebFetch — cần đọc trực tiếp `skills/` để biết đủ 6 mức |

### Công cụ / lệnh chính

| Lệnh | Chức năng |
|---|---|
| `/caveman [level]` | Bật compression ở mức chỉ định |
| `/caveman-commit` | Sinh commit message ≤ 50 ký tự |
| `/caveman-review` | Comment PR rút gọn còn 1 dòng |
| `/caveman-compress <file>` | Nén file memory (VD: CLAUDE.md) đi ~46%, giảm input token vĩnh viễn cho các session sau |
| `caveman-shrink` | MCP wrapper — nén mô tả tool (tool descriptions) của bất kỳ MCP server nào |

---

## 4. Benchmark công bố

| Task | Bình thường (tokens) | Caveman (tokens) | Tiết kiệm |
|---|---:|---:|---:|
| React re-render bug | 1.180 | 159 | 87% |
| Auth middleware | 704 | 121 | 83% |
| PostgreSQL setup | 2.347 | 380 | 84% |
| **Trung bình** | **1.214** | **294** | **65%** |

**Lưu ý quan trọng do chính README nêu:** Caveman chỉ nén **output tokens**. Input + reasoning tokens KHÔNG đổi, và skill còn tự thêm ~1–1,5k input token/turn (system prompt của skill). Do đó tiết kiệm thực tế trên toàn session luôn nhỏ hơn con số 65% quảng cáo. Lợi ích thật sự chính là: **tốc độ phản hồi nhanh hơn** và **output dễ đọc/scan hơn**, không hẳn là tiết kiệm chi phí tổng thể lớn như con số đầu bài.

---

## 5. Cài đặt

```bash
# macOS/Linux/WSL
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash
```

Yêu cầu Node ≥ 18. Thời gian cài đặt ~30 giây. Không có bước cấu hình phức tạp — cài xong dùng ngay qua slash command.

---

## 6. Điểm nổi bật kỹ thuật

1. **Không đổi model, không cần fine-tune** — toàn bộ cơ chế là prompt/skill engineering + hook, hoạt động trên bất kỳ agent nào hỗ trợ custom skill/slash command.
2. **Bảo mật/riêng tư cao** — không có telemetry, không phone-home, chạy hoàn toàn local sau khi cài.
3. **Có thể kiểm chứng công khai** — benchmark nằm trong `/benchmarks`, không chỉ là con số marketing.
4. **Tích hợp MCP (`caveman-shrink`)** — có thể wrap bất kỳ MCP server nào để nén luôn cả phần mô tả tool (giảm input token phía định nghĩa tool, khác với phần nén output chính).
5. **`/caveman-compress <file>`** — áp dụng kỹ thuật nén cho cả file memory/context (VD CLAUDE.md), tức là mở rộng phạm vi nén từ "câu trả lời" sang "tài liệu cấu hình dài" — giảm input token dài hạn chứ không chỉ output từng lượt.

## 7. Hệ sinh thái liên quan

| Repo | Vai trò |
|---|---|
| `caveman-code` | Full coding agent nén toàn bộ luồng, quảng cáo ~2× ít token hơn Codex |
| `cavemem` | Nén memory giữa các session |
| `cavekit` | Build loop spec-driven |
| `cavegemma` | Compression "bake" thẳng vào trọng số model Gemma (khác hướng — không phải prompt-based) |

---

## 8. Thông tin repo

| Thuộc tính | Giá trị |
|---|---|
| URL | https://github.com/juliusbrussee/caveman |
| License | MIT (thương mại được phép) |
| Ngôn ngữ | JavaScript/TypeScript |
| Nền tảng hỗ trợ | Claude Code, Gemini, Cursor, và 30+ agent khác |
| Yêu cầu | Node ≥ 18 |
| Độ sâu phân tích | Trung bình — dựa trên README + cấu trúc thư mục qua GitHub web, KHÔNG có bản clone source code đầy đủ (giới hạn cross-owner của session) |

---

## 9. Nhận xét chung

Caveman giải quyết một vấn đề thực tế nhưng hẹp: giảm độ dài **output** của agent bằng prompt engineering thuần túy, không đụng đến model hay pipeline suy luận. Điểm mạnh là triển khai cực nhẹ (chỉ 1 skill + hook, cài trong 30 giây) và minh bạch benchmark. Điểm cần lưu ý:

1. **Con số 65% cần đọc kèm caveat** — chỉ tính output tokens, session-level saving thực tế thấp hơn do input overhead ~1–1.5k token/turn của chính skill.
2. **Đánh đổi giữa súc tích và rõ ràng** — trả lời kiểu "fragment" có thể giảm khả năng đọc hiểu với người không quen, đặc biệt ở mức `ultra`/`wenyan`.
3. **Không kiểm chứng được logic implementation chi tiết** trong báo cáo này do giới hạn truy cập cross-repo của phiên hiện tại — nếu cần đánh giá sâu hơn (VD: cách hook hoạt động chính xác trên Claude Code, cách `caveman-shrink` wrap MCP server), cần một phiên mới với `juliusbrussee/caveman` là nguồn chính, hoặc user cung cấp nội dung file cụ thể.

---

*Báo cáo này thuộc Bước 3 WF-GITHUB-RESEARCH — phân tích trung lập. User đã chọn Mode A. Đề xuất áp dụng ở Bước 3b (mục 11) dưới đây.*

---

## 10b. Ràng buộc quan trọng trước khi đề xuất

Hệ thống KZTEK (CLAUDE.md §3.2, §3.3, §5, §6, §7) **BẮT BUỘC** mọi agent hiển thị đầy đủ header/box/format có cấu trúc (`╔═══╗`, checklist, artifact list...) — đây là yêu cầu tổ chức không được rút gọn vì lý do minh bạch/audit trail (Two-Eyes Principle §8). Vì vậy, các đề xuất dưới đây **KHÔNG** nhắm vào việc nén format hiển thị bắt buộc đó, mà nhắm vào những chỗ KZTEK đã tự thừa nhận là "tóm tắt ngắn, không phải log đầy đủ" hoặc là tài liệu nội bộ phình to theo thời gian — đúng phạm vi mà caveman giải quyết tốt.

---

## 11. Đề xuất cải tiến KZTEK (Mode A — Bước 3b)

> Mỗi đề xuất độc lập — chọn 0, 1, hoặc nhiều đề xuất để áp dụng ở bước tiếp theo. **CHƯA áp dụng bất kỳ thay đổi nào vào codebase/tài liệu KZTEK ở bước này.**

### Bảng tổng quan nhanh

| # | Đề xuất | Effort | Phụ thuộc ngoài | Rủi ro |
|---|---------|--------|-----------------|--------|
| P1 | Chuẩn hoá "chế độ súc tích" cho tóm tắt subagent → session chính (§16.5 Bước 2a.3) | Thấp (1–2h) | Không | Thấp |
| P2 | `/gotchas-compress` — nén định kỳ GOTCHAS.md/LESSONS.md khi phình to | Trung bình (4–6h) | Không | Trung bình (mất sắc thái nếu nén quá tay) |
| P3 | Giới hạn độ dài task description cho Tầng 3 Haiku (§13.1b) | Thấp (2–3h) | Không | Thấp |
| P4 | Rút gọn phần "Mô tả" trong PR description (không đụng checklist bắt buộc §15.3) | Rất thấp (1h) | Không | Rất thấp |

---

### P1 — Chuẩn hoá "chế độ súc tích" cho tóm tắt subagent → session chính

| Trường | Nội dung |
|--------|---------|
| **Hiện trạng KZTEK** | §16.5 Bước 2a.3 đã yêu cầu subagent "trả về tóm tắt ngắn ≤ 5 dòng" nhưng không có hướng dẫn PHONG CÁCH viết — subagent thường vẫn viết 5 dòng đầy đủ câu, có lời dẫn/kết luận thừa. |
| **Học từ đâu** | Nguyên tắc lõi của caveman: giữ nguyên số liệu/code/lỗi chính xác, cắt lời dẫn/kết luận, dùng câu rời rạc (fragment) thay vì câu hoàn chỉnh. Mức `lite`/`full` phù hợp nhất (không dùng `ultra`/`wenyan` — quá khó đọc cho non-technical stakeholder). |
| **Lý do thay đổi** | Tóm tắt 5 dòng hiện tại vẫn có xu hướng lặp lại ngữ cảnh ("Tôi đã hoàn thành việc...", "Kết quả cho thấy rằng..."). Với plan nhiều bước (§16), tổng các tóm tắt này cộng dồn vào session chính — càng súc tích càng giữ context window lâu hơn trước khi cần compact (liên quan trực tiếp khuyến nghị Strategic Compact §16.5 cuối). |
| **Áp dụng vào đâu** | CLAUDE.md §16.5 Bước 2a.3 — thêm 1 dòng hướng dẫn phong cách: "Tóm tắt PHẢI ở dạng fragment (không câu dẫn/kết luận), giữ nguyên số liệu/tên file/commit hash chính xác — tham khảo mức `lite`/`full` của caveman." |
| **Đạt được gì** | Giảm ước tính 20–30% độ dài tóm tắt handoff mà không mất thông tin — kéo dài thời điểm cần `/compact`, ít phải gợi ý Strategic Compact hơn. |
| **Rủi ro / Effort** | Rủi ro thấp — chỉ áp dụng cho 1 trường tóm tắt cụ thể, KHÔNG đụng format hiển thị bắt buộc §3.2/§5/§6. Effort: 1–2 giờ (thêm hướng dẫn + ví dụ before/after vào §16.5). |

---

### P2 — `/gotchas-compress`: nén định kỳ GOTCHAS.md/LESSONS.md

| Trường | Nội dung |
|--------|---------|
| **Hiện trạng KZTEK** | `.claude/shared/GOTCHAS.md` và `docs/LESSONS.md` chỉ CỘNG THÊM entry theo thời gian (§9a, §3.3), không có cơ chế nén/rút gọn khi file dài ra — agent đọc "5-10 entry gần nhất" (theo Pre-0b) nhưng file tổng vẫn phình to, tốn context nếu cần đọc toàn bộ. |
| **Học từ đâu** | `/caveman-compress <file>` — nén file memory dài đi ~46% để giảm input token vĩnh viễn cho các session sau, giữ nguyên thông tin cốt lõi. |
| **Lý do thay đổi** | Sau nhiều tháng, GOTCHAS.md/LESSONS.md có thể có nhiều entry trùng ý hoặc diễn giải dài dòng cho cùng 1 loại lỗi — không ai chủ động dọn lại. |
| **Áp dụng vào đâu** | Tạo skill `.claude/commands/gotchas-compress.md`: đọc toàn bộ GOTCHAS.md/LESSONS.md, gom nhóm entry trùng category (đã có label `[SCRIPT]`/`[ENCODING]`/... theo v1.8), viết lại súc tích hơn nhưng giữ đủ category + root cause + fix — chạy thủ công khi user gọi, KHÔNG tự động. |
| **Đạt được gì** | Giữ 2 file tham chiếu quan trọng luôn gọn, giảm token khi agent cần đọc toàn bộ (không chỉ 5-10 entry gần nhất) để tra cứu lỗi cũ. |
| **Rủi ro / Effort** | Rủi ro trung bình — nén sai có thể làm mất sắc thái/context quan trọng của 1 gotcha cụ thể (VD: điều kiện chính xác gây lỗi). Cần review thủ công sau khi nén trước khi ghi đè. Effort: 4–6 giờ (viết skill + test trên GOTCHAS.md hiện tại). |

---

### P3 — Giới hạn độ dài task description khi downshift sang Tầng 3 (Haiku)

| Trường | Nội dung |
|--------|---------|
| **Hiện trạng KZTEK** | §13.1b định nghĩa Tầng 3 (Haiku) cho task cơ học có template — nhưng không hướng dẫn cách VIẾT prompt/task description ngắn gọn khi giao việc cho Haiku, dễ giao prompt dài dòng không cần thiết cho task vốn đơn giản. |
| **Học từ đâu** | Nguyên tắc "few token do trick" của caveman — với task cơ học rõ ràng, không cần ngữ cảnh dài dòng, chỉ cần chỉ dẫn súc tích + template tham chiếu. |
| **Lý do thay đổi** | Prompt dài cho task cơ học (VD: điền smoke-test log theo template) làm tăng input token không cần thiết — đúng nhóm task mà §13.1b đã xác định là "không cần suy luận nghiệp vụ". |
| **Áp dụng vào đâu** | CLAUDE.md §13.1b — thêm ghi chú: "Khi giao task Tầng 3, viết task description dạng fragment súc tích (tham khảo mức `lite` caveman), trỏ thẳng đến template — không lặp lại ngữ cảnh nghiệp vụ đầy đủ vì Haiku không cần suy luận sâu." |
| **Đạt được gì** | Giảm input token cho các lượt gọi Haiku — nhất quán với lý do §13.1b đã chọn Haiku (tiết kiệm chi phí). |
| **Rủi ro / Effort** | Rủi ro thấp — chỉ là hướng dẫn viết prompt, không đổi logic downshift. Effort: 2–3 giờ. |

---

### P4 — Rút gọn phần "Mô tả" tự do trong PR description

| Trường | Nội dung |
|--------|---------|
| **Hiện trạng KZTEK** | §5 Format task giao việc và checklist PR (§15.3) đã có cấu trúc cố định (Definition of Done, checklist tài liệu...) — đây là phần BẮT BUỘC giữ nguyên. Nhưng phần "Mô tả" tự do (câu văn giải thích) trong PR description thường bị viết dài dòng, lặp lại nội dung đã có trong Definition of Done. |
| **Học từ đâu** | `/caveman-review` — rút PR comment còn 1 dòng súc tích, giữ đúng technical substance. |
| **Lý do thay đổi** | Phần mô tả tự do không có cấu trúc bắt buộc, nên đây là chỗ AN TOÀN để áp dụng compression mà không vi phạm §15.3 hay Two-Eyes Principle §8 (các checklist/DoD vẫn giữ nguyên đầy đủ). |
| **Áp dụng vào đâu** | Ghi chú nhỏ trong §5 (Format task) và `.claude/commands/verify-pr.md`: "Phần Mô tả PHẢI súc tích 2-3 câu tối đa, không lặp lại nội dung đã có ở Definition of Done/checklist — tham khảo phong cách `/caveman-review`." |
| **Đạt được gì** | PR description dễ scan hơn, Tech Lead review nhanh hơn vì không phải đọc đoạn mô tả trùng lặp thông tin đã có ở checklist. |
| **Rủi ro / Effort** | Rủi ro rất thấp. Effort: ~1 giờ (thêm 1 dòng ghi chú). |

---

> **Khuyến nghị ưu tiên:** P1 và P4 effort thấp nhất, áp dụng ngay không rủi ro. P3 hưởng lợi trực tiếp mục tiêu tiết kiệm chi phí đã có sẵn ở §13.1b. P2 giá trị dài hạn nhưng cần review kỹ sau khi nén — không nên tự động hoá hoàn toàn.
