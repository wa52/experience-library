# 项目经验库

这是视觉开发项目经验、问题解决记录、可复用模式和领域总结的统一知识库。

本库只保存提炼后的经验，不保存原始资料、手册、官方例程、图片、模型、训练集或第三方源码。

## 目录结构

```text
D:\项目经验库
├─ 00_索引/                       # 使用规则（非 Agent 必读入口）
├─ projects/                      # 项目经验
├─ failure_database/              # 跨项目失败记录 / Bug
├─ patterns/                      # 跨项目可复用模式
├─ domains/                       # 领域技术总结（halcon/pyqt5/yolo/label_studio 等）
├─ prompts/                       # Prompt 模板
├─ workflow/                      # 工作流定义
├─ tools/                         # 经验库工具（search/build_index/add_bug）
├─ index/                         # 可选的自动生成导航（由 tools/build_index.py 生成）
├─ knowledge-agent-mcp/           # Knowledge Agent MCP Server
├─ archive/                       # 历史结构和不再参与主流程的内容
├─ backup/                        # 自动备份
├─ templates/                     # 项目模板目录
├─ reports/                       # 工作流报告
├─ .ai/                           # AI 配置文件
└─ .opencode/                     # OpenCode 配置
```

## 使用入口

- Agent 开发前直接检索 `failure_database/`、`projects/`、`patterns/`、`domains/`。
- `CHANGELOG.md`：经验库结构变更记录。
- `00_索引/GLOBAL_RULES.md`：AI 助手检索行为全局规则。
- `index/`：供人工浏览的派生导航，不是知识源，也不是 Agent 检索门禁。

## 搜索方式

```powershell
rg -n "关键词1|关键词2" D:\项目经验库
```

推荐搜索路径：`00_索引` `projects/` `failure_database/` `patterns/` `domains/` `tools/`

> 注意：根目录 `bugs/` 和 `archive/` 不属于默认主流程；追溯历史时再显式搜索。

## 新增记录规范

| 内容类型 | 存放位置 | 要求 |
|---------|---------|------|
| 项目经验 | `projects/<项目名>/` | 9 个标准文件（overview/architecture/decisions/lessons/bugs/checklist/anti_patterns/reusable_parts/next_time_rules） |
| Bug 修复 | `failure_database/` | 现象、根因、修复方案 |
| 可复用模式 | `patterns/` | 场景、架构、流程、坑点 |
| 领域知识 | `domains/` | 技术要点、最佳实践 |

## OpenCode 快速检索策略

OpenCode 默认调用 MCP 或 `tools/search_experience.py` 检索四个权威内容目录，先读取 Top 3-5 条候选，再按适用性展开全文。

### 必查路径

| 顺序 | 路径 | 用途 |
|:---:|------|------|
| 1 | `failure_database/` | 找相同或相似失败案例 |
| 2 | `projects/` | 找类似项目的决策和教训 |
| 3 | `patterns/` | 找可复用架构和流程 |
| 4 | `domains/` | 找领域技术总结 |

### 快速命令

```powershell
rg -n "关键词" D:\项目经验库\00_索引 D:\项目经验库\projects D:\项目经验库\failure_database D:\项目经验库\patterns D:\项目经验库\domains D:\项目经验库\tools
```
