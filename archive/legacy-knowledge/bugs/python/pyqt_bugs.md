---
title: PyQt5 Bug 记录
tags: [bug, python, pyqt5, qthread, graphicsview, pyinstaller]
created: 2025-04-01
updated: 2026-07-12
category: bug
severity: high
resolved: true
---

# PyQt5 Bug 记录

## Bug 1：QThread 中更新 UI 导致崩溃

### 问题现象
在 QThread 的 worker 线程中直接调用 UI 更新方法（如 `setText()`、`addItem()`），程序闪退或报错。

### 可能原因
Qt 要求所有 UI 操作必须在主线程中执行。工作线程不能直接操作 UI 对象。

### 排查步骤
1. 确认崩溃时的调用栈是否有 UI 操作方法
2. 检查 worker 的 `run()` 方法中是否直接操作了 UI 控件

### 解决方案
通过信号/槽机制，让工作线程发射信号，主线程响应信号来更新 UI：

```python
class Worker(QObject):
    progress = pyqtSignal(int)
    result = pyqtSignal(object)
    error = pyqtSignal(str)

    @pyqtSlot()
    def run(self):
        try:
            for i in range(100):
                # 模拟工作
                import time
                time.sleep(0.1)
                self.progress.emit(i)
            self.result.emit("完成")
        except Exception as e:
            self.error.emit(str(e))

# 主线程连接信号
self.worker.progress.connect(self.progress_bar.setValue)
```

### 相关项目
- image_inference_tool
- file_matcher

---

## Bug 2：QGraphicsView 缩放后坐标偏移

### 问题现象
在 QGraphicsView 中缩放视图后，鼠标点击位置和实际场景坐标不一致。

### 可能原因
没有正确转换坐标，直接用了 widget 坐标而不是 scene 坐标。

### 解决方案
```python
# 鼠标事件中转换坐标
def mousePressEvent(self, event):
    # widget 坐标 → scene 坐标
    scene_pos = self.mapToScene(event.pos())
    # 现在 scene_pos 是场景坐标系中的准确位置
    print(f"Scene coordinates: ({scene_pos.x()}, {scene_pos.y()})")
    super().mousePressEvent(event)
```

### 相关项目
- image_inference_tool

---

## Bug 3：PyInstaller 打包后缺少 Qt 平台插件

### 问题现象
打包后的 exe 运行时报错 `"Failed to load platform plugin 'windows'. Available platforms are:"` 或直接没反应。

### 可能原因
PyInstaller 没有正确收集 Qt 平台插件，`--windowed` 模式隐藏了控制台导致看不到错误。

### 排查步骤
1. 临时改为 `console=True` 重新打包查看错误
2. 检查 dist 目录中是否有 `PyQt5\Qt5\plugins\platforms` 目录

### 解决方案
- 用 `--collect-data PyQt5` 收集 PyQt5 所有数据文件
- 或用 `--add-data` 手动添加插件目录
- 确保 `.spec` 文件中的 `datas` 包含了 Qt 插件

### 相关项目
- image_inference_tool
- LiteLLM Chat Client
