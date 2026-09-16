# OpenCode History Browser — 可复用模块

## 1. 内嵌 HTTP 服务器 + Token 认证模板

**位置**：`tui.js` 中 ensureServer() 和 isAuthorized()

**用途**：任何需要本地浏览器 UI + Node.js 后端的工具

**提取方式**：
```javascript
const server = createServer(handler);
server.on("connection", (socket) => { /* track sockets */ });
// 端口自动检测
for (let port = start; port < start + 20; port++) {
  // try listen
}
// Token 认证
const token = randomBytes(18).toString("base64url");
// Header + URL 参数双重校验
```

## 2. 进程锁（文件锁）实现

**位置**：`standalone.js` 中 acquireInstanceLock()

**用途**：防止同一程序重复启动

**核心逻辑**：
```javascript
const fd = await open(lockFile, "wx");   // 原子创建
// 异常退出兜底：读取旧锁 → 健康检查 → 清理
const existing = JSON.parse(await readFile(lockFile, "utf8"));
const response = await fetch(new URL("/api/health", existing.url));
if (response.ok) { /* 打开已有实例 */ }
```

## 3. 路径提取器（消息文本→可点击路径）

**位置**：`tui.js` 中 resolveLocalPaths() / longestExistingPath()

**用途**：从自由文本中提取并验证文件路径

**支持格式**：
- 反引号包裹的路径：`` `C:\path\to\file` ``
- 引号包裹的路径：`"C:\path\to\file"`
- Windows 绝对路径：`C:\Users\...`
- Unix 绝对路径：`/home/user/...`
- 相对路径：`./src/file.ts`, `../parent/file.ts`
- 网络路径：`\\server\share\...`

## 4. Balanced Snapshot 构建器

**位置**：`tui.js` 中 buildBalancedSnapshot()

**用途**：将长会话压缩为可继续工作的上下文

**组成**：
- Source（标题、ID、目录、更新时间）
- Goal（第一条用户消息）
- Current State（最后一条助手 + 用户消息）
- Important Details（路径、错误、决策等关键信号）
- Recent Context（最近 10 条消息摘要）

## 5. 命令重定向模式

**位置**：`tui.js` 中 ensureCommandRedirect() / restoreCommandRedirect()

**用途**：在保留原命令功能的前提下，劫持默认命令行为

**实现**：原命令备份为 `opencode-cli.cmd/ps1`，新命令加入判断逻辑，有参数时跳转到 cli 版本

## 6. 跨平台路径规范化

**位置**：`tui.js` 中 normalizeLocalPath() / cleanPathLabel()

**用途**：统一处理用户输入的路径，去除各种引号和前后缀

## 7. 闲置自动关闭机制

**位置**：`tui.js` 中 startIdleMonitor() / closeServer()

**用途**：防止后台进程残留

**核心**：15 秒轮询检查服务器是否在监听，浏览器通过心跳和 browser-close 通知报告存活