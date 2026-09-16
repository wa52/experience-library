# .env BOM 导致 dotenv 失效

## 问题
`load_dotenv` 读不到变量，但文件存在且内容正确。

## 根因
UTF-8 BOM 导致变量名变成 `\ufeffKEY`。

## 修复
```python
# 去除 BOM
content = open(".env", encoding="utf-8-sig").read()
open(".env", "w", encoding="utf-8").write(content)
```
