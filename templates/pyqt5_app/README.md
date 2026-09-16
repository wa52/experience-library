# PyQt5 应用模板

## 适用场景
新启动一个 PyQt5 桌面应用项目。

## 目录结构建议
```
project/
├── main.py              # 应用入口
├── requirements.txt     # 依赖
├── app/
│   ├── __init__.py
│   ├── config.py        # 应用配置
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   └── dialogs.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── workers.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── entities.py
│   └── db/
│       ├── __init__.py
│       └── database.py
├── resources/
│   ├── icons/
│   └── styles.qss
├── build.ps1            # Windows 打包脚本
└── build.sh             # Linux/macOS 打包脚本
```

## 入口模板
```python
import sys
from PyQt5.QtWidgets import QApplication
from app.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MyApp")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
```

## 打包命令
```bash
# Windows
pip install pyinstaller
pyinstaller --windowed --name MyApp --add-data "resources;resources" main.py

# Linux
pyinstaller --windowed --name MyApp --add-data "resources:resources" main.py
```

## 参考
- patterns/pyqt5_roi_tool.md
- patterns/yolo_inference_gui.md
