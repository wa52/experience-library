# 命令重定向 + 备份模式

## 适用场景
想劫持一个已有的 CLI 命令，在无参数时启动 GUI，但保留原有命令行为。

## 推荐架构
```
原始命令 (如 opencode.cmd)
  → 备份为 opencode-cli.cmd
  → 新 opencode.cmd 加入判断：
    无参数 → 启动 GUI
    有参数 → 跳转到 opencode-cli.cmd
```

## 核心实现
```batch
@ECHO off
REM REDIRECT_MARK
IF NOT "%~1"=="" GOTO cli
START "" /B wscript.exe "%LAUNCHER%"
EXIT /B 0
:cli
CALL "%CLI%" %*
```

## PowerShell 版本
```powershell
# REDIRECT_MARK
if ($args.Count -eq 0) {
  Start-Process -FilePath "wscript.exe" -ArgumentList '"launcher"' -WindowStyle Hidden
  exit 0
}
& "cli-command" @args
```

## 卸载
```javascript
async function restoreOriginal() {
  await writeFile(originalCmd, await readFile(backupCmd));
}
```

## 验收标准
- [ ] 无参数时启动 GUI
- [ ] 有参数时行为与原始命令一致
- [ ] 卸载后完全恢复
- [ ] 跨版本升级时备份不被覆盖