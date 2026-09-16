# OpenCode SDK API 版本兼容问题

## 问题现象
不同版本 OpenCode 的 API 结构不同，直接调用实验性 API 会失败。

## 影响项目
opencode-history-browser

## 根因
OpenCode SDK 快速迭代，session.list 可能在 experimental 命名空间下，也可能不在。

## 解决方案
```javascript
const client = api.client.experimental?.session || api.client.session;
```

## 备用方案
SDK 调用全部失败时回退到 CLI 命令行解析：
```javascript
const { stdout } = await execFileAsync(command, ["--pure", "session", "list"]);
const sessions = stdout.split("\n").map(parseLine).filter(Boolean);
```

## 教训
- 调用第三方 SDK 时始终假设 API 可能变更
- 提供至少两层 fallback
- 记录实际使用的 API 版本以便调试