---
step: 2.1
plan: ../PLAN-MASTER.md
agent: github-repo-researcher
status: done
completed_at: 2026-08-04 10:30
---

# STEP 2.1 — Clone repo & Phân tích cấu trúc

## Input nhận
Handoff từ STEP-1.2: nhánh `research/gitnexus-2026-08-04` đã tạo và push.

## Nhiệm vụ
Clone repo https://github.com/abhigyanpatwari/GitNexus về thư mục scratchpad (ngoài working tree KZTEK), đọc và phân tích cấu trúc: mục đích, tech stack, kiến trúc, điểm nổi bật kỹ thuật, pattern đáng chú ý.

## Definition of Done
- [ ] Clone thành công về scratchpad (KHÔNG vào working tree KZTEK)
- [ ] Đọc README, cấu trúc thư mục, file config chính, entry point
- [ ] Ghi chú sơ bộ: mục đích repo, tech stack, kiến trúc, điểm nổi bật
- [ ] Cập nhật step file này và MASTER (status → ✅)

## Đã làm
- Clone `git clone --depth 1 https://github.com/abhigyanpatwari/GitNexus` vào scratchpad
- Scratchpad path: `C:\Users\nguye\AppData\Local\Temp\claude\...\scratchpad\research\gitnexus`
- Lỗi nhỏ: một số file test fixture bị skip do Windows MAX_PATH (path quá dài) — chỉ ảnh hưởng fixtures trong `test/fixtures/lang-resolution/`, core source OK
- Đọc: README.md (full), ARCHITECTURE.md (full), AGENTS.md (60 dòng đầu), package.json, communities.ts, .claude/skills/gitnexus-impact-analysis/SKILL.md

## Artifact
- Repo đã clone tại scratchpad (NGOÀI working tree KZTEK — không commit .git của repo ngoài)

## Quyết định quan trọng
- Không đọc thêm source khi README + ARCHITECTURE đã đủ context để phân tích
- Đọc thêm hiện trạng KZTEK: `code-graph/CODE-GRAPH.md` để so sánh

## Handoff Log — bước sau cần biết
- Đã làm: Clone thành công, đọc 6 file chính từ repo nguồn + 1 file hiện trạng KZTEK
- Tech stack: TypeScript + Tree-sitter + LadybugDB + Leiden + MCP protocol
- Kiến trúc: monorepo (gitnexus/ CLI+MCP, gitnexus-web/ UI, gitnexus-shared/ types)
- Pipeline: 19-phase DAG (scan → parse → scope-resolution → communities → processes)
- 17 MCP tools: impact, context, query (BM25+vector hybrid), detect_changes, trace, rename, cypher...
- KZTEK hiện tại: CODE-GRAPH.md thủ công, không có MCP server, không có automated indexing
- License: PolyForm Noncommercial — KHÔNG dùng commercial
- Bước sau cần biết: Viết phân tích vào docs/research/RESEARCH-gitnexus-2026-08-04.md

## Commit
- Hash: (commit chung với bước 2.2)
- Đã push: không

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
