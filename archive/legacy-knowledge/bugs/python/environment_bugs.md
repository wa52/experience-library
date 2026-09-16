---
title: 环境 Bug 记录
tags: [bug, python, cuda, pip, matplotlib]
created: 2025-03-01
updated: 2026-07-12
category: bug
severity: medium
resolved: false
---

# 环境 Bug 记录

## Bug 1：CUDA 版本不兼容导致 torch 无法调用 GPU

### 问题现象
`torch.cuda.is_available()` 返回 `False`，但 `nvidia-smi` 能正常看到 GPU。

### 可能原因
- PyTorch 的 CUDA 版本与系统驱动不匹配
- 没有安装 CUDA 版本的 PyTorch（安装了 CPU-only 版本）
- CUDA 运行时库版本冲突

### 排查步骤
1. `nvidia-smi` 查看驱动支持的 CUDA 最高版本
2. `python -c "import torch; print(torch.version.cuda)"` 查看 PyTorch 的 CUDA 版本
3. 检查 PyTorch 安装方式：`pip list | findstr torch`

### 解决方案
```bash
# 查看当前驱动支持的最高 CUDA 版本
nvidia-smi

# 重新安装对应 CUDA 版本的 PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# 如果不需要 CUDA，使用 CPU 版本
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 相关项目
- image_inference_tool
- yolo_tool

---

## Bug 2：pip 依赖冲突

### 问题现象
安装某个包时出现 `pip check` 报告依赖版本冲突，或运行时导入报错。

### 可能原因
- 多个包依赖同一个库的不同版本
- 全局环境混用不同项目的依赖
- 使用了过时的 pip 版本

### 排查步骤
1. `pip check` 查看冲突详情
2. 查看冲突的包及其依赖树：`pipdeptree`

### 解决方案
- 使用虚拟环境（venv / conda），每个项目独立环境
- 明确约束版本：`pip install package==X.Y.Z`
- 先卸载冲突版本再安装兼容版本
- 最后手段：`pip install --force-reinstall` 强制重装

### 相关项目
- 所有项目

---

## Bug 3：中文字体在 matplotlib 中乱码

### 问题现象
matplotlib 绘图中文字显示为方框或乱码。

### 可能原因
matplotlib 默认不包含中文字体，需要额外配置。

### 解决方案
```python
import matplotlib.pyplot as plt

# 方法 1：指定系统已有中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # Windows
# 或 ['SimHei']、['KaiTi']

# 方法 2：下载并注册字体
import matplotlib.font_manager as fm
fm.fontManager.addfont('path/to/your/font.ttf')
plt.rcParams['font.sans-serif'] = ['Your Font Name']

# 关键：修复负号显示
plt.rcParams['axes.unicode_minus'] = False
```

### 相关项目
- image_inference_tool
