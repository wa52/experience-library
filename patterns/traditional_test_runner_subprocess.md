# 传统测试 Runner（子进程执行 + 证据归一化）

## 场景
验证工具需要对目标项目执行真实测试命令（pytest / npm test / dotnet test），
把子进程输出固化为证据，并归一化成 pass/fail/error 结果，供 UI 与后续判定使用。

## 模式
- **检测层扩展检测结果**：`DetectionResult` 增加 `runners: list[str]`。pytest 支持判定要保守：
  `pytest.ini`、配置文件中"提及 pytest"（pyproject.toml/setup.cfg/tox.ini 内容含 pytest）、
  `tests/` 目录、`conftest.py`、`test_*.py`/`*_test.py`。**仅存在 pyproject.toml 不算**（先踩过坑）。
- **runner 是一个 Step**：`make_pytest_step(timeout)` 返回契约可执行的 callable。RunContext 增加
  `run_id` / `evidence_dir` / `results`，step 把归一化结果写入 `ctx.results["traditional"]`，
  契约在 step 完成后读取并决定运行终态。
- **证据与工作区隔离**：stdout/stderr/junit 全部写到 `evidence/<run_id>/`（目标项目之外），
  这样 pytest 产生的 `__pycache__`/`.pytest_cache` 虽在项目内，但已列入边界噪声目录，只读边界仍 clean。
- **子进程错误分级捕获**：
  - `TimeoutExpired` → verdict=error, timed_out=true
  - `OSError`（可执行文件不存在）→ verdict=error, exit_code=None（进程根本没启动）
  - exit 0 → pass；exit != 0 且 junit 计数有 failures/errors → fail；其余 → error
- **解析 junit.xml**（`xml.etree` 遍历所有 testsuite 汇总），比解析终端文本稳。
- **默认 step 随工作区选择**：契约按 `workspace["runners"]` 组装默认管线（inventory + pytest），
  API 无需感知；也可显式传 steps 覆盖（测试用）。

## 关键教训
- 归一化结果要进运行记录（`traditional` 字段），而不是只留在事件里——事件是可丢的流，
  记录是持久结论。
- 测试失败 ≠ 边界违约：失败时 `boundary_ok=True`，只有源码被改才 False。二者语义要分开。
- 断言证据时用"目录内容恰好等于预期文件列表"，而不是比较整个工作区（__pycache__ 会干扰）。
- 验证自己的项目是最强冒烟测试：VeriAgent 对自身跑 pytest，91 通过。

## 复用
- 新增其他测试框架 runner（npm/dotnet）时复用同一 Step 契约与 verdict 归一化。
  - npm：`package.json` 含 `scripts.test` → runners=npm；Windows 用
    `shutil.which("npm")` + `["cmd", "/c", ...]` 包装 shim（见 failure_database
    `windows_npm_cmd_shim_subprocess.md`）。
  - dotnet：存在 `.csproj/.sln` → runners=dotnet；无 junit 产物时走
    `build_finding` 的非 junit 分支（stdout 末尾几行 + exit code 构造 finding）。
  - 子进程统一 `encoding="utf-8", errors="replace"`，防 Windows GBK 解码崩溃。
  - 参见 VeriAgent ticket 05/13（`src/veri_agent/runners/pytest.py|npm.py|dotnet.py`）。
