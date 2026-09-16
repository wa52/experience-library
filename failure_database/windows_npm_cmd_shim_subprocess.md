# Windows 下 npm 子进程 FileNotFoundError

## 问题现象

在 Windows 上用 `subprocess.run(["npm", "test", ...])` 启动 npm 测试时抛
`FileNotFoundError: [WinError 2] 系统找不到指定的文件`，即使 `npm -v` 在 PowerShell 里正常。

## 影响项目

- VeriAgent 传统测试 runner 的 npm 支持（ticket 13）

## 根因

Windows 的 `npm` 是 `npm.cmd` 批处理 shim，不是 `.exe`。`subprocess.run` 直接按名字
查找可执行文件时不会自动解析 `.cmd`，`CreateProcess` 找不到 `npm` 而抛 WinError 2。
同理适用于 `pip`、`tsc`、`dotnet` 之外的多数 Node 工具。

## 解决方案

- 用 `shutil.which("npm")` 拿到 shim 全路径（`...\npm.cmd`），再把命令拆成
  `["cmd", "/c", shim, "test", ...]` 由 cmd 解释执行（cmd 能解析 `.cmd`）。
- 兜底：`shutil.which` 也找不到时直接报 verdict=error、exit_code=None，进程没启动。

```python
import shutil, subprocess
shim = shutil.which("npm")          # -> C:\...\npm.cmd
cmd = ["cmd", "/c", shim, "test"]
subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
```

## 教训

- Windows 上"命令能跑"不等于 `subprocess` 能跑：先 `shutil.which` 看返回的是不是 `.cmd`。
- 子进程输出捕获统一 `encoding="utf-8", errors="replace"`，否则 GBK 解码崩溃
  （见 `python_windows_default_encoding_skill_validation.md`）。
- 失败要分级：可执行文件缺失（exit_code=None）与测试失败（exit != 0）语义不同。
