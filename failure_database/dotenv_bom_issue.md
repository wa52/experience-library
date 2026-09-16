# .env 文件 UTF-8 BOM 导致 python-dotenv 读不到变量

## 问题现象
`load_dotenv(".env", override=True)` 执行后 `os.getenv("KEY")` 返回 `None`。
但 `.env` 文件确实存在且内容正确。

## 影响项目
- global-flow-agent-desktop（PyInstaller 打包的应用）

## 根因
`.env` 文件开头有 UTF-8 BOM（3字节 `\xef\xbb\xbf`）。
`python-dotenv` 的 `load_dotenv()` 不处理 BOM，直接把 BOM 字符作为变量名的一部分：
- 实际变量名：`\ufeffOPENROUTER_API_KEY`（带 BOM 前缀）
- 查询变量名：`OPENROUTER_API_KEY`
- 匹配不上，返回 None

## 解决方案
### 方案一：去除 BOM（推荐）
```python
content = open(".env", "r", encoding="utf-8-sig").read()
open(".env", "w", encoding="utf-8").write(content)
```

### 方案二：代码中 BOM 容错
```python
if not os.getenv(key):
    raw = env_path.read_bytes()
    if raw.startswith(b'\xef\xbb\xbf'):
        text = raw.decode('utf-8-sig')
        for line in text.splitlines():
            if '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()
```

## 教训
- Windows 上某些编辑器（记事本、VS Code 某些配置）保存 UTF-8 文件时会加 BOM
- 使用 `utf-8-sig` 编码读取可以自动跳过 BOM
- `load_dotenv` 返回值可用来判断是否成功加载
