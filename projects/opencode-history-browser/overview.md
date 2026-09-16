# OpenCode History Browser — 项目总览

## 一句话
OpenCode 的浏览器式历史会话管理 UI 插件，替代默认 TUI 界面。

## 定位
作为 OpenCode 的全局 TUI 插件，当执行 `opencode`（无参数）时自动启动浏览器界面，提供比终端 TUI 更丰富的会话管理体验。属于 OpenCode 生态的增强工具。

## 技术栈
- Node.js >= 18 — 运行时
- 纯原生 Web 技术（HTML / CSS / Vanilla JS）— 前端 UI
- `@opencode-ai/sdk` v2 — OpenCode API 客户端
- Node.js 内置 `http` 模块 — 本地 HTTP 服务器
- Node.js 内置 `child_process` — 进程管理、终端启动

## 核心功能
1. 浏览器式会话列表（搜索、筛选、批量操作）
2. 会话详情查看（消息、工具调用、推理过程、任务进度）
3. 继续聊天、发送新消息、选择模型、附加图片
4. 会话管理（置顶、重命名、删除、批量删除、快照）
5. 权限审批、问题回答（OpenCode 交互式请求）
6. 打开独立 CLI 终端窗口
7. 浏览器命令（/skills, /mcp, /logs, /uninstall）
8. 内置诊断（/history-browser-doctor）
9. 闲置自动关闭（15 秒心跳检测）

## 完成状态
✅ 已发布（v0.1.0），在生产环境使用

## 项目规模
- 后端核心：tui.js ~1430 行
- 独立模式：standalone.js ~240 行
- 日志模块：log.js ~58 行
- 前端 UI：app.js ~1100 行，index.html ~119 行，styles.css
- 安装脚本：install-redirect.js ~4 行
- 总代码量：约 3000 行（不含 node_modules）