---
id: best-practice-request-id-logging
title: 请求ID与检索日志最佳实践
category: best_practice
knowledge_type: best_practice
domain: best-practice/logging/request-tracing
tags: [日志, request_id, tracing]
technologies: [Python, MCP]
languages: [Python]
versions:
  applicable: ["3.10"]
status: verified
confidence: 0.89
created_at: 2026-07-12
updated_at: 2026-07-12
---

# 请求ID与检索日志最佳实践

每次工具调用都应生成唯一 `request_id`，并记录查询、过滤条件、命中 ID、耗时和降级状态。
