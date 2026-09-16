# 验证工具注册表与验证只写策略（Tool Registry + permission-aware write policy）

## 场景

验证工作台要暴露可执行动作（跑命令、查页面、观察进程、插件切片），但必须守住
"对业务源码只读、高风险操作需批准"的承诺。需要一个统一的注册表让 API/Web/Agent
都能看到"有哪些工具、权限如何、会产生什么副作用"，并强制在**每次执行时**执行策略，
而不是散落在各调用点判断。

## 模式

- **工具 = 数据 + 元数据**：`Tool(name, description, source, permission, side_effect, handler, metadata)`。
  `source` 区分 builtin/plugin/user，`side_effect` 区分
  none / writes_safe_artifacts / writes_workspace_source / executes_process / network。
  快照 `snapshot_tools()` 供 API/Web 展示，只暴露元数据、不暴露 handler。
- **两级权限模型**：`permission`（工具自身行为：read / write_safe / write_source）+
  `side_effect`（执行后果）。策略函数 `verification_write_policy(tool)` 只对
  `write_source` 与 `writes_workspace_source` 返回 deny——**write_safe 永远放行**
  （证据、报告、生成的测试用例、临时产物），因为验证只写 VeriAgent 自己的产物。
- **执行即策略**：`registry.execute(name, params)` 内部先查工具、再跑策略、无 handler
  报错、结果必须是 dict。调用方（step、插件、MCP）一律走 execute，不直接碰 handler。
- **危险命令拒绝清单**：命令工具对 argv0 基名做 deny-list（format/deltree/mkfs），
  删除类工具（rm/del/rd/rmdir）仅在出现递归/强制旗标（-rf /s 等）时拒绝；`rm 文件`
  这类非递归删除不拦，保证合法验证命令（测试、启动检查、清理）照常运行。
- **观察器/检查器可注入探针**：任何涉及真实外部状态的动作（进程存活、浏览器后端、
  冻结计时）都接受可注入的 `alive`/`backend`/`probe` 回调，默认参数走真实实现，
  测试注入确定性实现（见 failure_database/windows_python_child_dll_init_flake.md）。
- **插件 = 工具来源**：WinForms/相机等切片以 `source="plugin"` 的 Tool + Capability
  注册，而不是硬编码进 runner 管线；能力（能做什么）与工具（能执行什么）分离。

## 关键教训

- 平台无关的"策略安全"别靠真实副作用验证：命令拒绝清单直接对 argv 数组判，
  不要在测试里真去跑 `rm -rf`。
- 工具元数据要能回答"写到哪里"：`metadata={"writes": "evidence files only"}` 让
  审批模型一眼可判；合成 `write_source` 工具（无 handler）是演示 deny 路径的好办法。
- 新工具注册后必须刷新快照（register 幂等 + 模块加载即注册），否则 API 看不到。

## 复用

- 新增验证动作（命令、页面、进程、插件切片）一律：定义 handler → 注册 Tool
  （带 permission/side_effect/metadata）→ step 工厂走 `registry.execute` →
  结果落 `ctx.results` 进 run 记录。参见 VeriAgent tickets 09/15/16/20。
