# Migration Plan — Knowledge Agent MCP

> 生成日期：2026-07-12
> 执行阶段：Stage 3: Migration Planning
> 执行角色：Planner Agent

---

## 1. Phase 1 任务列表（v0.1.0 → v0.2.0）

### 任务 T1：从 core.py 提取 SQLite 操作到 repositories/

| 属性 | 值 |
|------|-----|
| 文件 | `repositories/sqlite_repository.py` |
| 依赖 | 无 |
| 风险 | 🟢 低 — 纯提取，不改变逻辑 |
| 验收标准 | `core.py` 中不再直接调用 `self.connection.execute(...)` |

**具体步骤：**
1. 在 `sqlite_repository.py` 中实现 `SQLiteKnowledgeRepository` 类
2. 实现方法：`create_schema()`, `upsert_item()`, `delete_item()`, `load_item_by_id()`, `relations_for()`, `row_to_item()`
3. 从 `core.py` 复制对应逻辑，保持行为一致
4. `core.py` 改为注入 `repository` 实例
5. 更新 `__init__.py` 导出

### 任务 T2：从 core.py 提取索引构建到 indexing/

| 属性 | 值 |
|------|-----|
| 文件 | `indexing/index_builder.py` |
| 依赖 | T1（需 SQLite 操作） |
| 风险 | 🟡 中 — 索引与 SQLite 耦合，需同步更改 |
| 验收标准 | `IndexBuilder` 可独立调用 `sync_index()` |

**具体步骤：**
1. `index_builder.py` 实现 `IndexBuilder` 类
2. 实现方法：`sync_index()`, `parse_knowledge_file()`, `split_front_matter()`
3. 接受 `KnowledgeRepository` + `Scanner` 作为依赖
4. `core.py` 改为调用 `IndexBuilder.sync_index()`

### 任务 T3：从 core.py 提取检索逻辑到 retrieval/

| 属性 | 值 |
|------|-----|
| 文件 | `retrieval/retrieval_service.py`, `keyword_search.py`, `vector_search.py`, `metadata_filter.py`, `reranker.py`, `deduplicator.py`, `context_builder.py` |
| 依赖 | T1 |
| 风险 | 🟡 中 — 涉及多个子模块，需保证接口一致 |
| 验收标准 | `RetrievalService.search()` 完全替代 `core.py` 中的 `_search_knowledge()` |

**具体步骤：**
1. `keyword_search.py`: 实现 `KeywordSearch.search(query_tokens, item) → float`
2. `vector_search.py`: 实现 `VectorSearch.search(query_tokens, item) → float`
3. `metadata_filter.py`: 实现 `MetadataFilter.filter(items, filters) → list`
4. `reranker.py`: 实现 `Reranker.rerank(items, weights) → list`
5. `deduplicator.py`: 实现 `Deduplicator.deduplicate(batches, max) → list`
6. `context_builder.py`: 实现 `ContextBuilder.build(items) → dict`
7. `retrieval_service.py`: 编排上述组件，暴露 `search()` 和 `consult()` 方法

### 任务 T4：core.py 降为门面

| 属性 | 值 |
|------|-----|
| 文件 | `core.py` |
| 依赖 | T1, T2, T3 |
| 风险 | 🟡 中 — 需确保所有委托调用正确 |
| 验收标准 | `core.py` 行数减少 50%+，所有测试通过 |

**具体步骤：**
1. `__init__` 注入 `Repository`, `IndexBuilder`, `RetrievalService`
2. `list_tools()` 保持不变
3. `call_tool()` 保持不变（路由逻辑）
4. `_search_knowledge()` → 委托 `RetrievalService.search()`
5. `_consult_knowledge()` → 委托 Agents + RetrievalService
6. `_sync_index()` → 委托 `IndexBuilder.sync_index()`
7. 删除被提取的私有方法

---

## 2. Phase 2 任务列表（v0.2.0 → v0.3.0）

### 任务 T5：实现 LLM Provider

| 属性 | 值 |
|------|-----|
| 文件 | `llm/` |
| 依赖 | 无 |
| 风险 | 🔴 高 — 需对接外部 API |
| 验收标准 | `LLMClient` 能成功返回结构化输出 |

### 任务 T6：Agent 接入 LLM

| 属性 | 值 |
|------|-----|
| 文件 | `agents/query_planner.py`, `retrieval_agent.py`, `result_synthesizer.py` |
| 依赖 | T5 |
| 风险 | 🔴 高 — 需设计 prompt 模板 |
| 验收标准 | Agent 在有 LLM 时使用 LLM，无 LLM 时回归规则 |

### 任务 T7：实现 Embedding Provider + 向量搜索

| 属性 | 值 |
|------|-----|
| 文件 | `indexing/embedding_builder.py`, `retrieval/vector_search.py` |
| 依赖 | T3 |
| 风险 | 🟡 中 — 本地模型需额外依赖 |
| 验收标准 | 向量搜索使用真实嵌入而非词频 |

---

## 3. Phase 3 任务列表（v0.3.0 → v0.4.0）

### 任务 T8：SSE 传输支持

| 属性 | 值 |
|------|-----|
| 文件 | `server.py`, `config/settings.yaml` |
| 依赖 | 无 |
| 风险 | 🟡 中 — 需新增 aiohttp/starlette 依赖 |
| 验收标准 | `--transport sse` 可启动 SSE 服务器 |

---

## 4. 执行顺序与依赖图

```
T1 (SQLite Repository) ──────────┐
                                  ├── T4 (core 门面化)
T2 (Index Builder) ───────────────┤
                                  │
T3 (Retrieval Service) ──────────┘
       │
       ├── T5 (LLM Provider) ── T6 (Agent LLM)
       │
       └── T7 (Embedding) ── 替换 VectorSearch

T8 (SSE Transport) ── 无依赖，可单独执行
```

**执行策略：** Phase 1 必须按 T1 → T2 → T3 → T4 顺序执行。

---

## 5. 每次修改最多 3 个文件

根据经验库规则，每次 commit 最多修改 3 个文件。以下是分批方案：

| 批次 | 文件 | 任务 |
|------|------|------|
| Batch 1 | `repositories/knowledge_repository.py`, `repositories/sqlite_repository.py`, `repositories/__init__.py` | T1 抽象接口 + SQLite 实现 |
| Batch 2 | `core.py` | T1 将 SQLite 操作委托给 Repository |
| Batch 3 | `indexing/index_builder.py`, `indexing/__init__.py` | T2 IndexBuilder 实现 |
| Batch 4 | `core.py` | T2 委托 IndexBuilder |
| Batch 5 | `retrieval/keyword_search.py`, `retrieval/vector_search.py`, `retrieval/metadata_filter.py` | T3 搜索子模块 |
| Batch 6 | `retrieval/reranker.py`, `retrieval/deduplicator.py`, `retrieval/context_builder.py` | T3 后处理子模块 |
| Batch 7 | `retrieval/retrieval_service.py`, `retrieval/__init__.py` | T3 检索编排 |
| Batch 8 | `core.py` | T3 委托检索服务 |
| Batch 9 | `core.py` | T4 最终门面化 |

---

## 6. 风险评估

| # | 风险 | 等级 | 缓解措施 |
|---|------|------|---------|
| R1 | 提取时改变行为导致测试失败 | 🟡 中 | 每批次后运行 `pytest tests` |
| R2 | T2 与 T1 耦合，需同时修改 | 🟡 中 | T1 先完成并稳定后再开始 T2 |
| R3 | T5 LLM 对接依赖外部 API 可用性 | 🔴 高 | 保持规则降级路径始终可用 |
| R4 | T7 Embedding 需额外依赖 | 🟡 中 | 可选依赖，安装失败回退到词频 |

---

## 7. 出口条件

| 条件 | 状态 |
|------|------|
| 执行计划已写入 `reports/planner/` | ✅ |
| 每个任务有明确的验收标准 | ✅ |
| 任务无遗漏 | ✅ |
| 执行顺序和依赖已明确 | ✅ |
| 风险已评估 | ✅ |

---

*本报告供 Executor Agent 执行使用。*
