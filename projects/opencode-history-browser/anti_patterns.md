# OpenCode History Browser — 反模式

## AP-001：在日志中记录未脱敏的 URL

- **症状**：安全审计发现 token 泄漏
- **正确做法**：所有 URL 日志记录前替换 token 参数为 [redacted]

## AP-002：在前端全局状态中堆叠所有数据

- **症状**：代码中有 18 个全局变量（sessions, current, permissions, questions 等），难以追踪状态变化
- **正确做法**：使用简单的状态管理对象或 class 封装全局状态

## AP-003：DOM 操作直接渲染而非 diff

- **症状**：每次刷新重建整个 DOM，大列表时性能差
- **正确做法**：只更新变化的节点，或使用 innerHTML 缓存

## AP-004：一次函数承载过多职责

- **症状**：handleRequest ~200 行，包含 30+ 路由分支
- **正确做法**：按路由拆分为独立 handler 函数

## AP-005：硬编码超时和轮询间隔

- **症状**：promptPollMs=1500, promptMaxWaitMs=600000, 散落在代码各处
- **正确做法**：统一在文件头定义为常量并加注释说明理由

## AP-006：在同步路径检查中混合异步和同步文件 API

- **症状**：同时使用 existsSync()、statSync() 和 readFile()、writeFile() 等异步 API
- **正确做法**：统一风格，新代码全部使用 fs/promises

## AP-007：错误处理的方式不一致

- **症状**：部分地方 try/catch 静默忽略，部分地方 throw，部分地方 assertOk
- **正确做法**：统一错误处理策略：边界处捕获 + 转换 + 记录 + 恢复