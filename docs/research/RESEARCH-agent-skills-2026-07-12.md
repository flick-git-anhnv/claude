# Nghiên cứu: addyosmani/agent-skills

**Nguồn:** https://github.com/addyosmani/agent-skills
**Ngày nghiên cứu:** 2026-07-12
**Số liệu tại thời điểm khảo sát:** ~77.4k sao, ~8.3k fork
**License:** MIT

## Tổng quan

`agent-skills` là bộ quy trình kỹ thuật (skills) dành cho các agent lập trình AI, giúp agent tuân theo thực hành kỹ thuật chất lượng cao xuyên suốt vòng đời phát triển phần mềm, thay vì đi đường tắt (bỏ qua test, bảo mật, review). Được xây dựng dựa trên văn hóa kỹ thuật kiểu Google (Hyrum's Law, Beyoncé Rule, trunk-based development).

Điểm khác biệt: mỗi skill có "anti-rationalization table" — liệt kê các lý do phổ biến để bỏ qua bước, kèm lập luận phản bác — và yêu cầu xác minh (verification) rõ ràng, không chấp nhận kiểu "trông có vẻ đúng".

## Cấu trúc repo

```
agent-skills/
├── skills/                 # 24 skill folders
├── agents/                 # 4 agent personas
├── references/             # 7 checklist tham khảo
├── hooks/
├── .claude/commands/, .gemini/commands/, commands/
├── plugin.json
└── docs/
```

## 24 Skills (nhóm theo vòng đời)

| Giai đoạn | Skills |
|---|---|
| Define (3) | interview-me, idea-refine, spec-driven-development |
| Plan (1) | planning-and-task-breakdown |
| Build (7) | incremental-implementation, test-driven-development, context-engineering, source-driven-development, doubt-driven-development, frontend-ui-engineering, api-and-interface-design |
| Verify (2) | browser-testing-with-devtools, debugging-and-error-recovery |
| Review (4) | code-review-and-quality, code-simplification, security-and-hardening, performance-optimization |
| Ship (6) | git-workflow-and-versioning, ci-cd-and-automation, deprecation-and-migration, documentation-and-adrs, observability-and-instrumentation, shipping-and-launch |
| Meta (1) | using-agent-skills |

## 4 Agent Personas

- **code-reviewer** — Senior Staff Engineer
- **test-engineer** — QA Specialist
- **security-auditor** — Security Engineer
- **web-performance-auditor** — Web Performance Engineer

## 8 Slash Commands

`/spec` (định nghĩa) · `/plan` (lập kế hoạch) · `/build` (xây dựng) · `/test` (kiểm thử) · `/review` (đánh giá) · `/webperf` (hiệu năng) · `/code-simplify` (đơn giản hóa) · `/ship` (triển khai)

## Cài đặt

Hỗ trợ 70+ agent CLI (Claude Code, Cursor, Copilot, Cline, Gemini, ...) qua CLI hoặc marketplace:

```bash
npx skills add addyosmani/agent-skills
```

## Nhận định / khả năng áp dụng cho KZTEK

- Cấu trúc "vòng đời Define → Plan → Build → Verify → Review → Ship" tương đồng ở mức khái niệm với chain-of-command workflow hiện có trong `CLAUDE.md` (WF-FEATURE, WF-BUGFIX, ...), nhưng agent-skills tổ chức theo **skill/lifecycle stage** thay vì theo **vai trò tổ chức** (PM/BA/Tech Lead/...).
- Cơ chế "anti-rationalization table" là ý tưởng có thể tham khảo để bổ sung vào các skill nội bộ (VD: `security-audit-stride`) nhằm chặn agent lý luận để bỏ qua bước.
- Không phát hiện xung đột license hay yêu cầu tích hợp bắt buộc — đây thuần túy là tài liệu tham khảo, chưa có hành động tích hợp nào được thực hiện vào codebase KZTEK trong lần nghiên cứu này.

---

## Bảng đề xuất cải tiến (Nghiên cứu sâu — clone thực tế 2026-07-12)

> Nguồn: đọc trực tiếp từ clone tại scratchpad. Mỗi đề xuất nêu file/section cụ thể trong repo nguồn và file/agent cụ thể trong workspace KZTEK.

| # | Đề xuất | Học từ đâu (file/pattern cụ thể trong repo nguồn) | Áp dụng vào đâu trong KZTEK (file/agent cụ thể) | Lợi ích | Rủi ro / Effort |
|---|---|---|---|---|---|
| 1 | Thêm mục **"Common Rationalizations"** (bảng 2 cột: "Rationalization" / "Reality") vào `.claude/commands/security-audit-stride.md` | `skills/security-and-hardening/SKILL.md` §Common Rationalizations (8 entries, VD: "This is an internal tool, security doesn't matter" → "Internal tools get compromised"); `skills/code-review-and-quality/SKILL.md` §Common Rationalizations (9 entries) | `.claude/commands/security-audit-stride.md` — hiện thiếu section này hoàn toàn | Ngăn agent (và user) hợp lý hóa để bỏ qua bước audit — đây là điểm yếu thực tế nhất của skill bảo mật khi deadline gấp | Effort rất thấp: chỉ thêm table mới, không đổi logic; rủi ro zero |
| 2 | Thêm mục **"Red Flags"** vào các agent definition quan trọng nhất | `skills/code-review-and-quality/SKILL.md` §Red Flags (12 items cụ thể, VD: "PRs merged without any review", "LGTM without evidence of actual review"); `skills/test-driven-development/SKILL.md` §Red Flags | `.claude/agents/tech-lead.md`, `.claude/agents/senior-developer.md`, `.claude/agents/qa-engineer.md` — hiện chưa có section này | Agent tự nhận biết khi mình hoặc agent khác đang vi phạm quy trình, thay vì chỉ biết khi Dispatcher chặn | Effort thấp: thêm section mới vào 3 file; không thay đổi workflow |
| 3 | Thêm **"Verification checklist"** (checkbox `- [ ]`) vào cuối mỗi skill/command file như một "done gate" tường minh | Mọi SKILL.md trong repo đều kết thúc bằng `## Verification` với checklist checkbox — VD: `skills/test-driven-development/SKILL.md` §Verification (6 items) và `skills/security-and-hardening/SKILL.md` §Verification (9 items) | `.claude/commands/security-audit-stride.md`, `.claude/commands/scope-check.md`, `.claude/agents/code-migrator.md` — hiện có nội dung quy trình nhưng thiếu gate kiểm tra cuối | Tạo "exit criteria" rõ ràng: agent không thể tự khai hoàn thành khi chưa tick đủ checkpoint; đặc biệt có giá trị cho security audit và migration planning | Effort rất thấp; rủi ro zero |
| 4 | Thêm điều kiện **"When NOT to use"** bên cạnh "When to Use" trong skill/agent files | Mọi SKILL.md có sub-section "When NOT to use" — VD: `skills/test-driven-development/SKILL.md`: "Pure configuration changes, documentation updates, or static content changes that have no behavioral impact"; `skills/planning-and-task-breakdown/SKILL.md`: "Single-file changes with obvious scope" | `.claude/commands/security-audit-stride.md` (khi nào KHÔNG cần chạy full STRIDE?), `.claude/agents/code-migrator.md` (khi nào KHÔNG phải trigger WF-MIGRATE?), `.claude/commands/scope-check.md` | Giảm over-application: agent không áp dụng skill vào tình huống không phù hợp — tránh lãng phí token và làm chậm flow đơn giản | Effort rất thấp; rủi ro zero |
| 5 | Tách **reference checklists** ra file riêng `references/` thay vì nhúng vào skill chính | `references/security-checklist.md`, `references/testing-patterns.md`, `references/definition-of-done.md` — tách biệt hoàn toàn; skill chính dùng `## See Also` để link, VD: `skills/security-and-hardening/SKILL.md`: "For detailed security checklists, see references/security-checklist.md" | `.claude/commands/security-audit-stride.md` hiện chứa cả quy trình lẫn checklist dài → tách thành: `security-audit-stride.md` (quy trình, trigger, anti-rationalization) + `references/security-audit-checklist.md` (checklist chi tiết OWASP/STRIDE) | Giữ skill files ngắn gọn và dễ đọc; checklist được tái dùng bởi nhiều agent (tech-lead, senior-dev, security reviewer) mà không nhân bản nội dung; dễ cập nhật khi OWASP ra phiên bản mới | Effort trung bình: cần refactor file hiện có, tạo thư mục `references/`; rủi ro thấp nếu link đúng |
| 6 | Thêm format block **"ASSUMPTIONS I'M MAKING"** vào output instruction của `code-migrator.md` và `tech-lead.md` | `skills/using-agent-skills/SKILL.md` §Core Operating Behaviors §1 "Surface Assumptions" — format chuẩn: `ASSUMPTIONS I'M MAKING: 1. [assumption] → Correct me now or I'll proceed with these.`; `skills/spec-driven-development/SKILL.md` §Phase 1 dùng cùng format này trước khi viết spec | `.claude/agents/code-migrator.md` (trước khi lập migration plan ở Bước 1) và `.claude/agents/tech-lead.md` (trước khi viết TDD ở WF-FEATURE Bước 7) | Buộc agent hiển thị các giả định về scope/kiến trúc trước khi thực hiện, thay vì ngầm điền vào → giảm rework khi user không đồng ý với giả định | Effort rất thấp: thêm format block vào output instruction của 2 file |
| 7 | Thêm **severity label protocol** vào code review output format của `tech-lead.md` | `skills/code-review-and-quality/SKILL.md` §Step 4 "Categorize Findings" — prefix table 4 mức: *(no prefix)* = Required, **Critical** = blocks merge, **Nit** = optional, **Optional/Consider** = suggestion, **FYI** = informational; dẫn đến "Author Action" rõ ràng từng mức | `.claude/agents/tech-lead.md` §Code Review output format — hiện chỉ có "approve / request changes" mà không phân cấp từng comment | Phân biệt rõ comment nào bắt buộc sửa trước merge vs. chỉ là gợi ý → tránh developer phải hỏi lại; giảm vòng lặp review không cần thiết | Effort thấp: cập nhật output format template trong 1 file |
| 8 | Tạo slash command **`/ship`** dạng parallel fan-out với go/no-go decision | `commands/ship.toml` — fan-out 3 subagent song song (code-reviewer + security-auditor + test-engineer) + Phase B merge + Phase C go/no-go + rollback plan bắt buộc; `references/orchestration-patterns.md` §Pattern 3 "Parallel fan-out with merge" | `.claude/commands/` → tạo mới `ship.md` — fan-out: Tech Lead (code review 5 axes) song song với security-audit-stride song song với QA Engineer (smoke check) → merge thành **GO/NO-GO** kèm rollback plan; thay thế chuỗi WF-FEATURE Bước 10-14 dài dòng khi cần entry point nhanh | Tạo entry point duy nhất cho pre-deploy review với output chuẩn, có rollback plan bắt buộc; giảm thời gian wall-clock nhờ song song hóa 3 reviews | Effort trung bình-cao: cần thiết kế cẩn thận subagent types, merge logic, và định nghĩa điều kiện bỏ qua fan-out (diff nhỏ < 50 lines) |
| 9 | Ghi chú **"trade-off của dispatcher layer"** vào `CLAUDE.md` để team nhận thức rõ overhead | `references/orchestration-patterns.md` §Anti-patterns §A "Router persona (meta-orchestrator)": *"Adds two paraphrasing hops → information loss + roughly 2× token cost"*; §C "Sequential orchestrator that paraphrases": *"Loses the human checkpoints... doubles token cost: orchestrator turn + sub-agent turn for every step"* | `CLAUDE.md` §3 Dispatcher + `.claude/shared/CORE.md` — thêm ghi chú nhận thức: "Pattern Dispatcher là lựa chọn có chủ đích để enforce chain-of-command; trade-off là mỗi bước thêm 1 paraphrasing hop — với WF đơn giản (WF-FASTTRACK, WF-HOTFIX) có thể cân nhắc slash command trực tiếp thay vì full dispatcher chain" | Giúp team hiểu khi nào nên dùng full Dispatcher vs. slash command trực tiếp; định hướng tối ưu cho các WF đơn giản trong tương lai | Effort rất thấp: chỉ thêm ghi chú trong comment block, không thay đổi cấu trúc; rủi ro zero |
| 10 | Tạo `references/definition-of-done.md` như **standing checklist** tách biệt khỏi acceptance criteria từng task | `references/definition-of-done.md` — phân biệt rõ: AC = "Did we build *this thing*?" vs. DoD = "Is it *ready*?"; DoD gồm 5 nhóm: Correctness / Quality / Integration / Documentation / Ship-readiness; note: "A Definition of Done that is renegotiated every sprint is not a Definition of Done" | KZTEK hiện có DoD rải rác: CLAUDE.md §15 (checklist tài liệu), CLAUDE.md §11 (artifact checklist), `qa-engineer.md`, PR template §15.3 → tập trung vào 1 file `references/definition-of-done.md`, các file khác link đến | Mọi agent biết "done" nghĩa là gì mà không cần tra nhiều file; khi DoD thay đổi chỉ sửa 1 chỗ; tách biệt rõ DoD (cố định theo dự án) vs. AC (thay đổi theo task) | Effort trung bình: cần review tất cả file hiện có để extract nội dung DoD và consolidate; sau đó dùng `## See Also` để link từ các file cũ |

---

## Trạng thái áp dụng

| # | Đề xuất | Trạng thái |
|---|---|---|
| 1 | Anti-rationalization table trong security-audit-stride | Chờ duyệt |
| 2 | Red Flags trong tech-lead / senior-dev / qa-engineer | Chờ duyệt |
| 3 | Verification checklist cuối skill/command files | Chờ duyệt |
| 4 | "When NOT to use" trong skill/agent definitions | Chờ duyệt |
| 5 | Tách reference checklists ra `references/` | Chờ duyệt |
| 6 | "ASSUMPTIONS I'M MAKING" format block | Chờ duyệt |
| 7 | Severity label protocol trong code review output | Chờ duyệt |
| 8 | Slash command `/ship` fan-out | Chờ duyệt |
| 9 | Ghi chú trade-off dispatcher layer | Chờ duyệt |
| 10 | `references/definition-of-done.md` standing checklist | Chờ duyệt |
