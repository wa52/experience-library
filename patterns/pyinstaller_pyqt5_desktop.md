# PyInstaller 打包 PyQt5 桌面应用模式

## 适用场景
将 Python + PyQt5 桌面应用打包为 Windows 独立 exe，尤其是包含 langchain、yfinance、pandas 等重量级依赖的项目。

## 核心命令模板

```powershell
python -m PyInstaller --onedir `
    --name "AppName" `
    --distpath ".\dist" `
    --workpath ".\build" `
    --add-data "config;package/config" `
    --add-data "prompts;package/prompts" `
    --add-binary "path\to\libcrypto-3.dll;." `
    --hidden-import "package.module" `
    --collect-all "package" `
    --noconfirm `
    "launcher.py"
```

## 关键参数说明

| 参数 | 用途 |
|------|------|
| `--onedir` | 生成目录模式（比 onefile 启动快，便于调试） |
| `--add-data` | 打包数据文件（config、prompts 等） |
| `--add-binary` | 显式添加缺失的 DLL（如 libcrypto-3.dll） |
| `--hidden-import` | 强制包含动态导入的模块 |
| `--collect-all` | 收集包的所有子模块和数据 |

## 路径处理模式（冻结模式兼容）

```python
import sys
from pathlib import Path

def _data_root() -> Path:
    """只读数据目录（打包后指向 _MEIPASS）"""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS).resolve()
    return PROJECT_ROOT  # 开发时指向项目根

def _output_root() -> Path:
    """可写输出目录（打包后指向 exe 同级）"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.resolve()
    return PROJECT_ROOT  # 开发时指向项目根
```

## 常见坑点

### 1. SSL DLL 缺失
`_ssl.pyd` 需要 `libssl-3.dll` + `libcrypto-3.dll`，PyInstaller 可能遗漏后者。
显式 `--add-binary` 添加。

### 2. 动态导入丢失
`from x import y` 放在函数内部（懒加载）时，PyInstaller 静态分析可能发现不了。
用 `--hidden-import` 显式声明。

### 3. streamlit 等重型依赖
如果应用只用到了包中的某个函数（如 `ask_deepseek`），但包顶层 `import streamlit`，会导致打包体积暴增且 metadata 可能缺失。
**解决方案**：将所需函数独立到新模块，避免引入无关重型依赖。

### 4. .env 文件路径
打包后 `.env` 应放在 exe 同级目录。
开发时放在项目根目录。
用 `_output_root()` 统一查找路径。
