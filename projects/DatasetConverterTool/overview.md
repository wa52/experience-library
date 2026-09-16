# DatasetConverterTool — 项目总览

## 一句话
独立的 YOLO / Label Studio / HALCON 数据集转换工具，提供 CLI 和中文 PyQt5 界面，不修改 Label Studio 核心源码。

## 定位
用于自动标注平台第一阶段的数据准备层。目标是在训练、推理和 ML Backend 接入前，先打通数据能导入、能标注、能导出、能训练的格式闭环。

## 技术栈
- Python 3.10 — 项目运行环境和 Label Studio 1.23 推荐环境
- PyQt5 — 中文桌面界面
- Pillow — 图片尺寸读取
- PyYAML — YOLO `dataset.yaml` / `data.yaml` 解析与生成
- pytest — 自动化测试
- Label Studio 1.23.0 — 本地标注与一键导入目标
- MVTec HALCON runtime — `.hdict` 读写外部依赖

## 核心功能
1. YOLO -> Label Studio JSON
2. Label Studio JSON -> YOLO
3. HALCON `.hdict` / intermediate JSON -> Label Studio JSON
4. HALCON `.hdict` / intermediate JSON -> YOLO
5. YOLO -> HALCON `.hdict` / intermediate JSON
6. Label Studio JSON -> HALCON `.hdict` / intermediate JSON
7. Label Studio 一键导入
8. 图片路径策略：Local Files、Network Share、HTTP、Upload
9. `predictions` 预标注和 `annotations` 已提交标注两种 LS 输出模式

## 完成状态
✅ 第一版可运行。核心转换测试通过，GUI 可启动，Label Studio 1.23 + Python 3.10 环境已整理。

## 项目路径
```text
D:\codex\DatasetConverterTool
```

## 项目内经验文档
```text
D:\codex\DatasetConverterTool\docs\project_experience.md
```
