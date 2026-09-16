# OpenCode History Browser — 验收清单

## 功能验收
- [ ] 会话列表加载并显示（标题、时间、预览）
- [ ] 搜索过滤按 ID 和标题匹配
- [ ] 会话详情查看（消息、工具调用、推理、任务）
- [ ] 发送新消息（文本 + 图片）
- [ ] 模型选择和切换
- [ ] 会话重命名
- [ ] 会话置顶/取消
- [ ] 会话删除 / 批量删除
- [ ] 创建 Balanced 快照
- [ ] 中止正在回复的消息
- [ ] 打开独立 CLI 终端
- [ ] 点击路径打开文件/文件夹
- [ ] 审批权限请求
- [ ] 回答交互式问题

## 浏览器命令验收
- [ ] /skills — 显示已安装技能
- [ ] /mcp — 显示 MCP 服务状态
- [ ] /logs — 查看和清除日志
- [ ] /uninstall — 卸载插件

## 性能验收
- [ ] 会话列表 250+ 加载不卡顿
- [ ] 实时轮询不导致 CPU 持续高占用
- [ ] 浏览器闲置 60 秒后自动关闭
- [ ] 同时运行多个标签页不冲突

## 兼容性验收
- [ ] Windows 10/11（cmd.exe, PowerShell, Windows Terminal）
- [ ] macOS（Terminal）
- [ ] Linux（x-terminal-emulator）
- [ ] Chrome / Edge / Firefox
- [ ] 独立模式 + TUI 插件模式

## 安装/卸载验收
- [ ] `opencode plugin --global` 安装成功
- [ ] `/history-browser-doctor` 全部检查通过
- [ ] `/history-browser-uninstall` 恢复原始命令
- [ ] VBS 桌面快捷方式创建成功