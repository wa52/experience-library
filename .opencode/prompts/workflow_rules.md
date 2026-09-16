# Workflow Rules — 单 Agent 经验库流程

> 本项目只维护一个 Knowledge Agent，不再拆分多阶段 Agent。

## 流程

```text
查询经验 → 判断是否需要写入 → 写入经验 → 重建索引 → 验证
```

## 查询经验

优先顺序：

```text
00_索引/ → index/ → projects/ → failure_database/ → patterns/ → domains/ → tools/
```

必须给出命中的来源文件路径；未命中时说明已查路径。

## 写入经验

写入位置：

| 类型 | 位置 |
|------|------|
| 项目经验 | `projects/<项目名>/` |
| Bug 修复 | `failure_database/` |
| 模式 | `patterns/` |
| 领域总结 | `domains/` |
| 模板/规则/工具 | `templates/`、`00_索引/`、`.opencode/`、`tools/` |

规则：

- 写入前先读相关文件。
- 默认单轮最多修改 3 个既有文件；新建项目标准经验包可一次创建 9 个文件；自动索引不计入限额。
- 优先追加和修正，不做无关重构。

## 重建索引

写入经验后运行：

```powershell
python D:\项目经验库\tools\build_index.py
```

## 验证

- 检查自动索引是否更新。
- 用 `grep` 确认旧规则或旧路径没有残留。
- 最终回复列出改动文件和验证结果。
