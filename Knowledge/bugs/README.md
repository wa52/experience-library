---
title: Bug 知识库
tags: [index, bug]
created: 2026-07-12
updated: 2026-07-12
category: bug
---

# Bug 知识库

本目录按主题分类记录开发中遇到的 Bug 及解决方案。

## 目录结构

```
bugs/
├── halcon/
│   └── halcon_bugs.md        — HALCON 授权与 .NET 集成问题
├── python/
│   ├── dotenv_bom_issue.md   — .env BOM 导致 dotenv 失效
│   ├── environment_bugs.md   — CUDA / pip / 字体问题
│   └── pyqt_bugs.md          — QThread / QGraphicsView / PyInstaller 问题
└── deployment/
    ├── pyinstaller_ssl_dll_missing.md — SSL DLL 缺失
    └── yolo_bugs.md           — ONNX 推理 / OOM 问题
```

## 标签体系

| 标签 | 说明 |
|------|------|
| `bug` | 所有条目均为 Bug 记录 |
| `halcon` | HALCON 相关 |
| `python` | Python 环境与库相关 |
| `deployment` | 部署与打包相关 |
| `pyqt5` | PyQt5 相关 |
| `yolo` | YOLO 相关 |

## 快速入口

- [HALCON 授权问题](halcon/halcon_bugs.md)
- [Python 环境问题](python/environment_bugs.md)
- [PyQt5 线程问题](python/pyqt_bugs.md)
- [PyInstaller SSL 缺失](deployment/pyinstaller_ssl_dll_missing.md)
- [YOLO ONNX 问题](deployment/yolo_bugs.md)
