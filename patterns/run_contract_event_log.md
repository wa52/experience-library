# Run Contract + Event Log（验证运行核心接缝）

## 场景
需要一个 durable 的"运行"抽象：用户对某个目标（工作区/作业）发起一次执行，
运行有稳定 ID、生命周期状态（start/progress/completed/failed）、可持久化、
事后可回溯。同时运行边界必须默认对目标源码只读。

## 模式
- **领域包单独成层**（`runs/`），与 API 服务层、Web 层分离。Run Contract 是测试的主要接缝：
  测试直接构造 `RunContract(runs_dir=..., registry=...)` 执行，不依赖 HTTP。
- **每个运行一个 JSON 文件**（`data/runs/<id>.json`）+ **一个追加式 JSONL 事件日志**
  （`<id>.events.jsonl`）。JSONL 天然支持流式增量读取（后续 SSE 直接读尾部即可）。
- **构造函数路径注入**：`runs_dir`、`registry`、`steps` 全部可传入，测试用临时目录隔离，
  生产用模块级单例 + 懒加载 + 锁（与工作区注册表同款 `get_*()` 模式）。
- **只读边界 = 文件清单比对**：运行前后遍历工作区文件（跳过 .git/node_modules/__pycache__
  等噪声目录，带文件数上限防爆炸），记录 `relpath -> (size, mtime_ns)`；前后不一致则
  运行标记 failed + 写 `boundary_violation` 事件。不依赖 OS 沙箱，纯事后校验即可测。
- **steps 是可调用列表**：每个 step 拿到只读 `RunContext`（含 emit 通道），抛出异常即
  run_failed。真实 runner（pytest/npm/dotnet）后续以 step 形式插入，契约不变。
- **事件类型固定集合**：`run_started / progress / run_completed / run_failed / boundary_violation`，
  每个事件有 `seq`（从 1 递增）、`ts`、`type`、`message`、`data`。

## 关键教训
- 生命周期用显式常量（`RUNNING/COMPLETED/FAILED`），避免魔法字符串散落。
- 快照清单只比较集合差集时，`sorted(set(before) ^ set(after))` 能直接列出"变更了哪些文件"，
  对用户可读。
- `store.update(id, **changes)` 用参数化更新，避免每个字段一个 setter。
- 事件日志损坏时优雅降级（读到非法 JSON 行跳过），与服务配置损坏降级保持一致。

## 复用
- 新功能若需要"对某目标发起一次可回溯的执行"，直接采用本模式：持久化记录 + 事件日志 +
  生命周期状态机 + 注入式构造。参见 VeriAgent ticket 03（`src/veri_agent/runs/`）。
