# 只读护栏 + 守卫操作审批模型

## 场景
验证/自动化工具必须对业务源码只读，但又要执行高风险操作（杀进程、外部启动）。
需要把"允许写什么、什么必须批准"固化成可记录、可测试的模型。

## 模式
- **可写目标分类**：`is_writable(target) -> bool` 按顶层目录白名单
  （`data` / `evidence` / `reports` / `.scratch` / `tmp` / `temp`）判定；
  其余路径（业务源码）一律不可写。纯函数，直测。
- **边界清单比对**：运行前后对工作区做文件清单 manifest diff，
  被改动即 `boundary_ok=False` → run fail + `boundary_violation` 事件。
  注意：测试失败 ≠ 边界违约（测试只产生缓存/临时文件），二者语义分开。
- **守卫操作状态机**：`GuardedActionManager` 把高风险操作建模为
  `pending → approved|denied → executed|failed`，**默认拒绝**；
  `execute()` 只在 approved 后执行 fn，否则抛 `GuardrailViolation`。
  - `propose(kind, desc)` 生成 action（id、status=pending）
  - `approve(action_id)` / `deny(action_id)` 由人工/审批方调用
  - `execute(action_id, fn)` 运行 fn，异常时 status=failed 并 re-raise
- **记录即证据**：动作状态列表写入运行 `guardrails.actions` + `guardrails.json` 证据，
  API/UI 可展示"此 run 尝试过什么、被拒了什么"。

## 关键教训
- 审批模型测试易错：**execute 前必须先 approve**；拒绝路径要断言抛 GuardrailViolation
  且 status 保持 denied。
- 累积项合并后 `_build_guardrails` 读原始 item 的 `actions` 字段（合并可能丢自定义键），
  别从合并后的 findings 里反推动作。
- 默认拒绝要有"显式记录"：即使本次没有违规动作，也要在证据里写一份 actions=[]，
  保持证据文件恒存在（旧测试若断言证据目录精确文件列表要同步加 guardrails.json）。

## 复用
- 任何"只读验证 + 需要授权的外部副作用"工具。参见 VeriAgent ticket 16
  （`src/veri_agent/guardrails.py`、`accumulated/guardrails.py`）。
