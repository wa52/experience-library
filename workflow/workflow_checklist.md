# Workflow Checklist — 阶段检查清单

> Validator 按此清单逐项检查每个阶段的产出物。
> 每个阶段 Agent 完成时也应自行对照确认。

---

## Stage 1: Requirement

```
□ 是否理解了用户目标
  （明确用户想达到的状态，而非直接照搬指令）

□ 是否扫描了知识库根目录
  （用 Directory Tree 或 Glob 获取当前结构）

□ 是否识别了重复目录
  （同名目录、内容重叠目录）

□ 是否发现了 Broken Link
  （引用了不存在的文件或路径）

□ 是否记录了文件总数和类型分布
  （.md / .cs / .hdev / .csv 等）

□ 是否明确了执行范围
  （全库 / 子目录 / 特定主题）

□ 是否输出了 Markdown 格式的需求报告
  （路径：reports/requirement/requirement_report.md）

□ 是否未修改任何知识库文件
  （Requirement 阶段为只读）
```

---

## Stage 2: Architect

```
□ 是否输出了目标目录结构
  （从根到叶的完整目录树）

□ 是否定义了 Metadata 规范
  （字段名、字段类型、是否必填）

□ 是否定义了 Tag 分类体系
  （一级/二级标签，适用范围）

□ 是否设计了命名规范
  （目录命名、文件命名规则）

□ 是否评估了兼容性
  （新结构是否兼容已有文件路径引用）

□ 是否输出了架构设计报告
  （路径：reports/architecture/architecture_report.md）

□ 是否未修改任何知识库文件
  （Architect 阶段为只读）
```

---

## Stage 3: Planner

```
□ 是否将迁移任务逐项列出
  （每个任务有唯一编号）

□ 是否标注了任务依赖顺序
  （先做 A 才能做 B）

□ 是否评估了每个任务的风险
  （高风险 / 中风险 / 低风险）

□ 是否每个任务有验收标准
  （什么算"做完"）

□ 是否指定了回滚方案
  （任务失败后如何恢复）

□ 是否输出了执行计划
  （路径：reports/planner/planner_report.md）

□ 是否未修改任何知识库文件
  （Planner 阶段为只读）
```

---

## Stage 4: Executor

```
□ 是否生成了执行日志
  （路径：reports/execution/execution_log.md）

□ 是否按任务列表逐项执行
  （不得跳过、不得改序）

□ 是否可回滚
  （执行前备份/执行过程可逆）

□ 是否修改了 README
  （知识库目录变更时更新对应 README）

□ 是否更新了 Metadata
  （按架构设计写入 Metadata）

□ 是否更新了索引
  （索引文件同步更新）

□ 是否有未预期的文件变更
  （检查 Git diff / 文件变更清单）

□ 是否输出了执行日志
  （路径：reports/execution/execution_log.md）
```

---

## Stage 5: Reviewer

```
□ 是否检查了目录结构
  （实际结构是否与架构设计一致）

□ 是否检查了文件完整性
  （是否有文件遗漏或多余）

□ 是否检查了 Metadata 正确性
  （字段完整、格式正确、值合理）

□ 是否检查了 Tag 正确性
  （Tag 符合分类体系、无拼写错误）

□ 是否检查了文件名规范
  （是否遵循命名规范）

□ 是否记录了所有问题
  （每个问题有位置、类型、严重程度）

□ 是否区分了严重问题与可优化项
  （严重问题需退回，优化项目可记录待办）

□ 是否输出了审查报告
  （路径：reports/review/review_report.md）
```

---

## Stage 6: Validator

```
□ 是否验证了索引可正常生成
  （运行索引脚本无报错）

□ 是否验证了所有链接有效
  （内部引用/外部链接可访问）

□ 是否验证了 Metadata 可解析
  （解析脚本可读取所有 Metadata 字段）

□ 是否验证了无重复文件
  （文件名和内容去重检查）

□ 是否验证了无残留临时文件
  （.bak / .tmp / 空目录）

□ 是否验证了目录无空文件夹
  （空目录清理或说明）

□ 是否输出了验证报告
  （路径：reports/validation/validation_report.md）
```

---

## Stage 7: Evaluator

```
□ 是否按 workflow_score.md 逐项评分
  （每个维度有评分和评分依据）

□ 是否对比了执行前后状态
  （Before / After 对比）

□ 是否总结了可复用的经验
  （什么问题、怎么解决的）

□ 是否记录了改进建议
  （对后续 Workflow 的优化建议）

□ 是否输出了最终报告
  （路径：reports/final/evaluation_report.md）
```

---

## V1 系统验收

> 仅在 V1 阶段使用。验收知识库系统 8 项基础能力。

```
□ Markdown 扫描
  （是否能递归扫描目录中所有 .md 文件）

□ YAML 解析
  （是否能正确解析 YAML front matter）

□ SQLite
  （是否能将扫描结果写入 SQLite 数据库）

□ Metadata
  （每个文件是否有完整 Metadata）

□ Keyword Search
  （是否能按关键词搜索 title/tags/content）

□ consult_knowledge
  （是否提供 consult_knowledge(query) 函数）

□ Result Synthesizer
  （是否将多条结果合成结构化回复）

□ MCP Server
  （是否通过 MCP Server 对外暴露检索能力）

整体判定: [PASS | FAIL]
```

---

## 使用方式

### Reviewer 使用

逐项检查 Executor 的输出，在审查报告中标注：

- `[✓]` — 通过
- `[✗]` — 不通过（需退回）
- `[~]` — 部分通过（需修复）

### Validator 使用

逐项验证知识库最终状态，在验证报告中标注：

- `[PASS]` — 通过
- `[FAIL]` — 不通过
- `[WARN]` — 警告（记录但不阻塞）

### Agent 自检

每个 Agent 完成阶段任务后，自行对照本文逐项确认后再提交。

---

*本文详细清单详见各阶段。Validator 必须逐项检查，不得合并或跳过。*
