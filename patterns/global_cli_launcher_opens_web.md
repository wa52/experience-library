# 全局命令行启动器（自动打开 Web + 健康检查）

## 场景
桌面工具的"主命令"体验：用户在任意目录输入 `veriagent`，自动打开 Web 工作台。
服务没起就前台启动并等就绪后开浏览器；服务已起就直接开浏览器。

## 模式
- **入口即 CLI**：`[project.scripts]` 指向 `veri_agent.cli:main`，不是指向不存在的
  `app:run`。CLI 复用 Web 的 `create_app()` + `uvicorn.run`，与 `python main.py` 同一套逻辑。
- **健康检查先于启动**：`_service_running()` 用 `urllib.request.urlopen` 探
  `GET /api/v1/health`，成功则 `webbrowser.open(base_url)` 直接返回，不重复起服务。
- **前台启动 + 后台开浏览器**：未运行 → 环境检查 → 起 `threading.Thread(_open_when_ready,
  daemon=True)` 轮询健康端点（0.25s 间隔，上限 40 次）→ `uvicorn.run` 前台阻塞；
  终端保持服务进程，Ctrl+C 退出，不留僵尸。
- **环境检查失败即退出**：`check_environment()` 有问题时返回码 1，不开浏览器不启服务，
  输出可操作的错误（端口占用等）。
- **路径隔离**：入口在 `import config` 前把项目根插入 `sys.path`（见
  failure_database/global_cli_config_module_hijack.md），否则会被别的项目的 config 抢占。
- **UTF-8 stdio**：Windows 控制台重包 stdout/stderr 为 UTF-8，避免中文日志 GBK 乱码。

## 关键教训
- 健康探活只测 `status_code`，不解析 JSON 内容，简单且稳；探活失败（连接拒绝）
  一律视为"未运行"。
- 用 `threading.Thread(daemon=True)` 做"服务就绪后开浏览器"，避免在 uvicorn 主循环
  前同步阻塞；`webbrowser.open` 传入函数引用以便测试 patch。
- CLI 测试全部 patch 掉 `_configure_stdio`/`_service_running`/`uvicorn.run`，
  断言三态：已运行只开浏览器、未运行启动服务、环境失败不开不启。
- 全局命令验证必须从**非项目目录**执行 `where veriagent` + 实际启动（见 config hijack）。

## 复用
- 任何"安装后一条命令打开 Web"的工具。参见 VeriAgent `src/veri_agent/cli.py`
  与 `tests/test_cli.py`。
