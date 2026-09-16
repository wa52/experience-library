# Architecture Report — 经验库结构整理

> 生成日期：2026-07-12
> 执行阶段：Stage 2: Architecture
> 执行角色：Architect Agent

---

## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **不删内容** | 只删除空目录，不删除任何有内容的文件 |
| **不改路径** | 现有文件不移位，避免破坏外部引用 |
| **只更新索引** | 让 README 和索引反映真实结构，而非理想规划 |
| **统一检索入口** | 修正 `build_index.py` 使其覆盖实际内容目录 |

---

## 2. 目标结构

删除空目录后的真实结构：

```
D:\项目经验库
├── 00_索引/                      # 索引文件（保留）
├── projects/                     # 项目经验（8 个项目）
├── failure_database/             # 失败记录 / Bug（8 篇）
├── patterns/                     # 可复用模式（13 + 2 篇）
├── domains/                      # 领域知识（7 个领域）
├── templates/                    # 项目模板 stubs
├── reports/                      # 工作流报告
├── knowledge-agent-mcp/          # MCP 项目（独立项目）
├── tools/                        # 经验库工具脚本
├── index/                        # 自动生成索引
├── .ai/                          # AI 配置文件
├── .opencode/                    # OpenCode 配置
```

---

## 3. 变更清单

| 操作 | 目标 | 原因 |
|------|------|------|
| 删除 | `02_我的项目经验/` | 空目录，实际内容在 `projects/` |
| 删除 | `03_问题解决记录/` | 空目录，实际内容在 `failure_database/` |
| 删除 | `04_代码片段/` | 空目录，实际内容在 `patterns/` |
| 删除 | `05_数据集转换/` | 空目录，无任何内容对应 |
| 删除 | `06_自动标注/` | 空目录，无任何内容对应 |
| 删除 | `vector_db/` | 空目录 |
| 删除 | `99_VectorDB/` | 空目录，与 `vector_db/` 重复 |
| 更新 | `README.md` | 目录结构重新描述 |
| 更新 | `00_索引/README.md` | 目录描述修正 |
| 更新 | `00_索引/项目经验索引.md` | 索引路径修正 |
| 更新 | `GLOBAL_RULES.md` | 路径引用修正 |
| 更新 | `tools/build_index.py` | 增加 `failure_database/` 扫描 |

---

## 4. 不受影响的内容

以下内容不做任何变更：

- `projects/` — 完整保留
- `failure_database/` — 完整保留
- `patterns/` — 完整保留
- `domains/` — 完整保留
- `templates/` — 完整保留
- `reports/` — 完整保留（仅添加说明 README）
- `knowledge-agent-mcp/` — 完整保留
- `index/` — 自动生成，运行 `build_index.py` 重建
- `.ai/` 和 `.opencode/` — 保留
- `tools/` — 保留，仅更新 `build_index.py`

---

## 5. 风险与缓解

| 风险 | 等级 | 缓解 |
|------|------|------|
| 外部工具或脚本引用空目录路径 | 低 | 删除前先更新脚本，`build_index.py` 不依赖空目录 |
| 用户习惯通过编号目录查找内容 | 中 | 在 README 中注明原规划目录及其实际对应位置 |
| `build_index.py` 当前只扫描 `bugs/`（空）而遗漏 `failure_database/` | 中 | 更新脚本同时扫描 `failure_database/` |
