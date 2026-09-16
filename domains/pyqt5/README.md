# PyQt5 领域经验

> PyQt5 是 Qt5 框架的 Python 绑定，用于构建跨平台桌面应用。

## 关键要点

### 核心模块

| 模块 | 用途 |
|------|------|
| QtWidgets | 窗口、按钮、文本框等标准组件 |
| QtCore | 信号/槽、线程、定时器 |
| QtGui | 绘图、字体、图像处理 |
| QtNetwork | TCP/UDP/HTTP 网络通信 |
| QtMultimedia | 音视频播放 |

### 推荐项目结构

```
project/
├── main.py              # 入口
├── app/
│   ├── __init__.py
│   ├── config.py        # 配置
│   ├── ui/
│   │   ├── main_window.py
│   │   └── dialogs.py
│   ├── services/
│   │   └── worker.py
│   ├── models/
│   │   └── entities.py
│   └── db/
│       └── repository.py
├── resources/
│   └── icons/
├── requirements.txt
└── build.ps1 / build.sh
```

### 信号槽模式

```python
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class Worker(QObject):
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)

    @pyqtSlot()
    def run(self):
        try:
            result = self.do_work()
            self.finished.emit(result)
        except Exception as e:
            self.failed.emit(str(e))

# 使用
self.thread = QThread(self)
self.worker = Worker()
self.worker.moveToThread(self.thread)
self.thread.started.connect(self.worker.run)
self.worker.finished.connect(self.on_finished)
self.thread.start()
```

### 最佳实践

1. **UI 更新必须在主线程**：QThread 中不能直接操作 UI，应通过信号通知主线程
2. **资源管理**：`QApplication` 退出时清理所有资源
3. **布局管理**：使用 QSplitter 替代固定大小，使窗口可缩放
4. **模型/视图分离**：大数据量用 QAbstractTableModel / QSortFilterProxyModel
5. **QSS 样式**：用样式表实现主题切换
6. **打包**：使用 PyInstaller，注意 `--collect-data` 收集数据文件

### 常见坑点

1. **QThread 析构**：线程未结束时直接删除 QThread 对象会崩溃
2. **Python 导入顺序**：PyQt5 必须在 from PyQt5 之前先 import
3. **中文显示**：某些 Qt 版本需要设置字体才能正常显示中文
4. **PyInstaller**：打包时必须用 `--collect-data` 或 `hiddenimports` 确保资源完整

### PyInstaller 打包经验（2026-06 更新）

#### 必须添加的 DLL
`_ssl.pyd` 需要 `libssl-3.dll` + `libcrypto-3.dll`，后者常被遗漏：
```powershell
--add-binary "path\to\libcrypto-3.dll;."
--add-binary "path\to\libssl-3.dll;."
```

#### 路径处理（冻结模式兼容）
```python
def _output_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.resolve()
    return PROJECT_ROOT
```
- 可写文件（日志、报告、数据库）→ `_output_root()`
- 只读文件（配置、prompts）→ `_data_root()`
- `.env` 文件 → exe 同级目录

#### 避免引入重型依赖
如只需 `ask_deepseek` 函数，不要从 `ui.py`（含 `import streamlit`）导入，应独立到轻量模块。

#### 动态导入处理
函数内部的 `from x import y` 不会被 PyInstaller 静态扫描到，需要用 `--hidden-import` 显式声明：
```powershell
--hidden-import "package.module"
```
