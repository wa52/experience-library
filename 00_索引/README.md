# 项目经验库

这是视觉开发项目经验、问题解决记录、可复用模式和领域总结的统一知识库。

本库只保存提炼后的经验，不保存原始资料、手册、官方例程、图片、模型和训练数据。

## 目录结构

```text
D:\项目经验库
├─ 00_索引/                       # 索引 + 检索规则
├─ projects/                      # 项目经验
├─ failure_database/              # 失败记录 / Bug
├─ patterns/                      # 可复用模式
├─ domains/                       # 领域知识
├─ knowledge-agent-mcp/           # MCP 项目
├─ tools/                         # 经验库工具
└─ index/                         # 自动生成索引
```

## 核心索引

- `项目经验索引.md`：项目经验、失败记录、模式文档的完整入口。
- `OpenCode检索规则.md`：OpenCode 强制多路径检索规则。
- `../index/project_index.md`、`../index/bug_index.md`、`../index/pattern_index.md`：自动生成索引。

## 搜索方式

```powershell
rg -n "关键词1|关键词2" D:\项目经验库
```

## 新增记录规范

| 内容类型 | 存放位置 |
|---------|---------|
| 项目经验 | `projects/<项目名>/` |
| Bug 修复 | `failure_database/` |
| 可复用模式 | `patterns/` |
| 领域知识 | `domains/` |

## OpenCode 多路径检索策略

### 必查路径

| 顺序 | 路径 | 用途 |
|:---:|------|------|
| 1 | `README.md` | 确认目录和检索规则 |
| 2 | `项目经验索引.md`、`../index/` | 定位项目、Bug、模式索引 |
| 3 | `projects/` | 找项目经验 |
| 4 | `failure_database/`、`patterns/`、`domains/`、`tools/` | 找问题解决、可复用代码、领域总结 |

### 快速命令

```powershell
rg -n "关键词" D:\项目经验库\projects D:\项目经验库\failure_database D:\项目经验库\patterns D:\项目经验库\domains D:\项目经验库\tools
```
