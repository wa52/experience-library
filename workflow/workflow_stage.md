# Workflow Stage Definition

> 本文定义每个阶段的输入、输出、角色、工具权限和阶段转换。
> Workflow MCP 将据此编排各 Agent 的执行。

---

## 格式说明

每个阶段用以下 YAML 结构定义：

```yaml
stage:          {阶段名称}
role:           {执行 Agent}
description:    {阶段简述}

inputs:
  - {输入文件/目录路径}

outputs:
  - {输出文件路径}

allowed_tools:
  - {允许使用的工具}

permission:     [readonly | readwrite | admin]

allowed_return_stages:
  - {允许退回的阶段}

next_stage:     {下一阶段名称}
```

---

## Stage 1: Requirement

```yaml
stage:          Requirement
role:           requirement-agent
description:    分析知识库现状，明确整理目标和范围

inputs:
  - D:/项目经验库/    (知识库根目录)
  - 用户提供的 Task 描述

outputs:
  - reports/requirement/requirement_report.md

allowed_tools:
  - Read
  - Search (Grep)
  - Glob
  - Directory Tree

permission:     readonly

allowed_return_stages:
  - (起始阶段，无可退回)

next_stage:     Architect
```

---

## Stage 2: Architect

```yaml
stage:          Architect
role:           architect-agent
description:    设计知识库的目标目录结构和元数据规范

inputs:
  - reports/requirement/requirement_report.md

outputs:
  - reports/architecture/architecture_report.md

allowed_tools:
  - Read
  - Search (Grep)
  - Glob
  - Directory Tree

permission:     readonly

allowed_return_stages:
  - Requirement

next_stage:     Planner
```

---

## Stage 3: Planner

```yaml
stage:          Planner
role:           planner-agent
description:    将架构设计拆解为可执行的任务列表

inputs:
  - reports/requirement/requirement_report.md
  - reports/architecture/architecture_report.md

outputs:
  - reports/planner/planner_report.md

allowed_tools:
  - Read

permission:     readonly

allowed_return_stages:
  - Requirement
  - Architect

next_stage:     Executor
```

---

## Stage 4: Executor

```yaml
stage:          Executor
role:           executor-agent
description:    按任务列表执行文件移动、重命名、元数据写入

inputs:
  - reports/planner/planner_report.md

outputs:
  - reports/execution/execution_log.md
  - (修改知识库文件)

allowed_tools:
  - Read
  - Write
  - Move File
  - Create Directory
  - Glob
  - Directory Tree

permission:     readwrite

allowed_return_stages:
  - Planner
  - Architect

next_stage:     Reviewer
```

---

## Stage 5: Reviewer

```yaml
stage:          Reviewer
role:           reviewer-agent
description:    审查迁移结果，确保结构正确、内容完整

inputs:
  - reports/execution/execution_log.md
  - (知识库当前状态)

outputs:
  - reports/review/review_report.md

allowed_tools:
  - Read
  - Search (Grep)
  - Glob
  - Directory Tree

permission:     readonly

allowed_return_stages:
  - Executor

next_stage:     Validator
```

---

## Stage 6: Validator

```yaml
stage:          Validator
role:           validator-agent
description:    验证知识库的功能完整性和数据一致性

inputs:
  - reports/review/review_report.md
  - (知识库当前状态)

outputs:
  - reports/validation/validation_report.md

allowed_tools:
  - Read
  - Search (Grep)
  - Glob
  - Directory Tree

permission:     readonly

allowed_return_stages:
  - Reviewer
  - Executor

next_stage:     Evaluator
```

---

## Stage 7: Evaluator

```yaml
stage:          Evaluator
role:           evaluator-agent
description:    对本次 Workflow 执行结果进行综合评分

inputs:
  - reports/validation/validation_report.md

outputs:
  - reports/final/evaluation_report.md

allowed_tools:
  - Read

permission:     readonly

allowed_return_stages:
  - Requirement
  - Architect
  - Planner
  - Executor
  - Reviewer
  - Validator

next_stage:     (Workflow 结束)
```

---

## 阶段工具权限总表

| 阶段 | Read | Search | Glob | Directory Tree | Write | Move File | Create Dir |
|------|------|--------|------|---------------|-------|-----------|------------|
| Requirement | ✓ | ✓ | ✓ | ✓ | - | - | - |
| Architect | ✓ | ✓ | ✓ | ✓ | - | - | - |
| Planner | ✓ | - | - | - | - | - | - |
| Executor | ✓ | - | ✓ | ✓ | ✓ | ✓ | ✓ |
| Reviewer | ✓ | ✓ | ✓ | ✓ | - | - | - |
| Validator | ✓ | ✓ | ✓ | ✓ | - | - | - |
| Evaluator | ✓ | - | - | - | - | - | - |

---

*本文与 `workflow_rules.md` 配合使用。阶段定义修改时需同步更新本文。*
