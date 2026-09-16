# Start-Process 启动的服务被命令超时连带杀掉（端口反复"起不来"）

## 问题现象
用 PowerShell `Start-Process` 后台启动 uvicorn，健康检查也通了（日志显示 Uvicorn running），
但下一条命令一查端口又是空的，浏览器连不上；服务进程"消失了"，日志无报错、干净结束。

## 影响项目
- langchain-kb（E2E 浏览器验证时服务反复被杀，用户误以为"没打开"）

## 原因
opencode/CLI 的 bash 工具对**超时的命令会终止整棵进程树**（包括 Start-Process 派生的子进程）。
当"启动 + 长轮询健康"写在同一命令里，轮询超过命令 timeout → 工具杀树 → 服务一起死。
uvicorn 日志停在没有异常处，看起来像是被外部 kill。

## 解决方案
1. **启动与轮询拆开**：`Start-Process` 单独一条命令（立即返回），健康检查用**短轮询**（每条命令 ≤ 30-40s）分多次调用，绝不单条命令长时间等待。
2. **隐藏 cmd 全脱离 + 环境变量前置**：
```powershell
$env:HF_HUB_OFFLINE = "1"   # 必须在 PowerShell 里设，cmd 的 set 对子进程 python 不一定生效
$cmd = 'cd /d D:\... && python -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000 > C:\Temp\srv.log 2>&1'
Start-Process cmd.exe -ArgumentList "/c", $cmd -WindowStyle Hidden -PassThru
```
3. 停服务要杀对进程：venv 的 `Scripts\python.exe` 是启动器，会再拉一个 python 子进程占端口；按 `Get-NetTCPConnection -LocalPort 8000 -State Listen` 的 OwningProcess 杀，别只杀启动器。

## 教训
- 远程/CLI 环境里"后台服务 + 长命令"是高风险组合；把等待拆短、把启动和探测分离。
- 判断"服务到底有没有起来"用端口占用 + HTTP 健康码，别只看启动日志。
- HF 模型加载离线环境要 `HF_HUB_OFFLINE=1`，否则 huggingface.co 5 次重试会"看似卡死"几分钟。
