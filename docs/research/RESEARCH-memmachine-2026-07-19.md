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

## 8. Trạng thái áp dụng đề xuất

*(Sẽ điền sau khi Phase 2 — đề xuất — hoàn thành và user xác nhận)*

| # | Đề xuất | Trạng thái |
|---|---------|-----------|
| - | - | Chờ Phase 2 |
