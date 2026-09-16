# Architecture Report — Knowledge Agent MCP

> 生成日期：2026-07-12
> 执行阶段：Stage 2: Architecture Design
> 执行角色：Architect Agent

---

## 1. 目标架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│  MCP Client (OpenCode / 其他)                                    │
│  - 通过 stdio / SSE 传输调用工具                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ MCP Protocol (stdio / SSE)
┌──────────────────────────┴──────────────────────────────────────┐
│  Transport Layer (server.py)                                    │
│  - stdio (现有) / SSE (新增)                                    │
│  - 路由到 Application Layer                                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│  Application Layer (application.py / core.py)                   │
│  - 工具注册与路由 (list_tools, call_tool)                        │
│  - 请求验证与错误处理                                            │
│  - Agent 工作流编排                                              │
└──────┬──────────────────────────────────────┬───────────────────┘
       │                                      │
       ▼                                      ▼
┌──────────────┐  ┌──────────────────────────────────────────┐
│  Agent Layer  │  │  Retrieval Layer                          │
│  (agents/)    │  │  (retrieval/)                             │
│               │  │                                          │
│ query_planner │  │  KeywordSearch  VectorSearch  Reranker   │
│ retrieval_    │  │  MetadataFilter  ContextBuilder          │
│ agent         │  │  Deduplicator   KnowledgeRepository      │
│ result_       │  │                                          │
│ synthesizer   │  └──────────────────────────────────────────┘
└──────────────┘                      │
                                      ▼
┌──────────────────────────────────────────────────────────────┐
│  Data Layer                                                   │
│  SQLite (索引)  │  LLM Client  │  Embedding Provider          │
│  knowledge_base/ (只读 Markdown)                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. 分层目录结构（目标）

```
src/knowledge_agent_mcp/
├── __init__.py
├── server.py              # MCP Server 入口（传输层）
├── application.py         # 应用工厂 + 生命周期
├── core.py                # 轻量门面（委托到下层模块）
│
├── agents/                # Agent Layer
│   ├── __init__.py
│   ├── registry.py
│   ├── query_planner.py
│   ├── retrieval_agent.py
│   └── result_synthesizer.py
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── loader.py
│
├── exceptions/
│   ├── __init__.py
│   └── errors.py
│
├── indexing/
│   ├── __init__.py
│   ├── scanner.py
│   ├── markdown_parser.py
│   ├── metadata_parser.py
│   ├── chunker.py
│   ├── embedding_builder.py
│   └── index_builder.py   # 实现类（从 core 提取）
│
├── llm/
│   ├── __init__.py
│   ├── client.py          # Protocol
│   ├── provider.py        # Factory + 注册
│   └── structured_output.py
│
├── logging/
│   ├── __init__.py
│   └── logger.py
│
├── mcp_compat.py
├── mcp_tools/
│   ├── __init__.py
│   ├── consult_knowledge.py
│   ├── search_knowledge.py
│   ├── get_knowledge_item.py
│   └── get_related_knowledge.py
│
├── models/
│   ├── __init__.py
│   ├── knowledge_item.py
│   ├── consultation_request.py
│   └── search_request.py
│
├── repositories/
│   ├── __init__.py
│   ├── knowledge_repository.py  # 抽象接口
│   ├── sqlite_repository.py     # SQLite 实现
│   └── file_repository.py
│
└── retrieval/
    ├── __init__.py
    ├── retrieval_service.py     # 检索编排（从 core 提取）
    ├── keyword_search.py
    ├── vector_search.py         # 接入真实 Embedding
    ├── metadata_filter.py
    ├── deduplicator.py
    ├── reranker.py
    └── context_builder.py
```

---

## 3. 模块依赖关系

```
server.py → application.py → core.py
                                ├── agents/
                                ├── retrieval/
                                ├── repositories/
                                ├── indexing/
                                ├── llm/
                                ├── models/
                                └── config/
```

### 各模块当前 vs 目标状态

| 模块 | 当前状态 | 目标状态 |
|------|---------|---------|
| `server.py` | 仅 stdio | stdio + SSE |
| `application.py` | 一行工厂 | 完整 DI 组装 |
| `core.py` | ~650 行单体 | 轻量门面，委托到下层 |
| `agents/` | 空 dataclass | 含规则的 Agent 类 |
| `indexing/` | 部分实现 | index_builder 完整实现 |
| `repositories/` | 空协议 | SQLite 完整实现 |
| `retrieval/` | 空 dataclass | 从 core 提取的完整实现 |
| `llm/` | 全部抛异常 | 支持 provider 切换 + fallback |

---

## 4. LLM 架构

```
LLMClient (Protocol)
├── OpenCodeSDKProvider     # 通过 OpenCode 运行时
├── OpenRouterHTTPProvider  # 直接 HTTP 调用
└── FallbackRuleEngine      # 规则降级（兜底）
```

Provider 选择：`KNOWLEDGE_AGENT_LLM_PROVIDER` 环境变量 → opencode / openrouter → 规则降级

Agent 使用 LLM 的场景及降级：

| Agent | LLM 场景 | 降级 |
|-------|---------|------|
| query_planner | 关键词扩展 | 规则内置固定扩展词 |
| retrieval_agent | 任务阶段推断 | 规则关键词匹配 |
| result_synthesizer | 摘要、冲突检测 | 截取前 N 行 |

---

## 5. Embedding 架构

```
EmbeddingProvider (Protocol)
├── DeterministicTokenVector  # 词频（零依赖降级）
├── RemoteEmbeddingAPI        # HTTP 调用外部 API
└── LocalEmbeddingModel       # 本地 ONNX
```

持久化：`knowledge_chunks` 表新增 embedding 列，或独立 `embedding_index` 表

---

## 6. 检索流程

```
search_knowledge(query, filters)
  ├── KeywordSearch.search         → keyword_score
  ├── VectorSearch.search          → vector_score
  ├── MetadataFilter.filter        → filtered
  ├── Reranker.rerank              → scored
  └── Deduplicator.deduplicate     → unique

consult_knowledge(task, stage)
  ├── QueryPlanner.build_plan      → queries
  ├── for query: search_knowledge  → batches
  ├── RetrievalAgent.deduplicate   → merged
  ├── ResultSynthesizer.synthesize → structured
  └── ContextBuilder.build         → final
```

---

## 7. 配置扩展

`settings.yaml` 新增字段：

```yaml
llm:
  provider: opencode         # opencode / openrouter / none
  model: opencode/gpt-5.4-mini
  temperature: 0.1
  timeout_seconds: 60

embedding:
  provider: local            # local / remote / deterministic
  model: deterministic-token-vector
  dimension: 0
  batch_size: 32

server:
  transports: ["stdio"]
  sse_host: "127.0.0.1"
  sse_port: 8765
```

---

## 8. 关键技术决策

| # | 决策 | 方案 | 理由 |
|---|------|------|------|
| ADR-1 | LLM | 接口 + 多 Provider + 规则降级 | 逐步接入，始终可用 |
| ADR-2 | Embedding | 接口 + 词频降级 + 逐步替换 | 零依赖起步 |
| ADR-3 | 核心拆分 | 拆入 retrieval/ + repositories/ | 解决单体问题 |
| ADR-4 | Agent | 规则优先 + LLM 增强 | 稳定优先 |
| ADR-5 | 传输层 | 先 SSE，后 StreamableHTTP | 兼容最广 |
| ADR-6 | 索引 | SQLite + 嵌入持久化 | 零依赖 |
| ADR-7 | 配置 | YAML + Pydantic | 当前够用 |

---

## 9. 迁移路径

### Phase 1 (→v0.2.0) 基础设施
1. `repositories/sqlite_repository.py` — 从 core 提取 SQLite
2. `indexing/index_builder.py` — 从 core 提取索引构建
3. `retrieval/retrieval_service.py` — 从 core 提取搜索排序
4. `core.py` 降为门面

### Phase 2 (→v0.3.0) AI 能力
1. LLM Provider (OpenCode / OpenRouter)
2. Agent LLM 调用
3. Embedding Provider + 持久化

### Phase 3 (→v0.4.0) 传输层
1. SSE 支持
2. 传输配置化
3. 多传输共存

---

## 10. 出口条件

| 条件 | 状态 |
|------|------|
| 架构报告已写入 `reports/architecture/` | ✅ |
| 目标目录结构已确定 | ✅ |
| Metadata 规范已定稿 | ✅ |
| 索引策略已设计 | ✅ |
| 迁移路径已规划 | ✅ |

---

*本报告供下游 Planner Agent 使用。*
