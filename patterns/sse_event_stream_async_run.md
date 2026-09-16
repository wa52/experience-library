# SSE 事件流 + 异步运行（Run Stream / EventSource）

## 场景
运行是异步的（后台线程执行），浏览器需要实时看到事件，且结束后仍可回放。
同时要保留"契约是主接缝"的可测性，不能用 http 层把核心逻辑裹住。

## 模式
- **核心层只提供生成器**：`contract.stream_events(run_id)` 是个纯 Python 生成器，
  内部循环：读事件日志 → `yield` 新增事件 → 查 run 状态 → 未终态则 `sleep(poll)`。
  测试直接 `list(contract.stream_events(id))` 即可断言顺序与终态事件，不碰 HTTP。
- **同步执行与异步启动共享同一 job**：把"执行步骤+边界校验+落库"抽成
  `_run_job(workspace, run_id, steps)`。`verify_workspace`（同步，主接缝）先 `store.create`
  再调 job；`start_async` 用 `threading.Thread(daemon=True)` 包住 job 立即返回 status=running。
  关键坑：**不能让 job 自己 create run**，否则 async 里会出现两个 run id，返回的 id 永远不到终态，
  stream 会无限挂起。
- **路由层只做格式转换**：`StreamingResponse(generator(), media_type="text/event-stream")`，
  每个事件输出 `event: {type}\ndata: {json}\n\n`，外加 `retry: 1000`、`Cache-Control: no-cache`、
  `X-Accel-Buffering: no`。404 校验在生成器外先做（生成器是惰性的，异常要提前抛出）。
- **前端 EventSource**：`onmessage` 解析 JSON 追加到 console；终态事件（run_completed /
  run_failed / boundary_violation）触发 `source.close()` 防自动重连；`onerror` 也 close。
  已结束运行能打开，是因为流先重放持久化事件、读完之后再判定终态退出。
- **异步 API 的测试要轮询**：`POST /runs` 返回 running 后，helper 反复 GET 直到 status 进入
  completed/failed（带 timeout），再断言结果。

## 关键教训
- `event_count` 在 `store.update` 时才写，stream 判终态用 `status in (completed, failed)
  and seen >= event_count`，避免读到旧计数提前结束。
- 事件日志 JSONL 天然支持"先重放+后追加"，无需维护游标文件。
- 测试里 `types.count("progress")` 用下限断言，不要写死精确次数（步骤内 emit 次数是内部细节）。

## 复用
- 需要"异步执行 + 实时可见 + 事后回放"的界面，直接套用：后台线程跑 job、核心生成器流式事件、
  路由包装 SSE、前端 EventSource 消费。参见 VeriAgent ticket 04（`src/veri_agent/runs/contract.py`）。
