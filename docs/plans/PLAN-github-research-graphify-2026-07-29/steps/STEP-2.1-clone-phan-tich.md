---
step: "2.1"
plan: ../PLAN-MASTER.md
agent: github-repo-researcher
status: done
completed_at: "2026-07-29 13:49"
---

# STEP 2.1 — Clone repo về scratchpad & phân tích

## Input nhận
Từ Bước 1.1 — Handoff Log sẽ được nhúng vào đây khi giao việc (tên nhánh đã tạo, mode nếu đã xác định).

## Nhiệm vụ
Clone repo `https://github.com/Graphify-Labs/graphify` về thư mục scratchpad (NGOÀI working tree KZTEK). Đọc và phân tích toàn bộ: mục đích repo, stack công nghệ, cấu trúc thư mục, các module/thành phần chính, điểm nổi bật kỹ thuật (pattern, design decision, algo đặc biệt...). Ghi chú phân tích vào `_workspace/` để dùng cho Bước 2.2.

## Definition of Done
- [ ] Repo đã clone về scratchpad: `/tmp/claude-0/-home-user-claude/e57c930e-1f04-57e6-bd23-935399a30b38/scratchpad/graphify/`
- [ ] Đã đọc README, package.json/pyproject.toml/go.mod (tùy stack), cấu trúc thư mục cấp 1-2
- [ ] Đã đọc ít nhất 3-5 file source chính để hiểu pattern/architecture
- [ ] Ghi chú phân tích vào `_workspace/02_researcher_graphify-notes.md` (thư mục `_workspace/` trong project KZTEK)
- [ ] Cập nhật step file này (Đã làm, Handoff Log, commit hash, status: done, completed_at)
- [ ] Cập nhật đúng 1 dòng status trong PLAN-MASTER.md (⬜ → ✅)

## Đã làm
1. Clone repo `https://github.com/Graphify-Labs/graphify` về `/tmp/claude-0/-home-user-claude/e57c930e-1f04-57e6-bd23-935399a30b38/scratchpad/research/graphify/` (depth 1, ngoài working tree KZTEK).
2. Đọc README.md (856 dòng), pyproject.toml (149 dòng), ARCHITECTURE.md (85 dòng), skill.md (703 dòng), AGENTS.md, always_on/claude-md.md, extractors/csharp.py.
3. Xem cấu trúc thư mục: `graphify/` package (50+ files), `graphify/extractors/` (20 language-specific extractors), `graphify/skills/` (per-platform), `tests/`, `worked/`, `docs/`.
4. Đọc hiện trạng KZTEK: `code-graph/CODE-GRAPH.md` (214 dòng — flat Markdown, không query được, cập nhật thủ công).
5. Ghi chú phân tích đầy đủ vào `_workspace/02_researcher_graphify-notes.md`.

## Artifact
- `_workspace/02_researcher_graphify-notes.md` — ghi chú phân tích nháp (không commit vào git, ~200 dòng đầy đủ)

## Quyết định quan trọng
Không có — đây là bước đọc/phân tích thuần túy, không có quyết định kỹ thuật.

## Handoff Log — bước sau cần biết

- **Đã làm:** Clone + đọc README/ARCHITECTURE/skill.md/pyproject.toml/extractors/always_on/hiện trạng KZTEK. Ghi đầy đủ vào `_workspace/02_researcher_graphify-notes.md`.
- **File/module đã đọc:**
  - Repo ngoài: `scratchpad/research/graphify/README.md`, `pyproject.toml`, `ARCHITECTURE.md`, `AGENTS.md`, `graphify/skill.md`, `graphify/always_on/claude-md.md`, `graphify/extractors/csharp.py`, `ls graphify/` + `ls graphify/extractors/` + `ls graphify/always_on/` + `ls graphify/skills/`
  - KZTEK: `code-graph/CODE-GRAPH.md`
- **Stack chính của Graphify:** Python 3.10+, NetworkX (graph), tree-sitter AST (code extraction — local, no LLM), Leiden (community detection), LLM pluggable cho docs/PDFs/images. PyPI: `graphifyy` v0.9.29. License Apache-2.0. YC S26.
- **Pipeline:** detect → extract → build_graph → cluster → analyze → report → export. Mỗi stage độc lập, giao tiếp qua plain dicts.
- **5 điểm kỹ thuật nổi bật:**
  1. Real graph traversal (KHÔNG vector/embeddings) — `query`, `path A B`, `explain X`
  2. Parallel subagent dispatch (Agent tool, cùng 1 message) cho semantic extraction — giống ∥ pattern KZTEK §4
  3. Semantic cache by file hash + prompt hash — incremental `--update`
  4. `graphify claude install` inject always-on block vào CLAUDE.md — agent tự query graph trước khi đọc files
  5. PR dashboard + graph impact (`graphify prs`) — kết nối git workflow với graph
- **Hiện trạng KZTEK:** `code-graph/CODE-GRAPH.md` là flat Markdown, cập nhật thủ công bởi agents, không query được, không community detection, không auto-update. Value graphify sẽ thể hiện rõ nhất khi có product codebase C# thực tế (KztekComponent + project sản phẩm). Hiện workspace chỉ có agent framework config.
- **Bước sau cần biết:** KHÔNG cần đọc lại repo scratchpad — toàn bộ thông tin cần thiết đã tóm tắt ở `_workspace/02_researcher_graphify-notes.md`. Bước 2.2 chỉ cần đọc file đó để viết báo cáo chính thức.

## Commit
- Hash: 84cf140
- Đã push: có

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
