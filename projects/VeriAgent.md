# VeriAgent

**类型:** projects
**状态:** 进行中（ticket 01-24 已全部完成，437 项测试通过）
**语言:** Python 3.13 / FastAPI / FastMCP
**路径:** D:\VeriAgent

## 目标
Web 优先的验证工作台 + 编码代理子代理：对工作区跑传统测试（pytest/npm/dotnet）与
累积启发式检查，产出带证据的 Finding/Fix Brief、确定性质量门、Agent Brief，
并暴露 MCP 工具让编码平台直接调用。核心承诺：只读业务源码、高风险操作需批准。

## 关键组件
- `workspaces/`：技术栈与 runner 检测、持久化注册表
- `runs/`：Run Contract（生命周期/事件日志/只读边界）、RunStore、SSE 流
- `runners/`：pytest/npm/dotnet 子进程 runner，证据归一化
- `accumulated/`：绝对路径、环境依赖、进程生命周期、用户测试项、护栏
- `session.py`：Harness 会话（三层上下文、状态变更、停止策略 + ticket 24 动态探索循环）
- `hypotheses.py`、`patterns.py`、`regressions.py`：假设/故障模式库/回归用例
- `observers/`：进程生命周期、浏览器验证、UI 冻结
- `inspectors/`：可移植性、资源生命周期（acquire/check/release/reopen）
- `plugins/`：WinForms 切片、相机/视觉规划壳与相机资源切片
- `tools.py`：权限感知的验证工具注册表（read / write_safe / write_source + 拒绝策略）
- `findings/`、`gate.py`、`briefs/`、`reports/`、`validate/`：结构化结论链路
- `mcp_server.py`：8 个 MCP 工具（`veriagent-mcp` stdio）
- `guardrails.py`、`capabilities.py`：审批模型与插件注册

## 模式沉淀
tool_registry_with_verification_policy、accumulated_item_merge_shape、
agent_validation_closed_loop、mcp_tool_surface、plugin_capability_registry、
read_only_guardrails_approval、global_cli_launcher_opens_web、deterministic_quality_gate、
accumulated_heuristic_scan、sse_event_stream_async_run、traditional_test_runner_subprocess、
structured_finding_fix_brief、evidence_browser_and_reports、agent_brief_api、run_contract_event_log。

## 经验教训
- 中间件别吞业务 404；PowerShell 写文件带 BOM 会坑 pytest 9；子进程要指定 utf-8 编码；
  Windows 的 npm 是 .cmd shim 需 cmd /c 包装。
- 默认端口与 langchain-kb 冲突（都是 8000）：让路方改成 8300（env 可覆盖），
  envcheck 增加启动前端口占用探测 + 可操作报错，文档/测试断言同步（见
  failure_database/port_conflict_two_services.md）。
- Python 三重引号模板里的 JS `\n` 会被吃掉成真实换行 → 整段脚本语法错误、按钮无反应；
  校验必须抓渲染后的 HTML（见 failure_database/python_template_string_swallows_js_escape.md）。
- 全局命令 `veriagent`：入口在 import config 前把项目根插入 sys.path，否则被
  langchain-kb 的 config.py 抢占（见 failure_database/global_cli_config_module_hijack.md）。
- Windows 上 python -c 短子进程偶发 DLL 初始化失败（0xC0000142）挂起：进程生命周期
  类测试改用可注入 alive 探针，别依赖真实退出时序（见
  failure_database/windows_python_child_dll_init_flake.md）。
- 读合并后的 `run["accumulated"]` 逐项数据要进 `items[]` 过滤，别直读顶层项名（见
  patterns/accumulated_item_merge_shape.md）。
- 异步运行的终态必须单次原子写：分多次 store.update 会让轮询方读到
  status=completed 但 open_risks=None（负载抖动）；派生字段先在本地算齐再一次性落库
  （见 failure_database/async_terminal_write_polling_race.md）。
- 累积扫描噪声收敛：排除 data/evidence/reports 自指产物与工具目录、跳过 shebang 和
  文档，用真实项目当被测对象审计精度（见 patterns/accumulated_heuristic_scan.md）。
