# Workflow Output Schema — 统一输出结构

> 本文定义每个阶段产出物的统一格式。
> 所有 Agent 的输出必须遵循本文定义的结构。

---

## Schema 通用字段

每个阶段输出必须包含以下公共字段：

```yaml
metadata:
  stage:        {阶段名称}
  agent:        {Agent 名称}
  workflow:     {Workflow 名称}
  version:      {版本号，格式: v{数字}}
  timestamp:    {ISO 8601 格式时间戳}
  status:       [running | completed | rejected | failed]

inputs:
  - {引用的输入文件列表}

outputs:
  - {本阶段产出的文件列表}
```

---

## Stage 1: Requirement — 需求报告

```markdown
# Requirement Report

## Metadata
- Stage: Requirement
- Agent: requirement-agent
- Workflow: {workflow_name}
- Version: v{number}
- Timestamp: {ISO 8601}
- Status: [running | completed | rejected | failed]

## Summary
{对整个知识库当前状态的简要总结}

## Problems
{发现的问题列表，每个问题包含：}
- 位置：{路径}
- 类型：{重复/过期/断裂/混乱}
- 严重程度：[high | medium | low]
- 描述：{详细说明}

## Scope
{本次 Workflow 的执行范围定义}

## Risk Assessment
{风险项列表}

## Deliverables
- [ ] reports/requirement/requirement_report.md

## Next Stage Input
{传递给 Architect 的关键信息}
```

---

## Stage 2: Architect — 架构报告

```markdown
# Architecture Report

## Metadata
- Stage: Architect
- Agent: architect-agent
- Workflow: {workflow_name}
- Version: v{number}
- Timestamp: {ISO 8601}
- Status: [running | completed | rejected | failed]

## Target Directory Structure
{以树形结构展示目标目录布局}

## Metadata Schema
- {字段名}: {类型} ({是否必填})
- ...

## Tag Taxonomy
- 一级标签: {列表}
  - 二级标签: {列表}

## Naming Convention
- 目录命名规则：{规则说明}
- 文件命名规则：{规则说明}
- 版本号规则：{规则说明}

## Compatibility Note
{与现有体系的兼容性说明}

## Deliverables
- [ ] reports/architecture/architecture_report.md

## Next Stage Input
{传递给 Planner 的关键信息}
```

---

## Stage 3: Planner — 执行计划

```markdown
# Planner Report

## Metadata
- Stage: Planner
- Agent: planner-agent
- Workflow: {workflow_name}
- Version: v{number}
- Timestamp: {ISO 8601}
- Status: [running | completed | rejected | failed]

## Task List

### Task {编号}: {任务名称}
- 描述：{做什么}
- 依赖：[Task {编号}, ...]
- 风险：{高/中/低}
- 操作：{具体操作步骤}
  - {步骤 1}
  - {步骤 2}
- 验收标准：{如何确认完成}
- 回滚方案：{失败后如何恢复}

### Task {编号}: {任务名称}
...

## Execution Order
{按依赖排序后的任务执行顺序}

## Deliverables
- [ ] reports/planner/planner_report.md

## Next Stage Input
{传递给 Executor 的关键信息}
```

---

## Stage 4: Executor — 执行日志

```markdown
# Execution Log

## Metadata
- Stage: Executor
- Agent: executor-agent
- Workflow: {workflow_name}
- Version: v{number}
- Timestamp: {ISO 8601}
- Status: [running | completed | rejected | failed]

## Execution Summary
{总览：执行了哪些任务，结果如何}

## Task Execution Details

### Task {编号}: {任务名称}
- 状态：[completed | failed | skipped]
- 时间：{执行时间}
- 操作记录：
  - {具体操作 1}
  - {具体操作 2}
- 变更文件：
  - {路径} → {新路径}  (移动)
  - {路径}  (修改)
  - {路径}  (创建)
- 问题记录：
  - {如果有问题，记录详情}

## Rollback Info
{如果执行了回滚，记录回滚原因和结果}

## Changed Files Summary
{所有变更文件的汇总清单}

## Deliverables
- [ ] reports/execution/execution_log.md

## Next Stage Input
{传递给 Reviewer 的关键信息}
```

---

## Stage 5: Reviewer — 审查报告

```markdown
# Review Report

## Metadata
- Stage: Reviewer
- Agent: reviewer-agent
- Workflow: {workflow_name}
- Version: v{number}
- Timestamp: {ISO 8601}
- Status: [running | completed | rejected | failed]

## Review Summary
{审查总体结论}

## Checklist Results
{逐项标注 workflow_checklist.md 的检查结果}

### Structure Check
- [✓ / ✗ / ~] 目录结构是否与架构一致
  - 问题：{如有}

### Completeness Check
- [✓ / ✗ / ~] 文件是否完整
  - 遗漏：{如有}
  - 多余：{如有}

### Metadata Check
- [✓ / ✗ / ~] Metadata 是否正确
  - 问题：{如有}

## Problems Found
{严重问题：必须退回修复}
{优化项：可记录但不阻塞}

## Decision
[approve | reject | conditional_approve]
{如果 reject，说明退回原因和目标阶段}

## Deliverables
- [ ] reports/review/review_report.md

## Next Stage Input
{传递给 Validator 的关键信息}
```

---

## Stage 6: Validator — 验证报告

```markdown
# Validation Report

## Metadata
- Stage: Validator
- Agent: validator-agent
- Workflow: {workflow_name}
- Version: v{number}
- Timestamp: {ISO 8601}
- Status: [running | completed | rejected | failed]

## Validation Summary
{验证总体结论}

## Checklist Results

### Index Generation
- [PASS / FAIL] 索引可正常生成
  - 详情：{如有错误}

### Link Validation
- [PASS / FAIL / WARN] 链接有效性
  - Broken Links: {数量}
  - 详情：{列表}

### Metadata Parsing
- [PASS / FAIL] Metadata 可解析
  - 详情：{如有问题}

### Duplicate Check
- [PASS / FAIL / WARN] 无重复文件
  - 详情：{如有}

### Cleanup Check
- [PASS / FAIL / WARN] 无残留文件
  - 详情：{如有}

## Overall Result
[PASS | FAIL | PASS_WITH_WARN]

## Deliverables
- [ ] reports/validation/validation_report.md

## Next Stage Input
{传递给 Evaluator 的关键信息}
```

---

## Stage 7: Evaluator — 最终评分报告

```markdown
# Evaluation Report

## Metadata
- Stage: Evaluator
- Agent: evaluator-agent
- Workflow: {workflow_name}
- Version: v{number}
- Timestamp: {ISO 8601}
- Status: [running | completed | rejected | failed]

## Workflow Overview
{本次 Workflow 执行概览}

## Score Breakdown

| Stage | Score | Grade | Notes |
|-------|-------|-------|-------|
| Requirement | {score} | {S/A/B/C/D} | {备注} |
| Architect | {score} | {S/A/B/C/D} | {备注} |
| Planner | {score} | {S/A/B/C/D} | {备注} |
| Executor | {score} | {S/A/B/C/D} | {备注} |
| Reviewer | {score} | {S/A/B/C/D} | {备注} |
| Validator | {score} | {S/A/B/C/D} | {备注} |
| Evaluator | {score} | {S/A/B/C/D} | {备注} |

## Weighted Total
- 总分: {score}
- 等级: {S/A/B/C/D}

## V1 Acceptance

| # | 能力 | 状态 | 备注 |
|---|------|------|------|
| 1 | Markdown 扫描 | [PASS / FAIL] | |
| 2 | YAML 解析 | [PASS / FAIL] | |
| 3 | SQLite | [PASS / FAIL] | |
| 4 | Metadata | [PASS / FAIL] | |
| 5 | Keyword Search | [PASS / FAIL] | |
| 6 | consult_knowledge | [PASS / FAIL] | |
| 7 | Result Synthesizer | [PASS / FAIL] | |
| 8 | MCP Server | [PASS / FAIL] | |

**V1 整体判定：** [PASS | FAIL]

## Before / After Comparison
{执行前后知识库状态对比}

## Lessons Learned
{本次 Workflow 中发现的可复用经验}
- {经验 1}
- {经验 2}

## Improvement Suggestions
{对后续 Workflow 的优化建议}
- {建议 1}
- {建议 2}

## Deliverables
- [ ] reports/final/evaluation_report.md
```

---

## 输出校验规则

| 规则 | 说明 |
|------|------|
| 必含 Metadata | 缺少 Metadata 的输出为无效输出 |
| 必含 Checklist | 缺少 Checklist 的结果为未完成 |
| 必含 Deliverables | 缺少 Deliverables 清单的输出无法追踪 |
| 字段顺序不可变 | 字段顺序必须按本文定义排列 |
| 禁止添加自定义字段 | 如需扩展，先在本文登记 |

---

*所有 Agent 的输出必须严格遵循本文定义的结构。任何偏离都视为格式违规。*
