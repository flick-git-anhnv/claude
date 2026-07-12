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
