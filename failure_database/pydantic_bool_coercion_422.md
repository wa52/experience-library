# Pydantic 宽松模式把 "yes" 强转成 bool，422 测试误判

## 问题现象
FastAPI 端点 `POST /api/v1/settings/graph-mode`，body `{"enabled": "yes"}`，
测试断言应返回 422，实际返回 **200**，且配置被写成 `enabled=True`。

## 影响项目
- langchain-kb（图谱抽取模式开关端点）

## 原因
Pydantic v2 宽松（lax）模式下，`bool` 字段接受 `"true"/"false"/"1"/"0"/"yes"/"no"/"on"/"off"` 等
字符串并强制转成 bool——`"yes"` → `True`，所以校验通过、直接执行业务。

## 解决方案
测 422 时用**真正无法强转**的值，例如 `{"enabled": "not-a-bool"}` 或 `{"enabled": []}`，
不要用 `"yes"`/`"1"` 这类合法可转值。

## 教训
- 写校验失败的测试前，先确认框架是否做宽松类型强转（Pydantic/FastAPI、Express 的 body-parser 等）。
- 想知道"到底会不会转"，直接在小脚本里 `from pydantic import BaseModel; M(enabled="yes")` 跑一下。
