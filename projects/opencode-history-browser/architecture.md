# OpenCode History Browser — 架构设计

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│  浏览器端 (Browser)                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  app.js / index.html / styles.css                        │  │
│  │  - 纯前端 SPA                                            │  │
│  │  - 通过 fetch 调用后端 API                                │  │
│  │  - 轮询实现实时刷新（1.5s 间隔）                           │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │ HTTP (127.0.0.1:8765)                  │
├───────────────────────┼─────────────────────────────────────────┤
│  后端服务器 (Node.js http)                                    │
│  ┌────────────────────┴─────────────────────────────────────┐  │
│  │  tui.js (1430 行)                                       │  │
│  │  - 内嵌 HTTP 服务器（端口自动检测 8765~8795）              │  │
│  │  - 路由：/api/sessions, /api/models, /api/permissions    │  │
│  │  - 静态文件服务                                           │  │
│  │  - Token 认证（随机 18 字节 base64url）                   │  │
│  │  - 闲置监测（15 秒自动关闭）                              │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
├───────────────────────┼─────────────────────────────────────────┤
│  连接层 (OpenCode SDK)                                        │
│  ┌────────────────────┴─────────────────────────────────────┐  │
│  │  @opencode-ai/sdk/v2/client                              │  │
│  │  - session.list / session.get / session.prompt           │  │
│  │  - config.providers / question.* / permission.*          │  │
│  │  - tui.selectSession / tui.openModels 等                 │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
├───────────────────────┼─────────────────────────────────────────┤
│  独立模式 (Standalone)                                       │
│  ┌────────────────────┴─────────────────────────────────────┐  │
│  │  standalone.js (240 行)                                  │  │
│  │  - 自动启动 opencode serve 子进程                         │  │
│  │  - 进程锁（互斥，防重复启动）                              │  │
│  │  - 端口自动检测（4096 起）                                 │  │
│  │  - 故障恢复与兜底                                        │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 两种运行模式

### 模式 1：TUI 插件模式（默认）
```
opencode（无参数）
  → OpenCode 主进程加载 tui.js 插件
  → 插件注册 /history-browser 命令
  → 启动内嵌 HTTP 服务器（端口 8765~8795）
  → 打开浏览器 → 用户交互
  → 闲置 15 秒 + 浏览器关闭 → 自动关闭服务器
```

### 模式 2：独立模式（standalone.js）
```
用户双击 OpenCode Browser.vbs
  → standalone.js 启动
  → 获取进程锁（防止重复）
  → spawn opencode serve（隐藏窗口）
  → 等待 server ready（最长 20 秒）
  → 启动浏览器 host → 打开浏览器
  → 退出时 kill 子进程 + 清理锁
```

## 核心 API 路由

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /api/sessions?q= | 搜索会话列表 |
| GET | /api/sessions/:id | 获取会话详情 |
| POST | /api/sessions/:id/prompt | 发送消息 |
| POST | /api/sessions/:id/rename | 重命名 |
| POST | /api/sessions/:id/pin | 置顶/取消 |
| POST | /api/sessions/:id/delete | 删除 |
| POST | /api/sessions/:id/snapshot | 创建快照 |
| POST | /api/sessions/:id/abort | 中止回复 |
| POST | /api/sessions/:id/open | 在 TUI 中打开 |
| POST | /api/sessions/delete | 批量删除 |
| POST | /api/open-new | 新建聊天 |
| GET | /api/models | 模型列表 |
| GET | /api/permissions | 权限请求列表 |
| GET | /api/questions | 问题列表 |
| POST | /api/questions/:id/reply | 回答问题 |
| POST | /api/questions/:id/reject | 拒绝问题 |
| POST | /api/permissions/:id/reply | 审批权限 |
| POST | /api/open-terminal | 打开终端 |
| POST | /api/local-path | 打开本地路径 |
| POST | /api/heartbeat | 心跳 |
| GET | /api/skills | 技能列表 |
| GET | /api/mcp | MCP 状态 |
| GET | /api/logs | 日志 |
| POST | /api/uninstall | 卸载 |

## 认证机制
- 服务器启动时生成随机 18 字节 token
- 通过 URL query 参数 `?token=` 传递
- 前端通过 `X-History-Browser-Token` header 和 query 参数双重认证
- 日志中自动 redact token 信息

## 实时更新机制
- 消息发送后：前端轮询（1.5s）会话状态
- 通过 messageSignature 比对检测变化
- Stable fallback：3 分钟无变化则停止轮询
- 当前会话激活时持续 live refresh