# Node.js 内嵌 Web 应用 — API 设计指南

## 路由结构

```
GET    /api/health          → 健康检查
GET    /api/resource        → 列表
GET    /api/resource/:id    → 详情
POST   /api/resource/:id    → 更新
POST   /api/resource        → 创建
DELETE /api/resource/:id    → 删除
POST   /api/resource/:id/action → 自定义操作
```

## 请求格式
- POST/PUT 请求体：JSON (`application/json`)
- GET 参数：URL query string

## 响应格式

### 成功
```json
{ "ok": true, "data": { ... } }
```

### 失败
```json
{ "error": "Human readable message" }
```

### 列表
```json
{ "ok": true, "items": [ ... ], "total": 100 }
```

## HTTP 状态码
| 码 | 场景 |
|----|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 认证失败 |
| 404 | 资源不存在 |
| 500 | 服务端错误 |

## 认证
- Header: `X-App-Token: <token>`
- URL: `?token=<token>`（仅限 GET，日志脱敏）