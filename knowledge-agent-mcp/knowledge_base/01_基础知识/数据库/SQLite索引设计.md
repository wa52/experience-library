---
id: foundation-sqlite-index-design
title: SQLite索引设计基础
category: foundation
knowledge_type: architecture
domain: foundation/database/sqlite
tags: [SQLite, 索引, 查询]
technologies: [SQLite]
languages: [SQL, Python]
versions:
  applicable: ["3"]
status: reviewed
confidence: 0.84
created_at: 2026-07-12
updated_at: 2026-07-12
---

# SQLite索引设计基础

文本检索场景至少要区分主表、标签表、版本表、关联表和切块表，方便增量更新与过滤查询。
