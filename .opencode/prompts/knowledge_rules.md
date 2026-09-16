# Knowledge Rules — 经验检索规则

> 本文被 OpenCode Knowledge Agent 引用。经验库只维护一个 Agent，能力通过工具完成。

## 边界

`D:\项目经验库` 只保存提炼后的经验。

Agent 检索本项目时只查经验类目录。

## 可读知识来源

| 来源 | 路径 | 内容 |
|------|------|------|
| 项目经验 | `projects/` | 已完成项目的经验记录 |
| 失败记录 | `failure_database/` | Bug 现象、根因、修复和验证 |
| 可复用模式 | `patterns/` | 跨项目可复用架构和流程 |
| 领域总结 | `domains/` | 技术要点和下次规则 |
| 自动索引 | `index/` | 项目、Bug、模式索引 |
| 入口规则 | `00_索引/`、`README.md` | 检索入口和全局规则 |
| 工具说明 | `tools/` | 搜索、索引、录入工具 |

## 检索优先级

```text
00_索引/ → index/ → projects/ → failure_database/ → patterns/ → domains/ → tools/
```

## 工具

| 工具 | 使用场景 |
|------|----------|
| `grep` / `glob` / `read` | 精确检索和读取上下文 |
| `tools/search_experience.py` | 本地 Markdown 全文搜索 |
| `tools/add_bug.py` | 追加 Bug 记录 |
| `tools/build_index.py` | 写入后重建索引 |
| `apply_patch` | 修改经验文档和规则 |

## 写入规则

- Knowledge Agent 是唯一 Agent。
- 写入前必须先读相关文件。
- 默认单轮最多修改 3 个既有文件；新建项目标准经验包可一次创建 9 个文件；自动索引不计入限额。
- 可写入 `projects/`、`failure_database/`、`patterns/`、`domains/`、`templates/`、`tools/`、`00_索引/`、`.opencode/`。
- 写入后运行 `python D:\项目经验库\tools\build_index.py` 更新索引。
