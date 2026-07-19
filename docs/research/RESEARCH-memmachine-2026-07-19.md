---
title: "Nghiên cứu repo: MemMachine/MemMachine"
repo_url: https://github.com/MemMachine/MemMachine
research_date: 2026-07-19
researcher: github-repo-researcher
workflow: WF-GITHUB-RESEARCH
branch: research/memmachine-2026-07-19
status: analysis-complete
---

# RESEARCH: MemMachine/MemMachine

## 1. Tổng quan repo

### Mục đích

MemMachine là một **memory layer mã nguồn mở dành cho AI agents và ứng dụng LLM**. Mục tiêu cốt lõi là giải quyết vấn đề "stateless AI" — tức là chatbot/agent quên toàn bộ ngữ cảnh khi kết thúc session — bằng cách cung cấp lớp lưu trữ bộ nhớ bền vững, có thể tìm kiếm ngữ nghĩa.

Tagline: *"Stop building stateless agents. Give your AI persistent memory with just 5 lines of code."*

### Đối tượng sử dụng

- Developers xây dựng AI agents, assistants, autonomous workflows.
- Researchers thực nghiệm với kiến trúc agent và cognitive model.
- Teams cần cross-session memory cho LLM applications.

### Vấn đề giải quyết

| Vấn đề | Giải pháp MemMachine |
|--------|---------------------|
| AI quên toàn bộ sau mỗi session | Episodic memory lưu graph các hội thoại |
| Không nhớ sở thích/thông tin user | Profile memory (SQL) lưu facts dài hạn |
| RAG chỉ phù hợp kiến thức tĩnh | Kết hợp RAG + semantic memory động |
| Phải gửi toàn bộ lịch sử vào context | Truy xuất thông minh — chỉ lấy phần liên quan |

---

## 2. Cấu trúc dự án

```
MemMachine/
├── packages/
│   ├── server/          ← Server Python (FastAPI + bộ nhớ)
│   │   └── src/memmachine_server/
│   │       ├── semantic_memory/   ← Engine semantic/profile memory
│   │       │   ├── semantic_memory.py        ← SemanticService (coordinator)
│   │       │   ├── semantic_ingestion.py     ← Pipeline chuyển episodes→features
│   │       │   ├── semantic_llm.py           ← LLM calls (feature update/consolidate)
│   │       │   ├── semantic_model.py         ← Data models (SemanticFeature, SemanticCommand)
│   │       │   ├── cluster_manager.py        ← Quản lý cluster features
│   │       │   ├── storage/
│   │       │   │   ├── storage_base.py           ← Interface trừu tượng SemanticStorage
│   │       │   │   ├── sqlalchemy_pgvector_semantic.py  ← PostgreSQL + pgvector
│   │       │   │   └── neo4j_semantic_storage.py ← Neo4j graph storage
│   │       │   ├── cluster_store/            ← Phân cụm features theo ngữ nghĩa
│   │       │   └── config_store/             ← Cấu hình per-set-id (embedder, LLM, categories)
│   │       ├── server/
│   │       │   ├── app.py                    ← FastAPI app setup
│   │       │   ├── api_v2/
│   │       │   │   ├── router.py             ← REST endpoints
│   │       │   │   ├── service.py            ← Service layer
│   │       │   │   └── mcp.py                ← MCP server (stdio + HTTP)
│   │       │   └── prompt/                   ← System prompts cho từng use case
│   │       └── main/
│   │           └── memmachine.py             ← MemMachine (entry point chính)
│   ├── client/          ← Python SDK client
│   ├── common/          ← Shared API spec (Pydantic models)
│   ├── ts-client/       ← TypeScript SDK
│   └── meta/            ← Meta package
├── integrations/        ← Connectors cho LangChain, CrewAI, LlamaIndex...
│   ├── langchain/
│   ├── langgraph/
│   ├── crewai/
│   ├── llamaindex/
│   └── aws_strands_agent_sdk/
├── docs/                ← Tài liệu Mintlify
├── examples/            ← Demo agents (CRM, Healthcare, Finance, Writing)
├── evaluation/          ← Eval harness đo retrieval quality
├── deployments/         ← Helm charts, Kubernetes
└── docker-compose.yml   ← Quick start stack
```

---

## 3. Phân tích kỹ thuật

### 3.1 Ba loại bộ nhớ cốt lõi

MemMachine hiện thực ba tầng memory riêng biệt, phản ánh mô hình nhận thức của con người:

**Working Memory (Short-Term)**
- Ngữ cảnh của session hiện tại — lịch sử hội thoại gần nhất.
- Không persistent, chỉ tồn tại trong session.

**Episodic Memory (Long-Term — Graph-based)**
- Lưu trữ các episode hội thoại cụ thể dưới dạng graph (Neo4j).
- Hỗ trợ cả `short_term` (recent N messages) và `long_term` (summarized).
- `EpisodeStorage` là interface trừu tượng — dễ swap backend.

**Semantic/Profile Memory (Long-Term — SQL + Vector)**
- Trích xuất facts và sở thích từ hội thoại (VD: "Alice thích ghế aisle trên máy bay").
- Lưu vào PostgreSQL với pgvector extension để tìm kiếm semantic.
- Được tổ chức theo `set_id` (mỗi user/agent/session có set riêng).
- Có thể tìm theo vector similarity (cosine distance).

### 3.2 Kiến trúc tổng thể

```
Agent/App
    │
    ▼
[API Layer]  ─── REST v2 ─── FastAPI
             ─── Python SDK ─── MemMachineClient
             ─── MCP Server ─── Stdio / HTTP (Claude Desktop, Cursor...)
    │
    ▼
[MemMachine Core]  (packages/server/src/memmachine_server/main/memmachine.py)
    │
    ├── EpisodeStorage  (Neo4j graph)     ← Episodic memory
    └── SemanticService (PostgreSQL+pgvector) ← Semantic/Profile memory
            │
            └── [Background Ingestion Task]
                    │
                    └── IngestionService
                            │
                            ├── Pull un-ingested episodes
                            ├── LLM call → generate SemanticCommands (ADD/DELETE)
                            ├── Apply commands to vector store
                            └── Consolidate redundant features (LLM call)
```

### 3.3 Ingestion Pipeline — Pattern nổi bật

File: `packages/server/src/memmachine_server/semantic_memory/semantic_ingestion.py`

Pattern quan trọng nhất trong MemMachine là **background ingestion**:

1. Agent gửi episode (hội thoại) vào MemMachine qua `add_episodes()`.
2. Background task chạy định kỳ (mặc định 2 giây) — kiểm tra set_id nào có `uningested_messages >= 5` HOẶC `age >= 5 phút`.
3. Với mỗi set_id "dirty", `IngestionService`:
   - Pull các episode chưa ingest từ EpisodeStorage.
   - Gửi cho LLM để sinh danh sách `SemanticCommand` (ADD/DELETE feature).
   - Apply commands vào vector store.
   - Nếu số feature vượt ngưỡng (threshold=20) → LLM consolidation (gộp/xoá duplicate).
4. Purge các row đã ingest để tránh xử lý lại.

Backoff mechanism khi lỗi: `backoff_sec = min(backoff_sec * 2, 60.0)` — tránh hammering LLM/DB khi có sự cố.

**Điểm mạnh:** Không blocking — agent tiếp tục làm việc, ingestion chạy ngầm. Khi search, vector store đã "fresh" nhờ background job.

### 3.4 Search — Parallel Vector Search

File: `packages/server/src/memmachine_server/semantic_memory/semantic_memory.py`, hàm `search()`:

```python
# Tạo iterators cho mỗi set_id (song song)
iterators = [
    self._set_id_search(set_id=set_id, embedding=embeddings[set_id], ...)
    for set_id in set_ids
]
# Merge và yield kết quả ngay khi có
async for feature in merge_async_iterators(iterators):
    yield feature
```

Khi search nhiều set_id cùng lúc (VD: search cả user-profile + agent-profile), hệ thống fan-out song song và merge kết quả streaming — không chờ từng cái xong mới xử lý tiếp.

### 3.5 Category System — Cấu trúc phân loại memory

Memory được tổ chức theo "category" (VD: "travel preferences", "dietary restrictions"):
- Mỗi set_id có danh sách category riêng (có thể clone từ default hoặc tạo mới).
- Mỗi category có `prompt` hướng dẫn LLM trích xuất loại thông tin nào.
- Tag system cho phép phân loại chi tiết hơn trong một category.
- Config được cache (pattern `caching_semantic_config_storage.py`) để tránh DB query liên tục.

### 3.6 MCP Server — Tích hợp Claude Desktop/Cursor

File: `packages/server/src/memmachine_server/server/api_v2/mcp.py`

MemMachine cung cấp native MCP server (dùng `fastmcp`):
- `memmachine-mcp-stdio`: cho Claude Desktop, chạy qua stdin/stdout.
- `memmachine-mcp-http`: cho web clients.

MCP tools expose: `add_memory`, `search_memory`, `delete_memory` — agent LLM có thể gọi trực tiếp các tools này trong conversation.

### 3.7 Multi-Framework Integration

Integrations sẵn có cho: LangChain, LangGraph, CrewAI, LlamaIndex, AWS Strands, n8n, Dify, FastGPT. Tất cả đều wrap Python SDK hoặc REST API.

### 3.8 Điểm mạnh / Điểm yếu

**Điểm mạnh:**
- LLM-agnostic hoàn toàn (OpenAI, Anthropic, Bedrock, Ollama).
- Self-hosted được (Docker, Kubernetes) hoặc dùng managed cloud.
- Python SDK rất clean (`5 lines of code` là thật — xem README).
- MCP native — tích hợp trực tiếp vào Claude Desktop.
- Background ingestion không blocking.
- Category system linh hoạt — tự định nghĩa schema memory.

**Điểm yếu:**
- Yêu cầu infra phức tạp (Neo4j + PostgreSQL + pgvector).
- LLM call ở mỗi ingestion cycle tốn token — chi phí cao nếu volume lớn.
- Không có TTL (Time-To-Live) tự động cho memory cũ — cần tự quản lý.
- Latency ingestion (2 giây poll) — không realtime.

---

## 4. Công nghệ / Stack

| Thành phần | Công nghệ |
|---|---|
| Backend server | Python 3.12+, FastAPI, asyncio |
| Package manager | uv (UV workspace monorepo) |
| Episodic memory storage | Neo4j (graph database) |
| Semantic memory storage | PostgreSQL + pgvector |
| DB migrations | Alembic |
| Embeddings | Configurable (OpenAI, Bedrock, Ollama, local) |
| LLM | Configurable (OpenAI, Anthropic, Bedrock, Ollama) |
| SDK | Python + TypeScript |
| MCP server | fastmcp |
| Containerization | Docker, Docker Compose, Kubernetes (Helm) |
| Lint/Format | Ruff |
| Type check | ty |
| Test | pytest + pytest-asyncio, testcontainers |
| Code quality | complexipy (complexity checker) |

---

## 5. Thông tin repo

| Thuộc tính | Giá trị |
|---|---|
| License | Apache 2.0 |
| Ngôn ngữ chính | Python (server/SDK), TypeScript (ts-client) |
| Python version | 3.12+ |
| Hoạt động gần đây | Clone depth=1 — repo đang được phát triển tích cực (có alembic migrations gần đây, nhiều phiên bản) |
| MCP support | Native (stdio + HTTP) |
| Cloud option | Có — console.memmachine.ai |

---

## 6. Hiện trạng KZTEK

### Cơ chế "memory" hiện tại của KZTEK

KZTEK hiện không có AI memory layer. Workspace này là hệ thống AI Agent Creator — các agent (Claude Code) chạy trong session ngắn, không có persistence cross-session ngoại trừ:

**Cơ chế hiện có:**

| Cơ chế | File | Mục đích |
|---|---|---|
| Handoff Log | `.claude/plans/PLAN-*.md` (mục `## Handoff Log`) | Agent bước N ghi tóm tắt → bước N+1 đọc để không phải nghiên cứu lại. File-based, trong git. |
| Progress Ledger | `_workspace/progress.md` (git-ignored) | Append-only log nhẹ cho mỗi bước — phục hồi nhanh khi session compact/restart. |
| GOTCHAS.md | `.claude/GOTCHAS.md` | Ghi lại lỗi ngầm đã gặp — "long-term memory" dạng human-curated. |
| Plan File | `.claude/plans/PLAN-*.md` | Tiến độ task, trạng thái từng bước, artifacts. Là "working memory" có cấu trúc. |

**Không có:**
- Lưu trữ hội thoại cross-session (mỗi session bắt đầu từ đầu).
- Profile agent (agent không nhớ style/preference của user vietanh@kztek.vn từ session trước).
- Vector search trên lịch sử tương tác.
- Graph relationship giữa các concept đã thảo luận.
- MCP server riêng cho memory.

Tóm lại: KZTEK dùng file markdown + git làm "bộ nhớ dài hạn" — đủ cho workflow tài liệu/code, nhưng không có semantic retrieval hay user profiling.

---

## 7. So sánh: MemMachine vs Hiện trạng KZTEK

| Điểm so sánh | MemMachine | KZTEK hiện tại |
|---|---|---|
| Persistence cross-session | Graph DB (Neo4j) + SQL (PostgreSQL) | Plan file .md trong git, đọc thủ công |
| User profiling | Profile memory — facts/preferences per user | Không có |
| Semantic search | Vector similarity (pgvector) | Không có — chỉ Grep/Read text thuần |
| Ingestion | Background pipeline, LLM-driven | Thủ công — Handoff Log viết bởi agent |
| Recovery khi context compact | Không áp dụng | _workspace/progress.md (file nhẹ, append-only) |
| Loại thông tin lưu | Episodes (hội thoại) + semantic features | Bước task, artifact, lỗi đã biết |
| MCP integration | Native MCP server | Không có |
| Infrastructure cần thiết | Neo4j + PostgreSQL + LLM | Chỉ git + filesystem |

---

## 8. Bảng đề xuất cải tiến

> Mỗi đề xuất rút ra từ pattern cụ thể trong MemMachine và đối chiếu với hiện trạng KZTEK. KHÔNG tự áp dụng — chờ user xác nhận ở Bước 2.2.

| # | Đề xuất | Hiện trạng KZTEK (đang có gì / chưa có gì) | Học từ đâu (file/pattern cụ thể trong repo nguồn) | Lý do thay đổi (vấn đề/khoảng trống cụ thể ở hiện trạng) | Áp dụng vào đâu trong KZTEK (file/agent/skill cụ thể) | Đạt được gì (kết quả cụ thể, quan sát/đo được) | Rủi ro/Effort |
|---|---------|------|------|------|------|------|------|
| E1 | **Category tagging cho GOTCHAS.md** — thêm thẻ category vào mỗi entry và bảng lọc nhanh theo loại lỗi ở đầu file | GOTCHAS.md hiện có mục lục phẳng (G001, G002...) không phân loại theo domain — chỉ có số thứ tự và tên vấn đề ngắn. Khi số entry tăng, agent phải đọc tuần tự để tìm entry liên quan đến loại lỗi cụ thể | `packages/server/src/memmachine_server/semantic_memory/config_store/` — mỗi set_id có danh sách category (VD: "travel preferences", "dietary restrictions") với `prompt` hướng dẫn trích xuất thông tin đúng loại. Pattern: phân loại trước → tìm kiếm theo category thay vì scan toàn bộ | GOTCHAS.md với 1 entry duy nhất (G001) hiện không cần phân loại. Nhưng khi có 10+ entries, Dispatcher phải đọc toàn bộ file để tìm, ví dụ, "tất cả lỗi script". Hiện không có cách lọc theo loại lỗi mà không đọc hết | `.claude/GOTCHAS.md` — thêm (a) bảng lọc nhanh ở đầu file với cột "Category" (`[SCRIPT]`, `[GIT]`, `[AGENT-LOOP]`, `[CONFIG]`, `[NETWORK]`), và (b) thêm dòng `Category:` vào header của mỗi entry mới. Template entry ở comment cuối file cũng cập nhật | Khi agent gặp `ModuleNotFoundError`, tra GOTCHAS.md theo category `[SCRIPT]` thay vì đọc tất cả entries — tìm đúng entry trong 1 bước thay vì scan N entries. Với 10+ entries, giảm số dòng cần đọc từ ~100% xuống ~30% (chỉ đọc đúng category) | Rủi ro: thấp — chỉ thêm metadata vào file text, không đổi logic. Effort: thấp — sửa template comment + bảng lọc ở GOTCHAS.md, 1 file duy nhất |
| E2 | **Threshold rule cho plan files cũ** — định nghĩa ngưỡng archive tự động cho `.claude/plans/PLAN-*.md` đã hoàn thành | `.claude/plans/` không có chính sách cleanup. Các PLAN-*.md status=done/completed tích lũy vô thời hạn. Hiện có khoảng 2-3 plan files (ít vì workspace còn mới); chưa gây vấn đề. Không có rule nào trong CLAUDE.md hay task-planner về archiving | `packages/server/src/memmachine_server/semantic_memory/semantic_ingestion.py`, hàm `_consolidate_features()` — khi `feature_count > threshold (20)` → gọi LLM consolidation gộp/xoá entries thừa. Pattern: kiểm tra số lượng theo ngưỡng → hành động dọn dẹp | `Glob ".claude/plans/PLAN-*.md"` ở Pre-0 sẽ trả nhiều file hơn theo thời gian. Task-planner phải đọc metadata của từng file để tìm plan liên quan. Nếu có 20+ plans, scan tốn ~10-20 dòng đọc thêm mỗi session. Không có gì ngăn plans Done tích lũy mãi | `CLAUDE.md §16` (Quản lý Plan File) — thêm rule: "Khi `.claude/plans/` có ≥ 5 plan với `status: done` và `updated` cũ hơn 7 ngày → task-planner move chúng vào `.claude/plans/archive/`". Và `.claude/templates/PLAN-template.md` — thêm ghi chú về lifecycle | Dispatcher Pre-0 chỉ Glob được 1-4 active plans thay vì 20+ tổng cộng. Thời gian plan lookup ổn định (không tăng theo số task đã xong). Sau 10+ tasks hoàn thành, số file ở `.claude/plans/` giữ ổn định ≤ 5 (active) thay vì tăng tuyến tính | Rủi ro: thấp-trung bình — cần định nghĩa "done" rõ ràng để không archive plan đang dùng. Effort: thấp — chỉ thêm 3-4 dòng rule vào CLAUDE.md §16 và ghi chú vào PLAN-template.md; không thay đổi code |
| E3 | **Handoff Log pruning khi vượt ngưỡng** — thêm rule giới hạn kích thước Handoff Log để tránh phình context window ở task nhiều bước | Handoff Log trong PLAN-*.md là append-only (CLAUDE.md §16.5: "KHÔNG xoá entry cũ"). Template không có giới hạn số entry. Trên task dài (10+ bước), Handoff Log có thể dài 500-1000 từ — toàn bộ được nhúng vào prompt của mỗi subagent mới, kể cả phần bước cũ không còn liên quan | `packages/server/src/memmachine_server/semantic_memory/semantic_ingestion.py` — sau khi process episodes, `_purge_ingested_episodes()` xoá các row đã xử lý xong: "Purge các row đã ingest để tránh xử lý lại". Pattern: giữ chỉ dữ liệu "còn giá trị" thay vì giữ lại mãi mãi | Bước N+1 cần đọc Handoff Log để biết bối cảnh — nhưng thực tế chỉ cần biết 2-3 bước gần nhất và các "cảnh báo còn hiệu lực". Entries của bước 1-3 trong task 15 bước thường không còn liên quan đến bước 13-15. Nhúng toàn bộ vào prompt mỗi lần = token lãng phí | `CLAUDE.md §16.5 Bước 4` và `.claude/templates/PLAN-template.md` — thêm rule: "Khi Handoff Log có > 7 entries, task-planner tóm tắt các entry từ 1 đến (N-3) thành 1 block `[ARCHIVED SUMMARY]` ngắn (≤ 5 dòng), giữ nguyên 3 entry cuối đầy đủ chi tiết. Bước sau chỉ nhận 3 entries mới nhất + 1 summary khối cũ" | Prompt của subagent bước N không vượt quá ~300 từ Handoff Log bất kể task có bao nhiêu bước. Trên task 15 bước, giảm Handoff Log từ ~900 từ xuống ~350 từ (60% giảm) — trực tiếp giảm context window mỗi subagent dùng, giúp task dài không bị auto-compact giữa chừng | Rủi ro: trung bình — cần rule tóm tắt rõ ràng để không mất thông tin quan trọng. Nếu bước cũ có "gotcha" vẫn còn hiệu lực, summary có thể bỏ sót. Effort: thấp-trung — thêm rule vào CLAUDE.md §16.5 và PLAN-template.md; không cần thay đổi tool/code, chỉ quy trình |
| E4 | **Exponential backoff timing cụ thể cho §9a Phase 3** — thêm hướng dẫn chờ có thời gian cụ thể trước khi retry khi gặp lỗi thoáng qua | CLAUDE.md §9a Phase 3 "Contained Recovery" chỉ ghi "Thử 1 hành động nhỏ nhất có thể giải quyết vấn đề" — không có hướng dẫn chờ bao lâu hay tăng thời gian chờ theo số lần retry. Với lỗi thoáng qua (network timeout, file lock), retry ngay lập tức thường thất bại ngay lần 2 vì điều kiện chưa thay đổi | `packages/server/src/memmachine_server/semantic_memory/semantic_ingestion.py`: `except Exception: backoff_sec = min(backoff_sec * 2, 60.0); await asyncio.sleep(backoff_sec)` — khởi đầu từ 2 giây, mỗi lỗi nhân đôi (2→4→8→16→32→60), trần 60 giây. Tránh hammering external service khi có sự cố thoáng qua | §9a hiện không phân biệt lỗi cấu trúc (sai path, thiếu dependency — không ích gì khi chờ) với lỗi thoáng qua (network timeout, process lock, rate limit — chờ rồi retry có thể giải quyết). Thiếu guidance này khiến agent hoặc retry quá nhanh (lãng phí turn) hoặc dừng hẳn khi nên chờ | `CLAUDE.md §9a Phase 2 — Diagnose` và `Phase 3 — Contained Recovery` — bổ sung: (a) Phase 2 thêm phân loại lỗi: "transient" (network/timeout/lock/rate-limit → chờ có thể giúp) vs "structural" (path sai/thiếu dependency → chờ không giúp); (b) Phase 3 thêm: "Với lỗi transient: chờ N giây trước khi thử (N = 2 × số lần đã retry, trần 30 giây) — KHÔNG retry ngay lập tức" | Khi gặp rate-limit hoặc network timeout, agent chờ 2 giây trước lần thử đầu, 4 giây nếu vẫn fail — thay vì retry 3 lần liên tiếp ngay. Trong thực tế, lỗi thoáng qua thường giải quyết sau 2-8 giây; agent tiết kiệm 1-2 turn failed so với retry-ngay. Ngược lại, lỗi cấu trúc → không chờ, báo Phase 4 ngay (không lãng phí 30 giây wait vô ích) | Rủi ro: rất thấp — chỉ thêm hướng dẫn timing vào văn bản CLAUDE.md, không thay đổi logic bắt buộc nào. Effort: rất thấp — thêm ~4-5 dòng vào §9a Phase 2 và Phase 3 |

---

## 9. Trạng thái áp dụng đề xuất

*(Điền sau khi user xác nhận ở Bước 2.2)*

| # | Đề xuất | Trạng thái |
|---|---------|-----------|
| E1 | Category tagging cho GOTCHAS.md | Chờ user xác nhận |
| E2 | Threshold rule cho plan files cũ | Chờ user xác nhận |
| E3 | Handoff Log pruning khi vượt ngưỡng | Chờ user xác nhận |
| E4 | Exponential backoff timing cụ thể cho §9a Phase 3 | Chờ user xác nhận |
