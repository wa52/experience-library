# 项目经验库

这是视觉开发项目经验、问题解决记录、可复用模式和领域总结的统一知识库。

本库只保存提炼后的经验，不保存原始资料、手册、官方例程、图片、模型、训练集或第三方源码。

## 目录结构

```text
D:\项目经验库
├─ 00_索引/                       # 索引 + 检索规则
├─ projects/                      # 项目经验（详见 index/project_index.md）
├─ failure_database/              # 失败记录 / Bug（详见 index/bug_index.md）
├─ patterns/                      # 可复用模式（详见 index/pattern_index.md）
├─ domains/                       # 领域技术总结（halcon/pyqt5/yolo/label_studio 等）
├─ prompts/                       # Prompt 模板
├─ workflow/                      # 工作流定义
├─ tools/                         # 经验库工具（search/build_index/add_bug）
├─ index/                         # 自动生成索引（由 tools/build_index.py 生成）
├─ knowledge-agent-mcp/           # Knowledge Agent MCP Server（独立项目）
├─ Knowledge/                     # 历史结构化 Bug 数据（待合并/归档）
├─ backup/                        # 自动备份
├─ templates/                     # 项目模板目录
├─ reports/                       # 工作流报告
├─ .ai/                           # AI 配置文件
└─ .opencode/                     # OpenCode 配置
```

## 核心索引

- `00_索引\项目经验索引.md`：项目经验、失败记录、模式文档的完整入口。
- `CHANGELOG.md`：经验库结构变更记录。
- `00_索引/GLOBAL_RULES.md`：AI 助手检索行为全局规则。
- `00_索引\OpenCode检索规则.md`：OpenCode 强制多路径检索规则。
- `index\project_index.md`、`index\bug_index.md`、`index\pattern_index.md`：自动生成索引，请以这些文件的数量为准。

## 搜索方式

```powershell
rg -n "关键词1|关键词2" D:\项目经验库
```

推荐搜索路径：`00_索引` `projects/` `failure_database/` `patterns/` `domains/` `tools/`

> 注意：根目录 `bugs/` 已废弃（内容已迁移至 `Knowledge/bugs/`），搜索时勿遗漏 `failure_database/`。

## 新增记录规范

| 内容类型 | 存放位置 | 要求 |
|---------|---------|------|
| 项目经验 | `projects/<项目名>/` | 9 个标准文件（overview/architecture/decisions/lessons/bugs/checklist/anti_patterns/reusable_parts/next_time_rules） |
| Bug 修复 | `failure_database/` | 现象、根因、修复方案 |
| 可复用模式 | `patterns/` | 场景、架构、流程、坑点 |
| 领域知识 | `domains/` | 技术要点、最佳实践 |

## OpenCode 多路径检索策略

OpenCode 检索本经验库时必须先查多个入口，不能只命中一个文件就总结。

### 必查路径

| 顺序 | 路径 | 用途 |
|:---:|------|------|
| 1 | `00_索引/README.md`、`README.md` | 确认目录和检索规则 |
| 2 | `00_索引/项目经验索引.md`、`index/` | 定位项目、Bug、模式的当前索引 |
| 3 | `projects/` | 找项目经验、架构、踩坑、验收 |
| 4 | `failure_database/`、`patterns/`、`domains/`、`tools/` | 找问题解决、可复用代码、领域总结 |

### 快速命令

```powershell
rg -n "关键词" D:\项目经验库\00_索引 D:\项目经验库\projects D:\项目经验库\failure_database D:\项目经验库\patterns D:\项目经验库\domains D:\项目经验库\tools
```
