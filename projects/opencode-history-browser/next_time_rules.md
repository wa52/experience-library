# OpenCode History Browser — 下次开发注意事项

## 架构层面

1. **HTTP 路由拆分**
   - 当前 handleRequest 函数 200+ 行，30+ 路由分支
   - 下次新增路由前应先拆分：Router(pattern → handler) 模式或 Express-like 中间件
   - 最小改动：把路由 handler 提取为独立函数

2. **前端状态管理**
   - 18 个全局变量散布在 app.js 中
   - 下次重构时使用状态对象：`const state = { sessions: [], current: null, ... }`
   - 或使用简单的发布/订阅模式管理状态变化

3. **API 版本兼容策略**
   - OpenCode SDK 可能继续变更 API
   - 建立 API 版本检测 + fallback 的标准化模式
   - 考虑从 OpenCode 的 `/config/providers` 探测可用 API

## 开发流程

1. **跨平台测试**
   - 每次修改路径/进程/终端相关代码必须在 Win/macOS/Linux 上测试
   - CI 中至少增加 Windows + Ubuntu 两个 runner

2. **日志先行**
   - 新增功能时先在关键路径加入 `writeLog()` 日志
   - 错误处理时记录完整上下文（方法、路径、参数、error stack）

3. **Token 安全**
   - 所有 URL 拼接处检查是否有 token 泄漏风险
   - 日志、错误消息、前端显示都要脱敏

## 已知待改进

1. 前端无单元测试（1100 行 Vanilla JS）
2. 后端无单元测试（1430 行 Node.js）
3. 路径解析逻辑复杂度高（约 150 行），缺少边界 case 测试
4. 未使用 TypeScript，类型错误只能在运行时发现
5. 卸载后可能遗留 VBS 文件、锁文件
6. standalone 模式在 OpenCode 进程崩溃后无自动重启机制