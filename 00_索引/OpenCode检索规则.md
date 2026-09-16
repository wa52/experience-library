# OpenCode检索规则

本文件是 OpenCode 使用 `D:\项目经验库` 时的快速检索说明。目标是在不增加固定前置步骤的情况下，减少重复踩坑。

本库只保存提炼后的经验，不保存原始资料、手册、官方例程、图片、模型、训练集或第三方源码。检索本库时只查经验类目录。

## 一句话原则

先快速检索，再按相关性展开；索引页是可选导航，不是 Agent 门禁。

## 必查路径矩阵

| 层级 | 必查路径 | 判断依据 |
|---|---|---|
| 项目经验 | `projects/` | 已做项目、架构、踩坑、验收 |
| 问题库 | `failure_database/` | 错误现象、原因、解决方案 |
| 模式和领域 | `patterns/`、`domains/` | 可复用方案和领域总结 |

## 检索步骤

1. 从用户问题提取关键词：中文描述、英文术语、项目名、错误现象、技术栈。
2. 直接搜索 `failure_database/`、`projects/`、`patterns/`、`domains/`。
3. 默认先取 Top 3-5 条候选，明显相关时再读取全文。
4. 检查版本、平台和约束后决定是否复用。
5. 需要说明依据时列出实际采用的来源文件。

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
failure_database → projects → patterns → domains
```

## 回答模板

```text
检索结果：
- 检索词：...
- 候选：...
- 采用结果及适用性判断：...

结论：...
路径：...
关键内容：...
```
