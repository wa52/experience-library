# Workflow Context — 阶段上下文可见范围

> 本文定义每个阶段 Agent 可以访问的知识范围。
> 限制上下文以降低 Token 消耗、减少 Agent 跑偏风险。

---

## 原则

1. **最小上下文原则** — 每个阶段只看到完成当前任务所需的最少信息
2. **渐进可见** — 阶段越靠后，看到的上下文越广
3. **禁止越级访问** — 下游 Agent 不可直接读取上游未交付的原始知识

---

## Stage 1: Requirement

```
可访问:
  ├── D:/项目经验库/  (仅目录结构和文件名)
  ├── 用户提供的 Task 描述
  └── workflow/       (仅 workflow_stage.md, workflow_checklist.md)

不可访问:
  ├── 知识库文件内容  (只看文件名，不读内容)
  ├── reports/        (尚无报告)
  └── 其他 Workflow 定义
```

**目的：** 从外部观察知识库结构，避免被内容影响判断。

---

## Stage 2: Architect

```
可访问:
  ├── reports/requirement/requirement_report.md
  ├── D:/项目经验库/  (仅目录结构)
  ├── 00_索引/       (阅读现有索引作为参考)
  └── workflow/       (仅 workflow_stage.md, workflow_context.md)

不可访问:
  ├── 知识库文件内容  (只读目录结构，不读文件)
  ├── 用户原始 Task
  └── Executor 相关定义
```

**目的：** 基于需求报告设计结构，不被已有内容固化思维。

---

## Stage 3: Planner

```
可访问:
  ├── reports/requirement/requirement_report.md
  ├── reports/architecture/architecture_report.md
  └── workflow/       (全部)

不可访问:
  ├── 知识库文件内容
  └── 用户原始 Task
```

**目的：** 基于需求和架构制定计划，独立设计执行方案。

---

## Stage 4: Executor

```
可访问:
  ├── reports/planner/planner_report.md
  ├── reports/architecture/architecture_report.md  (仅目录结构部分)
  ├── D:/项目经验库/  (完整读写访问)
  ├── workflow/       (全部)
  └── backup/         (写入备份)

不可访问:
  ├── reports/requirement/  (不直接读需求)
  ├── 其他阶段报告
  └── reports/execution/ 之前版本的日志 (只看当前)
```

**目的：** 只按计划执行，不自行判断"应该做什么"。

---

## Stage 5: Reviewer

```
可访问:
  ├── reports/architecture/architecture_report.md
  ├── reports/execution/execution_log.md
  ├── reports/planner/planner_report.md  (验证是否按计划执行)
  ├── D:/项目经验库/  (完整只读访问)
  └── workflow/       (全部)

不可访问:
  ├── reports/requirement/  (不回溯需求)
  └── 用户原始 Task
```

**目的：** 对照架构和计划审查执行结果，独立判断。

---

## Stage 6: Validator

```
可访问:
  ├── reports/review/review_report.md
  ├── reports/architecture/architecture_report.md  (仅指标部分)
  ├── D:/项目经验库/  (完整只读访问)
  ├── workflow/       (全部)
  └── 索引脚本/验证工具

不可访问:
  ├── 用户原始 Task
  └── Executor 日志 (避免被执行过程影响判断)
```

**目的：** 独立验证最终状态，不关心过程。

---

## Stage 7: Evaluator

```
可访问:
  └── reports/        (全部阶段报告)
  └── workflow/       (全部，特别是 workflow_score.md)

不可访问:
  ├── D:/项目经验库/  (不直接检查，基于报告评分)
  └── 用户原始 Task
```

**目的：** 基于所有报告和评分标准做最终评价。

---

## 上下文可见范围总表

| 阶段 | 知识库文件 | 用户 Task | 需求报告 | 架构报告 | 计划报告 | 执行日志 | 审查报告 | 验证报告 | 评分标准 |
|------|-----------|-----------|---------|---------|---------|---------|---------|---------|---------|
| Requirement | 目录仅 | ✓ | - | - | - | - | - | - | - |
| Architect | 目录仅 | - | ✓ | - | - | - | - | - | - |
| Planner | - | - | ✓ | ✓ | - | - | - | - | ✓ |
| Executor | ✓ | - | - | 部分 | ✓ | - | - | - | ✓ |
| Reviewer | ✓ | - | - | ✓ | ✓ | ✓ | - | - | ✓ |
| Validator | ✓ | - | - | 部分 | - | - | ✓ | - | ✓ |
| Evaluator | - | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

*本文与 `workflow_stage.md` 配合使用。Agent 在执行时严格遵守本文定义的可见范围。*
