# Knowledge Agent MCP — 项目总览

> 最后更新：2026-07-12
> 当前版本：v0.2.0
> 目标：只读知识检索 MCP Server

## 项目结构

```
knowledge-agent-mcp/
├── config/              # 配置文件（YAML）
├── knowledge_base/      # 知识库（Markdown 文档）
├── prompts/             # Agent 提示模板
├── reports/             # 开发阶段报告
├── src/knowledge_agent_mcp/
│   ├── core.py          # MCP 门面
│   ├── models/          # 数据模型
│   ├── repositories/    # 数据持久层
│   ├── indexing/        # 索引构建
│   ├── retrieval/       # 检索服务
│   ├── agents/          # 固定子智能体
│   ├── llm/             # LLM 客户端
│   └── ...
└── tests/               # 测试（acceptance/integration/unit）
```

## 技术栈
- Python >= 3.10
- mcp（MCP 协议）
- pydantic（配置 + 数据模型）
- httpx（LLM 客户端，可选）

## 架构演进

### Phase 1 (v0.1.0 → v0.2.0) ✅
- 重构 core.py：提取 Repository / IndexBuilder / RetrievalService
- 实现 SQLite 仓库层
- 实现检索编排服务（7 个子模块）
- core.py ~650 → 460 行

### Phase 2 (v0.2.0 → v0.3.0) ✅
- 实现 LLM 客户端（OpenAI 兼容 API）
- Agent 接入 LLM（QueryPlanner / RetrievalAgent / ResultSynthesizer）
- TF-IDF 嵌入模型 + 实向量搜索

### Phase 3 (v0.3.0 → v0.4.0) ⏳
- SSE 传输支持

## 关键指标
- 9/9 测试通过
- core.py 461 行
- 1 个抽象接口 + 1 个具体仓库
- 7 个检索子模块
