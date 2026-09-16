# Agent 验证闭环（validate-fix / MCP / 护栏）

## 场景
把"验证 → 简报 → 修复 → 再验证"做成闭环，且能被编码代理直接消费（MCP 工具），
同时必须保证对业务源码只读、高风险操作需批准。

## 模式
- **validate-fix = 结构化失败签名比较**：从运行提取失败签名（traditional 失败测试 id
  `file::name` + accumulated 阻断发现），聚焦重跑最小相关集（`make_pytest_step(targets=...)`），
  用集合运算分类 fixed / still_failing / new_regression，并链接新旧证据与 gate。
  关键：**junit.xml 通常无 file 属性**，要从 classname 推导文件路径才能得到合法 pytest node id。
- **MCP 是同一核心契约的薄壳**：工具函数直接调用 `RunContract`/`build_agent_brief` 等，
  不依赖 HTTP；响应统一 JSON。FastMCP 3.x 的 `mcp.call_tool` 返回 `(content_list, extra)` 元组，
  测试要取 `result[0][0].text`。
- **累积测试项合并**：每个 item 写 `ctx.results["accumulated"][item_name]`，契约统一
  `_merge_accumulated` 合并 findings/blocking_count/evidence，保证 gate 与简报只读合并后的结构。
- **只读护栏**：`is_writable(target)` 按顶层目录分类（data/evidence/reports/.scratch/tmp/temp 可写，
  其余业务源码不可写）；边界清单比对在运行前后执行，违反即 fail。
- **守卫操作审批模型**：`GuardedActionManager` 把高风险操作（杀进程/外部启动）建模为
  pending→approved/denied→executed/failed 状态机，**默认拒绝**；`execute` 只在 approved 后运行，
  否则抛 `GuardrailViolation`。状态记录进运行 `guardrails.actions`。

## 关键教训
- 新 runner 子进程要 `encoding="utf-8", errors="replace"`，否则 Windows GBK 解码崩溃；
  npm 在 Windows 是 `.cmd` shim，需 `shutil.which` + `cmd /c` 包装。
- 合并累积项会改变 `accumulated.item`（变拼接字符串）与 `evidence`（变 list），
  旧测试断言要同步改，schema 类型要跟对。
- MCP 工具返回原始 dict（`validate` 键），HTTP schema 用 `validation_alias` 映射为 `validation`——
  同一数据两种接口字段名不同，测试按各自契约断言。

## 复用
- 任何"验证-修复-再验证"闭环 + 代理集成套用本模式。参见 VeriAgent ticket 11-16
  （`validate/`、`mcp_server.py`、`guardrails.py`、`capabilities.py`）。
