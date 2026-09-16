# OpenCode检索规则

本文件是 OpenCode 使用 `D:\项目经验库` 时的强制检索入口。目标是解决检索范围过窄、只命中一个相关文件就开始总结的问题。

本库只保存提炼后的经验，不保存原始资料、手册、官方例程、图片、模型、训练集或第三方源码。检索本库时只查经验类目录。

## 一句话原则

先多路径检索，再总结；先看索引，再核对原文；命中一个文件不能停止。

## 必查路径矩阵

| 层级 | 必查路径 | 判断依据 |
|---|---|---|
| 目录入口 | `README.md`、`00_索引/README.md` | 目录结构、固定入口、当前规则 |
| 全局规则 | `00_索引/GLOBAL_RULES.md` | 是否有强制搜索和复用要求 |
| 项目经验 | `00_索引/项目经验索引.md`、`projects/` | 已做项目、架构、踩坑、验收 |
| 问题库 | `failure_database/` | 错误现象、原因、解决方案 |
| 代码片段 | `patterns/`、`domains/`、`tools/` | 可复用代码、模式、领域总结、工具 |

## 检索步骤

1. 从用户问题提取关键词：中文描述、英文术语、项目名、错误现象、技术栈。
2. 先搜 `00_索引`、`README.md`，确定候选方向。
3. 搜索 `projects/`、`failure_database/`、`patterns/`、`domains/`、`tools/`。
4. 如果命中项目经验，必须同时检查相关 Bug、模式和领域总结。
5. 输出结论前列出检索证据，包括已查路径和命中文件。

## 禁止行为

- 禁止只查一个命中文档就总结。
- 禁止只读 README 就回答技术方案。
- 禁止检索或引用本库外的原始资料作为经验库结论。
- 禁止只查旧目录而忽略当前经验目录。
- 禁止搜索词过窄，例如只搜 `OCR`，不搜 `read_ocr`、`deep_ocr`、`text recognition`。

## 推荐命令

```powershell
# 第一轮：索引和入口
rg -n "关键词1|关键词2|算子名|文件名" D:\项目经验库\00_索引 D:\项目经验库\README.md

# 第二轮：项目经验、问题库、代码片段
rg -n "关键词1|关键词2|算子名|文件名" D:\项目经验库\projects D:\项目经验库\failure_database D:\项目经验库\patterns D:\项目经验库\domains D:\项目经验库\tools
```

## 视觉开发关键词扩展表

| 问题 | 同时搜索 |
|---|---|
| 模板匹配 | `模板匹配`、`template matching`、`shape_model`、`find_shape_model`、`create_shape_model`、`ncc_model` |
| OCR | `OCR`、`read_ocr`、`do_ocr`、`deep_ocr`、`text recognition` |
| 异常检测 | `异常检测`、`anomaly`、`anomaly detection`、`surface inspection` |
| 目标检测 | `目标检测`、`object_detection`、`object detection`、`detect object` |
| 数据集 | `dataset.hdict`、`hdict`、`数据集`、`dataset`、`HALCON 数据集` |
| 相机采集 | `相机采集`、`framegrabber`、`grab_image`、`open_framegrabber`、`acquisition` |
| Blob 分析 | `Blob分析`、`blob`、`threshold`、`connection`、`select_shape` |
| 测量 | `测量`、`measure`、`metrology`、`caliper`、`distance` |
| 形状匹配 | `形状匹配`、`shape matching`、`shape_model`、`find_shape_model` |

### 查询优先级

```
00_索引 → index → projects → failure_database → patterns → domains → tools
```

## 回答模板

```text
检索证据：
- 检索词：...
- 已查索引：...
- 已查项目经验：...
- 已查问题库/代码片段：...
- 采用结果：...

结论：...
路径：...
关键内容：...
```
