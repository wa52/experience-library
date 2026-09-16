# 两个项目默认端口冲突（8000）

## 问题现象

VeriAgent 与 langchain-kb 都默认监听 `8000`：langchain-kb 的 `main.py` 硬编码
`uvicorn.run(app, host="0.0.0.0", port=8000)`，VeriAgent 的 `config.py` 默认
`VERI_PORT=8000`。先启动 KB 后，VeriAgent 启动时报 `[Errno 10048]` 端口被占用
（或用 `--reload` 时进程反复重启）。

## 根因

两个项目各自独立选择默认端口，都选了最常用的 8000；且其中一个（langchain-kb）
把端口硬编码在入口脚本里，**无法通过环境变量覆盖**。没有启动前探测，
冲突要到 `uvicorn.bind` 阶段才暴露。

## 解决方案

- **让路方 = 可配置方**：改 VeriAgent 默认端口为 `8300`（`config.py` 的
  `VERI_PORT` 默认值），保留 env 覆盖能力；不动 langchain-kb（只读项目 + 硬编码无法改）。
- **启动前端口探测**：`envcheck.py` 新增 `_port_in_use(host, port)`——
  `socket.bind` 失败即认为被占用；`check_environment()` 在绑定前报告
  「Port ... already in use ... Set VERI_PORT to a free port, or stop the program holding the port」，
  启动即失败并给可操作指令，而不是让 uvicorn 抛晦涩的 WinError 10048。
- **同步文档**：README 环境变量表、.env.example、本地启动说明三处一致改端口。
- **同步测试断言**：`test_config.py` 断言默认端口的用例要跟着改（`assert config.PORT == 8300`）。

## 教训

- 两个项目都在本机跑时，默认端口冲突是必然的：先查对方用什么端口，再定自己的默认值。
- 端口绑定失败属于"启动环境问题"，应放在环境依赖检查里提前报错，
  报错要带可操作指令（设哪个 env、可能是谁占用），而不是等 ASGI 服务器抛异常。
- 改动默认配置值后，必须全局搜索旧值（README/.env.example/测试断言），
  只改 config.py 会让文档与测试继续咬住旧端口。
- 端口占用探测用 `socket` 而非 `psutil`：零依赖，测试可 patch 返回值，
  或用真实绑定 socket 验证（`bind(("127.0.0.1", 0))` 拿空闲端口再探测，避免 flaky）。
