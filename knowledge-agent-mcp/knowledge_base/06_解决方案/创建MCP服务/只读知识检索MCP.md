---
id: solution-mcp-stdio-readonly
title: 创建只读知识检索 MCP 服务
category: solution
knowledge_type: solution
domain: ai/mcp/knowledge-retrieval
tags:
  - MCP
  - KnowledgeBase
  - SQLite
  - Retrieval
technologies:
  - MCP
  - SQLite
  - Python
languages:
  - Python
versions:
  applicable:
    - "3.11"
status: verified
confidence: 0.92
source_type: project_experience
source_ids:
  - knowledge-agent-mcp-project
related_items:
  related_to:
    - ai-mcp-server-concept
    - best-practice-fixed-retrieval-agent
created_at: 2026-07-12
updated_at: 2026-07-12
---

# 创建只读知识检索 MCP 服务

## 适用场景

需要让 OpenCode 或其他客户端通过固定工具访问本地知识库。

## 总体结构

- MCP server 负责协议接入
- retrieval agent 负责任务理解和检索编排
- SQLite 负责索引和过滤
- 知识库保持只读

## 完整步骤

1. 扫描 Markdown + YAML Front Matter。
2. 建立 SQLite 索引。
3. 暴露 consult_knowledge 等工具。
4. 用固定子智能体做查询规划和结果压缩。
5. 模型不可用时退化为纯检索。

## 风险

- 空知识库会导致结果不足。
- 没有版本信息时结论适用范围会变宽。
