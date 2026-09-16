# 404 中间件吞掉业务 404

## 症状
某 API 端点（GET /runs/{id}/finding）对"无 Finding"抛 HTTPException(404, "no finding available")，
但客户端收到的却是 "Route GET ... not found"，完全看不到业务 detail，排障时以为是路由没注册。

## 根因
`catch_unmatched_routes` 中间件对**所有** 404 响应统一改写为 "Route ... not found"。
服务层通过 exception_handler 抛出的业务 404 也是 404，被中间件一并吞掉并覆盖。

## 修复
删除该中间件。Starlette 对未匹配路由本就返回 JSON `{"detail": "Not Found"}`，
自定义改写没有意义；业务 404 由 `http_exception_handler` 统一产出 ErrorResponse。
（另一思路：保留中间件但只在响应是纯文本 404 时改写，但既然默认行为已满足需求，直接删除更干净。）
- 新增一个抛 HTTPException(404) 的端点，断言响应 body 是业务 detail 而非 "Route ... not found"。
- 用真实服务 + curl 对不存在路由和业务 404 各打一次，对比返回体。

## 教训
中间件做"美化/兜底"时，必须只匹配它该管的那一类响应（用 content-type 或状态码+body 特征
区分默认响应与业务响应），否则会掩盖真实错误，让排障成本成倍上升。
