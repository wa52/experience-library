# 项目经验库

这是视觉开发项目经验、问题解决记录、可复用模式和领域总结的统一知识库。

本库只保存提炼后的经验，不保存原始资料、手册、官方例程、图片、模型和训练数据。

## 目录结构

```text
D:\项目经验库
├─ 00_索引/                       # 使用规则（非 Agent 必读入口）
├─ projects/                      # 项目经验
├─ failure_database/              # 失败记录 / Bug
├─ patterns/                      # 可复用模式
├─ domains/                       # 领域知识
├─ knowledge-agent-mcp/           # MCP 项目
├─ tools/                         # 经验库工具
└─ archive/                       # 历史内容
```

## 使用入口

- Agent 默认直接检索 `../failure_database/`、`../projects/`、`../patterns/`、`../domains/`。
- `../index/` 仅供人工浏览，不是 Agent 必读入口。

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

### 默认检索路径

| 顺序 | 路径 | 用途 |
|:---:|------|------|
| 1 | `../failure_database/` | 找失败案例 |
| 2 | `../projects/` | 找项目经验 |
| 3 | `../patterns/` | 找复用模式 |
| 4 | `../domains/` | 找领域总结 |

### 快速命令

```powershell
rg -n "关键词" D:\项目经验库\projects D:\项目经验库\failure_database D:\项目经验库\patterns D:\项目经验库\domains D:\项目经验库\tools
```
