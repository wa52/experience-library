# 全局 CLI 命令的 config 模块被其他项目抢占

## 问题现象

把工具安装为全局命令（`pip install -e .`）后，在任意目录执行 `veriagent`，
启动即抛 `AttributeError: module 'config' has no attribute 'HOST'`，
或更隐蔽地：读到的是**别的项目**的配置（端口、数据目录全不对）。

## 影响项目

- VeriAgent 全局命令 `veriagent` / `veri-agent`（`src/veri_agent/cli.py`）
- 任何依赖顶层 `config.py` 且需要全局运行的 Python 工具

## 根因

项目使用顶层 `config.py`（非包内模块），并在代码里 `import config`。
全局命令从任意工作目录启动时，Python 把**当前工作目录**加入 `sys.path` 首位；
如果该目录（或它的上级入口）恰好也有 `config.py`（例如 langchain-kb 的根目录就有），
`import config` 就会解析到错误的那一个。`pip install -e .` 只保证了包内模块可导入，
**管不到顶层模块的命名冲突**。

实测：在 `C:\Users\feng\AppData\Local\Temp\opencode` 下运行，
`python -c "import config"` 解析到的是 `D:\AiProjects\langchain-kb\config.py`。

## 解决方案

- 入口模块在 `import config` 之前，**显式把本项目根目录插到 `sys.path` 最前面**：

```python
from pathlib import Path
_ROOT = Path(__file__).resolve().parents[2]
if (_ROOT / "config.py").exists() and str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
import config  # 现在一定解析到本项目
```

- 更彻底的做法：把 `config.py` 迁进包内（如 `veri_agent.config`），彻底消除顶层命名冲突；
  但会改动所有 `import config` 调用点，收益大、成本也大，按需取舍。

## 教训

- 顶层模块（`config.py`、`utils.py` 等）在"多项目共存 + 全局安装"场景极易被抢占，
  启动路径相关的 bug 要先用 `import module; print(module.__file__)` 确认解析到谁。
- 全局命令的可移植性要用**非项目目录**实测，不能只在项目根目录跑一遍就交付。
- 排查"全局命令行为异常"时，第一件事：打印 `config.__file__` 看是不是自己的。
