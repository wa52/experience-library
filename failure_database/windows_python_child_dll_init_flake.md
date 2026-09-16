# Windows 下 python -c 子进程偶发挂起（DLL 初始化失败）

## 问题现象

测试里用 `subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.05)"])`
再断言子进程会很快退出，偶尔变成：

- 进程 3 秒后仍 `alive`，`poll()` 返回 `3221225794`（`0xC0000142`，`STATUS_DLL_INIT_FAILED`）。
- 同类断言（clean exit within wait）随机失败，但单独跑该文件又通过。

## 影响项目

- VeriAgent 进程生命周期观察器（ticket 14）与相关 observer 测试。
- 任何依赖"子进程立即退出"做确定性断言的测试套件。

## 根因

Windows 上频繁 spawn `python -c`（尤其在全量测试并行/重负载时）会偶发 DLL
初始化失败：子进程 `python.exe` 尚未跑完入口就僵死在进程里，代码根本没执行，
`time.sleep(0.05)` 自然永不返回。用"真实短生命周期子进程"验证"是否在时限内退出"
在本环境不可靠，是环境抖动而非逻辑错误。

## 解决方案

把"进程是否存活"做成可注入探针（`alive: Callable[[int], bool]`），让 observer
与 step 都用探针判定，测试注入确定性的 `lambda pid: True/False` 或"第 N 次调用后
返回 False"；真实进程只用于单点探针验证（`pid_exists`），不再依赖真实退出时序。

```python
result = observe_process_exit(pid, wait_seconds=1.0, alive=lambda pid: False)  # clean
result = observe_process_exit(pid, wait_seconds=0.05, alive=lambda pid: True)  # leaked
```

## 教训

- 涉及真实子进程生命周期的确定性测试，一律抽象出可注入探针，别依赖真实进程的
  退出时序；Windows + `python -c` 短子进程尤其不可靠。
- 看到 `0xC0000142` / 进程 poll 值异常但退出码缺失时，先怀疑子进程本身没跑起来，
  而不是被观察的逻辑错了。
- 观察器/工具类模块默认参数走真实探针、测试显式注入探针，两者互不干扰。
