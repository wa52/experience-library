# Architecture Report

## Metadata
- Stage: Architect
- Agent: architect-agent
- Workflow: knowledge_workflow
- Version: v1
- Timestamp: 2026-07-12T12:05:00+08:00
- Status: completed

## Target Directory Structure

```
Knowledge/
└── bugs/
    ├── halcon/
    │   └── halcon_bugs.md
    ├── python/
    │   ├── dotenv_bom_issue.md
    │   ├── environment_bugs.md
    │   └── pyqt_bugs.md
    ├── deployment/
    │   ├── pyinstaller_ssl_dll_missing.md
    │   └── yolo_bugs.md
    └── README.md
```

## Metadata Schema

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 文档标题 |
| tags | string[] | 是 | 标签列表 |
| created | date (YYYY-MM-DD) | 是 | 创建日期 |
| updated | date (YYYY-MM-DD) | 是 | 最后更新日期 |
| category | enum | 是 | 分类：bug / failure / pattern / project |
| severity | enum | 否 | 严重程度：critical / high / medium / low |
| resolved | boolean | 否 | 是否已解决 |

## Tag Taxonomy

- 一级: `bug`
  - 二级: `halcon`, `python`, `deployment`, `pyqt`, `yolo`, `dotenv`, `pyinstaller`

## Naming Convention

- 目录命名: 全小写英文，`_` 连接
- 文件命名: `{主题}_bug.md` 或 `{组件}_bugs.md`
- 版本号: `v{数字}`

## Compatibility Note

- 当前 `bugs/` 不在任何索引中，迁移无外部依赖
- `failure_database/` 中的同名文件 `dotenv_bom_issue.md` 和 `pyinstaller_ssl_dll_missing.md` 需确认是否合并

## Deliverables
- [x] reports/architecture/architecture_bugs_v1.md

## Next Stage Input

传递给 Planner 的关键信息：
- 创建 4 个目录 + 目标目录 README
- 移动 6 个文件到目标子目录
- 为每个文件添加 YAML front matter
- 创建 `Knowledge/bugs/README.md`
