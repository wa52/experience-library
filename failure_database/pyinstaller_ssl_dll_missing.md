# PyInstaller 打包后 SSL 模块加载失败（libcrypto-3.dll 缺失）

## 问题现象
打包后的 exe 在调用 `requests` / `urllib3` 等 HTTPS 请求时报错：
```
DLL load failed while importing _ssl: 找不到指定的模块。
```

## 影响项目
- global-flow-agent-desktop（PyInstaller 打包 PyQt5 应用）

## 根因
PyInstaller 6.x 自动发现 `_ssl.pyd` 和 `libssl-3.dll`，但可能遗漏 `libcrypto-3.dll`。
`_ssl.pyd` 运行时需要 `libcrypto-3.dll` 在同一个目录下。

## 解决方案
在 PyInstaller 命令中显式添加缺失的 DLL：
```powershell
--add-binary "C:\Users\<user>\AppData\Local\Python\pythoncore-3.14-64\DLLs\libcrypto-3.dll;."
--add-binary "C:\Users\<user>\AppData\Local\Python\pythoncore-3.14-64\DLLs\libssl-3.dll;."
```

## 教训
- PyInstaller 的自动依赖发现对 OpenSSL DLL 不完整
- 打包后应先验证 `_ssl` 模块能否正常 import
- 检查 `_internal` 目录下是否同时存在 `libcrypto-3.dll` 和 `libssl-3.dll`
