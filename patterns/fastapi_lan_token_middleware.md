# FastAPI 局域网访问令牌中间件模式

## 适用场景
本地 Web 服务（FastAPI/Starlette）默认绑 127.0.0.1，需支持局域网访问时做简单令牌保护：
本机回环免登录、非回环需 `Authorization: Bearer <TOKEN>`，不引入完整账号体系。

## 实现要点（Starlette BaseHTTPMiddleware）
```python
def is_loopback(host: str) -> bool:
    if host in ("localhost", "localhost."):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback   # 含 ::ffff:127.0.0.1
    except ValueError:
        return False

def _authorized(host, auth_header) -> bool:
    if is_loopback(host): return True            # 本机永远免登录
    if not LAN_TOKEN: return True                # 未配置令牌 = 无保护
    if not auth_header: return False
    scheme, _, token = auth_header.partition(" ")
    return scheme.lower() == "bearer" and hmac.compare_digest(token, LAN_TOKEN)
```

- 门控路径：`path.lower().startswith(("/api/", "/mcp"))`（大小写不敏感）。
- 注册顺序：中间件要**最外层**（`add_middleware` 顺序 = 后注册先执行，注意 FastAPI 是后注册的反向）。
- `hmac.compare_digest` 常量时间比较，防时序侧信道。
- `LAN_TOKEN` 为空 = 允许（默认仅本机安全），web 前端 401 弹令牌输入框，token 存 sessionStorage。

## 测试封闭性（关键）
环境 `.env` 里开发者可能设置了 `LAN_TOKEN`，会污染整个 API/MCP 测试套件（全部 401）。
**必须**在 `tests/conftest.py` 加 autouse fixture 强制 `config.LAN_TOKEN = ""`：

```python
@pytest.fixture(autouse=True)
def _no_lan_token(monkeypatch):
    monkeypatch.setattr("config.LAN_TOKEN", "")
```

具体安全测试再用 `patch("config.LAN_TOKEN", "sekrit")` 显式覆盖。
TestClient 的 client host 是 `"testclient"`（非回环）→ 正好用来测 401/200 集成路径。

## 配套
- 运行配置开关实时切换：`dotenv.set_key(env_path, KEY, value)` + `os.environ[KEY]=v` + 更新 `config` 模块属性 → 下次调用即生效，无需重启（见 runtime_env_config_toggle 模式）。
