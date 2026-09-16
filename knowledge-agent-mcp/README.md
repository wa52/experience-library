# Knowledge Agent MCP Server

独立运行的只读知识检索 MCP Server。OpenCode 或其他 MCP 客户端只通过 `consult_knowledge` 等工具访问知识库，不直接读取知识库文件。

## 当前实现范围

- `consult_knowledge`
- `search_knowledge`
- `get_knowledge_item`
- `get_related_knowledge`
- Markdown + YAML Front Matter 解析
- SQLite 索引构建与增量更新
- 关键词检索 + 轻量向量式相似度重排
- LLM 不可用时降级到纯检索模式

## 运行环境

- Python `>=3.10`
- 推荐使用 `uv`

## 目录

```text
knowledge-agent-mcp/
├── config/
├── data/
├── knowledge_base/
├── prompts/
├── schemas/
├── scripts/
├── src/knowledge_agent_mcp/
└── tests/
```

## 运行

```powershell
uv run --project . knowledge-agent-mcp --transport stdio
```

测试请在子项目目录执行，避免把经验库里其他第三方仓库测试一起收集进来：

```powershell
uv run --project . pytest tests
```

常用脚本：

```powershell
uv run --project . python scripts\rebuild_index.py
uv run --project . python scripts\validate_knowledge.py
uv run --project . python scripts\inspect_index.py
```

## 设计说明

- 第一版保持知识库只读
- 不执行知识文件中的任何命令或指令
- 索引存入 `data/knowledge.db`
- 向量能力先用本地确定性嵌入实现，后续可替换真实 embedding provider
