# Requirement Report — Knowledge Agent MCP

> 生成日期：2026-07-12
> 执行阶段：Stage 1: Requirement Analysis
> 执行角色：Requirement Agent
> 范围：全量扫描 `D:\项目经验库\knowledge-agent-mcp`

---

## 1. 项目概述

| 属性 | 值 |
|------|-----|
| 项目名称 | `knowledge-agent-mcp` |
| 版本 | 0.1.0 |
| 描述 | 独立运行的只读知识检索 MCP Server |
| 运行时 | Python >= 3.10 |
| 包管理器 | `uv` |
| 构建后端 | hatchling |
| 入口点 | `knowledge_agent_mcp.server:main` |
| 传输层 | stdio（目前仅支持 stdio） |
| 许可证 | 未指定 |

**一句话定位**：通过 MCP 协议暴露只读知识检索工具，供 OpenCode 或其他 MCP 客户端调用，不直接读取知识库文件。

---

## 2. 目录结构总览

```
knowledge-agent-mcp/
├── .env.example                        # 环境变量模板
├── CHANGELOG.md                        # 变更日志
├── README.md                           # 项目说明
├── pyproject.toml                      # 项目元数据与依赖
├── uv.lock                             # 依赖锁定文件
│
├── config/                             # 配置文件（5 个 YAML）
│   ├── settings.yaml                   # 主设置（路径、检索权重、Agent 参数）
│   ├── agent_workflow.yaml             # 内部 Agent 工作流定义
│   ├── models.yaml                     # LLM/Embedding 模型配置
│   ├── retrieval.yaml                  # 检索权重与阶段优先级
│   └── logging.yaml                    # 日志配置
│
├── data/
│   └── knowledge.db                    # SQLite 索引数据库（运行时生成）
│
├── knowledge_base/                     # 知识库源文件（Markdown + YAML Front Matter）
│   ├── 01_基础知识/                    # Python、数据库
│   ├── 02_技术知识/                    # HALCON、LabelStudio
│   ├── 03_AI知识/                      # Agent、MCP
│   ├── 04_项目经验/                    # CSharp-Halcon、LabelStudio-Deployment
│   ├── 05_问题与Bug/                   # 坐标偏移、版本不兼容
│   ├── 06_解决方案/                    # 模板匹配工具、MCP服务、LabelStudio
│   ├── 07_代码案例/                    # HALCON、Python
│   ├── 08_最佳实践/                    # Agent设计、日志、测试验收
│   └── 09_资料来源/                    # GitHub、官方文档
│
├── prompts/                            # Agent 提示词模板（3 个 MD）
│   ├── query_planner.md
│   ├── retrieval_agent.md
│   └── result_synthesizer.md
│
├── schemas/                            # 知识条目 JSON Schema（6 个 YAML）
│   ├── knowledge_item.schema.yaml      # 通用知识条目
│   ├── solution.schema.yaml            # 解决方案
│   ├── bug_case.schema.yaml            # Bug 案例
│   ├── best_practice.schema.yaml       # 最佳实践
│   ├── code_example.schema.yaml        # 代码案例
│   └── project_experience.schema.yaml  # 项目经验
│
├── scripts/                            # 工具脚本（4 个 Python）
│   ├── rebuild_index.py                # 重建索引
│   ├── validate_knowledge.py           # 验证知识条目
│   ├── inspect_index.py                # 查看索引统计
│   └── run_stdio_server.py             # 运行服务器（入口转发）
│
├── src/knowledge_agent_mcp/            # 核心源码
│   ├── __init__.py                     # 版本声明
│   ├── settings.py                     # 设置别名加载
│   ├── server.py                       # MCP Server 入口
│   ├── application.py                  # 应用工厂
│   ├── core.py                         # 核心逻辑（~650 行）
│   ├── mcp_compat.py                   # MCP 类型兼容层
│   ├── agents/                         # 内部子智能体
│   │   ├── registry.py                 # Agent 注册表
│   │   ├── query_planner.py            # 查询规划器
│   │   ├── retrieval_agent.py          # 检索智能体
│   │   └── result_synthesizer.py       # 结果合成器
│   ├── config/                         # 配置加载
│   │   ├── settings.py                 # Pydantic 模型
│   │   └── loader.py                   # 加载函数
│   ├── exceptions/                     # 异常定义
│   │   └── errors.py
│   ├── indexing/                       # 索引构建
│   │   ├── scanner.py                  # Markdown 文件扫描
│   │   ├── markdown_parser.py          # Front Matter 解析
│   │   ├── metadata_parser.py          # YAML 元数据解析
│   │   ├── chunker.py                  # 文档分块
│   │   ├── embedding_builder.py        # 嵌入构建（占位）
│   │   └── index_builder.py            # 索引构建器（占位）
│   ├── llm/                            # LLM 接口
│   │   ├── client.py                   # LLM 客户端（返回不可用）
│   │   ├── provider.py                 # Provider 工厂
│   │   └── structured_output.py        # 结构化输出验证
│   ├── logging/                        # 日志
│   │   └── logger.py
│   ├── mcp_tools/                      # MCP 工具定义
│   │   ├── consult_knowledge.py        # 高级咨询工具
│   │   ├── search_knowledge.py         # 精确搜索工具
│   │   ├── get_knowledge_item.py       # 知识条目读取
│   │   └── get_related_knowledge.py    # 关联知识查询
│   ├── models/                         # 数据模型
│   │   ├── knowledge_item.py           # 知识条目 Pydantic 模型
│   │   ├── consultation_request.py     # 咨询请求模型
│   │   └── search_request.py           # 搜索请求模型
│   ├── repositories/                   # 数据仓库（占位）
│   │   ├── file_repository.py
│   │   ├── knowledge_repository.py
│   │   └── sqlite_repository.py
│   └── retrieval/                      # 检索服务（占位）
│       ├── retrieval_service.py
│       ├── deduplicator.py
│       ├── keyword_search.py
│       ├── vector_search.py
│       ├── metadata_filter.py
│       ├── reranker.py
│       └── context_builder.py
│
└── tests/                              # 测试
    ├── conftest.py                     # 测试配置
    ├── test_core.py                    # 核心功能测试
    ├── unit/
    │   └── test_knowledge_files.py     # 知识库文件结构测试
    ├── integration/
    │   └── test_retrieval_flow.py      # 检索流集成测试
    ├── acceptance/
    │   └── test_acceptance_scenarios.py # 验收场景测试
    └── fixtures/                       # 测试夹具（空）
```

---

## 3. 目录结构统计

| 类别 | 数量 |
|------|------|
| 总目录层数 | 最深 6 层（`src/knowledge_agent_mcp/...`） |
| 一级子目录 | 12（config, data, knowledge_base, prompts, schemas, scripts, src, tests, reports, .venv, .pytest_cache, uv.lock） |
| Python 源文件 | ~40 个 |
| Markdown 知识文件 | 36 个 |
| YAML 配置文件 | 11 个（5 config + 6 schemas） |
| 测试文件 | 4 个 |
| 工具脚本 | 4 个 |

---

## 4. 已发现的问题

### 4.1 结构性问题

| # | 问题描述 | 严重度 | 详情 |
|---|---------|--------|------|
| R1 | `data/` 目录中的 `knowledge.db` 是运行时生成文件，被版本跟踪 | 中 | 开发提交总是包含脏的 SQLite 数据库文件，应在 `.gitignore` 中忽略 |
| R2 | `.venv/` 目录存在于项目根目录 | 中 | Python 虚拟环境不应提交到版本管理，可能有排除但目录层级中存在 |
| R3 | `reports/` 目录为空（刚创建） | 低 | 本报告是第一个写入的文件 |
| R4 | `.pytest_cache/` 目录存在于项目根目录 | 低 | 测试缓存不应提交，可能已被 `.gitignore` 排除但目录存在 |
| R5 | `tests/fixtures/` 目录为空 | 低 | 测试夹具目录已创建但未填充内容 |
| R6 | `.env.example` 包含空的 API Key 占位 | 低 | 使用 `opencode` provider 不需要 API Key，但 `.env.example` 保留 `OPENROUTER_API_KEY=` 可能造成混淆 |

### 4.2 功能性问题

| # | 问题描述 | 严重度 | 详情 |
|---|---------|--------|------|
| R7 | LLM 客户端始终返回不可用 | 高 | `LLMClient` 所有方法 `raise RuntimeError("LLM_UNAVAILABLE")`，`get_llm_client()` 直接返回未配置的实例。即使 `models.yaml` 配置了 LLM Provider，实际未接入 |
| R8 | Embedding 为占位实现 | 高 | `embedding_builder.py` 只返回 `{"length": len(text)}`，不是真正的向量嵌入。`config/models.yaml` 中配置的 `dimension: 0` 也表明 embedding 未接入 |
| R9 | 检索服务模块为占位 | 中 | `retrieval_service.py`, `deduplicator.py`, `keyword_search.py`, `vector_search.py`, `metadata_filter.py`, `reranker.py`, `context_builder.py` 全部为空或只含 `pass`。实际检索逻辑在 `core.py` 中直接实现 |
| R10 | Repository 层为占位 | 中 | `file_repository.py`, `sqlite_repository.py`, `knowledge_repository.py` 全部为空的协议/边界定义。实际数据访问在 `core.py` 中直接实现 |
| R11 | IndexBuilder 为占位 | 中 | `index_builder.py` 只包含一个空 dataclass。实际索引构建在 `core.py` 的 `_sync_index()` 中实现 |
| R12 | agents 子包主要逻辑在 core.py | 中 | `query_planner.py`, `retrieval_agent.py`, `result_synthesizer.py` 仅有简单 dataclass，核心编排逻辑在 `core.py` 的 `_consult_knowledge()` 中直接内联 |

### 4.3 设计问题

| # | 问题描述 | 严重度 | 详情 |
|---|---------|--------|------|
| R13 | 仅支持 stdio 传输层 | 中 | `server.py` 只实现了 stdio 传输。SSE、StreamableHTTP 等其他传输层未支持 |
| R14 | 向量搜索使用确定性 Token 向量 | 中 | `_vector_score()` 使用 `Counter` 做词频向量，不是真正的语义嵌入。精度有限，无法理解同义词和上下文 |
| R15 | 无 embedding 索引持久化 | 中 | `knowledge_chunks` 表的 `embedding_id` 列为 `NULL`，向量搜索在查询时通过全文 Token 计数实时计算 |
| R16 | `mcp_compat.py` 中 fallback 实现不完整 | 低 | `PaginatedRequestParams` 和 `CallToolRequestParams` fallback 为 `object`，可能导致参数传递错误 |
| R17 | `agent_degraded: true` 硬编码 | 低 | `_consult_knowledge()` 始终返回 `agent_degraded: true`，即使将来 LLM 可用也未设计切换逻辑 |

### 4.4 知识库问题

| # | 问题描述 | 严重度 | 详情 |
|---|---------|--------|------|
| R18 | 知识库只有 36 个 Markdown 文件 | 低 | 知识库规模较小，覆盖范围有限（主要围绕 HALCON、LabelStudio、MCP 三个领域） |
| R19 | 知识库领域集中在机器视觉 | 低 | `02_技术知识` 只有 HALCON 和 LabelStudio，缺少其他技术栈 |
| R20 | 无跨语言知识 | 低 | 所有文件均为中文，缺少英文知识条目 |

---

## 5. 执行范围

### 5.1 本次覆盖范围

| 范围 | 包含 | 说明 |
|------|------|------|
| 全量扫描 | ✅ | 扫描整个 `knowledge-agent-mcp/` 项目 |
| 源码分析 | ✅ | 所有 Python 源文件 |
| 配置分析 | ✅ | 所有 YAML 配置和 schema |
| 知识库分析 | ✅ | 所有 Markdown 知识条目 |
| 测试分析 | ✅ | 所有测试用例 |
| 文档分析 | ✅ | README、CHANGELOG、Prompt 文件 |

### 5.2 本次不覆盖范围

| 范围 | 原因 |
|------|------|
| `.venv/` 中的第三方依赖 | 标准 Python 虚拟环境，非本项目代码 |
| 经验库父目录 `D:\项目经验库` | 超出本项目边界 |
| 其他 MCP 参考实现 | 属于外部参考资料，非本项目产出 |

---

## 6. 风险项

| # | 风险 | 等级 | 影响 | 说明 |
|---|------|------|------|------|
| F1 | LLM 未接入导致 Agent 能力缺失 | 🔴 高 | `query_planner`、`retrieval_agent`、`result_synthesizer` 的所有 LLM 驱动的智能行为不可用 | 当前所有 Agent 逻辑是规则硬编码，LLM 调用全部抛异常 |
| F2 | Embedding 未接入导致语义检索缺失 | 🔴 高 | 向量评分基于词频而非语义，同义词、上下文理解能力为零 | 当前 `vector_score` 是词袋 `Counter` 余弦相似度，不是一个 embedding 模型 |
| F3 | 核心逻辑集中在 `core.py`（~650 行） | 🟡 中 | 职责不分层，难以测试和维护 | Agent、索引、检索、元数据过滤等逻辑全部在一个类中 |
| F4 | 无 SSE/HTTP 传输支持 | 🟡 中 | 无法与不支持 stdio 的 MCP 客户端集成 | 当前只实现了 `stdio` 传输 |
| F5 | `consult_knowledge` 工具参数复杂 | 🟡 中 | 调用方需要提供 `stage`、`project_context` 等结构化参数，增加集成门槛 | Agent 未做任务理解自动推断，依赖客户端前置处理 |
| F6 | 测试覆盖不足 | 🟡 中 | 仅 4 个测试文件，缺少单元测试覆盖 | 只有集成测试和验收测试，核心方法无独立测试 |
| F7 | 知识库规模有限 | 🟢 低 | 结果质量受限于知识库覆盖范围 | 36 个文件仅覆盖 3 个领域 |

---

## 7. 依赖项

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| `anyio` | >=4.4.0 | 异步运行支持 |
| `click` | >=8.1.7 | CLI 命令行解析 |
| `mcp` | >=1.10.0 | MCP 协议 SDk |
| `pydantic` | >=2.8.2 | 数据模型验证 |
| `pyyaml` | >=6.0.2 | YAML Front Matter 解析 |

---

## 8. 当前工作流状态

根据 `config/agent_workflow.yaml` 定义的 Agent 工作流：

| 阶段 | Agent | 实现状态 |
|------|-------|---------|
| `query_planner` | 查询规划器 | 规则硬编码在 `core.py`，无 LLM |
| `retrieval_agent` | 检索智能体 | 规则硬编码在 `core.py`，去重逻辑在独立类 |
| `result_synthesizer` | 结果合成器 | 规则硬编码在 `core.py`，元数据构建在独立类 |

---

## 9. 出口条件检查

| 条件 | 状态 | 说明 |
|------|------|------|
| 需求报告已写入 `reports/requirement/` | ✅ | 本文件 |
| 执行范围已明确 | ✅ | 见第 5 节 |
| 风险项已列出 | ✅ | 见第 6 节 |
| 无代码修改 | ✅ | 仅读取，未写入任何源文件 |

---

*本报告由 Requirement Agent 自动生成，供下游 Architect Agent 使用。*
