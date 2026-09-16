# Knowledge Agent MCP — 架构模式

> 最后更新：2026-07-12

## 适用场景
只读知识库 + MCP 协议的智能体知识检索服务。核心需求是将本地 Markdown 知识文档目录暴露为 MCP 工具，供 AI 智能体调用。

## 架构分层

```
core.py（门面）
  ├── SQLiteKnowledgeRepository（数据持久层）
  ├── IndexBuilder（索引构建层）
  │     └── TfidfEmbedding（TF-IDF 嵌入模型）
  └── RetrievalService（检索编排层）
        ├── keyword_search（BM25 式关键词）
        ├── vector_search（TF-IDF 余弦相似度）
        ├── metadata_filter（分类/技术/版本/状态过滤）
        └── context_builder（结果结构化封装）
```

## 关键决策

### 1. 门面模式
`core.py` 从 ~650 行降到 ~460 行，职责仅剩 MCP 工具路由 + 高层编排。所有数据库、索引、检索逻辑委托到子模块。

### 2. 仓库模式
`KnowledgeRepository` 抽象接口（Protocol） + `SQLiteKnowledgeRepository` 具体实现。接口 11 个方法覆盖全部数据操作。

### 3. 单例嵌入模型
`TfidfEmbedding` 在 `sync_index()` 时拟合，通过模块级 `get_embedding_model()` / `set_embedding_model()` 全局访问。避免在检索时重建词汇表。

### 4. LLM 降级策略
`LLMClient` 无 API Key 时抛出 `RuntimeError("LLM_UNAVAILABLE")`，所有 Agent 调用 LLM 失败时自动降级到规则策略。

### 5. 固定子智能体模式
`QueryPlanner` / `RetrievalAgent` / `ResultSynthesizer` 是内部固定子智能体，各自负责一个环节，组合成检索工作流。

## 依赖关系
- Python >= 3.10
- mcp（MCP 协议）
- pydantic（配置 + 数据模型）
- httpx（LLM HTTP 客户端，可选）
