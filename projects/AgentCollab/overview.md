# AgentCollab — 项目总览

> 最后更新：2026-09-03
> 当前版本：v0.1.0（MVP）
> 目标：通用多 Agent 协作环境（不绑定业务项目）：四专业 Agent + 协调器，计划/实施双模式，自由消息协作，全程审计

## 项目结构

```
AgentCollab/
├── src/agentcollab/
│   ├── protocol.py      # 全部数据模型（pydantic v2）
│   ├── eventlog.py      # TaskStore：JSONL 追加 + 原子写
│   ├── permissions.py   # 模式 × 副作用 × 路径白名单
│   ├── tools.py         # 8 内置工具 + invoke() 统一入口（权限→审计→执行）
│   ├── coordinator.py   # 路由、自由讨论、循环保护、批准流、实施闭环、报告
│   ├── agents/          # base(LLM 可选) + opencode/knowledge/experience/test
│   └── cli.py           # Typer：doctor/init/new/plan/set-plan/approve/implement/export
└── tests/               # 31 个离线用例（conftest 注入 tmp 环境，删 LLM Key）
```

## 技术栈

- Python >= 3.10（开发 3.13），项目本地 `.venv`
- pydantic>=2.7（协议模型）、typer>=0.12（CLI），无重型框架（刻意不用 LangGraph/消息队列）
- 持久化：纯文件（task.json / messages.jsonl / audit.jsonl / runs.jsonl / findings/ / reports/）

## 关键设计决策

1. **自由沟通 + 循环保护**：Agent 可广播/定向/质疑/移交，不固定发言顺序；同类发言（sender+type+内容哈希）重复 ≥2 次即暂停转人工（resume 恢复），防止无限互聊。
2. **双模式权限矩阵**：plan 只读；implement 允许 evidence_write+source_write；external_write（删除文件/Git 推送）一律拒绝；`edit_source` 仅 opencode Agent 可用。
3. **LLM 可选降级**：Key 只从环境变量读（`llm_api_key_env`），无 Key 时模板化确定性发言——测试与演示不依赖网络。
4. **测试即证据**：命令白名单执行 → RunRecord（退出码+日志路径）→ 失败生成结构化 Finding；不允许"口头宣布通过"。
5. **Agent 间不共享隐式上下文**：只看 messages.jsonl 中发给自己的消息；工具调用必须经 `invoke()`（权限检查+审计）。

## 踩坑记录（首轮开发实测）

- **pydantic v2 枚举序列化**：`model_dump()` 默认 mode 保留枚举对象，直接 `json.dumps` 崩溃。所有落盘必须 `model_dump(mode="json")`。
- **invoke 参数名撞车**：`invoke(registry, name, ctx, **kwargs)` 与工具参数 `name`（如 write_evidence 的文件名）冲突 → TypeError。统一改形参为 `tool_name`。
- **run_command 的路径校验误伤**：曾把 argv 拼接串当 target_path 做白名单校验，导致合法命令全部被拒。审计展示串与权限校验串必须分离。
- **循环保护懒构建双计数**：post() 先落盘再构建计数，history 已含当前消息，又手动 +1 → 首条消息即触发暂停。构建时用 `history[:-1]`。
- **pytest 收集 TestAgent**：类名以 Test 开头被当测试类收集并警告。pyproject 设 `python_classes = ["TestCheck"]` 解决。
- **子串检索语义**：经验库 Agent 用任务标题整串做 `in` 匹配，"显存泄漏修复" 匹配不到只含 "显存泄漏" 的文档——检索词要么短、要么分词。

## 验收状态

- `pytest tests/`：31 passed（<1s，离线）
- CLI 全流程（init→new→plan→set-plan→approve→implement→export）有端到端测试覆盖
- doctor 自检：python/data_home/白名单 OK；experience_root/kb/llm 未配置时 WARN 降级不阻断

## Phase 2：opencode MCP 桥接（v0.2.0，2026-09-03）

把真实 opencode CLI 经 stdio MCP 服务器接入协作对话（`{python} -m agentcollab.opencode_server`），OpenCode Agent 的分析/改码由真实 opencode 执行，桥接不可用时回退内置行为。外部 MCP 走 settings 的 `external_mcp`（opencode 风格配置），工具在注册表中与内置工具走同一 invoke（权限+审计）路径。

新增踩坑：
- **invoke 工具函数第一参数约定**：所有经 `invoke` 的工具函数第一个位置参数必须是 ToolContext。MCP caller 闭包曾把 ctx 误绑到配置参数（报错 `'ToolContext' object is not subscriptable`），看似协议层问题实为函数签名问题。
- **MCP 服务器内 spawn 子进程必须 stdin=DEVNULL**：桥接服务器的 stdin 是 MCP 协议管道，`opencode run` 继承后等待交互输入挂死 7 分钟；修复后同样调用 23s 返回。
- **mcp 2.x 破坏性改名**：FastMCP→MCPServer，依赖必须 `mcp>=1.2,<2`。
- **批处理回显中文经 GBK 码页乱码**：测试假 CLI 不要断言 `%*` 的中文内容，用 monkeypatch 捕获 argv 断言。
- **LLM 观点必须喂工具证据**：`llm_opinion` 增加 evidence_text 参数，否则 LLM 在已有真实桥接输出时仍声称没看到文件内容。

验收：44 测试全过（<1.5s，离线）；端到端冒烟中真实 opencode 给出行号级只读分析（demo.py:1-3 global MODEL / load 未导入隐患）。

## Phase 2：opencode MCP 桥接（v0.2.0，2026-09-03）

把真实 opencode CLI 经 stdio MCP 服务器接入协作对话（`{python} -m agentcollab.opencode_server`），OpenCode Agent 的分析/改码由真实 opencode 执行，桥接不可用时回退内置行为。外部 MCP 走 settings 的 `external_mcp`（opencode 风格配置），工具在注册表中与内置工具走同一 invoke（权限+审计）路径。

新增踩坑：
- **invoke 工具函数第一参数约定**：所有经 `invoke` 的工具函数第一个位置参数必须是 ToolContext。MCP caller 闭包曾把 ctx 误绑到配置参数（报错 `'ToolContext' object is not subscriptable`），看似协议层问题实为函数签名问题。
- **MCP 服务器内 spawn 子进程必须 stdin=DEVNULL**：桥接服务器的 stdin 是 MCP 协议管道，`opencode run` 继承后等待"交互输入"挂死 7 分钟；修复后同样调用 23s 返回。
- **mcp 2.x 破坏性改名**：FastMCP→MCPServer，依赖必须 `mcp>=1.2,<2`。
- **批处理回显中文经 GBK 码页乱码**：测试假 CLI 不要断言 `%*` 的中文内容，用 monkeypatch 捕获 argv 断言。
- **LLM 观点必须喂工具证据**：`llm_opinion` 增加 evidence_text 参数，否则 LLM 在已有真实桥接输出时仍声称"没看到文件内容"。

验收：44 测试全过（<1.5s，离线）；端到端冒烟中真实 opencode 给出行号级只读分析（demo.py:1-3 global MODEL / load 未导入隐患）。
