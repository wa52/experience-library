# OpenCode History Browser — 经验教训

## 1. Node.js HTTP 服务器 + 浏览器的 CORS/SOP

- 服务端和前端同机 127.0.0.1，无跨域问题
- Token 通过 URL 参数传递，注意 URL 日志中 redact
- 前端用 sendBeacon 做页面关闭通知，比 fetch 更可靠

## 2. 进程管理最佳实践

- spawn 子进程时用 `windowsHide: true` 避免弹出黑窗口
- 子进程 spawn 后必须 unref()，否则会阻止父进程退出
- 进程退出处理要覆盖：exit、SIGINT、SIGTERM、SIGHUP
- Windows 下 cmd.exe 启动的 batch 文件需要额外的 call 处理

## 3. 文件锁的可靠性

- `fs.open(lockFile, "wx")` 原子创建锁文件
- 异常退出时锁文件残留，需要兜底：读取锁文件 URL → 健康检查 → 清理
- 锁文件内容包含 URL + PID，便于调试

## 4. 端口检测的竞态

- 多个实例同时检测端口可用性可能冲突
- 方案：先 listen 再检测，而不是先检测再 listen
- listen 失败后尝试下一个端口（8765-8795, 4096+）

## 5. 前端实时更新的设计

- 轮询比 WebSocket 实现简单 10 倍
- 关键优化：只有 signature 变化时才重新渲染
- signature 包含：role:id:created:completed:error:text.length:activities.length
- 避免不必要的 DOM 操作

## 6. 路径解析的复杂性

- 从消息文本中提取文件路径是最复杂的功能之一
- 路径格式多种多样：反引号、引号、绝对路径、相对路径
- Windows 路径 `C:\xxx` 和 Unix 路径 `/xxx` 都要支持
- 错误路径要静默忽略，不要打断正常渲染

## 7. 跨平台兼容的坑

- `.cmd` vs `.bat` vs `.ps1` 在 Windows 下的行为差异
- wt.exe（Windows Terminal） vs cmd.exe 的传参不同
- macOS 下 `open -a Terminal` 的行为
- Linux 下 `x-terminal-emulator` 不确定可用
- `which` vs `where.exe` 的程序查找命令差异