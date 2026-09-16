# 内嵌 HTTP 服务器 + Token 认证模式

## 适用场景
需要本地浏览器 UI 但不想引入 Express/Koa 等框架的 Node.js 工具。

## 推荐架构
```
Node.js 进程
  └── http.createServer(handler)
      ├── API 路由 (/api/*)
      ├── 静态文件服务
      └── Token 认证中间件

Browser ←→ HTTP (127.0.0.1:port)
```

## 核心实现

### 服务器
```javascript
import { createServer } from "node:http";
import { randomBytes } from "node:crypto";

const token = randomBytes(18).toString("base64url");
const server = createServer((req, res) => {
  if (!isAuthorized(req)) return send401(res);
  // ... route handling
});
```

### 端口自动检测
```javascript
async function listenOnAvailablePort(server, startPort) {
  for (let port = startPort; port < startPort + 20; port++) {
    const ok = await new Promise((resolve) => {
      server.once("error", () => resolve(false));
      server.listen(port, "127.0.0.1", () => resolve(true));
    });
    if (ok) return port;
  }
  throw new Error("No available port");
}
```

### Token 认证
```javascript
function isAuthorized(req, url) {
  const header = req.headers["x-auth-token"];
  const param = url.searchParams.get("token");
  return header === token || param === token;
}
```

## 常见坑点
- Token 在 URL 中传递，日志必须脱敏
- 静态文件服务必须拦截路径穿越攻击（`..`）
- 所有 socket 必须跟踪，关闭时销毁
- 端口范围不要太窄（建议 20+）

## 验收标准
- [ ] Token 认证通过前所有 API 返回 401
- [ ] 静态文件路径穿越被阻止
- [ ] 端口被占用时自动尝试下一个
- [ ] 关闭时所有 socket 被销毁
- [ ] 日志不包含 Token 明文