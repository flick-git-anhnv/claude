---
title: "Nghiên cứu repo: revfactory/harness"
repo_url: https://github.com/revfactory/harness
date: 2026-07-12
researcher: github-repo-researcher
workflow: WF-GITHUB-RESEARCH
branch: research/harness-2026-07-12
status: draft — chờ user chọn đề xuất áp dụng
---

# Nghiên cứu repo: revfactory/harness

**URL:** https://github.com/revfactory/harness  
**Ngày nghiên cứu:** 2026-07-12  
**License:** Apache 2.0  
**Version tại thời điểm khảo sát:** 1.2.0  
**Độ trưởng thành:** Plugin đang hoạt động, có changelog, có README đa ngôn ngữ (EN/KO/JA), có nghiên cứu A/B kèm theo ở repo chị.

---

## 1. Tổng quan repo

**Harness** là một **Team-Architecture Factory** cho Claude Code — một meta-skill (skill sinh ra skill và agent) cho phép chuyển đổi mô tả domain thành toàn bộ hệ thống agent team gồm file định nghĩa agent (`.claude/agents/`) và file skill (`.claude/skills/`), theo một trong 6 kiến trúc mẫu định sẵn.

Nói nôm na: thay vì tự thiết kế từng agent và skill, người dùng chỉ cần gõ "Build a harness for X", và Harness tự phân tích domain, chọn kiến trúc, sinh ra cả bộ agent + skill + orchestrator.

**Cấu trúc repo:**

```
harness/
├── skills/harness/
│   ├── SKILL.md                      # Meta-skill chính (6-phase workflow)
│   └── references/
│       ├── agent-design-patterns.md  # 6 kiến trúc mẫu
│       ├── orchestrator-template.md  # Template orchestrator A/B/C
│       ├── team-examples.md          # 5 ví dụ thực tế
│       ├── skill-writing-guide.md    # Hướng dẫn viết skill
│       ├── skill-testing-guide.md    # Hướng dẫn test skill
│       └── qa-agent-guide.md         # Hướng dẫn QA agent
├── _workspace/                        # Ví dụ workspace thực tế
└── docs/
```

---

## 2. Phân tích kiến trúc & kỹ thuật

### 2.1 Sáu kiến trúc mẫu cho agent team

| # | Tên | Mô tả | Khi dùng |
|---|-----|--------|----------|
| 1 | **Pipeline** | Tuần tự: output bước trước = input bước sau | Mỗi bước phụ thuộc hoàn toàn vào bước trước |
| 2 | **Fan-out/Fan-in** | Song song → tổng hợp | Cùng input, nhiều góc nhìn độc lập |
| 3 | **Expert Pool** | Router chọn chuyên gia theo tình huống | Input đa dạng, cần chuyên gia khác nhau |
| 4 | **Producer-Reviewer** | Sinh → Kiểm (có thể lặp) | Cần đảm bảo chất lượng output |
| 5 | **Supervisor** | Central agent phân phối task động | Khối lượng công việc thay đổi runtime |
| 6 | **Hierarchical Delegation** | Ủy quyền đệ quy theo tầng | Bài toán phân rã tự nhiên theo cây |

### 2.2 Phân tách Agent vs Skill (Who vs How)

Harness tách rõ hai khái niệm:
- **Agent** (`.claude/agents/`): "Ai làm?" — persona, nguyên tắc, giao thức giao tiếp
- **Skill** (`.claude/skills/`): "Làm thế nào?" — quy trình, công cụ, tham chiếu

Đây là separation of concerns rõ ràng, giúp tái sử dụng cả hai chiều: nhiều agent có thể dùng cùng 1 skill; 1 agent có thể dùng nhiều skill.

### 2.3 Progressive Disclosure — Quản lý context window 3 tầng

Harness giải quyết vấn đề context window bằng tải thông tin 3 tầng:

| Tầng | Nội dung | Thời điểm tải | Mục tiêu kích thước |
|------|----------|--------------|-------------------|
| Metadata | name + description | Luôn có trong context | ~100 từ |
| SKILL.md body | Workflow chính | Khi skill được kích hoạt | < 500 dòng |
| references/ | Chi tiết, ví dụ, template | Chỉ khi cần thiết | Không giới hạn |

Nguyên tắc: nếu SKILL.md vượt 500 dòng → tách sang `references/`, để pointer "đọc file này khi gặp trường hợp X".

### 2.4 Convention `_workspace/` cho artifact trung gian

Harness quy định một thư mục scratchpad chuẩn trong project:
- Tên thư mục: `_workspace/`
- Naming file: `{phase}_{agent}_{artifact}.{ext}` — VD: `01_analyst_requirements.md`
- Quy tắc: **chỉ** output cuối cùng mới ghi vào đường dẫn do user chỉ định; file trung gian luôn vào `_workspace/` (để audit trail)
- Khi chạy lại: rename `_workspace/` → `_workspace_{YYYYMMDD_HHMMSS}/` trước khi tạo mới

### 2.5 "Pushy" description — Kích hoạt skill chủ động

Harness nhận ra Claude có xu hướng **bảo thủ** khi quyết định kích hoạt skill. Giải pháp: viết description "pushy" — mô tả rõ:
1. Những gì skill làm được (cụ thể, liệt kê)
2. Điều kiện kích hoạt rõ ràng ("khi user đề cập X, PHẢI dùng skill này")
3. Ranh giới phân biệt với skill/tool khác (near-miss case)

### 2.6 Phase 0 Audit — Kiểm tra trạng thái trước khi làm

Trước khi chạy bất kỳ phase nào, Harness bắt buộc một **Phase 0 kiểm tra hiện trạng**:
- Harness mới hay đang mở rộng?
- Agent/skill nào đã tồn tại?
- Có drift (bất đồng bộ) giữa file và CLAUDE.md không?

Sau đó đưa ra ma trận quyết định: phase nào cần chạy, phase nào bỏ qua.

### 2.7 Phương pháp kiểm thử With-skill vs Without-skill

Harness có một testing framework cụ thể:
1. Viết 2–3 test prompt thực tế
2. Chạy song song: một agent có skill, một agent không có skill (baseline)
3. Đánh giá kết quả: định tính (user review) + định lượng (assertion-based scoring)
4. Vòng lặp cải tiến: nếu phát hiện vấn đề → sửa ở mức nguyên lý, không patch từng case
5. Kiểm tra should-trigger (8–10 query) và should-NOT-trigger (8–10 near-miss query)

### 2.8 Nghiên cứu A/B về hiệu quả

Repo chị `revfactory/claude-code-harness` đo lường trên 15 task:
- Điểm chất lượng trung bình: 49.5 → 79.3 (**+60%**)
- Win rate: 15/15 (100%)
- Variance: giảm 32%
- Hiệu quả tăng theo độ phức tạp task: +23.8 (Basic) → +29.6 (Advanced) → +36.2 (Expert)

*(Lưu ý: n=15, tự đo bởi tác giả, chưa có replication độc lập)*

---

## 3. Bảng đề xuất cải tiến cho KZTEK

> **Lưu ý bảo mật:** Không có đề xuất nào dưới đây đụng auth/payment/DB schema/dữ liệu nhạy cảm — không cần chạy `security-audit-stride` trước khi áp dụng.

| # | Tên đề xuất | Học từ đâu trong repo Harness | Áp dụng vào đâu trong KZTEK | Lợi ích | Rủi ro / Effort |
|---|------------|-------------------------------|------------------------------|---------|----------------|
| **P1** | **`_workspace/` convention cho artifact trung gian** | `orchestrator-template.md` §Data Transfer Protocol; `_workspace/` thực tế trong repo | Mọi workflow nhiều bước (WF-FEATURE, WF-MIGRATE, WF-GITHUB-RESEARCH): agent dùng `_workspace/` thay vì ghi thẳng vào `docs/` cho file trung gian | Dễ audit trail; agent sau dễ tìm input từ agent trước; không ô nhiễm `docs/` với file nháp | Effort thấp: thêm 1 quy ước vào CLAUDE.md §11; cần update agent templates; không có rủi ro kỹ thuật |
| **P2** | **Progressive Disclosure cho `.claude/commands/` và `.claude/agents/`** | `SKILL.md` §4-4; `skill-writing-guide.md` §5 | Tách các file command/agent dài (>300 dòng) thành `SKILL.md` + `references/` trong cùng thư mục; thêm pointer "đọc file X khi gặp trường hợp Y" | Giảm context window per session; agent chỉ tải phần cần thiết; dễ bảo trì | Effort trung bình: cần refactor từng file; không phá vỡ interface hiện tại |
| **P3** | **"Pushy" description cho commands/agents** | `SKILL.md` §4-2; `skill-writing-guide.md` §1 | Rewrite phần `description:` trong frontmatter của tất cả file `.claude/commands/*.md` và `.claude/agents/*.md` theo pattern: [việc làm] + [điều kiện kích hoạt rõ] + [ranh giới với tool/command khác] | Dispatcher tự routing chính xác hơn; giảm trường hợp agent bị bỏ qua hoặc gọi nhầm | Effort thấp–trung bình: chỉ sửa frontmatter description, không đụng logic |
| **P4** | **Thêm Phase 0 Audit vào WF-GITHUB-RESEARCH và WF-MIGRATE** | `SKILL.md` §Phase 0; ma trận chọn phase khi mở rộng harness | Trước mỗi lần chạy WF-GITHUB-RESEARCH/WF-MIGRATE: kiểm tra đã có branch/plan/artifact chưa, phát hiện drift, báo cáo trạng thái trước khi vào bước 1 | Tránh làm trùng; phát hiện inconsistency sớm; agent biết mình đang làm mới hay nối tiếp | Effort thấp: thêm pre-check step vào 2 workflow trong CLAUDE.md §4 |
| **P5** | **Skill trigger testing — should-trigger / should-NOT-trigger** | `skill-testing-guide.md` §7; `SKILL.md` §6-4 | Tạo skill mới `.claude/commands/skill-trigger-test.md`: với mỗi command/agent mới, chạy 8–10 should-trigger query và 8–10 near-miss (should-NOT-trigger) query để xác nhận routing | Phát hiện sớm trigger conflict; đảm bảo Dispatcher routing đúng; có checklist rõ ràng | Effort thấp: viết 1 command file mới; không đụng code hiện tại |
| **P6** | **Why-first writing — bỏ ALWAYS/NEVER, thay bằng giải thích lý do** | `skill-writing-guide.md` §2 Why-First Principle | Refactor phần nội dung trong agent/command file dùng ALWAYS/NEVER → thay bằng "làm X vì lý do Y, điều này giúp agent xử lý edge case Z đúng hơn" | LLM hiểu context sâu hơn, ít bị fail ở edge case; dễ maintain hơn | Effort trung bình: cần đọc lại từng file, không có risk phá vỡ behavior nếu viết đúng |
| **P7** | **Fan-out implementation guide với `run_in_background: true`** | `agent-design-patterns.md` §Fan-out/Fan-in; `orchestrator-template.md` §Sub-agent Mode | Thêm hướng dẫn kỹ thuật cụ thể cho notation `∥` trong CLAUDE.md §4: cách gọi song song bằng Agent tool với `run_in_background: true`, cách collect kết quả | Dispatcher và agent biết chính xác cách implement song song; tránh implement sai (tuần tự thay vì song song) | Effort thấp: chỉ thêm ghi chú kỹ thuật vào CLAUDE.md; không thay đổi logic |
| **P8** | **Changelog harness trong CLAUDE.md** | `SKILL.md` §5-4 và §7-3; template CLAUDE.md pointer | Thêm bảng "Lịch sử thay đổi agent/workflow" vào CLAUDE.md (tương tự bảng §10 đang có nhưng ở dạng compact table: ngày | nội dung | đối tượng | lý do) — để track harness evolution | Có audit trail rõ ràng khi agent system phát triển; phát hiện regression; onboarding dễ hơn | Effort rất thấp: chỉ thêm section vào CLAUDE.md; không cần thay đổi workflow |

---

## 4. Đánh giá mức độ ưu tiên áp dụng

| Nhóm | Đề xuất | Lý do ưu tiên cao |
|------|---------|------------------|
| Nên làm trước (low effort, high impact) | P3, P4, P7, P8 | Chỉ thêm/sửa văn bản trong CLAUDE.md và frontmatter; không rủi ro; tác động ngay lập tức |
| Nên làm tiếp theo (medium effort, medium–high impact) | P1, P5 | Cần viết 1 file mới hoặc thêm convention; không đụng code hiện tại |
| Có thể để sau (medium effort, long-term value) | P2, P6 | Cần refactor nhiều file; giá trị tích lũy theo thời gian; không urgency cao |

---

## 5. Thông tin repo nguồn

| Thuộc tính | Giá trị |
|-----------|---------|
| URL | https://github.com/revfactory/harness |
| License | Apache 2.0 |
| Version | 1.2.0 |
| Ngôn ngữ | Markdown (không có code runtime) |
| Target platform | Claude Code |
| Hỗ trợ ngôn ngữ | Tiếng Anh, Hàn Quốc, Nhật Bản |
| Độ trưởng thành | Đang phát triển tích cực, có CHANGELOG, có issue template, có PR template |

---

## 6. Trạng thái đề xuất

| # | Tên | Trạng thái |
|---|-----|-----------|
| P1 | `_workspace/` convention | ⬜ Chờ user duyệt |
| P2 | Progressive Disclosure | ⬜ Chờ user duyệt |
| P3 | "Pushy" description | ⬜ Chờ user duyệt |
| P4 | Phase 0 Audit | ⬜ Chờ user duyệt |
| P5 | Skill trigger testing | ⬜ Chờ user duyệt |
| P6 | Why-first writing | ⬜ Chờ user duyệt |
| P7 | Fan-out implementation guide | ⬜ Chờ user duyệt |
| P8 | Changelog harness trong CLAUDE.md | ⬜ Chờ user duyệt |

---

*Báo cáo tạo bởi GITHUB REPO RESEARCHER — nhánh `research/harness-2026-07-12` — 2026-07-12*
