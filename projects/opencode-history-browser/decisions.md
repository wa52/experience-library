# OpenCode History Browser — 关键决策记录

## ADR-1：纯原生 Web 前端而非 React/Vue

- **背景**：作为 OpenCode 插件发布，需要最小化依赖和打包体积
- **方案**：React（功能强但依赖大） vs Vanilla JS（零依赖，无构建步骤）
- **结论**：Vanilla JS + HTML + CSS，零前端依赖
- **代价**：前端代码组织靠手动维护，无组件化抽象，可维护性较低

## ADR-2：内嵌 HTTP 服务器而非 WebSocket

- **背景**：浏览器需要通过 API 与后端通信
- **方案**：WebSocket（双向推送，实时性好） vs HTTP fetch + 轮询（简单可靠）
- **结论**：Node.js 内置 http 模块 + 前端轮询
- **代价**：实时性依赖轮询间隔（1.5s），长轮询时浏览器打开多个标签页增加服务端负载

## ADR-3：Token 认证而非无认证

- **背景**：服务器监听 127.0.0.1，理论上只能本地访问
- **方案**：无认证（信任 localhost） vs Token 认证
- **结论**：随机 Token + URL 参数 + Header 双重校验
- **代价**：额外的复杂度，Token 存储在 kv store 中持久化

## ADR-4：双模式架构（TUI 插件 + Standalone）

- **背景**：用户可能通过 opencode 命令启动，也可能通过桌面快捷方式启动
- **方案**：仅 standalone（功能限制） vs 双模式适配不同使用场景
- **结论**：支持两种模式运行
- **代价**：维护两套启动逻辑，TUI 插件模式依赖 OpenCode 进程生命周期

## ADR-5：进程锁互斥而非端口占用检测

- **背景**：防止 standalone 模式重复启动
- **方案**：端口检测（可能误判） vs 文件锁（更可靠）
- **结论**：文件锁 + 健康检查兜底，锁文件包含 URL 和 PID
- **代价**：锁文件需要清理逻辑，异常退出可能留下脏锁

## ADR-6：快照使用 Balanced 策略

- **背景**：需要压缩长会话到可继续工作的上下文
- **方案**：Full（全部消息，太长） vs Balanced（筛选高信号内容，压缩）
- **结论**：提取目标、当前状态、重要细节、最近上下文，约 20-30 行
- **代价**：可能丢失非结构化的上下文细节

## ADR-7：OpenCode 命令重定向

- **背景**：让 `opencode`（无参数）自动打开浏览器，而非 TUI
- **方案**：修改 opencode.cmd/ps1 加入判断逻辑
- **结论**：用 `OPENCODE_HISTORY_BROWSER_REDIRECT` 标记，原命令备份为 opencode-cli
- **代价**：卸载时需要恢复原命令