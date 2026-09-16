---
title: PyInstaller SSL DLL 缺失
tags: [bug, deployment, pyinstaller, ssl, dll]
created: 2025-05-01
updated: 2026-07-12
category: bug
severity: critical
resolved: true
---

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
