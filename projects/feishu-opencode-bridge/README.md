# feishu-opencode-bridge

飞书机器人 ↔ OpenCode 的双向桥接。手机飞书发消息 → OpenCode 会话执行 → 流式输出回推飞书卡片；支持多会话、权限确认、问答交互、自定义菜单。

## 技术栈
- TypeScript + Node.js（ESM / NodeNext），tsc 编译到 `dist/`
- `@opencode-ai/sdk`（固定 `"latest"`，字段名会变，需防御性归一化）
- 飞书开放平台卡片消息（`schema: 2.0`）
- Electron 桌面客户端（`desktop/`，仅查看用）

## 状态
菜单功能、跨目录会话聚合、事件去重、TUI 通知已落地并验证；桌面客户端 preload 修复完成。运行中服务：opencode serve（4096）+ 桥接（8098 状态端口 / 8097 诊断端口）。

## 关键要点
- **事件去重（重要）**：桥接同时订阅全局事件流（`/event` 无参，覆盖 serve 默认目录）和目录事件流（`/event?directory=xxx`，每次带 directory 的 API 调用会 `ensureDirectoryEventStream`）。同一事件可能被两条流同时推送 → 业务逻辑执行两遍（飞书回复两次）。修复：`handleEvent` 入口按 `事件类型 + sessionID + 事件ID` 生成指纹，3 秒窗口内去重（`isDuplicateEvent`）。**新增带 directory 的 API 调用点时会自动拉起目录事件流，务必保留去重。**
- **跨目录会话聚合**：`listSessionsAcrossProjects` 只扫 `listProjects()` 返回的 project worktree，会漏掉**非顶层项目**目录（如 `D:/AiProjects/langchain-kb` 是 `D:/AiProjects` 的子 git 根）。修复：对每个 project worktree 递归发现所有子 git 根（`discoverGitRoots`，检测 `.git`，跳过 node_modules 和点目录），逐个 `listSessions({directory})` 聚合。聚合数 179 → 194。
- **会话卡片展示最近 5 天活跃会话**：按 `time.updated ?? time.created` 过滤 5 天窗口，当前绑定会话始终保留；已移除搜索框（用户明确不要）。
- **TUI 会话通知**：手机发消息后调用 `POST /tui/publish`，body `{ type: "tui.session.select", properties: { sessionID } }`，让电脑 opencode TUI 跳转到对应会话。SDK v1/v2 均有此端点。
- **桌面客户端 preload**：`sandbox: true` + `contextIsolation: true` 下 preload 必须用 CommonJS（`preload.cjs`，`require('electron')`），ESM `preload.mjs` 会报 `api not defined`。
- **流式输出保护**：卡片组件预算 180，超限自动分页（`paginateElementsByComponentBudget`）；正文 6000 字、文本段 5000 字、思考 2600 字、工具输出 4000 字上限（截断/中间省略）；刷新 500ms 节流；代码块转义 `\`\`\``。
- **opencode 事件字段变体**：`sessionID`/`sessionId`/`session_id` 等，解析时用 `getFirstString` 兜底。

## 结构
- 入口：`src/index.ts`（bootstrap）→ `src/app.ts` 的 `createApp()`（装配/接线/生命周期）
- 运行态集中在 `src/stream/stream-state.ts`（StreamStateManager）
- 各模块单例：`src/handlers/*`（命令/私聊/群聊/卡片动作/生命周期）、`src/feishu/*`（SDK/卡片/流式）、`src/opencode/*`（SDK/缓冲/队列/提问）、`src/store/*`（持久化）、`src/permissions/handler.ts`
- 命令解析 `src/commands/parser.ts`，执行 `src/handlers/command.ts`
- 桌面客户端：`desktop/main.mjs` + `preload.cjs`
- 状态文件（gitignore，勿提交）：`.chat-sessions.json`、`.user-sessions.json`、`.session-directories.json`、`.session-groups.json`

## 运行
- 前置：已运行 `opencode serve --hostname 127.0.0.1 --port 4096`（默认 4096）+ `.env` 配置 `FEISHU_APP_ID`/`FEISHU_APP_SECRET`
- 开发：`npm run dev`（tsx watch）；构建：`npm run build`（唯一校验）；生产：`npm start`（先 build）
- 桌面客户端：`npm run desktop`；自检：`npm run diagnose`（8097）
- 注意：`opencode serve` 会因 `opencode-mobile` 插件弹出 ngrok authtoken 交互，需按回车跳过

## 位置
`D:\feishu-opencode-bridge\`

## 本次会话要点（2026-08-15）
- 修复"飞书回复两次"：根因是全局事件流 + 目录事件流重复推送同一事件，`handleEvent` 入口加指纹去重（3 秒窗口）
- 修复会话卡片漏会话：`listSessionsAcrossProjects` 递归发现子 git 根目录，覆盖 langchain-kb 等非顶层项目（179 → 194）
- 会话卡片改为展示最近 5 天活跃会话，移除搜索框
- 手机发消息后向 `POST /tui/publish` 广播 `tui.session.select`，让电脑 TUI 刷新到当前会话
- 桌面客户端 preload 修复（ESM → CJS）

## 环境变量
`FEISHU_APP_ID`/`FEISHU_APP_SECRET`（必需）、`OPENCODE_HOST`/`OPENCODE_PORT`（默认 localhost:4096）、`OPENCODE_SERVER_USERNAME`/`PASSWORD`（Basic 鉴权）、`BRIDGE_STATUS_PORT`（8098）、`DIAGNOSE_PORT`（8097）、`ALLOWED_DIRECTORIES`（目录白名单，未配置禁止用户自定义路径）、`DEFAULT_WORK_DIRECTORY`、`TOOL_WHITELIST`、`ENABLE_MANUAL_SESSION_BIND`。
