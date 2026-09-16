# PyInstaller SSL DLL 缺失

## 问题
PyInstaller 打包后 `import _ssl` 报 `DLL load failed`。

## 根因
`libcrypto-3.dll` 未自动包含。

## 修复
```powershell
--add-binary "path\to\libcrypto-3.dll;."
--add-binary "path\to\libssl-3.dll;."
```
